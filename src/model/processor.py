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
            
            # DEBBUG
            print(f"[processor] audio_chunk type={type(audio_chunk)} len={(len(audio_chunk) if isinstance(audio_chunk, (bytes, bytearray)) else 'N/A')}")

            audio_result = analyze_audio(audio_chunk) if isinstance(audio_chunk, (bytes, bytearray)) else None
            video_result = analyze_video(frame)

            # Decide qual evento (prioriza áudio)
            result_final = None
            if audio_result:
                result_final = audio_result
            elif video_result and video_result.get("descricao") != "ok":
                result_final = video_result

            # -------------------------
            # LÓGICA SIMPLIFICADA (state machine)
            # -------------------------
            # in_event: estamos dentro de um evento (True) ou não (False)
            if 'in_event' not in locals():
                in_event = False
                detected_false_count = 0

            # Se result_final existe -> temos um evento agora
            if result_final:
                # Entrou no evento
                if not in_event:
                    in_event = True
                    detected_stamp_initial = time.time()
                    resultsHold = result_final
                    detected_true_count = 1
                    detected_false_count = 0
                    print(f"[{dt.now().strftime('%d/%m/%Y %H:%M:%S')}] - Ocorrencia detectada (start) -> {resultsHold}")
                else:
                    # já dentro do evento: reseta contadores
                    detected_true_count += 1
                    detected_false_count = 0

            else:
                # nenhum evento neste frame
                if in_event:
                    detected_false_count += 1
                    # Espera N frames consecutivos sem evento para confirmar o fim
                    if detected_false_count >= DETECTION_THRESHOLD:
                        detected_stamp_finish = time.time()
                        duracao = detected_stamp_finish - detected_stamp_initial
                        print(f"[{dt.now().strftime('%d/%m/%Y %H:%M:%S')}] - Ocorrencia registrada: {resultsHold} duracao={duracao:.3f}s")
                        event_log.append((detected_stamp_initial, detected_stamp_finish))

                        # salvar / cortar se aplicável
                        if config.SOURCE_TYPE == "srt" and output_path_live_stream and os.path.exists(output_path_live_stream):
                            cortar_video(output_path_live_stream, detected_stamp_initial, detected_stamp_finish, config.SAVE_FOLDER)

                        # atualiza status
                        with status_lock:
                            print(f"[processor] atualizando status_dict com evento {resultsHold}")
                            status_dict["thread"] = {
                                "tipo": resultsHold.get("tipo"),
                                "descricao": resultsHold.get("descricao"),
                                "gravidade": resultsHold.get("gravidade"),
                                "origem": resultsHold.get("origem"),
                                "duracao": f"{time.strftime('%H:%M:%S', time.gmtime(duracao))}.{int((duracao % 1) * 1000):03d}ms",
                            }

                        # reset state
                        in_event = False
                        detected_false_count = 0
                        detected_stamp_initial = None
                        resultsHold = None
                else:
                    # não estamos em evento, nada a fazer
                    pass

            config.PROCESSOR_ON = True

        except Exception as e:
            safe_log(f"Erro na detecção", e)
            config.PROCESSOR_ON = False
            time.sleep(0.5)