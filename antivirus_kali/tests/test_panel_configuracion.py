import pytest
from PySide6.QtWidgets import QApplication
from antivirus_kali.interfaz.panel_configuracion import PanelConfiguracion

app = QApplication.instance() or QApplication([])

def test_panel_configuracion_instanciable():
    panel = PanelConfiguracion()
    assert panel is not None
    assert hasattr(panel, 'guardar_configuracion')
    assert callable(panel.guardar_configuracion)

def test_panel_configuracion_cambios():
    panel = PanelConfiguracion()
    panel.combo_idioma.setCurrentIndex(0)
    panel.check_notificaciones.setChecked(True)
    panel.check_darkmode.setChecked(False)
    panel.input_export.setText('/tmp')
    panel.guardar_configuracion()
    # No excepción = éxito
