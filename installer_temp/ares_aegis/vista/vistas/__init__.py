#!/usr/bin/env python3
"""
Vistas Especializadas para Ares Aegis
"""

from .vista_dashboard import VistaDashboard
from .vista_escaneador import VistaEscaneador
from .vista_monitor import VistaMonitor
from .vista_cuarentena import VistaCuarentena
from .vista_reportes import VistaReportes

__all__ = [
    'VistaDashboard',
    'VistaEscaneador', 
    'VistaMonitor',
    'VistaCuarentena',
    'VistaReportes'
]
