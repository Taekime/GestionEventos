class ValidadorEvento:
    """Responsable de validar datos de eventos"""

    @staticmethod
    def validar_nombre(nombre: str) -> bool:
        """Valida que el nombre del evento sea válido"""
        return isinstance(nombre, str) and len(nombre.strip()) > 0
