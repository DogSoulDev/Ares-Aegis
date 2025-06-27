import pytest
from PySide6.QtWidgets import QApplication
from antivirus_kali.interfaz.panel_historial import PanelHistorial

app = QApplication.instance() or QApplication([])

def test_panel_historial_instanciable():
    panel = PanelHistorial()
    assert panel is not None
    assert hasattr(panel, 'tabla')
    assert hasattr(panel, 'exportar_pdf')

def test_panel_historial_exportar_seleccion_exists():
    panel = PanelHistorial()
    assert hasattr(panel, 'exportar_seleccion')
    assert callable(panel.exportar_seleccion)

def test_panel_historial_ver_detalles_exists():
    panel = PanelHistorial()
    assert hasattr(panel, 'ver_detalles')
    assert callable(panel.ver_detalles)
