class Logger:
    def __init__(self):
        self._logs = []

    def info(self, mensaje: str) -> None:
        log = f"[INFO] {mensaje}"
        self._logs.append(log)
        print(log)

    def error(self, mensaje: str) -> None:
        log = f"[ERROR] {mensaje}"
        self._logs.append(log)
        print(log)