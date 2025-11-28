import tkinter as tk
from datetime import datetime
from src.interface.ui.helpers import connect
from src.interface.settings import COLORS_DARK

START_TIME = datetime.now()

def criar_box(parent, titulo, valor, bg="#1e1e1e"):
    box = tk.Frame(parent, bg=bg, padx=15, pady=10)
    box.config(
        highlightbackground=COLORS_DARK["background"],
        highlightthickness=1,
        bd=8,
    )
    box.place(
        width=200,
        height=100
    )

    tk.Label(box, text=titulo, font=("Arial", 11, "bold"), fg="white", bg=bg).pack()
    tk.Label(box, text=valor, font=("Arial", 22, "bold"), fg="#00adb5", bg=bg).pack()
    return box

def render_dashboard(root):
    total, video, audio = contar_ocorrencias()

    painel = tk.Frame(root, bg=COLORS_DARK["background"])
    painel.pack(pady=20)

    box1 = criar_box(painel, "Total de Ocorrências", total, bg="#5e9dc2")
    box2 = criar_box(painel, "Ocorrências de Vídeo", video, bg="#d35c5c")
    box3 = criar_box(painel, "Ocorrências de Áudio", audio, bg="#dad26b")
    box4 = criar_box(painel, "Data de inicialização", START_TIME.strftime("%d/%m/%Y"), bg="#71e067")
    box5 = criar_box(painel, "Horário de início", START_TIME.strftime("%H:%M:%S"), bg="#b260d3")
    box1.grid(row=0, column=0, padx=5, pady=5)
    box2.grid(row=0, column=1, padx=5, pady=5)
    box3.grid(row=0, column=2, padx=5, pady=5)

    # 2 embaixo (centralizados usando as colunas 0 e 2, deixando 1 vazio)
    box4.grid(row=1, column=0, padx=5, pady=5)
    box5.grid(row=1, column=2, padx=5, pady=5)


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