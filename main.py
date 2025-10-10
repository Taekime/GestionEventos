from exepciones import EventoNoEncontradoError, CuposAgotadosError, DatosInvalidosError
from validador_evento import ValidadorEvento
from logger import Logger
from servicios.notificador_sms import NotificadorSMS
from servicios.servicio_reportes import ServicioReportes
from servicios.servicio_inscripcion import ServicioInscripcion
from gestion_eventos import RepositorioEventos

def mostrar_menu():
    print("\n===== Sistema de Gestión de Eventos =====")
    print("1. Crear evento")
    print("2. Inscribir estudiante")
    print("3. Generar reporte")
    print("4. Salir")
    return input("Seleccione una opción: ")

def main():
    logger = Logger()
    validador = ValidadorEvento()
    repositorio = RepositorioEventos(validador)
    notificador = NotificadorSMS(logger)  # También podrías usar NotificadorEmail(logger)
    inscripcion = ServicioInscripcion(repositorio, notificador)
    reportes = ServicioReportes(repositorio)

    while True:
        opcion = mostrar_menu()

        if opcion == "1":
            nombre = input("Nombre del evento: ")
            cupos = input("Cantidad de cupos: ")

            try:
                evento = {
                    "nombre": nombre,
                    "cupos": int(cupos),
                    "inscritos": []
                }
                repositorio.guardar(evento)
                print("✅ Evento creado exitosamente.")
            except DatosInvalidosError as e:
                print(f"❌ Error: {e}")

        elif opcion == "2":
            nombre = input("Nombre del evento: ")
            email = input("Email del estudiante: ")
            try:
                inscripcion.inscribir_estudiante(nombre, email)
            except (EventoNoEncontradoError, CuposAgotadosError) as e:
                print(f"❌ Error: {e}")

        elif opcion == "3":
            nombre = input("Nombre del evento: ")
            try:
                reportes.generar_reporte_participacion(nombre)
            except EventoNoEncontradoError as e:
                print(f"❌ Error: {e}")

        elif opcion == "4":
            print("👋 Saliendo del sistema...")
            break
        else:
            print("❗ Opción no válida, intente nuevamente.")

if __name__ == "__main__":
    main()
