#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Inicializador del paquete de paneles especializados
"""

from .panel_escaneo_antivirus import PanelEscaneoAntivirus
from .panel_mini_siem import PanelMiniSiem  
from .panel_herramientas_sistema import PanelHerramientasSistema

__all__ = [
    'PanelEscaneoAntivirus',
    'PanelMiniSiem',
    'PanelHerramientasSistema'
]
