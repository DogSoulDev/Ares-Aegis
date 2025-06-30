
from .base_panel_visual import BasePanelVisual

class VisorResultados(BasePanelVisual):
    def __init__(self, controlador=None):
        super().__init__(
            titulo="Resultados de Escaneo",
            acciones=None,
            columnas_tabla=["Archivo", "Amenaza", "Nivel de Riesgo", "Detalles"]
        )
        self.agregar_vista_placeholder("Resultados de Escaneo")
