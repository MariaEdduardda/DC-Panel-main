import os
from collections import deque
import time

# =============== Configurações ===============

# Caminhos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # diretório onde está o config.py
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))  # sobe um nível, para a raiz do projeto

STREAM_URL = "srt://168.90.225.116:6053?mode=caller&latency=2000&transtype=live&passphrase=yKz585@354&pbkeylen=16"
# VIDEO_PATH = "C:/Users/User/Downloads/Ocorrências_Globo/freeze/1/Ocorrência BDPE_Variação_20082025_06h32m59s.mp4" # Freeze
VIDEO_PATH = "C:/Users/User/Downloads/Ocorrências_Globo/fade/1/Ocorrência BDPE_Corte de Sinal_22082025_08h29m02s.mp4" # Fade
MODEL_PATH = r".\weights\best.pt" # caminho do modelo da I.A.
SAVE_FOLDER = f"cortes/{time.strftime('%d%m%Y')}" # Pasta para salvar frames selecionados
ALARM_FILE = os.path.join(ROOT_DIR, "sounds", "alarm.mp3") # arquivo de audio
STANDBY_FILE = os.path.join(ROOT_DIR, "sounds", "standby.mp3") # arquivo de audio
STANDON_FILE = os.path.join(ROOT_DIR, "sounds", "standon.mp3") # arquivo de audio

# Valores 
SOURCE_TYPE = "file" # srt ou file
WIDTH, HEIGHT = 640, 360 # Tamanho dos frames
YOLO_CONF = 0.70 # Valor de Confiança da I.A.
NUM_THREADS = 1 # Numero de Threads de processamento
VOLUME = 60 # Volume das notificações
FPS_ESTIMATED = 30  # FPS do video/transmissão
BUFFER_SECONDS = 2 # Buffer de segundos antes do corte
DETECTION_APPEAR_THRESHOLD = 1 # Quantidade de frames para confirmar que houve uma ocorrencia 
DETECTION_DISAPPEAR_THRESHOLD = 5 # Quantidade de frames para confirmar que acabou a ocorrencia 

# Outros
FRAME_BUFFER = deque(maxlen=BUFFER_SECONDS * FPS_ESTIMATED) # Lista do buffer de corte
os.makedirs(SAVE_FOLDER, exist_ok=True) # Garante que a pasta existe