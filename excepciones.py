# EXCEPCIONES PERSONALIZADAS AGREGADAS
class EventoNoEncontradoError(Exception):
    """Excepción lanzada cuando no se encuentra un evento"""
    pass

class CuposAgotadosError(Exception):
    """Excepción lanzada cuando ya no hay cupos disponibles"""
    pass

class DatosInvalidosError(Exception):
    """Excepción lanzada cuando los datos ingresados no son válidos"""
    pass

