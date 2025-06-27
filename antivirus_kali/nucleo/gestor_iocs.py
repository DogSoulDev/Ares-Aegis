"""
Módulo para la gestión de IOCs y reputación de repositorios.
Descarga feeds de IOCs y analiza URLs/repositorios sospechosos.
"""

import requests

class GestorIOCs:
    def __init__(self, url_feed):
        self.url_feed = url_feed
        self.iocs = set()

    def actualizar_iocs(self):
        advertencias = []
        try:
            respuesta = requests.get(self.url_feed, timeout=5)
            if respuesta.status_code == 200:
                self.iocs = set(respuesta.text.splitlines())
            else:
                advertencias.append("No se pudo descargar el feed de IOCs. El análisis puede estar incompleto.")
        except Exception:
            advertencias.append("Error de red al descargar el feed de IOCs. Verifica tu conexión.")
        return advertencias

    def es_malicioso(self, hash_o_url):
        advertencias = []
        if not self.iocs:
            advertencias.append("No hay IOCs cargados. El análisis puede no ser confiable.")
        return (hash_o_url in self.iocs, advertencias)
