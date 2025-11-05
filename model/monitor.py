import sys
import time
from colorama import Back, Fore, Style # type: ignore
from config import FILENAME
from database.db_functions import criar_ocorrencia
import datetime as dt


def monitor_status(status_dict, status_lock):
    logo_anterior = None  # Guarda o último estado do logo (para detectar mudança)

    while True:
        with status_lock:
            if not status_dict:
                time.sleep(0.5)
                continue

            total_fps = sum(st['fps'] for st in status_dict.values())
            avg_cpu = sum(st['cpu'] for st in status_dict.values()) / len(status_dict)
            avg_yolo = sum(st['yolo_time'] for st in status_dict.values()) / len(status_dict)
            logo_on = any(st['logo'] for st in status_dict.values())  # True se o logo está visível
            datetime_str = min(st['datetime'] for st in status_dict.values())

            combined = (
                f"🧠 Threads: {len(status_dict)} | "
                f"{Fore.LIGHTYELLOW_EX}FPS:{Style.RESET_ALL} {total_fps:5.1f} | "
                f"{Fore.LIGHTCYAN_EX}CPU:{Style.RESET_ALL} {avg_cpu:5.1f}% | "
                f"{Fore.MAGENTA}YOLO:{Style.RESET_ALL} {avg_yolo*1000:6.1f} ms | "
                f"{Fore.LIGHTWHITE_EX}Logo:{Style.RESET_ALL} {'🟢 ON' if logo_on else '🔴 OFF'}   "
            )

        # Exibe no terminal
        sys.stdout.write("\r" + combined)
        sys.stdout.flush()

        # 🔹 Se o logo sumiu (falha detectada) e antes estava ON, registra a ocorrência no banco
        if logo_anterior is True and logo_on is False:
            print("\n🚨 Falha detectada! Registrando no banco de dados...")

            tipo = "vídeo"         # pode mudar conforme tipo de detecção
            gravidade = "grave"    # pode ser calculada pela IA
            origem = "Rede"        # ou G5 / RSPO
            data = datetime_str.date().isoformat()
            hora = datetime_str.time().strftime("%H:%M:%S")
            duracao = "00:00"      # pode ser ajustado pelo IA
            usuario_id = 1

            # Salva no banco
            criar_ocorrencia(
                tipo=tipo,
                descricao="Falha detectada automaticamente pela IA",
                gravidade=gravidade,
                origem=origem,
                data=data,
                hora=hora,
                duracao=duracao,
                usuario_id=usuario_id
            )

        logo_anterior = logo_on
        time.sleep(0.5)
