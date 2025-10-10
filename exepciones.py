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

# 4. Responsabilidad: Lógica de negocio de la inscripción
class ServicioInscripcion:
    def __init__(self, repositorio: RepositorioEventos, notificador: ServicioNotificacion):
        self._repositorio = repositorio
        self._notificador = notificador

    def inscribir_estudiante(self, nombre_evento, email_estudiante):
        evento = self._repositorio.buscar_por_nombre(nombre_evento)
        # CAMBIO: Se reemplazó el print por lanzamiento de excepción personalizada
        if not evento:
            raise EventoNoEncontradoError(f"El evento '{nombre_evento}' no existe")

        if len(evento["inscritos"]) < evento["cupos"]:
            evento["inscritos"].append(email_estudiante)
            mensaje = f"Inscripción confirmada en '{nombre_evento}'"
            self._notificador.enviar(email_estudiante, mensaje)
            print(f"Inscripción de {email_estudiante} en '{nombre_evento}' fue exitosa.")
        else:
            # CAMBIO: Se reemplazó el print por lanzamiento de excepción personalizada
            raise CuposAgotadosError(f"No hay cupos disponibles para '{nombre_evento}'")

# 5. Responsabilidad: Generar reportes
class ServicioReportes:
    def __init__(self, repositorio: RepositorioEventos):
        self._repositorio = repositorio

    def generar_reporte_participacion(self, nombre_evento):
        evento = self._repositorio.buscar_por_nombre(nombre_evento)
        if evento:
            print("--- Reporte de Participación ---")
            print(f"Evento: {evento['nombre']}")
            print(f"Inscritos: {len(evento['inscritos'])} de {evento['cupos']}")
            print("------------------------------")
        else:
            # CAMBIO: Se reemplazó el print por lanzamiento de excepción personalizada
            raise EventoNoEncontradoError(f"No se puede generar reporte: El evento '{nombre_evento}' no existe")