import os
import datetime
from tkinter import filedialog, messagebox
from moviepy.video.io.VideoFileClip import VideoFileClip # type: ignore
from src.database.db_functions import criar_ocorrencia, listar_ocorrencias
from src.interface.ui.helpers import format_duration
from src.interface.ui.pages import atualizar_tabela_ocorrencias

def get_video_duration(path):
    try:
        with VideoFileClip(path) as clip:
            return clip.duration
    except Exception:
        return None

def upload_arquivo_ocorrencia():
    filepath = filedialog.askopenfilename(title="Selecione o arquivo de ocorrência",
                                          filetypes=[("Arquivos de vídeo", "*.mp4;*.avi;*.mov")])
    if not filepath:
        return

    nome = os.path.basename(filepath)
    data_mod = datetime.datetime.fromtimestamp(os.path.getmtime(filepath)).strftime("%Y-%m-%d %H:%M:%S")
    duracao = format_duration(get_video_duration(filepath))

    try:
        criar_ocorrencia("video", nome, "leve", "Rede",
                         data_mod.split(" ")[0], data_mod.split(" ")[1], duracao, 1)
        messagebox.showinfo("Sucesso", f"Ocorrência salva!\nArquivo: {nome}")
        atualizar_tabela_ocorrencias()
    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao salvar: {e}")

def imprimir_pagina():
    messagebox.showinfo("Impressão", "Função de impressão simulada.")
