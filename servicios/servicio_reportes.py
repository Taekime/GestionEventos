from typing import List, Dict, Optional

class ServicioReportes:
    """Servicio para generar reportes de participación en eventos"""

    def _init_(self, repositorio_eventos):
        self._repositorio = repositorio_eventos

    def generar_reporte_participacion(self, nombre_evento: str) -> None:
        evento = self._repositorio.buscar_por_nombre(nombre_evento)
        if evento:
            print("--- Reporte de Participación ---")
            print(f"Evento: {evento['nombre']}")
            print(f"Inscritos: {len(evento.get('inscritos', []))} de {evento['cupos']}")
            print("------------------------------")
        else:
            print(f"Error: Evento '{nombre_evento}' no encontrado para generar reporte.")
