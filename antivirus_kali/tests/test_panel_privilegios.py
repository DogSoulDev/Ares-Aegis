from antivirus_kali.interfaz.panel_privilegios import PanelPrivilegios
from PySide6.QtWidgets import QApplication
import sys

def test_panel_privilegios_instanciable():
    app = QApplication.instance() or QApplication(sys.argv)
    class DummyControlador:
        def monitorear_privilegios(self):
            return []
    panel = PanelPrivilegios(DummyControlador())
    assert panel.windowTitle().startswith("Ares Aegis")
    assert panel.resultados is not None
