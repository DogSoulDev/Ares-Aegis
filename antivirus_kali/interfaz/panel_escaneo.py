
from .base_panel_visual import BasePanelVisual

class PanelEscaneo(BasePanelVisual):
    def __init__(self, controlador=None):
        super().__init__(
            titulo="Escaneo Principal",
            acciones=[
                ("Iniciar Escaneo", self.iniciar_escaneo),
                ("Ver Progreso", self.ver_progreso)
            ],
            columnas_tabla=["Archivo", "Estado", "Amenaza", "Detalles"]
        )
        self.agregar_vista_placeholder("Progreso de Escaneo")

    def iniciar_escaneo(self):
        self.status.showMessage("Escaneo iniciado...")

    def ver_progreso(self):
        self.status.showMessage("Mostrando progreso del escaneo...")
