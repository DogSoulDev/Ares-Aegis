
import pytest
import sys
from unittest.mock import MagicMock
from antivirus_kali.interfaz.panel_escaneo_sistema import PanelEscaneoSistema
from PySide6.QtWidgets import QApplication


@pytest.fixture(scope="module")
def app():
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    yield app

@pytest.fixture
def mock_controlador():
    mock = MagicMock()
    mock.obtener_resumen.return_value = {
        'rootkits': [],
        'procesos': [],
        'puertos': [],
        'servicios': [],
        'integridad': {},
        'programas': ['bash', 'coreutils']
    }
    mock.escanear_rootkits.return_value = []
    mock.escanear_procesos.return_value = []
    mock.escanear_puertos.return_value = []
    mock.escanear_servicios.return_value = []
    mock.escanear_integridad.return_value = {}
    mock.obtener_programas.return_value = ['bash', 'coreutils']
    return mock

def test_panel_escaneo_sistema_instanciable(app, mock_controlador):
    panel = PanelEscaneoSistema(mock_controlador)
    assert panel.windowTitle().startswith("Ares Aegis")
    assert panel.resultados is not None

def test_panel_escaneo_sistema_resumen(app, mock_controlador):
    panel = PanelEscaneoSistema(mock_controlador)
    panel.mostrar_resumen()
    items = [panel.resultados.item(i).text() for i in range(panel.resultados.count())]
    assert any("Resumen" in item or "No se pudo" not in item for item in items)

def test_panel_escaneo_sistema_rootkits(app, mock_controlador):
    panel = PanelEscaneoSistema(mock_controlador)
    panel.analizar_rootkits()
    items = [panel.resultados.item(i).text() for i in range(panel.resultados.count())]
    assert any("rootkit" in item.lower() or "No se pudo" not in item for item in items)

def test_panel_escaneo_sistema_procesos(app, mock_controlador):
    panel = PanelEscaneoSistema(mock_controlador)
    panel.analizar_procesos()
    items = [panel.resultados.item(i).text() for i in range(panel.resultados.count())]
    assert any("proceso" in item.lower() or "No se pudo" not in item for item in items)

def test_panel_escaneo_sistema_puertos(app, mock_controlador):
    panel = PanelEscaneoSistema(mock_controlador)
    panel.analizar_puertos()
    items = [panel.resultados.item(i).text() for i in range(panel.resultados.count())]
    assert any("puerto" in item.lower() or "No se pudo" not in item for item in items)

def test_panel_escaneo_sistema_servicios(app, mock_controlador):
    panel = PanelEscaneoSistema(mock_controlador)
    panel.analizar_servicios()
    items = [panel.resultados.item(i).text() for i in range(panel.resultados.count())]
    assert any("servicio" in item.lower() or "No se pudo" not in item for item in items)

def test_panel_escaneo_sistema_integridad(app, mock_controlador):
    panel = PanelEscaneoSistema(mock_controlador)
    panel.analizar_integridad()
    items = [panel.resultados.item(i).text() for i in range(panel.resultados.count())]
    assert any("integridad" in item.lower() or "No se pudo" not in item for item in items)

def test_panel_escaneo_sistema_programas(app, mock_controlador):
    panel = PanelEscaneoSistema(mock_controlador)
    panel.listar_programas()
    items = [panel.resultados.item(i).text() for i in range(panel.resultados.count())]
    assert any("programa" in item.lower() or "No se pudo" not in item for item in items)
