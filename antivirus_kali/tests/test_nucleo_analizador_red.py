from antivirus_kali.nucleo.analizador_red import AnalizadorRed
import pytest

def test_es_root():
    analizador = AnalizadorRed('192.168.1.0/24')
    assert isinstance(analizador.es_root(), bool)

def test_escanear_dispositivos():
    analizador = AnalizadorRed('192.168.1.0/24')
    dispositivos, advertencias = analizador.escanear_dispositivos()
    assert isinstance(dispositivos, list)
    assert isinstance(advertencias, list)

def test_fingerprint_dispositivo():
    analizador = AnalizadorRed('192.168.1.0/24')
    result = analizador.fingerprint_dispositivo('127.0.0.1')
    assert isinstance(result, dict)

def test_detectar_honeypots():
    analizador = AnalizadorRed('192.168.1.0/24')
    sospechosos, advertencias, explicaciones = analizador.detectar_honeypots()
    assert isinstance(sospechosos, list)
    assert isinstance(advertencias, list)
    assert isinstance(explicaciones, list)
