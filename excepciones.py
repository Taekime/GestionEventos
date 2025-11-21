class EventoNoEncontradoError(Exception):
    """Excepción lanzada cuando no se encuentra un evento"""
    pass

class CuposAgotadosError(Exception):
    """Excepción lanzada cuando ya no hay cupos disponibles"""
    pass

class DatosInvalidosError(Exception):
    """Excepción lanzada cuando los datos ingresados no son válidos"""
    pass

class TopeHorarioError(Exception):
    """Excepción lanzada cuando el estudiante ya tiene un evento a la misma hora"""
    pass