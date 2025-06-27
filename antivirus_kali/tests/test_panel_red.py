from antivirus_kali.interfaz.panel_red import PanelRed
from antivirus_kali.controladores.controlador_red import ControladorRed
from PySide6.QtWidgets import QApplication
import sys

def test_panel_red_instanciable():
    app = QApplication.instance() or QApplication(sys.argv)
    class DummyAnalizador:
        def detectar_honeypots(self):
            return [], [], []
    class DummyControlador:
        def __init__(self):
            self.analizador = DummyAnalizador()
        def analizar_red(self):
            return [], [], []
    panel = PanelRed(DummyControlador())
    assert panel.windowTitle().startswith("Ares Aegis")
    assert panel.resultados is not None
