"""
Módulo para monitorizar procesos y detectar uso inapropiado de privilegios.
Utiliza psutil para analizar procesos y escaladas sospechosas.
"""

import psutil

class MonitorPrivilegios:
    def __init__(self):
        pass

    def procesos_root_sospechosos(self):
        sospechosos = []
        for proc in psutil.process_iter(['pid', 'name', 'username', 'cmdline']):
            try:
                if proc.info['username'] == 'root' and proc.info['name'] not in ['systemd', 'init']:
                    sospechosos.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return sospechosos
