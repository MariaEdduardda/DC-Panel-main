import threading
from src.interface.ui.layout import init_interface
from src.model.main import init_model
import sys

if __name__ == "__main__":

    sys.stdout = open("src/logs/model_log.txt", "w", encoding="utf-8")
    sys.stderr = open("src/logs/model_error.txt", "w", encoding="utf-8")

    # Cria e inicia o modelo em uma thread separada
    model_thread = threading.Thread(target=init_model, daemon=True)
    model_thread.start()

    # Inicia a interface (deve rodar no thread principal)
    init_interface()
