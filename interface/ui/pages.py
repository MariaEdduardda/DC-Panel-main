from tkinter import ttk
from interface.ui.tabela_ocorrencias import criar_tabela_ocorrencias
from interface.controllers.settings import VIDEO_PATH
def mudar_pagina(titulo, texto, frame, pagina_id=None):
    for widget in frame.winfo_children():
        widget.destroy()

    ttk.Label(frame, text=titulo, font=('Arial', 16, 'bold')).pack(pady=10)

    if pagina_id == "ocorrencias":
        criar_tabela_ocorrencias(frame)
    # elif pagina_id == "video" and VIDEO_PATH:
    #     ttk.Button(header_video_frame, text="X",
    #                command=lambda: mudar_pagina("Ocorrências", "Conteúdo da página de ocorrências.", "ocorrencias")
    #                ).pack(side="right", padx=10)
    #     video_label = ttk.Label(main_content_frame)
    #     video_label.place(relx=0.5, rely=0.5, anchor='center')
    #     try:
    #         player_video = tkvideo(VIDEO_PATH, video_label, loop=1, size=(600, 400))
    #         player_video.play()
    #     except Exception as e:
    #         messagebox.showerror("Erro de Reprodução", f"Ocorreu um erro ao reproduzir o vídeo: {e}")
    else:
        ttk.Label(frame, text=texto, wraplength=500).pack(padx=20, pady=10)

# callback global
def atualizar_tabela_ocorrencias():
    import ui.tabela_ocorrencias as tabela
    if tabela.tabela_global:
        tabela.atualizar_tabela()
