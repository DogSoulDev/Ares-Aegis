
from .base_panel_visual import BasePanelVisual

class PanelMonitorSistema(BasePanelVisual):
    def __init__(self, controlador=None):
        super().__init__(
            titulo="Monitorización de Sistema",
            acciones=None,
            columnas_tabla=["Recurso", "Uso Actual", "Máximo", "Detalles"]
        )
        self.agregar_vista_placeholder("Monitor de Recursos")
