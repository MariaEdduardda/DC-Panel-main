from tkinter import ttk
from src.database.db_functions import listar_ocorrencias
from src.sounds.audio import play_alarm
from src.interface.settings import COLORS_DARK

tabela_global = None
ocorrencias_data = []
ultima_quantidade = 0  # usado para detectar novas ocorrências
root_ref = None  # referência à janela principal para usar .after()
pagina_atual = 0
linhas_por_pagina = 20


def carregar_ocorrencias_do_banco():
    registros = listar_ocorrencias()
    data_convertida = []
    for id_, tipo, descricao, gravidade, origem, data, hora, duracao, usuario_id in registros:
        data_convertida.append({
            "id": id_,
            "tipo": tipo,
            "descricao": descricao,
            "gravidade": gravidade,
            "origem": origem,
            "data": data,
            "hora": hora,
            "duracao": duracao,
            "usuario_id": usuario_id
        })
    return data_convertida

def get_dados_paginados():
    global pagina_atual, linhas_por_pagina, ocorrencias_data

    inicio = pagina_atual * linhas_por_pagina
    fim = inicio + linhas_por_pagina
    return ocorrencias_data[inicio:fim]

def atualizar_label_paginacao():
    global pagina_atual, linhas_por_pagina, ocorrencias_data, label_paginacao

    total = len(ocorrencias_data)

    if total == 0:
        label_paginacao.config(text="Nenhum registro encontrado")
        return

    inicio = pagina_atual * linhas_por_pagina + 1
    fim = min((pagina_atual + 1) * linhas_por_pagina, total)

    label_paginacao.config(text=f"Mostrando {inicio}–{fim} de {total}")

def proxima_pagina():
    global pagina_atual, linhas_por_pagina, ocorrencias_data
    
    total_paginas = max(1, (len(ocorrencias_data) - 1) // linhas_por_pagina + 1)

    if pagina_atual < total_paginas - 1:
        pagina_atual += 1
        atualizar_tabela()

def pagina_anterior():
    global pagina_atual
    if pagina_atual > 0:
        pagina_atual -= 1
        atualizar_tabela()


def criar_tabela_ocorrencias(frame_pai):
    global tabela_global, ocorrencias_data, ultima_quantidade, root_ref, label_paginacao
    root_ref = frame_pai.winfo_toplevel()
    ocorrencias_data = carregar_ocorrencias_do_banco()
    ultima_quantidade = len(ocorrencias_data)

    # ---- CONTAINER VERTICAL ----
    container = ttk.Frame(frame_pai)
    container.pack(fill="both", expand=True)

    # ---- FRAME DA TABELA ----
    frame_tabela = ttk.Frame(container)
    frame_tabela.pack(fill="both", expand=True)

    colunas = ("id", "tipo", "descricao", "gravidade", "origem", "data", "hora", "duracao", "usuario_id")
    tabela_global = ttk.Treeview(frame_tabela, columns=colunas, show="headings", style="mystyle.Treeview")

    # Configurar tags para linhas alternadas (Zebra)
    tabela_global.tag_configure("linha_par", background=COLORS_DARK["table_background_zebra_1"])   # cinza escuro
    tabela_global.tag_configure("linha_impar", background=COLORS_DARK["table_background_zebra_2"]) # mais escuro ainda


    for col in colunas:
        tabela_global.heading(col, text=col.capitalize())
        tabela_global.column(col, width=100, anchor="center")

    tabela_global.pack(fill="both", expand=True)


    # ---- PAGINAÇÃO (FICA FIXA EMBAIXO) ----
    frame_paginacao = ttk.Frame(container)
    frame_paginacao.pack(fill="x", pady=5)

    btn_anterior = ttk.Button(frame_paginacao, text="◀ Anterior", command=pagina_anterior)
    btn_anterior.pack(side="left", padx=10)

    btn_proxima = ttk.Button(frame_paginacao, text="Próxima ▶", command=proxima_pagina)
    btn_proxima.pack(side="left")

    label_paginacao = ttk.Label(frame_paginacao, text="")
    label_paginacao.pack(side="right", padx=10)

    atualizar_label_paginacao()
    atualizar_tabela()




def atualizar_tabela():
    global tabela_global

    if tabela_global is None:
        return

    tabela_global.delete(*tabela_global.get_children())

    dados = get_dados_paginados()
    for idx, item in enumerate(dados):
        tag = "linha_par" if idx % 2 == 0 else "linha_impar"
        tabela_global.insert("", "end", values=tuple(item.values()), tags=(tag,))


    atualizar_label_paginacao()

def verificar_novas_ocorrencias():
    global ocorrencias_data, ultima_quantidade, root_ref, pagina_atual, linhas_por_pagina

    novos_dados = carregar_ocorrencias_do_banco()
    nova_qtd = len(novos_dados)

    # Detecta ALTERAÇÃO -> dispara alerta e atualiza tabela
    if nova_qtd != ultima_quantidade:
        ultima_quantidade = nova_qtd
        ocorrencias_data = novos_dados
        play_alarm()

        # Ajuste para evitar ir para uma página inexistente
        total_paginas = max(1, (len(ocorrencias_data) - 1) // linhas_por_pagina + 1)

        if pagina_atual >= total_paginas:
            pagina_atual = total_paginas - 1
        atualizar_tabela()

    # Reagendar verificação normal
    if root_ref:
        root_ref.after(3000, verificar_novas_ocorrencias)