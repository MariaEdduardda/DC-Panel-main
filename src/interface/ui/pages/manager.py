from tkinter import ttk
from src.interface.ui.pages.tb_ocorrencias import criar_tabela_ocorrencias
from src.interface.settings import VIDEO_PATH

def mudar_pagina(titulo, texto, frame, pagina_id=None):
    for widget in frame.winfo_children():
        widget.destroy()

    ttk.Label(frame, text=titulo, font=('Arial', 16, 'bold')).pack(pady=(10, 20))

    match pagina_id:
        case "ocorrencias":
            criar_tabela_ocorrencias(frame)
        case "video":
            pass
        case _:
            ttk.Label(frame, text=texto, wraplength=500).pack(padx=20)

