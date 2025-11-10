import cv2
import numpy as np
from src.model.config import BLACK_THRESHOLD, FREEZE_THRESHOLD, FREEZER_FRAMES_THRESHOLD

last_frame = None
freeze_counter = 0

def analyze(frame):
    global last_frame, freeze_counter

    # Tela preta
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    brilho_medio = np.mean(gray)
    if brilho_medio < BLACK_THRESHOLD:
        return {
            "tipo": "video",
            "gravidade": "leve",
            "origem": "Rede",
            "descricao": "fade"
        }  # Tela preta detectada

    # Frame congelado
    if last_frame is not None:
        diff = cv2.absdiff(frame, last_frame)
        media_diff = np.mean(diff)

        if media_diff < FREEZE_THRESHOLD:
            freeze_counter += 1
        else:
            freeze_counter = 0

        # se ficou igual por X frames seguidos, confirma freeze
        if freeze_counter >= FREEZER_FRAMES_THRESHOLD:
            freeze_counter = 0
            last_frame = frame.copy()
            return {
                "tipo": "video",
                "gravidade": "leve",
                "origem": "Rede",
                "descricao": "freeze"
            }

    # Atualiza o último frame (importante!)
    last_frame = frame.copy()
