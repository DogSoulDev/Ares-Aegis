"""
Controlador para el modo pentesting seguro y auditoría.
Conecta la lógica del modo seguro y auditor con el panel visual.
"""
from antivirus_kali.nucleo.modo_seguro import ModoSeguro
from antivirus_kali.nucleo.auditor_configuracion import AuditorConfiguracion

class ControladorModoSeguro:
    def __init__(self):
        self.modo = ModoSeguro()
        self.auditor = AuditorConfiguracion()

    def activar_modo_seguro(self):
        self.modo.activar()
        return self.modo.advertencia

    def desactivar_modo_seguro(self):
        self.modo.desactivar()
        return self.modo.advertencia

    def auditar_configuracion(self):
        return self.auditor.revisar_ssh()
