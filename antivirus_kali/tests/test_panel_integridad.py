from antivirus_kali.interfaz.panel_integridad import PanelIntegridad
from antivirus_kali.controladores.controlador_integridad import ControladorIntegridad
from PySide6.QtWidgets import QApplication
import sys

def test_panel_integridad_instanciable():
    app = QApplication.instance() or QApplication(sys.argv)
    rutas = ["/bin/ls"]
    referencia = {"ls": "HASH_FAKE"}
    panel = PanelIntegridad(ControladorIntegridad(rutas, referencia))
    assert panel.windowTitle().startswith("Ares Aegis")
    assert panel.resultados is not None
