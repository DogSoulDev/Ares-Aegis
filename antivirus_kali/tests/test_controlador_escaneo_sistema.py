from antivirus_kali.controladores.controlador_escaneo_sistema import ControladorEscaneoSistema
import tempfile

def test_exportar_informe():
    controlador = ControladorEscaneoSistema()
    resumen = {
        'rootkits': [],
        'procesos': [],
        'puertos': [],
        'servicios': [],
        'integridad': {},
        'programas': []
    }
    with tempfile.TemporaryDirectory() as tmpdir:
        ruta = f"{tmpdir}/test.pdf"
        result = controlador.exportar_informe(resumen, ruta, usuario="testuser")
        assert result is not None, f"La exportación devolvió None. Resultado: {result}"
        if not (isinstance(result, str) and result.endswith('.pdf')):
            import pytest
            pytest.fail(f"Error al exportar PDF: {result}")
