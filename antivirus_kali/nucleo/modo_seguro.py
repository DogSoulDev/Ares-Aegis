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
        self.activo = False  # Siempre inicializa a False antes de intentar activar
        if self.ufw_disponible():
            ret = os.system('ufw enable && ufw default deny outgoing')
            if ret == 0:
                self.activo = True
                self.advertencia = None
            else:
                self.activo = False
                self.advertencia = 'Error: Fallo al activar UFW. Comprueba permisos o instalación.'
        else:
            self.activo = False
            self.advertencia = 'Advertencia: UFW no está instalado. No se puede activar el modo seguro.'

    def desactivar(self):
        self.activo = False  # Siempre inicializa a False antes de intentar desactivar
        if self.ufw_disponible():
            os.system('ufw disable')
            self.activo = False
            self.advertencia = None
        else:
            self.activo = False
            self.advertencia = 'Advertencia: UFW no está instalado. No se puede desactivar el modo seguro.'
