import tkinter as tk
from datetime import datetime
from src.interface.ui.helpers import connect, get_uptime, get_status_model
from src.interface.settings import COLORS_DARK, COLORS_WIDGETS

START_TIME = datetime.now()

BOX_W = 220
BOX_H = 110

def contar_ocorrencias():
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM ocorrencias")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM ocorrencias WHERE tipo='video'")
    video = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM ocorrencias WHERE tipo='audio'")
    audio = c.fetchone()[0]
    conn.close()
    return total, video, audio

def criar_box(parent, titulo, valor, bg):
    box = tk.Frame(parent, bg=bg, width=BOX_W, height=BOX_H)
    box.pack_propagate(False)  # força o tamanho fixo real

    tk.Label(box, text=titulo, font=("Courier New", 12, "bold"), fg="white", bg=bg).pack(pady=(10, 10))
    tk.Label(box, text=valor, font=("Arial", 24, "bold"), fg="white", bg=bg).pack()
    return box

def render_dashboard(root):

    top_row = tk.Frame(root, bg=COLORS_DARK["background"])
    bottom_row = tk.Frame(root, bg=COLORS_DARK["background"])

    top_row.pack(pady=(0,10))
    bottom_row.pack(pady=(0,10))

    # cria as caixas
    box1 = criar_box(top_row, "Total de Ocorrências", 0, COLORS_WIDGETS["primary"])
    box2 = criar_box(top_row, "Ocorrências de Vídeo", 0, COLORS_WIDGETS["secondary"])
    box3 = criar_box(top_row, "Ocorrências de Áudio", 0, COLORS_WIDGETS["tertiary"])
    box4 = criar_box(bottom_row, "Data de inicialização", START_TIME.strftime("%d/%m/%Y"), COLORS_WIDGETS["quaternary"])
    box5 = criar_box(bottom_row, "Tempo de execução", START_TIME, COLORS_WIDGETS["quaternary"])
    box6 = criar_box(bottom_row, "Status do Modelo", get_status_model().get("status"), get_status_model().get("color"))

    # posiciona lado a lado no pack das rows
    for b in (box1, box2, box3):
        b.pack(side="left", padx=10)

    for b in (box4, box5, box6):
        b.pack(side="left", padx=10)

    # labels dinâmicos de atualização
    def safe_set(box, child_index, value):
        """Seta texto com segurança: só se o widget existir e tiver filhos."""
        try:
            if not box.winfo_exists():
                return False
            children = box.winfo_children()
            if len(children) > child_index and children[child_index].winfo_exists():
                children[child_index].config(text=value)
                return True
        except Exception:
            return False
        return False

    def atualizar():
        try:
            # se o painel foi destruído, aborta (não reagenda)
            if not root.winfo_exists():
                return

            total, video, audio = contar_ocorrencias()

            # atualiza cada box de forma segura (seus Labels são filhos do Frame)
            safe_set(box1, 1, total)   # supondo que o segundo filho seja o Label do valor
            safe_set(box2, 1, video)
            safe_set(box3, 1, audio)
            safe_set(box4, 1, START_TIME.strftime("%d/%m/%Y"))
            # calcular tempo em execução para box5, exemplo:
            safe_set(box5, 1, get_uptime(START_TIME))

        except Exception as e:
            # loga e aborta para evitar loop de erros
            print("dashboard atualizar abortado:", e)
            return

        # Reagenda apenas se root ainda existir
        if root.winfo_exists():
            root.after(1000, atualizar)

    # inicia a atualização
    atualizar()
