import subprocess
import time
import src.model.config as config

# Grava a live stream e armazena no output_path

MAIN_RECORD = None  # caminho do arquivo principal
RECORD_START_TIME = None 

def start_recording():
    global MAIN_RECORD, RECORD_START_TIME

    timestamp = time.strftime("%d%m%Y_%H%M%S")
    output_path = f"{config.CONFIG['SAVE_FOLDER']}/full_{timestamp}.ts"
    MAIN_RECORD = output_path
    RECORD_START_TIME = time.time()

    ffmpeg_cmd = [
        "ffmpeg",
        "-y",  # sobrescreve arquivo se existir
        "-i", config.CONFIG["STREAM_URL"],
        "-c", "copy",  # não recodifica, grava direto
        "-f", "mpegts",  # formato que pode ser cortado enquanto grava
        output_path
    ]
    process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return process, output_path

record_process, output_path_live_stream = False, False

if config.CONFIG["SOURCE_TYPE"] == "srt":
    record_process, output_path_live_stream = start_recording()