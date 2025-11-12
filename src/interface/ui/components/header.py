import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
from config import PROJECT_ROOT
from src.interface.controllers.ocorrencias_controller import imprimir_pagina, upload_arquivo_ocorrencia
from src.interface.ui.config_ui import COLORS_DARK
from src.model import config  # <— importe o módulo, não a variável

def atualizar_logo(janela, logo_label):
    if not logo_label:
        return

    # pega o valor atualizado de PROCESSOR_ON diretamente do módulo
    img_file = "globo_logo_on.png" if config.PROCESSOR_ON else "globo_logo_off.png"
    img_path = os.path.join(PROJECT_ROOT, "src", "assets", "images", img_file)

    if not os.path.exists(img_path):
        logo_label.config(text="GLOBO", image="", font=("Arial", 16, "bold"))
    else:
        img = Image.open(img_path).convert("RGBA").resize((80, 80))
        fundo = tuple(int(COLORS_DARK["background"].lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (255,)
        bg = Image.new("RGBA", img.size, fundo)
        bg.paste(img, (0, 0), img)
        logo_img = ImageTk.PhotoImage(bg)
        logo_label.config(image=logo_img)
        logo_label.image = logo_img  # evita GC

    # agenda a próxima atualização (a cada 100ms = 0.1s)
    janela.after(100, atualizar_logo, janela, logo_label)


def set_header(janela):
    header_frame = ttk.Frame(janela)
    header_frame.pack(fill="x", pady=5)

    # Cria o label do logo
    logo_label = tk.Label(header_frame, bg="#2b2b2b")
    logo_label.pack(side="left", padx=10)

    # Inicia a verificação do logo dinâmico
    atualizar_logo(janela, logo_label)

    ttk.Label(header_frame, text="DC Panel - v 0.0.0.1", font=("Arial", 12), foreground="gray").pack(side="left")

    header_buttons_frame = ttk.Frame(header_frame)
    header_buttons_frame.pack(side="right")

    ttk.Button(header_buttons_frame, text="Gerar relatório", command=imprimir_pagina).pack(side="left", padx=5)
    ttk.Button(header_buttons_frame, text="Adicionar ocorrência", command=upload_arquivo_ocorrencia).pack(side="left", padx=5)
