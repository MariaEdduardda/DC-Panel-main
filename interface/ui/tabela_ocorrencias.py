from tkinter import ttk
from database.db_functions import listar_ocorrencias

tabela_global = None
ocorrencias_data = []

def carregar_ocorrencias_do_banco():
    global ocorrencias_data
    ocorrencias_data = []
    registros = listar_ocorrencias()
    for id_, tipo, descricao, gravidade, origem, data, hora, duracao, usuario_id in registros:
        ocorrencias_data.append({
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

def criar_tabela_ocorrencias(frame_pai):
    global tabela_global
    carregar_ocorrencias_do_banco()

    colunas = ("id", "tipo", "descricao", "gravidade", "origem", "data", "hora", "duracao", "usuario_id")
    tabela_global = ttk.Treeview(frame_pai, columns=colunas, show="headings")

    for col in colunas:
        tabela_global.heading(col, text=col.capitalize())
        tabela_global.column(col, width=100, anchor="center")

    tabela_global.pack(fill="both", expand=True)
    atualizar_tabela()

def atualizar_tabela():
    tabela_global.delete(*tabela_global.get_children())
    for item in ocorrencias_data:
        tabela_global.insert("", "end", values=tuple(item.values()))
