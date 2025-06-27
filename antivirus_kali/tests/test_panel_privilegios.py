import pytest
from PySide6.QtWidgets import QApplication
from antivirus_kali.interfaz.panel_privilegios import PanelPrivilegios
import sys

class DummyControlador:
    def monitorear_privilegios(self):
        # Simula un proceso peligroso
        return [
            {'pid': 1234, 'name': 'evilproc', 'cmdline': ['evilproc', '--danger'], 'username': 'root'}
        ]

@pytest.fixture(scope="module")
def app():
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    yield app

def test_panel_privilegios_resalta_procesos(app):
    panel = PanelPrivilegios(DummyControlador())
    panel.monitorear()
    # Debe haber al menos un proceso resaltado
    items = [panel.resultados.item(i).text() for i in range(panel.resultados.count())]
    assert any('evilproc' in item for item in items)
    # Debe mostrar advertencia
    assert 'sospechosos' in panel.advertencia_label.text().lower()
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
