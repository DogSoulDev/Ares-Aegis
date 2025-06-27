from antivirus_kali.nucleo.gestor_firmas import *
from antivirus_kali.nucleo.gestor_iocs import GestorIOCs

def test_gestor_firmas_importable():
    # El módulo debe poder importarse aunque esté vacío
    assert True

def test_gestor_iocs_actualizar_y_es_malicioso(monkeypatch):
    class DummyResponse:
        status_code = 200
        text = 'hash1\nhash2\nhash3'
    monkeypatch.setattr('requests.get', lambda url, timeout=5: DummyResponse())
    gestor = GestorIOCs('https://example.com/feed.txt')
    advertencias = gestor.actualizar_iocs()
    assert isinstance(advertencias, list)
    assert 'hash1' in gestor.iocs
    malicioso, adv = gestor.es_malicioso('hash1')
    assert malicioso is True
    assert isinstance(adv, list)
    no_malicioso, adv2 = gestor.es_malicioso('noexiste')
    assert no_malicioso is False
    assert isinstance(adv2, list)
