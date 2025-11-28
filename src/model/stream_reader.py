from datetime import datetime as dt
import subprocess
import threading
import queue
import time
from src.model.utils import safe_log
from src.model.config import SOURCE_TYPE, STREAM_URL, VIDEO_PATH, WIDTH, HEIGHT, SAMPLE_RATE

# Melhorar a velocidade de LEITURA

process = None
process_lock = threading.Lock()
frame_queue = queue.Queue(maxsize=15)

video_proc = None
proc_lock = threading.Lock()

def start_video_ffmpeg():
    global video_proc
    with proc_lock:
        if video_proc:
            try:
                video_proc.kill()
            except:
                pass
        try:
            if SOURCE_TYPE == "srt":
                cmd = [
                    "ffmpeg","-re","-i", STREAM_URL,
                    "-an",
                    "-f", "rawvideo","-pix_fmt","bgr24",
                    "-vf", f"scale={WIDTH}:{HEIGHT}",
                    "pipe:1"
                ]
            else:
                cmd = [
                    "ffmpeg","-re","-nostdin","-i", VIDEO_PATH,
                    "-an",
                    "-f", "rawvideo","-pix_fmt","bgr24",
                    "-vf", f"scale={WIDTH}:{HEIGHT}",
                    "pipe:1"
                ]
            video_proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=10**8)
            print(f"[{dt.now().strftime('%d/%m/%Y %H:%M:%S')}] - FFMpeg vídeo iniciado")
        except Exception as e:
            safe_log("Falha ao iniciar FFmpeg vídeo", e)
            video_proc = None
            time.sleep(2)

def read_exact(fd, size):
    """Lê exatamente `size` bytes do file-like fd. Retorna bytes lidos (len==size) ou b'' no EOF."""
    buf = bytearray()
    while len(buf) < size:
        chunk = fd.read(size - len(buf))
        if not chunk:
            # EOF ou nada disponível
            return b'' if len(buf) == 0 else bytes(buf)
        buf.extend(chunk)
    return bytes(buf)

def read_frames():
    global video_proc
    frame_size = WIDTH * HEIGHT * 3
    while True:
        try:
            if not video_proc:
                start_video_ffmpeg()

            raw = read_exact(video_proc.stdout, frame_size)
            if not raw or len(raw) != frame_size:
                # reconectar em caso de EOF/incompleto (stream) ou encerrar para arquivo
                safe_log("Frame incompleto/EOF no vídeo", None)
                # se for arquivo (não srt), encerra
                if SOURCE_TYPE != "srt":
                    break
                # reinicia
                with proc_lock:
                    if video_proc:
                        try: video_proc.kill()
                        except: pass
                    video_proc = None
                time.sleep(1)
                continue

            # coloca na fila (descarta velho se estiver cheia)
            if frame_queue.full():
                try: frame_queue.get_nowait()
                except: pass
            frame_queue.put_nowait(raw)

        except Exception as e:
            safe_log("Erro na leitura do stream vídeo", e)
            with proc_lock:
                if video_proc:
                    try: video_proc.kill()
                    except: pass
                video_proc = None
            time.sleep(1)

    # close
    with proc_lock:
        if video_proc:
            try: video_proc.kill()
            except: pass
        video_proc = None
    print(f"[{dt.now().strftime('%d/%m/%Y %H:%M:%S')}] - Leitura vídeo finalizada")