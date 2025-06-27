import pytest
from PySide6.QtWidgets import QApplication
from antivirus_kali.interfaz.panel_consola import PanelConsola
from antivirus_kali.interfaz.panel_configuracion import PanelConfiguracion
from antivirus_kali.interfaz.panel_historial import PanelHistorial
from antivirus_kali.interfaz.panel_escaneo_sistema import PanelEscaneoSistema
from antivirus_kali.controladores.controlador_escaneo_sistema import ControladorEscaneoSistema

app = QApplication.instance() or QApplication([])

def test_paneles_independientes():
    consola = PanelConsola()
    config = PanelConfiguracion()
    historial = PanelHistorial()
    escaneo = PanelEscaneoSistema(ControladorEscaneoSistema(), panel_consola=consola)
    assert consola is not config
    assert consola is not historial
    assert config is not historial
    assert escaneo.panel_consola is consola
    # Cada panel debe poder funcionar sin los otros
    config.guardar()
    historial.refrescar()
    escaneo.pausar_analisis()
    escaneo.reanudar_analisis()
    escaneo.cancelar_analisis()
