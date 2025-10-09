# validador_evento.py

class ValidadorEvento:
    """Responsable de validar datos de eventos"""

    @staticmethod
    def validar_nombre(nombre: str) -> bool:
        """Valida que el nombre del evento sea válido"""
        return isinstance(nombre, str) and len(nombre.strip()) > 0

    @staticmethod
    def validar_cupos(cupos: int) -> bool:
        """Valida que los cupos sean un número positivo"""
        return isinstance(cupos, int) and cupos > 0

    @staticmethod
    def validar_email(email: str) -> bool:
        """Valida formato básico de email"""
        return isinstance(email, str) and '@' in email and '.' in email
