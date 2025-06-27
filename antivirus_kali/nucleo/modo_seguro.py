"""
Módulo para activar el modo pentesting seguro.
Aplica configuraciones temporales de seguridad y monitorización extra.
"""

import os
import shutil

class ModoSeguro:
    def __init__(self):
        self.activo = False
        self.advertencia = None

    def ufw_disponible(self):
        return shutil.which('ufw') is not None

    def activar(self):
        if self.ufw_disponible():
            os.system('ufw enable && ufw default deny outgoing')
            self.activo = True
            self.advertencia = None
        else:
            self.advertencia = 'Advertencia: UFW no está instalado. No se puede activar el modo seguro.'
            self.activo = False

    def desactivar(self):
        if self.ufw_disponible():
            os.system('ufw disable')
            self.activo = False
            self.advertencia = None
        else:
            self.advertencia = 'Advertencia: UFW no está instalado. No se puede desactivar el modo seguro.'
