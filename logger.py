# logger.py

class Logger:
    """
    Logger simple para registrar eventos y errores del sistema.
    Implementado por Martín Rojas (Estudiante 2)
    """

    def _init_(self):
        self._logs = []

    def info(self, mensaje: str) -> None:
        """Registra un mensaje informativo"""
        log = f"[INFO] {mensaje}"
        self._logs.append(log)
        print(log)

    def error(self, mensaje: str) -> None:
        """Registra un mensaje de error"""
        log = f"[ERROR] {mensaje}"
        self._logs.append(log)
        print(log)

    def obtener_logs(self):
        """Devuelve el historial de logs"""
        return self._logs.copy()