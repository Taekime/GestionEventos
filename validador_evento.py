from datetime import datetime

class ValidadorEvento:
    """Responsable de validar datos de eventos"""

    @staticmethod
    def validar_nombre(nombre: str) -> bool:
        return isinstance(nombre, str) and len(nombre.strip()) > 0

    @staticmethod
    def validar_descripcion(descripcion: str) -> bool:
        return isinstance(descripcion, str) and len(descripcion.strip()) > 0

    @staticmethod
    def validar_cupos(cupos: int) -> bool:
        if isinstance(cupos, str) and cupos.isdigit():
            cupos = int(cupos)
        return isinstance(cupos, int) and cupos > 0

    @staticmethod
    def validar_email(email: str) -> bool:
        """
        Valida que el email tenga formato correcto Y 
        pertenezca al dominio de la universidad.
        """
        if not isinstance(email, str) or '@' not in email:
            return False
        
        # --- REGLA DE NEGOCIO: Solo correos UBO ---
        dominio_requerido = "@pregrado.ubo.cl" or "@postgrado.ubo.cl"
        return email.strip().lower().endswith(dominio_requerido)

    @staticmethod
    def validar_fecha_futura(fecha_str: str) -> bool:
        try:
            fecha_evento = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            hoy = datetime.now().date()
            return fecha_evento >= hoy
        except ValueError:
            return False