import os
import pytest
from antivirus_kali.reports import pdf_generator

def test_generar_informe_pdf(tmp_path):
    resumen = {
        'rootkits': ['RootkitTest'],
        'procesos': ['proc1'],
        'puertos': [22, 80],
        'servicios': ['ssh', 'apache2'],
        'integridad': {'/bin/ls': 'Íntegro', '/bin/bash': 'Modificado'},
        'programas': ['nano', 'vim', 'python3']
    }
    ruta = tmp_path / "test_informe.pdf"
    result = pdf_generator.generar_informe_pdf(resumen, str(ruta), usuario="testuser")
    assert result is not None, f"El generador de PDF devolvió None. Resultado: {result}"
    if not (isinstance(result, str) and result.endswith('.pdf') and os.path.exists(result)):
        pytest.fail(f"Error al generar PDF: {result}")
    assert os.path.getsize(result) > 0, "El archivo PDF está vacío"
