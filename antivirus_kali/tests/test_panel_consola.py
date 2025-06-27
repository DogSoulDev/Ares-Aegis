import pytest
from PySide6.QtWidgets import QApplication
from antivirus_kali.interfaz.panel_consola import PanelConsola

app = QApplication.instance() or QApplication([])

def test_panel_consola_instanciable():
    panel = PanelConsola()
    assert panel is not None
    assert hasattr(panel, 'log')
    assert callable(panel.log)

def test_panel_consola_log_and_filter():
    panel = PanelConsola()
    panel.log('Mensaje info', 'info')
    panel.log('Mensaje advertencia', 'warning')
    panel.log('Mensaje error', 'error')
    panel.filtro_combo.setCurrentText('Info')
    assert 'Mensaje info' in panel.log_text.toPlainText()
    panel.filtro_combo.setCurrentText('Advertencia')
    assert 'Mensaje advertencia' in panel.log_text.toPlainText()
    panel.filtro_combo.setCurrentText('Error')
    assert 'Mensaje error' in panel.log_text.toPlainText()
