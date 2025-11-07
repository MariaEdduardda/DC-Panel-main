from tkinter import ttk
from src.database.db_functions import listar_ocorrencias
from src.sounds.audio import play_alarm

tabela_global = None
ocorrencias_data = []
ultima_quantidade = 0  # usado para detectar novas ocorrências
root_ref = None  # referência à janela principal para usar .after()


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


def criar_tabela_ocorrencias(frame_pai):
    global tabela_global, ocorrencias_data, ultima_quantidade, root_ref
    root_ref = frame_pai.winfo_toplevel()  # pega referência da janela principal
    ocorrencias_data = carregar_ocorrencias_do_banco()
    ultima_quantidade = len(ocorrencias_data)

    colunas = ("id", "tipo", "descricao", "gravidade", "origem", "data", "hora", "duracao", "usuario_id")
    tabela_global = ttk.Treeview(frame_pai, columns=colunas, show="headings")

    for col in colunas:
        tabela_global.heading(col, text=col.capitalize())
        tabela_global.column(col, width=100, anchor="center")

    tabela_global.pack(fill="both", expand=True)
    atualizar_tabela()


def atualizar_tabela():
    global tabela_global, ocorrencias_data
    if tabela_global is None:
        return

    tabela_global.delete(*tabela_global.get_children())
    for item in ocorrencias_data:
        tabela_global.insert("", "end", values=tuple(item.values()))


def verificar_novas_ocorrencias():
    """Verifica periodicamente se há novas ocorrências no banco e atualiza a tabela."""
    global ocorrencias_data, ultima_quantidade, root_ref

    novos_dados = carregar_ocorrencias_do_banco()
    nova_qtd = len(novos_dados)

    # só atualiza se houve alteração
    if nova_qtd != ultima_quantidade:
        ultima_quantidade = nova_qtd
        ocorrencias_data = novos_dados
        play_alarm()
        atualizar_tabela()

    # agenda nova verificação a cada 3 segundos (3000 ms)
    if root_ref:
        root_ref.after(3000, verificar_novas_ocorrencias)
