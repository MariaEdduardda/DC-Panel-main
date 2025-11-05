import cv2
import numpy as np

last_frame = None

def analyze(frame, limiar_preto=10, limiar_freeze=3.0):
    global last_frame

    # Tela preta
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    brilho_medio = np.mean(gray)
    if brilho_medio < limiar_preto:
        return {
            "tipo": "video",
            "gravidade": "leve",
            "origem": "Rede",
            "descricao": "fade"
        }  # Tela preta detectada

    # Frame congelado
    elif last_frame is not None:
        diff = cv2.absdiff(frame, last_frame)
        media_diff = np.mean(diff)
        if media_diff < limiar_freeze:
            return {
            "tipo": "video",
            "gravidade": "leve",
            "origem": "Rede",
            "descricao": "freexe"
        }  # Frame congelado
    else:
        last_frame = frame.copy()
        return None
