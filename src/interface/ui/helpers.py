import csv
import subprocess
import sys
import os
from src.database.db_functions import DB_NAME, listar_ocorrencias
from datetime import datetime as dt
from src.database.db_functions import criar_relatorio
import sqlite3
import src.model.config as config
from src.interface.settings import COLORS_WIDGETS


def restart():
    python = sys.executable  # caminho do python que está rodando
    script = sys.argv[0]    # arquivo que iniciou o programa (main.py)
    subprocess.Popen([python, script])
    sys.exit()  # encerra a instância atual

def connect():
    return sqlite3.connect(DB_NAME)

def format_duration(seconds):
    if seconds is None:
        return "N/A"
    total_seconds = int(round(seconds))
    if total_seconds < 60:
        return f"{total_seconds}s"
    elif total_seconds < 3600:
        m, s = divmod(total_seconds, 60)
        return f"{m}m {s}s"
    else:
        h, r = divmod(total_seconds, 3600)
        m, s = divmod(r, 60)
        return f"{h}h {m}m {s}s"

def obter_periodo_ocorrencias():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("SELECT MIN(data || ' ' || hora), MAX(data || ' ' || hora) FROM ocorrencias")
    inicio, fim = cursor.fetchone()

    conn.close()

    if inicio is None or fim is None:
        return "Sem registros"

    # Converter para formato bonito
    try:
        from datetime import datetime as dt
        inicio_fmt = dt.strptime(inicio, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M:%S")
        fim_fmt = dt.strptime(fim, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M:%S")

        return f"{inicio_fmt} - {fim_fmt}"
    except:
        return f"{inicio} - {fim}"


def exportar_csv():

    # --- Gerar arquivo ---
    caminho_arquivo = os.path.abspath(
        f"sheets/ocorrencias_{dt.now().strftime('%d_%m_%Y-%H_%M_%S')}.csv"
    )
    dados = listar_ocorrencias()

    colunas = [
        "id", "tipo", "descricao", "gravidade", "origem",
        "data", "hora", "duracao", "usuario_id"
    ]

    with open(caminho_arquivo, "w", newline="", encoding="utf-8") as arquivo_csv:
        writer = csv.writer(arquivo_csv, delimiter=';')

        writer.writerow(colunas)

        for linha in dados:
            linha = list(linha)

            # Força EXCEL a tratar como TEXTO
            try:
                data_excel = dt.strptime(linha[5], "%Y-%m-%d").strftime("%d/%m/%Y")
                linha[5] = f"'{data_excel}"   # <-- AQUI
            except:
                pass

            writer.writerow(linha)

    # --- Registrar relatório no banco ---
    periodo = obter_periodo_ocorrencias()
    total_falhas = len(dados)
    gerado_por = 0  # usuário fixo
    criar_relatorio(periodo, total_falhas, gerado_por, caminho_arquivo)

    # --- Abrir no explorador ---
    abrir_pasta_do_arquivo(caminho_arquivo)



def abrir_pasta_do_arquivo(caminho_arquivo):
    caminho_abs = os.path.abspath(caminho_arquivo)
    subprocess.Popen(f'explorer /select,"{caminho_abs}"')

def abrir_arquivo(caminho):
    if not caminho or caminho == "Nenhum":
        return

    caminho = os.path.abspath(caminho)
    subprocess.Popen(f'explorer /select,\"{caminho}\"')

def get_uptime(start_time):
    delta = dt.now() - start_time

    dias = delta.days
    segundos = delta.seconds

    horas = segundos // 3600
    minutos = (segundos % 3600) // 60

    return f"{dias}d {horas}h {minutos}m"

def get_status_model():
    if config.CONFIG["PROCESSOR_ON"]:
        return {"color": COLORS_WIDGETS["success"], "status": "Ativo"}
    else:
        return {"color": COLORS_WIDGETS["danger"], "status": "Inativo"}