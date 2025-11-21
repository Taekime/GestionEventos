import sys
import os

# Ajuste de ruta para encontrar el módulo padre
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gestion_eventos import ServicioNotificacion
from logger import Logger

class NotificadorSMS(ServicioNotificacion):
    """Implementación de notificaciones por SMS"""

    def __init__(self, logger: Logger):
        self._logger = logger

    def enviar(self, destinatario: str, mensaje: str) -> bool:
        self._logger.info(f"[SMS] Enviando SMS a {destinatario}: {mensaje}")
        return True