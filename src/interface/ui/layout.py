import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk # type: ignore
from PIL import Image, ImageTk
import os

from src.interface.controllers.ocorrencias_controller import imprimir_pagina, upload_arquivo_ocorrencia
from src.interface.ui.pages import mudar_pagina
from src.interface.ui.tabela_ocorrencias import atualizar_tabela
from src.interface.ui.config_ui import *

def init_interface():
    janela = ThemedTk(theme="adapta")
    janela.title("Globo.com - Painel de Ocorrências")
    janela.geometry("900x600")

    set_theme(janela)

    # --- Header ---
    header_frame = ttk.Frame(janela)
    header_frame.pack(fill="x", pady=5)

    # Logo
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        img_path = os.path.join(base_dir, "..", "img", "globosf.png")
        img = Image.open(img_path).resize((80, 80))
        logo_img = ImageTk.PhotoImage(img)
        logo_label = tk.Label(header_frame, image=logo_img)
        logo_label.image = logo_img
        logo_label.pack(side="left", padx=10)
    except Exception:
        ttk.Label(header_frame, text="GLOBO", font=("Arial", 16, "bold")).pack(side="left", padx=10)

    ttk.Label(header_frame, text="Sistema de Ocorrências", font=("Arial", 12), foreground="gray").pack(side="left")

    header_buttons_frame = ttk.Frame(header_frame)
    header_buttons_frame.pack(side="right")


    ttk.Button(header_buttons_frame, text="IMPRIMIR RELATÓRIO", command=imprimir_pagina).pack(side="left", padx=5)
    ttk.Button(header_buttons_frame, text="ENVIAR CLIP OCORRÊNCIA", command=upload_arquivo_ocorrencia).pack(side="left", padx=5)

    # --- Layout Principal ---
    main_layout_frame = ttk.Frame(janela)
    main_layout_frame.pack(fill='both', expand=True)

    sidebar_frame = ttk.Frame(main_layout_frame, width=200)
    sidebar_frame.pack(side="left", fill="y", padx=10, pady=10)

    main_content_frame = ttk.Frame(main_layout_frame)
    main_content_frame.pack(side="left", fill="both", expand=True)

    menu_opcoes = [
        ("Menu Principal", lambda: mudar_pagina("Página Principal", "Conteúdo principal.", main_content_frame)),
        ("Ocorrências", lambda: mudar_pagina("Ocorrências", "", main_content_frame, pagina_id="ocorrencias")),
        ("Relatórios", lambda: mudar_pagina("Relatórios", "Página de relatórios.", main_content_frame)),
    ]

    for texto, comando in menu_opcoes:
        ttk.Button(sidebar_frame, text=texto, command=comando, width=25).pack(pady=5)

    mudar_pagina("Página Principal", "Conteúdo inicial.", main_content_frame)
    atualizar_tabela()
    janela.mainloop()
