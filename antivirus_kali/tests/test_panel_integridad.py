import pytest
from PySide6.QtWidgets import QApplication
from antivirus_kali.interfaz.panel_integridad import PanelIntegridad
from unittest.mock import MagicMock
import sys

@pytest.fixture(scope="module")
def app():
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    yield app

def test_panel_integridad_valida_predeterminado(app):
    mock_controlador = MagicMock()
    mock_controlador.validar.return_value = (
        {"/bin/ls": "Íntegro. Coincide con el hash oficial de Kali.", "/bin/bash": "No encontrado. Reinstale el paquete."}, []
    )
    panel = PanelIntegridad(mock_controlador)
    panel.validar()
    items = [panel.resultados.item(i).text() for i in range(panel.resultados.count())]
    assert any("Íntegro" in item or "No encontrado" in item or "Modificado" in item for item in items)

def test_panel_integridad_instanciable():
    app = QApplication.instance() or QApplication(sys.argv)
    mock_controlador = MagicMock()
    mock_controlador.validar.return_value = ({}, [])
    panel = PanelIntegridad(mock_controlador)
    assert panel.windowTitle().startswith("Ares Aegis")
    assert panel.resultados is not None
