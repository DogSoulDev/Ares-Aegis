
from .base_panel_visual import BasePanelVisual

class PanelHistorial(BasePanelVisual):
    def __init__(self, controlador=None):
        super().__init__(
            titulo="Historial de Escaneos",
            acciones=None,
            columnas_tabla=["Fecha", "Tipo de Escaneo", "Resultados", "Detalles"]
        )
        self.agregar_vista_placeholder("Historial de Escaneos")
