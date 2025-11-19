import tkinter as tk
from tkinter import ttk
from src.interface.settings import *



def set_theme(janela: tk.Tk):
    """Aplica um tema escuro personalizado na janela Tkinter."""

    janela.configure(bg=COLORS_DARK["background"])

    style = ttk.Style()
    style.theme_use("clam")  # Usa um tema base customizável

    # Configuração geral de labels e botões
    style.configure(
        "TLabel",
        background=COLORS_DARK["background"],
        foreground=COLORS_DARK["foreground"],
        font=FONTS["default"]
    )

    style.configure(
        "Treeview",
        background=COLORS_DARK["background"],
        foreground=COLORS_DARK["foreground"],
        fieldbackground=COLORS_DARK["background"],
        borderwidth=0,
        font=FONTS["default"]
    )

    style.configure(
        "mystyle.Treeview",
        rowheight=28
    )  # altura das linhas

    style.configure(
        "mystyle.Treeview.Heading",
        font=FONTS["header"]
    )

    style.configure(
        "TButton",
        background=COLORS_DARK["button_bg"],
        foreground=COLORS_DARK["button_fg"],
        font=FONTS["default"],
        padding=10
    )

    style.map(
        "TButton",
        background=[("active", COLORS_DARK["accent"])],
        foreground=[("active", COLORS_DARK["foreground"])]
    )

    style.configure(
        "TFrame",
        background=COLORS_DARK["background"]
    )
