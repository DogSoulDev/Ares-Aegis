from antivirus_kali.interfaz.panel_modo_seguro import PanelModoSeguro
from PySide6.QtWidgets import QApplication
import sys

def test_panel_modo_seguro_instanciable():
    app = QApplication.instance() or QApplication(sys.argv)
    class DummyControlador:
        def activar_modo_seguro(self):
            return ""
        def desactivar_modo_seguro(self):
            return ""
        def auditar(self):
            return ""
    panel = PanelModoSeguro(DummyControlador())
    assert panel.windowTitle().startswith("Ares Aegis")
    # Eliminado: referencia a widget obsoleto
