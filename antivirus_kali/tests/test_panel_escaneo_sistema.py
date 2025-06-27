from antivirus_kali.interfaz.panel_escaneo_sistema import PanelEscaneoSistema
from antivirus_kali.controladores.controlador_escaneo_sistema import ControladorEscaneoSistema
from PySide6.QtWidgets import QApplication
import sys

def test_panel_escaneo_sistema_instanciable():
    app = QApplication.instance() or QApplication(sys.argv)
    panel = PanelEscaneoSistema(ControladorEscaneoSistema())
    assert panel.windowTitle().startswith("Ares Aegis")
    assert panel.resultados is not None
