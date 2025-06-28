
from .base_panel_visual import BasePanelVisual

class VisorInformes(BasePanelVisual):
    def __init__(self, controlador=None):
        super().__init__(
            titulo="Visor de Informes PDF",
            acciones=None,
            columnas_tabla=["Informe", "Fecha", "Estado", "Acción"]
        )
        self.agregar_vista_placeholder("Informes Generados")
