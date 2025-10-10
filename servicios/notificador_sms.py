from servicios.servicio_notificacion import ServicioNotificacion
from servicios.logger import Logger

class NotificadorSMS(ServicioNotificacion):
    """Implementación de notificaciones por SMS"""

    def init(self, logger: Logger):
        self._logger = logger

    def enviar(self, destinatario: str, mensaje: str) -> bool:
        """Envía un mensaje SMS (simulado)"""
        self._logger.info(f"[SMS] Enviando SMS a {destinatario}: {mensaje}")
        return True
