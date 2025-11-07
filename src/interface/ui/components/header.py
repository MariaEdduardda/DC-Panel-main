import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
from config import PROJECT_ROOT
from src.interface.controllers.ocorrencias_controller import imprimir_pagina, upload_arquivo_ocorrencia
from src.interface.ui.config_ui import COLORS_DARK

def set_header(janela):
    header_frame = ttk.Frame(janela)
    header_frame.pack(fill="x", pady=5)

    # Caminho da imagem
    img1_path = os.path.join(PROJECT_ROOT, "src", "assets", "images", "globo_logo.png")
    print(f"VARIAVEL DEV: {PROJECT_ROOT}")

    if not os.path.exists(img1_path):
        ttk.Label(header_frame, text="GLOBO", font=("Arial", 16, "bold")).pack(side="left", padx=10)
    else:
        # --- Correção da transparência ---
        img = Image.open(img1_path).convert("RGBA").resize((80, 80))

        fundo = tuple(int(COLORS_DARK["background"].lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (255,) # converte HEX em RGBA

        bg = Image.new("RGBA", img.size, fundo)
        bg.paste(img, (0, 0), img)

        logo_img = ImageTk.PhotoImage(bg)

        logo_label = tk.Label(header_frame, image=logo_img, bg="#2b2b2b")
        logo_label.image = logo_img
        logo_label.pack(side="left", padx=10)

    ttk.Label(header_frame, text="DC Panel - v 1.0.1.1", font=("Arial", 12), foreground="gray").pack(side="left")

    header_buttons_frame = ttk.Frame(header_frame)
    header_buttons_frame.pack(side="right")

    ttk.Button(header_buttons_frame, text="Gerar relatório", command=imprimir_pagina).pack(side="left", padx=5)
    ttk.Button(header_buttons_frame, text="Adicionar ocorrência", command=upload_arquivo_ocorrencia).pack(side="left", padx=5)
