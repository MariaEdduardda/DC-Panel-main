import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
from src.model.config import BLACK_THRESHOLD, FREEZE_THRESHOLD, FREEZER_FRAMES_THRESHOLD, CLIP_THRESHOLD, SILENCE_THRESHOLD

last_frame_small = None
freeze_counter = 0



def analyze_video(frame):
    global last_frame_small, freeze_counter

    # ====================== Tela preta ======================
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    brilho = np.mean(gray)

    if frame is None or frame.size == 0:
        freeze_counter = 0
        return {"tipo": "video", "descricao": "ok"}

    if brilho < BLACK_THRESHOLD:
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
        if freeze_counter >= 30:   # 1 segundo em 30fps
            freeze_counter = 0
            last_frame_small = small.copy()
            return {
                "tipo": "video",
                "descricao": "freeze",
                "gravidade": "leve",
                "origem": "Rede"
            }

    last_frame_small = small.copy()
    return {"tipo": "video", "descricao": "ok"}


def analyze_audio(chunk):
    if not chunk:
        return None
    # converte bytes -> int16 -> float
    data = np.frombuffer(chunk, dtype=np.int16).astype(np.float32) / 32768.0

    rms = np.sqrt(np.mean(data ** 2))
    clipped = np.mean(np.abs(data) > CLIP_THRESHOLD)

    silence = rms < SILENCE_THRESHOLD
    clipping = clipped > 0.01

    if silence:
        return {
            "tipo": "audio",
            "descricao": "silencio",
            "gravidade": "leve",
            "origem": "Rede"
        }

    if clipping:
        return {
            "tipo": "audio",
            "descricao": "clipping",
            "gravidade": "moderado",
            "origem": "Rede"
        }
    return None
