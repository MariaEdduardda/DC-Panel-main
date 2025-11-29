import os
from collections import deque
import time
from config import VIDEO_PATH

# =============== Configurações ===============

# Caminhos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # diretório onde está o config.py
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))  # sobe um nível, para a raiz do projeto
SAVE_FOLDER = f"cortes/{time.strftime('%d%m%Y')}" # Pasta para salvar frames selecionados

CONFIG = {
    # Caminhos e arquivos
    "STREAM_URL": "srt://168.90.225.116:6053?mode=caller&latency=2000&transtype=live&passphrase=yKz585@354&pbkeylen=16",
    "MODEL_PATH": r".\weights\best.pt",
    "VIDEO_PATH": VIDEO_PATH,  # Será setado externamente se necessário
    "SAVE_FOLDER": SAVE_FOLDER,
    "ALARM_FILE": os.path.join(ROOT_DIR, "sounds", "alarm.mp3"),
    "STANDBY_FILE": os.path.join(ROOT_DIR, "sounds", "standby.mp3"),
    "STANDON_FILE": os.path.join(ROOT_DIR, "sounds", "standon.mp3"),

    # Gerais
    "SOURCE_TYPE": "file",
    "WIDTH": 640,
    "HEIGHT": 360,
    "NUM_THREADS": 1,
    "BUFFER_SECONDS": 2,
    "CPU_LOAD_LIMIT": 90,

    # Detecção (YOLO)
    "YOLO_CONF": 0.70,
    "DETECTION_THRESHOLD": 5,
    "OCCURRENCE_END_THRESHOLD": 5,

    # Áudio Analyze
    "SILENCE_THRESHOLD": 0.05,
    "CLIP_THRESHOLD": 0.98,
    "SAMPLE_RATE": 16000,

    # Vídeo Analyze
    "FPS_ESTIMATED": 30,
    "BLACK_THRESHOLD": 10,
    "FREEZE_THRESHOLD": 8,
    "FREEZE_FRAMES_THRESHOLD": 30,

    # Leitura de áudio
    "CHUNK_MS": 100,
    "CHUNK_SIZE": int(16000 * 2 * (100 / 1000)),  # int16 mono

    # Processamento
    "PROCESSOR_ON": False,
}

# Métodos auxiliares
def set_value(key, value):
    """Atualiza um valor da configuração."""
    CONFIG[key] = value

def get_value(key):
    """Lê um valor da configuração."""
    return CONFIG.get(key)

# Garante que a pasta de cortes exista
os.makedirs(CONFIG["SAVE_FOLDER"], exist_ok=True)

# Outros
FRAME_BUFFER = deque(maxlen=CONFIG["BUFFER_SECONDS"] * CONFIG["FPS_ESTIMATED"]) # Lista do buffer de corte