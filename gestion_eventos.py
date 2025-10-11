# CÓDIGO REFACTORIZADO SOLID

from abc import ABC, abstractmethod
from validador_evento import ValidadorEvento
from excepciones import (
    EventoNoEncontradoError,
    CuposAgotadosError,
    DatosInvalidosError
)

# 1. Repositorio de eventos
class RepositorioEventos:
    def init(self):
        self._eventos = []
        self.validador = ValidadorEvento()

    def guardar(self, evento):
        if not self.validador.validar_nombre(evento.get("nombre", "")):
            raise DatosInvalidosError("Nombre de evento inválido")

        if not self.validador.validar_cupos(evento.get("cupos", 0)):
            raise DatosInvalidosError("Cupos inválidos")

        self._eventos.append(evento)

    def buscar_por_nombre(self, nombre):
        for evento in self._eventos:
            if evento["nombre"] == nombre:
                return evento
        return None

# 2. Abstracción notificación
class ServicioNotificacion(ABC):
    @abstractmethod
    def enviar(self, destinatario, mensaje):
        pass

# 3. Notificador por email
class NotificadorEmail(ServicioNotificacion):
    def enviar(self, destinatario, mensaje):
        print(f"Enviando correo a {destinatario}: {mensaje}")

# 4. Lógica de inscripción
class ServicioInscripcion:
    def init(self, repositorio: RepositorioEventos, notificador: ServicioNotificacion):
        self._repositorio = repositorio
        self._notificador = notificador

    def inscribir_estudiante(self, nombre_evento, email_estudiante):
        evento = self._repositorio.buscar_por_nombre(nombre_evento)

        if not evento:
            raise EventoNoEncontradoError(f"El evento '{nombre_evento}' no existe.")

        if len(evento["inscritos"]) < evento["cupos"]:
            evento["inscritos"].append(email_estudiante)
            mensaje = f"Inscripción confirmada en '{nombre_evento}'"
            self._notificador.enviar(email_estudiante, mensaje)
            print(f"Inscripción de {email_estudiante} en '{nombre_evento}' fue exitosa.")
        else:
            raise CuposAgotadosError(f"No quedan cupos disponibles para '{nombre_evento}'")

# 5. Generar reportes
class ServicioReportes:
    def init(self, repositorio: RepositorioEventos):
        self._repositorio = repositorio

    def generar_reporte_participacion(self, nombre_evento):
        evento = self._repositorio.buscar_por_nombre(nombre_evento)

        if not evento:
            raise EventoNoEncontradoError(f"No se encontró el evento '{nombre_evento}' para el reporte.")

        print("--- Reporte de Participación ---")
        print(f"Evento: {evento['nombre']}")
        print(f"Inscritos: {len(evento['inscritos'])} de {evento['cupos']}")
        print("------------------------------")