"""
Panel visual de Ares Aegis para mostrar amenazas detectadas por IOCs y reputación de repositorios.
Estilo minimalista japonés, limpio y diferente.
"""

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt


class PanelIOCs(QWidget):
    def __init__(self, controlador):
        super().__init__()
        self.controlador = controlador
        self.setWindowTitle("Ares Aegis - Detección de IOCs y Reputación")
        pass
        self.iocs_manuales = set()
        self.iocs_manuales = set()





