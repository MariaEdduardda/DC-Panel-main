import numpy as np
import time
import psutil
from ultralytics import YOLO
from datetime import datetime as dt
from src.model.utils import *
from src.sounds.audio import play_standby, play_standon
from src.model.config import *
import src.model.config as config
from src.model.recorder import output_path_live_stream
from src.model.analyzer import analyze_audio, analyze_video


def call_processor(frame_queue, audio_queue, status_dict, status_lock): # Carregando Thread
    model = YOLO(config.MODEL_PATH)
    processor(model, frame_queue, audio_queue, status_dict, status_lock)

def processor(model, frame_queue, audio_queue, status_dict, status_lock):

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

            cpu_load = psutil.cpu_percent(interval=0.025)
            if cpu_load > 90:
                time.sleep(cpu_load_time)
                continue

            try:
                raw_frame = frame_queue.get(timeout=0.5)
                if standby_alerted: # Thread ligada
                    play_standon()
                    print(f"[{dt.now().strftime('%d/%m/%Y %H:%M:%S')}] - Thread on-line")
                standby_alerted = False
                last_standby_time = time.time()
            except:
                if not standby_alerted and time.time() - last_standby_time > 3: # Thread em STANDBY
                    standby_alerted = True
                    play_standby()
                    print(f"[{dt.now().strftime('%d/%m/%Y %H:%M:%S')}] - Thread off-line")
                continue

            # Inferência do analyzer
            if not raw_frame or len(raw_frame) < config.HEIGHT * config.WIDTH * 3:
                print(f"[{dt.now().strftime('%H:%M:%S')}] - Frame vazio ou corrompido")
                continue

            if raw_frame and len(raw_frame) == config.HEIGHT * config.WIDTH * 3:
                frame = np.frombuffer(raw_frame, dtype=np.uint8).reshape(config.HEIGHT, config.WIDTH, 3)
            else:
                # não manda pro analyze()
                continue
            config.FRAME_BUFFER.append(frame.copy())

            # tenta pegar áudio sem bloquear
            try:
                audio_chunk = audio_queue.get_nowait()
            except:
                audio_chunk = None

            audio_result = analyze_audio(audio_chunk) if audio_chunk else None
            video_result = analyze_video(frame)

            # MONTAR RESULTADO FINAL
            if audio_result:
                result_final = audio_result
            elif video_result and video_result["descricao"] != "ok":
                result_final = video_result
            else:
                result_final = {"tipo": "none", "descricao": "ok"}

            # LÓGICA DE DETECÇÃO
            if result_final["descricao"] != "ok":
                detected = True
            else:
                detected = False
                detected_false_count += 1
                if detected_false_count >= DETECTION_THRESHOLD:
                    detected = False

            if not bool(audio_result) and not bool(result_final):
                detected_false_count += 1
                if detected_false_count >= DETECTION_THRESHOLD:
                    detected = False

            if detected:
                detected_true_count += 1
                detected_false_count = 0

            if detected and not bool(detected_stamp_initial):
                detected_stamp_initial = time.time()
                detected = True
                resultsHold = result_final

            elif not detected and bool(detected_stamp_initial) and resultsHold["descricao"] != "ok":
                detected_stamp_finish = time.time()
                detected = False
                duracao = detected_stamp_finish - detected_stamp_initial
                event_log.append((detected_stamp_initial, detected_stamp_finish))
                detected_stamp_initial = 0

                # Recorta o clipe do "video main"
                if config.SOURCE_TYPE == "srt":
                    if not output_path_live_stream or not os.path.exists(output_path_live_stream):
                        print(f"[{dt.now().strftime('%d/%m/%Y %H:%M:%S')}] - Arquivo principal não existe: path({output_path_live_stream})")
                    else:
                        cortar_video(output_path_live_stream, detected_stamp_initial, detected_stamp_finish, config.SAVE_FOLDER)
                with status_lock:
                    status_dict["thread"] = {
                        "tipo": resultsHold["tipo"],
                        "descricao": resultsHold["descricao"],
                        "gravidade": resultsHold["gravidade"],
                        "origem": resultsHold["origem"],
                        "duracao": f"{time.strftime('%H:%M:%S', time.gmtime(duracao))}.{int((duracao % 1) * 1000):03d}ms",
                    }
            config.PROCESSOR_ON = True

        except Exception as e:
            safe_log(f"Erro na detecção", e)
            config.PROCESSOR_ON = False
            time.sleep(0.5)