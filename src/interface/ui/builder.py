from tkinter import ttk
from ttkthemes import ThemedTk # type: ignore

# Imports de arquivos locais
import src.interface.ui.pages.tb_ocorrencias as tb
from src.interface.ui.pages.manager import mudar_pagina
from src.interface.ui.config_ui import *
from src.interface.ui.components.header import set_header
from src.interface.ui.components.sidebar import set_sidebar

def init_interface():
    janela = ThemedTk(theme="adapta")
    janela.title("DC Panel v1.0.1.1 - Painel principal")
    janela.geometry("900x600")

    set_theme(janela) # Setando o thema da janela
    set_header(janela) # Setando o header da janela

    # --- Layout Principal ---
    main_layout_frame = ttk.Frame(janela)
    main_layout_frame.pack(fill="both", expand=True, padx=10, pady=10)

    main_content_frame = set_sidebar(main_layout_frame) # Setando a sidebar

    mudar_pagina("Página Principal", "Conteúdo inicial.", main_content_frame) # Direciona automaticamente para a primeira pagina

    # Observando se há alterações no banco de dados, consequentemente na tabela
    tb.root_ref = janela
    tb.verificar_novas_ocorrencias()
    
    janela.mainloop()
