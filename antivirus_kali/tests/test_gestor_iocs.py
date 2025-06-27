from antivirus_kali.nucleo.gestor_iocs import GestorIOCs

def test_gestor_iocs_basico():
    gestor = GestorIOCs('https://example.com/feed.txt')
    assert hasattr(gestor, 'actualizar_iocs')
    assert hasattr(gestor, 'es_malicioso')
    # No excepción al llamar métodos aunque el feed no exista
    gestor.actualizar_iocs()
    gestor.es_malicioso('testhash')
