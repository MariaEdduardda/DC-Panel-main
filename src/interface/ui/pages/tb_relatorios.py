from tkinter import ttk
import sqlite3
from src.interface.settings import COLORS_DARK
from src.interface.ui.helpers import abrir_arquivo

tabela_relatorios = None
dados_relatorios = []
pagina_atual = 0
linhas_por_pagina = 20
label_paginacao = None

def get_dados_paginados():
    global pagina_atual, linhas_por_pagina, dados_relatorios
    inicio = pagina_atual * linhas_por_pagina
    fim = inicio + linhas_por_pagina
    return dados_relatorios[inicio:fim]

def atualizar_label_paginacao():
    global pagina_atual, linhas_por_pagina, dados_relatorios, label_paginacao

    total = len(dados_relatorios)
    if total == 0:
        label_paginacao.config(text="Nenhum registro encontrado")
        return

    inicio = pagina_atual * linhas_por_pagina + 1
    fim = min((pagina_atual + 1) * linhas_por_pagina, total)

    label_paginacao.config(text=f"Mostrando {inicio}–{fim} de {total}")


def atualizar_tabela_relatorios():
    global tabela_relatorios

    tabela_relatorios.delete(*tabela_relatorios.get_children())
    dados = get_dados_paginados()

    for idx, item in enumerate(dados):
        tag = "linha_par" if idx % 2 == 0 else "linha_impar"
        tabela_relatorios.insert("", "end", values=tuple(item.values()), tags=(tag,))

    atualizar_label_paginacao()


def proxima_pagina():
    global pagina_atual, linhas_por_pagina, dados_relatorios
    total_paginas = max(1, (len(dados_relatorios) - 1) // linhas_por_pagina + 1)
    if pagina_atual < total_paginas - 1:
        pagina_atual += 1
        atualizar_tabela_relatorios()

def pagina_anterior():
    global pagina_atual
    if pagina_atual > 0:
        pagina_atual -= 1
        atualizar_tabela_relatorios()


def listar_relatorios():
    conn = sqlite3.connect("src/database/gfo_system.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, periodo, total_falhas, gerado_por, caminho_arquivo
        FROM relatorios
        ORDER BY id DESC
    """)

    dados = cursor.fetchall()
    conn.close()

    lista_fmt = []
    for id_, periodo, total_falhas, gerado_por, caminho in dados:
        lista_fmt.append({
            "id": id_,
            "periodo": periodo,
            "total_falhas": total_falhas,
            "gerado_por": gerado_por,
            "caminho_arquivo": caminho if caminho else "Nenhum"
        })
    return lista_fmt

def clique_na_tabela(event):
    item_id = tabela_relatorios.focus()  # item selecionado
    if not item_id:
        return

    valores = tabela_relatorios.item(item_id, "values")

    # índice da coluna "caminho_arquivo"
    caminho = valores[4]

    abrir_arquivo(caminho)


def criar_tabela_relatorios(frame_pai):
    global tabela_relatorios, dados_relatorios

    dados_relatorios = listar_relatorios()

    container = ttk.Frame(frame_pai)
    container.pack(fill="both", expand=True)

    frame_tabela = ttk.Frame(container)
    frame_tabela.pack(fill="both", expand=True)

    colunas = ("id", "periodo", "total_falhas", "gerado_por", "caminho_arquivo")

    tabela_relatorios = ttk.Treeview(
        frame_tabela,
        columns=colunas,
        show="headings",
        style="mystyle.Treeview"
    )

    # Evento de clique duplo
    tabela_relatorios.bind("<Double-1>", clique_na_tabela)

    # Zebra
    tabela_relatorios.tag_configure("linha_par", background=COLORS_DARK["table_background_zebra_1"])
    tabela_relatorios.tag_configure("linha_impar", background=COLORS_DARK["table_background_zebra_2"])

    # Cabeçalhos
    tabela_relatorios.heading("id", text="ID")
    tabela_relatorios.heading("periodo", text="Período")
    tabela_relatorios.heading("total_falhas", text="Total de Falhas")
    tabela_relatorios.heading("gerado_por", text="Gerado Por")
    tabela_relatorios.heading("caminho_arquivo", text="Arquivo")

    # Larguras
    tabela_relatorios.column("id", width=60, anchor="center")
    tabela_relatorios.column("periodo", width=140, anchor="center")
    tabela_relatorios.column("total_falhas", width=120, anchor="center")
    tabela_relatorios.column("gerado_por", width=100, anchor="center")
    tabela_relatorios.column("caminho_arquivo", width=250, anchor="w")

    tabela_relatorios.pack(fill="both", expand=True)

        # ---- PAGINAÇÃO ----
    frame_paginacao = ttk.Frame(container)
    frame_paginacao.pack(fill="x", pady=5)

    btn_anterior = ttk.Button(frame_paginacao, text="◀ Anterior", command=pagina_anterior)
    btn_anterior.pack(side="left", padx=10)

    btn_proxima = ttk.Button(frame_paginacao, text="Próxima ▶", command=proxima_pagina)
    btn_proxima.pack(side="left")

    global label_paginacao
    label_paginacao = ttk.Label(frame_paginacao, text="")
    label_paginacao.pack(side="right", padx=10)
    
    atualizar_tabela_relatorios()

