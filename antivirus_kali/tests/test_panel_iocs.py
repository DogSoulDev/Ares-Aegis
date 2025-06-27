import pytest
from PySide6.QtWidgets import QApplication
from antivirus_kali.interfaz.panel_iocs import PanelIOCs
import sys

class DummyControlador:
    def verificar_ioc(self, valor):
        if valor == "malicioso.com":
            return f"{valor}: IOC detectado (malicioso)", []
        return f"{valor}: Sin coincidencias", []

@pytest.fixture(scope="module")
def app():
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    yield app

def test_panel_iocs_agregar_y_verificar_manual(app):
    panel = PanelIOCs(DummyControlador())
    # Agregar IOC manualmente
    panel.entrada.setText("manual-ioc")
    panel.agregar_ioc()
    assert "manual-ioc" in panel.iocs_manuales
    # Verificar IOC manual
    panel.entrada.setText("manual-ioc")
    panel.verificar()
    items = [panel.resultados.item(i).text() for i in range(panel.resultados.count())]
    assert any("manualmente marcado" in item for item in items)

def test_panel_iocs_verificar_api(app):
    panel = PanelIOCs(DummyControlador())
    panel.entrada.setText("malicioso.com")
    panel.verificar()
    items = [panel.resultados.item(i).text() for i in range(panel.resultados.count())]
    assert any("malicioso" in item for item in items)
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
    assert panel.resultados is not None
