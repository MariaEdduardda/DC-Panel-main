import os
from collections import deque
import time
from config import VIDEO_PATH

# =============== Configurações ===============

# Caminhos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # diretório onde está o config.py
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))  # sobe um nível, para a raiz do projeto

STREAM_URL = "srt://168.90.225.116:6053?mode=caller&latency=2000&transtype=live&passphrase=yKz585@354&pbkeylen=16"

MODEL_PATH = r".\weights\best.pt" # caminho do modelo da I.A.
VIDEO_PATH = VIDEO_PATH
SAVE_FOLDER = f"cortes/{time.strftime('%d%m%Y')}" # Pasta para salvar frames selecionados
ALARM_FILE = os.path.join(ROOT_DIR, "sounds", "alarm.mp3") # arquivo de audio
STANDBY_FILE = os.path.join(ROOT_DIR, "sounds", "standby.mp3") # arquivo de audio
STANDON_FILE = os.path.join(ROOT_DIR, "sounds", "standon.mp3") # arquivo de audio

# Variaveis GERAIS 
SOURCE_TYPE = "file" # srt ou file
WIDTH, HEIGHT = 640, 360 # Tamanho dos frames
NUM_THREADS = 1 # Numero de Threads de processamento
BUFFER_SECONDS = 2 # Buffer de segundos antes do corte
CPU_LOAD_LIMIT = 90 # Limite de uso de CPU para processar (em %)

# Variaveis de DETECÇÃO

YOLO_CONF = 0.70 # Valor de Confiança da I.A.
DETECTION_THRESHOLD = 5 # Quantidade de frames para confirmar que uma ocorrencia acabou


# Variaveis de ANALYZE AUDIO

SILENCE_THRESHOLD = 0.05 # TH de silêncio (RMS)
CLIP_THRESHOLD = 0.98
SAMPLE_RATE = 16000 # Taxa de amostragem do áudio


# Variaveis de ANALYZE VIDEO

FPS_ESTIMATED = 30  # FPS do video/transmissão
BLACK_THRESHOLD = 10 # TH de quadro preto (0-255)
FREEZE_THRESHOLD = 8 # TH de similaridade para freeze (0-10)
FREEZER_FRAMES_THRESHOLD = 30 # Quantidade de frames similares para confirmar freeze

# Variaveis de LEITURA AUDIO

CHUNK_MS = 100  # Duração de cada chunk de áudio em ms
CHUNK_SIZE = int(SAMPLE_RATE * 2 * (CHUNK_MS / 1000))  # 2 bytes por sample (int16 mono)


# Variaveis de PROCESSAMENTO
PROCESSOR_ON = False

# Outros
FRAME_BUFFER = deque(maxlen=BUFFER_SECONDS * FPS_ESTIMATED) # Lista do buffer de corte
os.makedirs(SAVE_FOLDER, exist_ok=True) # Garante que a pasta existe