
from .base_panel_visual import BasePanelVisual

class PanelConfiguracion(BasePanelVisual):
    def __init__(self, controlador=None):
        super().__init__(
            titulo="Configuración de la Aplicación",
            acciones=None,
            columnas_tabla=["Opción", "Valor Actual", "Descripción", "Acción"]
        )
        self.agregar_vista_placeholder("Preferencias Generales")
