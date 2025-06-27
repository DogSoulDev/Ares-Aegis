"""
Controlador para la validación de integridad de herramientas.
Conecta la lógica del validador con el panel visual.
"""
from antivirus_kali.nucleo.validador_integridad import ValidadorIntegridad

class ControladorIntegridad:
    def __init__(self, rutas_herramientas, referencia_hashes):
        self.validador = ValidadorIntegridad(rutas_herramientas, referencia_hashes)

    def validar(self):
        return self.validador.validar()
