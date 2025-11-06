import numpy as np
import time
import psutil
from ultralytics import YOLO
from datetime import datetime as dt
from model.utils import *
from sounds.audio import play_standby, play_standon
from model.config import *
from model.recorder import output_path_live_stream
from colorama import Fore, Back # type: ignore
from model.analyzer import analyze


def call_processor_thread(frame_queue, thread_id, status_dict, status_lock): # Carregando Thread
    model = YOLO(MODEL_PATH)
    process(model, frame_queue, status_dict, status_lock, thread_id)

def process(model, frame_queue, status_dict, status_lock, thread_id=1):

    # =============== VARIAVEIS ===============

    # Variáveis de BUFFER DE CONTINUIDADE
    detected_true_count, detected_false_count = 0, 0

    # Variaveis de GRAVAÇÃO DE CORTE

    detected_stamp_initial, detected_stamp_finish = None, None
    detected = False
    event_log = []

    # Variáveis de STANDBY
    last_standby_time = 0
    standby_alerted = False

    # Variáveis de DESEMPENHO
    cpu_load_time = 0.043

    # =============== LOOP PRINCIPAL ===============
    while True:
        try:
            t0 = time.time()

            cpu_load = psutil.cpu_percent(interval=0.025)
            if cpu_load > 90:
                time.sleep(cpu_load_time)
                continue

            try:
                raw_frame = frame_queue.get(timeout=0.3)
                if standby_alerted: # Thread ligada
                    play_standon()
                    print(f"[{dt.now().strftime('%d/%m/%Y %H:%M:%S')}] - Thread #{thread_id} on-line")
                standby_alerted = False
                last_standby_time = time.time()
            except:
                if not standby_alerted and time.time() - last_standby_time > 3: # Thread em STANDBY
                    standby_alerted = True
                    play_standby()
                    print(f"[{dt.now().strftime('%d/%m/%Y %H:%M:%S')}] - Thread #{thread_id} off-line")
                continue

            # Inferência do analyzer
            frame = np.frombuffer(raw_frame, np.uint8).reshape((HEIGHT, WIDTH, 3))
            FRAME_BUFFER.append(frame.copy())

            results = analyze(frame)
            detected = bool(results)

            if detected:
                detected_true_count += 1
                detected_false_count = 0
            else:
                detected_false_count += 1
                detected_true_count = 0

            if detected and not bool(detected_stamp_initial):
                detected_stamp_initial = time.time()
                detected = True
                resultsHold = results

            elif not detected and bool(detected_stamp_initial):
                detected_stamp_finish = time.time()
                detected = False
                duracao = detected_stamp_finish - detected_stamp_initial
                event_log.append((detected_stamp_initial, detected_stamp_finish))
                detected_stamp_initial = 0

                # Recorta o clipe do "video main"
                if SOURCE_TYPE == "srt":
                    if not output_path_live_stream or not os.path.exists(output_path_live_stream):
                        print(f"[{dt.now().strftime('%d/%m/%Y %H:%M:%S')}] - Arquivo principal não existe: path({output_path_live_stream})")
                    else:
                        cortar_video(output_path_live_stream, detected_stamp_initial, detected_stamp_finish, SAVE_FOLDER)
                with status_lock:
                    status_dict[thread_id] = {
                        "tipo": resultsHold["tipo"],
                        "descricao": resultsHold["descricao"],
                        "gravidade": resultsHold["gravidade"],
                        "origem": resultsHold["origem"],
                        "duracao": f"{time.strftime('%H:%M:%S', time.gmtime(duracao))}.{int((duracao % 1) * 1000):03d}ms",
                    }

        except Exception as e:
            safe_log(f"Erro na detecção (Thread #{thread_id})", e)
            time.sleep(0.5)