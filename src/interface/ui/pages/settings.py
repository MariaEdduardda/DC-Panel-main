import tkinter as tk
from tkinter import ttk
import src.model.config as cf
from src.interface.settings import COLORS_DARK, COLORS_WIDGETS
from src.interface.ui.helpers import restart  

def render_settings(painel: tk.Frame):
    # Limpa o painel
    for w in painel.winfo_children():
        w.destroy()

    painel.pack(fill="both", expand=True)
    painel.update()

    # Título
    tk.Label(
        painel,
        text="⚙️ Configurações",
        font=("Inter", 16, "bold"),
        fg="white",
        bg=COLORS_DARK["background"]
    ).pack(pady=10)

    # ==== SCROLL SETUP ====
    scroll_container = tk.Frame(painel, bg=COLORS_DARK["background"])
    scroll_container.pack(fill="both", expand=True, padx=20, pady=10)
    scroll_container.update()

    canvas = tk.Canvas(scroll_container, bg=COLORS_DARK["background"], highlightthickness=0)
    scroll_frame = tk.Frame(canvas, bg=COLORS_DARK["background"])
    scrollbar = tk.Scrollbar(scroll_container, orient="vertical", command=canvas.yview)

    canvas.configure(yscrollcommand=scrollbar.set)
    window_id = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

    # Faz o frame do scroll acompanhar a largura do container
    def ajustar_largura(event):
        canvas.itemconfig(window_id, width=event.width)

    scroll_container.bind("<Configure>", ajustar_largura)
    scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    # ==== FIM DO SCROLL SETUP ====

    # ==== CRIAÇÃO DOS CAMPOS ====
    campos = []

    def criar_campo(label, key, widget="entry", options=None):
        frame = tk.Frame(scroll_frame, bg=COLORS_DARK["background"])
        frame.pack(fill="x", pady=5)

        tk.Label(
            frame,
            text=label,
            font=("Inter", 12, "bold"),
            fg="white",
            bg=COLORS_DARK["background"],
            anchor="w"
        ).pack(side="top", fill="x")

        valor = cf.get_value(key)
        var = tk.StringVar(value=str(valor))

        if widget == "entry":
            tk.Entry(
                frame, textvariable=var, font=("Inter", 12),
                bg="#262626", fg="white", insertbackground="white", relief="flat"
            ).pack(fill="x", ipady=4, padx=2)

        elif widget == "dropdown" and options:
            ttk.Combobox(
                frame, textvariable=var, values=options,
                state="readonly", font=("Inter", 11)
            ).pack(fill="x", ipady=4, padx=2)

        campos.append((key, var))

    # Lista de campos
    for label, key in [
        ("Confiança YOLO (0–1)", "YOLO_CONF"),
        ("Tela preta threshold", "BLACK_THRESHOLD"),
        ("Freeze threshold (frames)", "FREEZE_THRESHOLD"),
        ("Silêncio áudio threshold", "SILENCE_THRESHOLD"),
        ("Clipping áudio threshold", "CLIP_THRESHOLD"),
        ("FPS estimado", "FPS_ESTIMATED"),
        ("Buffer de corte (segundos)", "BUFFER_SECONDS"),
        ("Threads de análise", "NUM_THREADS"),
        ("Taxa de amostragem áudio", "SAMPLE_RATE"),
    ]:
        criar_campo(label, key)

    criar_campo("Tipo de análise", "SOURCE_TYPE", widget="dropdown", options=["file", "srt"])
    # ==== FIM DA CRIAÇÃO DOS CAMPOS ====

    # ==== FUNÇÃO SALVAR ====
    def salvar():
        for key, var in campos:
            v = var.get()

            try:
                if v.replace('.', '', 1).isdigit() and "." in v:
                    valor = float(v)
                elif v.isdigit():
                    valor = int(v)
                else:
                    valor = v  # texto (ex dropdown)

                cf.set_value(key, valor)

            except:
                print(f"⚠️ valor inválido para {key}: {v}")

        print("✅ Config atualizado:", cf.CONFIG)
    # ==== FIM DA FUNÇÃO SALVAR ====

    # ==== FOOTER FIXO ====
    footer = tk.Frame(painel, bg=COLORS_DARK["background"])
    footer.pack(fill="x", side="bottom", pady=10)

    tk.Button(
        footer, text="🔄 Reiniciar", command=restart,
        font=("Inter", 11, "bold"), bg="#444444",
        fg="white", width=16, height=1, relief="flat"
    ).pack(pady=4)
    # ==== FIM DO FOOTER ====
