from datetime import datetime as dt
import subprocess
import threading
import queue
import time
from model.utils import safe_log
from model.config import SOURCE_TYPE, STREAM_URL, VIDEO_PATH, WIDTH, HEIGHT

# Melhorar a velocidade de LEITURA

process = None
process_lock = threading.Lock()
frame_queue = queue.Queue(maxsize=15)

def start_ffmpeg():
    global process
    with process_lock:
        if process:
            try:
                process.kill()
            except:
                pass
        try:
            if SOURCE_TYPE == "srt":
                cmd = [
                    "ffmpeg",
                    "-re",
                    "-i", STREAM_URL,
                    "-an",
                    "-f", "rawvideo",
                    "-pix_fmt", "bgr24",
                    "-vf", f"scale={WIDTH}:{HEIGHT}",
                    "pipe:1"
                ]
            else:
                cmd = [
                    "ffmpeg",
                    "-re",  # força playback em tempo real, essencial para pipes
                    "-nostdin",
                    "-i", VIDEO_PATH,
                    "-an",
                    "-f", "rawvideo",
                    "-pix_fmt", "bgr24",
                    "-vf", f"scale={WIDTH}:{HEIGHT}",
                    "pipe:1"
                ]

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                bufsize=10**8
            )
            print(f"[{dt.now().strftime('%d/%m/%Y %H:%M:%S')}] - FFMpeg iniciado")

        except Exception as e:
            safe_log("Falha ao iniciar FFmpeg", e)
            process = None
            time.sleep(2)


def read_frames():
    global process
    frame_size = WIDTH * HEIGHT * 3

    while True:
        try:
            # inicia o ffmpeg se ainda não estiver rodando
            if not process:
                start_ffmpeg()

            raw_frame = process.stdout.read(frame_size)

            # fim do arquivo
            if not raw_frame and SOURCE_TYPE == "srt":
                    raise RuntimeError("Stream parou de enviar dados")

            # frame incompleto (geralmente fim do vídeo)
            if len(raw_frame) != frame_size:
                if SOURCE_TYPE == "srt":
                    raise RuntimeError("Frame incompleto")

            # adiciona frame na fila
            if frame_queue.full():
                frame_queue.get_nowait()
            frame_queue.put_nowait(raw_frame)

        except Exception as e:
            safe_log("Erro na leitura do stream", e)

            # se for arquivo, encerra de vez
            if SOURCE_TYPE != "srt":
                break

            # se for stream, tenta reconectar
            with process_lock:
                if process:
                    try:
                        process.kill()
                    except:
                        pass
                    process = None
            time.sleep(2)

    # encerra o processo no fim do vídeo
    with process_lock:
        if process:
            try:
                process.kill()
            except:
                pass
            process = None

    print(f"[{dt.now().strftime('%d/%m/%Y %H:%M:%S')}] - Leitura finalizada")
