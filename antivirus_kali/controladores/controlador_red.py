"""
Controlador para el análisis de red y honeypots.
Conecta la lógica del analizador con el panel visual.
"""
from antivirus_kali.nucleo.analizador_red import AnalizadorRed


class ControladorRed:
    def __init__(self, rango_red):
        self.analizador = AnalizadorRed(rango_red)

    def analizar_red(self):
        sospechosos, advertencias, explicaciones = self.analizador.detectar_honeypots()
        return sospechosos, advertencias, explicaciones
