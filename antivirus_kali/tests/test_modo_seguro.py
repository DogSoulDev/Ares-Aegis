import pytest
import shutil
from antivirus_kali.controladores.controlador_modo_seguro import ControladorModoSeguro

def test_ufw_binario_disponible():
    assert shutil.which('ufw'), 'ufw no está instalado ni como binario'

def test_controlador_modo_seguro_instanciable():
    ctrl = ControladorModoSeguro()
    assert hasattr(ctrl, 'activar_modo_seguro')
    assert hasattr(ctrl, 'desactivar_modo_seguro')
from antivirus_kali.nucleo.modo_seguro import ModoSeguro
import pytest

def test_ufw_no_disponible(monkeypatch):
    monkeypatch.setattr('antivirus_kali.nucleo.modo_seguro.os.system', lambda x: 0)
    modo = ModoSeguro()
    monkeypatch.setattr(modo, 'ufw_disponible', lambda: False)
    modo.activar()
    assert modo.activo is False
    assert 'UFW no está instalado' in (modo.advertencia or '')
    modo.desactivar()
    assert 'UFW no está instalado' in (modo.advertencia or '')

def test_ufw_disponible(monkeypatch):
    monkeypatch.setattr('shutil.which', lambda x: True)
    monkeypatch.setattr('os.system', lambda x: 0)
    modo = ModoSeguro()
    modo.activar()
    assert modo.activo is True
    modo.desactivar()
    assert modo.activo is False
