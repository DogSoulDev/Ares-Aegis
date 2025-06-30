
from .base_panel_visual import BasePanelVisual

class PanelOpcionesEscaneo(BasePanelVisual):
    def __init__(self, controlador=None):
        super().__init__(
            titulo="Opciones Avanzadas de Escaneo",
            acciones=[
                ("Seleccionar Carpeta", self.seleccionar_carpeta),
                ("Configurar YARA", self.configurar_yara)
            ],
            columnas_tabla=["Opción", "Valor", "Descripción", "Acción"]
        )
        self.agregar_vista_placeholder("Opciones Avanzadas")

    def seleccionar_carpeta(self):
        self.status.showMessage("Seleccionar carpeta para escaneo...")

    def configurar_yara(self):
        self.status.showMessage("Configurando reglas YARA...")
