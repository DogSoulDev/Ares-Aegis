from antivirus_kali.nucleo.validador_integridad import ValidadorIntegridad

def test_validador_integridad_fake():
    rutas = ["/bin/ls"]
    referencia = {"ls": "HASH_FAKE"}
    validador = ValidadorIntegridad(rutas, referencia)
    resultados, advertencias = validador.validar()
    # Eliminado: referencia a widget obsoleto
    assert isinstance(advertencias, list)
