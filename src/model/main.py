import threading
import time
from datetime import datetime as dt
from ultralytics import YOLO
import src.model.audio_reader as sr

from src.model.stream_reader import read_frames, frame_queue
from src.model.processor import call_processor
from src.sounds.audio import init_audio
from src.model.config import ALARM_FILE, MODEL_PATH, STANDBY_FILE, STANDON_FILE, NUM_THREADS
from src.model.monitor import monitor_status
from src.model.status_manager import *
from src.model.utils import stop_recording
from src.model.recorder import record_process

def init_model():
    # Inicializa o som e o modelo
    init_audio(ALARM_FILE, STANDBY_FILE, STANDON_FILE)
    model = YOLO(MODEL_PATH)

    print(f"[{dt.now().strftime('%d/%m/%Y %H:%M:%S')}] - Iniciando modelo de analise")

    # Threads
    threading.Thread(
        target=read_frames,
        daemon=True
    ).start() # PipeLine frames

    #==============================================

    # Inicia FFmpeg áudio
    sr.start_audio_ffmpeg()

    # Inicia imediatamente a leitura do pipe para evitar EOF precoce ✅
    if sr.audio_proc and sr.audio_proc.stdout:
        threading.Thread(
            target=sr.read_audio_pipe,
            args=(sr.audio_proc.stdout, sr.audio_queue),
            daemon=True
        ).start()
    else:
        print("❌ Pipe de áudio não está disponível!")
        return

    # Agora sim aguarda o processo ser atribuído no global ✅
    wait = 0
    while sr.audio_proc is None and wait < 100:
        time.sleep(0.01)
        wait += 1

    if sr.audio_proc is None:
        print("❌ Não iniciou áudio, abortando!")
        return

    #==============================================

    threading.Thread(
        target=monitor_status,
        args=(status_dict, status_lock),
        daemon=True
    ).start() # Monitor

    threading.Thread(
        target=call_processor,
        args=(frame_queue, sr.audio_queue, status_dict, status_lock),
        daemon=True
    ).start() # Analyzer

    print(f"[{dt.now().strftime('%d/%m/%Y %H:%M:%S')}] - Threads iniciada: video e udio analyzer")

    # Mantém o programa ativo
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_recording(record_process)
        PROCESSOR_ON = False
        print(f"[{dt.now().strftime('%d/%m/%Y %H:%M:%S')}] - Interrompido pelo usuário")
