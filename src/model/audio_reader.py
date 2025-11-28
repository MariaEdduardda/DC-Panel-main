import threading
import subprocess
import queue
import time
import numpy as np
from datetime import datetime as dt
from src.model.config import SAMPLE_RATE, VIDEO_PATH, SILENCE_THRESHOLD
from src.model.utils import safe_log

audio_proc = None
audio_queue = queue.Queue(maxsize=30)
proc_lock = threading.Lock()

CHUNK_MS = 100
CHUNK_SIZE = int(SAMPLE_RATE * 2 * (CHUNK_MS / 1000))  # 2 bytes por sample (int16 mono)

def start_audio_ffmpeg():
    global audio_proc
    with proc_lock:
        try:
            if audio_proc:
                audio_proc.kill()

            audio_proc = subprocess.Popen(
                ["ffmpeg", "-i", VIDEO_PATH, "-vn", "-ac", "1", "-ar", str(SAMPLE_RATE), "-f", "s16le", "pipe:1"],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                bufsize=0
            )
            print(f"[{dt.now().strftime('%d/%m/%Y %H:%M:%S')}] - FFmpeg áudio iniciado ✅")

        except Exception as e:
            safe_log("Erro ao iniciar FFmpeg áudio", e)
            audio_proc = None

def read_audio_pipe(pipe, q):
    """Lê áudio do FFmpeg, detecta silêncio localmente e envia bytes ao processor."""
    while True:
        try:
            raw = pipe.read(CHUNK_SIZE)
            if raw is None or len(raw) == 0:
                print("[AudioReader] EOF do áudio – finalizado 🔚")
                break

            # Calcula silêncio apenas para log, sem interferir no envio ao processor
            audio = np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0
            rms = float(np.sqrt(np.mean(audio**2)))

            if rms < SILENCE_THRESHOLD:
                print(f"[SilenceDetector] 🔇 Silêncio detectado (RMS={rms:.6f})")

            # Se a fila estiver cheia, descarta o mais antigo (não bloqueia a thread)
            if q.full():
                try:
                    q.get_nowait()
                except queue.Empty:
                    pass

            # 🚀 Sempre entrega os bytes brutos ao processor
            q.put_nowait(raw)

        except Exception as e:
            safe_log("Erro na leitura do áudio", e)
            q.put(None)
            break

    print("[AudioReader] Thread de áudio encerrada.")
