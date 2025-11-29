import cv2
import numpy as np
from datetime import datetime as dt
from skimage.metrics import structural_similarity as ssim # type: ignore
import src.model.config as config
from src.model.utils import safe_log

last_frame_small = None
freeze_counter = 0

def analyze_video(frame): # Recebe frame um frame
    global last_frame_small, freeze_counter

    # ====================== Tela preta ======================
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    brilho = np.mean(gray)

    if frame is None or frame.size == 0:
        freeze_counter = 0
        return {"tipo": "video", "descricao": "ok"}

    if brilho < config.CONFIG["BLACK_THRESHOLD"]:
        freeze_counter = 0
        last_frame_small = None
        return {
            "tipo": "video",
            "descricao": "fade",
            "gravidade": "leve",
            "origem": "Rede"
        }

    # ====================== Pré-processamento ======================
    # Reduza para 64x36 → muito mais estável e rápido
    small = cv2.resize(gray, (64, 36))

    if last_frame_small is not None:
        score = ssim(small, last_frame_small)

        # SSIM muito alto = imagem igual (provável freeze)
        if score > 1:  # DETECÇÃO DE FREEZE REAL
            freeze_counter += 1
        else:
            freeze_counter = 0

        # Confirma freeze depois de X frames
        if freeze_counter >= config.CONFIG["FREEZE_FRAMES_THRESHOLD"]:   # 1 segundo em 30fps
            freeze_counter = 0
            last_frame_small = small.copy()
            return {
                "tipo": "video",
                "descricao": "freeze",
                "gravidade": "leve",
                "origem": "Rede"
            }

    last_frame_small = small.copy()
    return {
        "tipo": "video",
        "descricao": "ok"
    }


def analyze_audio(chunk): # Recebe bytes brutos do áudio
    if chunk is None or len(chunk) == 0:
        return None
    try:
        data = np.frombuffer(chunk, np.int16).astype(np.float32) / 32768.0
    except Exception as e:
        safe_log("Erro ao converter chunk de áudio", e)
        return None

    # RMS do bloco (valor entre 0 e ~1)
    rms = float(np.sqrt(np.mean(data ** 2)))
    # taxa de samples 'clipped'
    clipped_ratio = float(np.mean(np.abs(data) > config.CONFIG["CLIP_THRESHOLD"]))

    # Silence detection
    if rms < config.CONFIG["SILENCE_THRESHOLD"]:
        return {
            "tipo": "audio",
            "descricao": "silence",
            "gravidade": "leve",
            "origem": "Rede"
        }

    # clipping
    if clipped_ratio > 0.01:
        return {
            "tipo": "audio",
            "descricao": "clipping",
            "gravidade": "moderado",
            "origem": "Rede"
        }
    # sem evento relevante
    return None
