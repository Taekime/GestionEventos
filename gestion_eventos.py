# CÓDIGO REFACTORIZADO SOLID

from abc import ABC, abstractmethod
from validador_evento import ValidadorEvento

# 1. Responsabilidad: Almacenar y gestionar datos de eventos
class RepositorioEventos:
    def __init__(self):
        self._eventos = []

    def guardar(self, evento):
        self._eventos.append(evento)

    def buscar_por_nombre(self, nombre):
        for evento in self._eventos:
            if evento["nombre"] == nombre:
                return evento
        return None
    validador = ValidadorEvento()

if not validador.validar_nombre(evento.get("nombre", "")):
    raise Exception("Nombre inválido")


# 2. Abstracción para notificaciones (OCP y DIP)
class ServicioNotificacion(ABC):
    @abstractmethod
    def enviar(self, destinatario, mensaje):
        pass

# 3. Implementación concreta para notificaciones por email
class NotificadorEmail(ServicioNotificacion):
    def enviar(self, destinatario, mensaje):
        print(f"Enviando correo a {destinatario}: {mensaje}")

# (Futura extensión sin modificar código existente)
# class NotificadorSMS(ServicioNotificacion):
#     def enviar(self, destinatario, mensaje):
#         print(f"Enviando SMS a {destinatario}: {mensaje}")

# 4. Responsabilidad: Lógica de negocio de la inscripción
class ServicioInscripcion:
    def __init__(self, repositorio: RepositorioEventos, notificador: ServicioNotificacion):
        self._repositorio = repositorio
        self._notificador = notificador

    def inscribir_estudiante(self, nombre_evento, email_estudiante):
        evento = self._repositorio.buscar_por_nombre(nombre_evento)
        if not evento:
            print("Error: Evento no encontrado.")
            return

        if len(evento["inscritos"]) < evento["cupos"]:
            evento["inscritos"].append(email_estudiante)
            mensaje = f"Inscripción confirmada en '{nombre_evento}'"
            self._notificador.enviar(email_estudiante, mensaje)
            print(f"Inscripción de {email_estudiante} en '{nombre_evento}' fue exitosa.")
        else:
            print("Error: No quedan cupos.")

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
            print("Error: Evento no encontrado para generar reporte.")
