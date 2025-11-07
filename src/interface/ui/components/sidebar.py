from tkinter import ttk

from src.interface.ui.pages.manager import mudar_pagina

def set_sidebar(main_layout_frame):
    sidebar_frame = ttk.Frame(main_layout_frame, width=200)
    sidebar_frame.pack(side="left", fill="y", padx=(0, 10), pady=(53, 0))

    main_content_frame = ttk.Frame(main_layout_frame)
    # área principal cresce e encolhe automaticamente
    main_content_frame.pack(side="left", fill="both", expand=True)

    menu_opcoes = [
        ("Menu Principal", lambda: mudar_pagina("Página Principal", "Conteúdo principal.", main_content_frame)),
        ("Ocorrências", lambda: mudar_pagina("Ocorrências", "", main_content_frame, pagina_id="ocorrencias")),
        ("Relatórios", lambda: mudar_pagina("Relatórios", "Página de relatórios.", main_content_frame)),
    ]

    for texto, comando in menu_opcoes:
        ttk.Button(sidebar_frame, text=texto, command=comando, width=18).pack(pady=5)

    return main_content_frame