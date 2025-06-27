"""
Módulo para auditoría de configuración de seguridad.
Revisa configuraciones básicas y sugiere mejoras.
"""

import os

class AuditorConfiguracion:
    def __init__(self):
        pass

    def revisar_ssh(self):
        try:
            with open('/etc/ssh/sshd_config') as f:
                contenido = f.read()
            if 'PermitRootLogin yes' in contenido:
                return 'Advertencia: PermitRootLogin está habilitado.'
            return 'SSH seguro.'
        except Exception:
            return 'No se pudo revisar SSH.'
