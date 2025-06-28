from antivirus_kali.interfaz.panel_iocs import PanelIOCs
from PySide6.QtWidgets import QApplication
import sys

def test_panel_iocs_instanciable():
    app = QApplication.instance() or QApplication(sys.argv)
    class DummyControlador:
        def verificar_ioc(self, valor):
            return ("limpio", [])
    panel = PanelIOCs(DummyControlador())
    assert panel.windowTitle().startswith("Ares Aegis")
    # Eliminado: referencia a widget obsoleto
