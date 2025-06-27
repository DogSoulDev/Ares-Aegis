"""
Controlador para la gestión de IOCs y reputación.
Conecta la lógica del gestor con el panel visual.
"""
from antivirus_kali.nucleo.gestor_iocs import GestorIOCs

class ControladorIOCs:
    def __init__(self, url_feed):
        self.gestor = GestorIOCs(url_feed)
        self.advertencias_feed = self.gestor.actualizar_iocs()

    def verificar_ioc(self, valor):
        resultado, advertencias_ioc = self.gestor.es_malicioso(valor)
        advertencias = list(self.advertencias_feed or []) + list(advertencias_ioc or [])
        if resultado:
            return f"{valor}: IOC detectado (malicioso)", advertencias
        return f"{valor}: Sin coincidencias", advertencias
