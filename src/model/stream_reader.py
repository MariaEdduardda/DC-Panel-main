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
audio_queue = queue.Queue(maxsize=30)

video_proc = None
audio_proc = None
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

def start_audio_ffmpeg():
    global audio_proc
    with proc_lock:
        if audio_proc:
            try: audio_proc.kill()
            except: pass

        cmd = [
            "ffmpeg",
            "-nostdin",
            "-hide_banner",
            "-loglevel", "quiet",
            "-i", VIDEO_PATH,
            "-vn",
            "-ac", "1",
            "-ar", str(SAMPLE_RATE),
            "-f", "s16le",
            "pipe:1"
        ]

        audio_proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            bufsize=0   # <<< o segredo !
        )

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

def read_audio():
    global audio_proc

    chunk_ms = 200
    bytes_per_sample = 2
    samples_per_chunk = int((chunk_ms/1000) * SAMPLE_RATE)
    chunk_size = samples_per_chunk * bytes_per_sample

    while True:
        if not audio_proc:
            start_audio_ffmpeg()

        try:
            raw = audio_proc.stdout.read(chunk_size)

            # EOF ou erro
            if not raw:
                print("[AudioReader] EOF detectado. Finalizando thread de áudio.")
                try:
                    audio_queue.put_nowait(None)
                except:
                    pass
                break

            # Chunk muito pequeno → final do arquivo
            if len(raw) < chunk_size:
                if len(raw) > 1024:   # (+1 KB = útil, senão descarta)
                    print(f"[AudioReader] Chunk final útil ({len(raw)} bytes), enviando...")
                    # evita queue.Full
                    if audio_queue.full():
                        try: audio_queue.get_nowait()
                        except: pass
                    audio_queue.put_nowait(raw)
                else:
                    print(f"[AudioReader] Chunk final pequeno ({len(raw)} bytes), descartado.")
                break

            # Queue cheia → descarta o mais antigo
            if audio_queue.full():
                print("[AudioReader] Fila cheia, descartando chunk antigo.")
                try:
                    audio_queue.get_nowait()
                except:
                    pass

            audio_queue.put_nowait(raw)

        except Exception as e:
            safe_log("Erro no audio", e)
            try:
                audio_queue.put_nowait(None)
            except:
                pass
            break

    # Finalização segura
    try:
        audio_proc.kill()
    except:
        pass

    audio_proc = None
    print("[AudioReader] Thread de áudio finalizada.")
