import threading
import time
from datetime import datetime as dt
from ultralytics import YOLO
from src.model.stream_reader import read_frames, frame_queue
from src.model.processor import call_processor_thread
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
    ).start() # PipeLine

    threading.Thread(
        target=monitor_status,
        args=(status_dict, status_lock),
        daemon=True
    ).start() # Monitor

    # Threads YOLO
    for i in range(NUM_THREADS):
        t = threading.Thread(
            target=call_processor_thread,
            args=(frame_queue, i+1, status_dict, status_lock),
            daemon=True
        )
        t.start()
    print(f"[{dt.now().strftime('%d/%m/%Y %H:%M:%S')}] - Threads iniciadas: {NUM_THREADS}")


    # Mantém o programa ativo
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_recording(record_process)
        print(f"[{dt.now().strftime('%d/%m/%Y %H:%M:%S')}] - Interrompido pelo usuário")
