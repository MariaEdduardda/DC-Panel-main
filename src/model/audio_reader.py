import threading
import subprocess
import queue
from datetime import datetime as dt
from src.model.config import SAMPLE_RATE, VIDEO_PATH, CHUNK_SIZE
from src.model.utils import safe_log

audio_proc = None
audio_queue = queue.Queue(maxsize=30)
proc_lock = threading.Lock()

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
    while True:
        try:
            raw = pipe.read(CHUNK_SIZE)
            if raw is None or len(raw) == 0:
                print("[AudioReader] EOF do áudio – finalizado 🔚")
                break
            if q.full():
                try:
                    q.get_nowait()
                except queue.Empty:
                    pass
            q.put_nowait(raw)

        except Exception as e:
            safe_log("Erro na leitura do áudio", e)
            q.put(None)
            break

    print(f"[{dt.now().strftime('%d/%m/%Y %H:%M:%S')}] - Thread de áudio encerrada.")
