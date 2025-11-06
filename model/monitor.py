import time
from database.db_functions import criar_ocorrencia
from datetime import datetime as dt

def save_DB(values):
    # Salva no banco
    criar_ocorrencia(
        tipo=values["tipo"],
        descricao=values["descricao"],
        gravidade=values["gravidade"],
        origem=values["origem"],
        data=dt.date.today(),
        hora=dt.datetime.now().strftime("%H:%M:%S"),
        duracao=values["duracao"],
        usuario_id="0"
            )
    print(f"[{dt.now().strftime('%d/%m/%Y %H:%M:%S')}] - Ocorrencia registrada: data: {dt.date.today()}; hora: {dt.datetime.now().strftime('%H:%M:%S')};")

def monitor_status(status_dict, status_lock):

    last_values = None
    while True:
        with status_lock:
            if not status_dict:
                time.sleep(0.5)
                continue

            values = list(status_dict.values())[-1]

            if values != last_values:
                print(f"[{dt.now().strftime('%d/%m/%Y %H:%M:%S')}] - Ocorrencia detectada")
                save_DB(values)
                last_values = values

        time.sleep(0.5)
