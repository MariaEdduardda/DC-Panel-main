from tkinter import ttk
from src.interface.ui.pages.tb_ocorrencias import criar_tabela_ocorrencias
from src.interface.ui.pages.tb_relatorios import criar_tabela_relatorios
from src.interface.ui.pages.dashboard import render_dashboard
from src.interface.ui.pages.settings import render_settings
from src.interface.settings import VIDEO_PATH

def mudar_pagina(titulo, texto, frame, pagina_id=None):
    for widget in frame.winfo_children():
        widget.destroy()

    ttk.Label(frame, text=titulo, font=('Arial', 16, 'bold')).pack(pady=(10, 20))

    match pagina_id:
        case "ocorrencias":
            criar_tabela_ocorrencias(frame)
        case "relatorios":
            criar_tabela_relatorios(frame)
            pass
        case "dashboard":
            render_dashboard(frame)
            pass
        case "settings":
            render_settings(frame)
        case _:
            ttk.Label(frame, text=texto, wraplength=500).pack(padx=20)

