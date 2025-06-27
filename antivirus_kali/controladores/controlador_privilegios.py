"""
Controlador para el monitoreo de privilegios.
Conecta la lógica del monitor con el panel visual.
"""
from antivirus_kali.nucleo.monitor_privilegios import MonitorPrivilegios

class ControladorPrivilegios:
    def __init__(self):
        self.monitor = MonitorPrivilegios()

    def monitorear_privilegios(self):
        return self.monitor.procesos_root_sospechosos()
