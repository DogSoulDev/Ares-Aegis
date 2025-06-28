"""
Módulo para actualización de firmas y reglas (ClamAV, YARA, feeds de IOCs) desde Python.
Permite lanzar freshclam, descargar reglas YARA y feeds de IOCs.
"""
import subprocess
import requests
from pathlib import Path

class ActualizadorFirmas:
    def __init__(self, url_yara=None, url_iocs=None):
        self.url_yara = url_yara or "https://yaraify.abuse.ch/downloads/rules/index.yar"
        self.url_iocs = url_iocs or "https://urlhaus.abuse.ch/downloads/text/"

    def actualizar_clamav(self):
        try:
            resultado = subprocess.run(['freshclam'], capture_output=True, text=True, check=False)
            return resultado.stdout
        except Exception as e:
            return f'Error actualizando ClamAV: {e}'

    def descargar_reglas_yara(self, destino):
        try:
            r = requests.get(self.url_yara, timeout=10)
            if r.status_code == 200:
                Path(destino).write_text(r.text)
                return f'Reglas YARA descargadas en {destino}'
            return f'Error descargando reglas YARA: {r.status_code}'
        except Exception as e:
            return f'Error descargando reglas YARA: {e}'

    def descargar_feed_iocs(self, destino):
        try:
            r = requests.get(self.url_iocs, timeout=10)
            if r.status_code == 200:
                Path(destino).write_text(r.text)
                return f'Feed de IOCs descargado en {destino}'
            return f'Error descargando feed IOCs: {r.status_code}'
        except Exception as e:
            return f'Error descargando feed IOCs: {e}'
