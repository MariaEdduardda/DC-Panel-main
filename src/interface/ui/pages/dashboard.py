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
    def atualizar():
        total, video, audio = contar_ocorrencias()
        box1.winfo_children()[1].config(text=total)
        box2.winfo_children()[1].config(text=video)
        box3.winfo_children()[1].config(text=audio)
        box5.winfo_children()[1].config(text=get_uptime(START_TIME))
        box6.winfo_children()[1].config(bg=get_status_model().get("color"), text=get_status_model().get("status"))
        root.after(1000, atualizar)

    root.after(1000, atualizar)
