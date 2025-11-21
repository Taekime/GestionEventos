import csv
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from excepciones import EventoNoEncontradoError

class ServicioReportes:
    def __init__(self, repositorio_eventos):
        self._repositorio = repositorio_eventos

    def generar_reporte_participacion(self, nombre_evento: str) -> None:
        # Este método era para consola, no es crítico para la web pero lo dejamos
        pass

    def exportar_lista_csv(self, nombre_evento: str):
        evento = self._repositorio.buscar_por_nombre(nombre_evento)
        if not evento:
            raise EventoNoEncontradoError(f"Evento '{nombre_evento}' no encontrado.")
            
        # Ahora esto devuelve tuplas (nombre, email)
        datos_inscritos = self._repositorio.obtener_inscritos_lista(evento["id"])
        
        if not datos_inscritos:
            print(f"⚠️ El evento '{nombre_evento}' no tiene inscritos.")
            return

        nombre_limpio = nombre_evento.replace(' ', '_')
        nombre_archivo = f"asistencia_{nombre_limpio}.csv"
        
        try:
            with open(nombre_archivo, mode='w', newline='', encoding='utf-8-sig') as archivo:
                writer = csv.writer(archivo)
                # Nuevos encabezados
                writer.writerow(["Evento", "Fecha", "Hora", "Nombre Alumno", "Email", "Firma"])
                
                for dato in datos_inscritos:
                    nombre_alumno = dato[0]
                    email_alumno = dato[1]
                    writer.writerow([evento['nombre'], evento['fecha'], evento['hora'], nombre_alumno, email_alumno, "_______"])
            
            print(f"✅ Archivo generado: {nombre_archivo}")
            
        except IOError as e:
            print(f"❌ Error al escribir el archivo: {e}")