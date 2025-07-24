#!/usr/bin/env python3
"""
Creado por DogSoulDev (https://github.com/DogSoulDev)
Todos los derechos reservados. Este código es propietario y confidencial.

Modelos MVC - Arquitectura Simplificada
"""

# Modelos principales simplificados
from .siem import SIEM, TipoEvento
from .escaneador import EscaneadorMalware
from .fim import FIMAvanzado
from .monitor_red import MonitorRed
from .gestor_cuarentena import GestorCuarentenaAvanzado
from .monitor_procesos import MonitorProcesos
from .analizadores import AnalizadoresUnificados

__all__ = [
    'SIEM',
    'TipoEvento',
    'EscaneadorMalware',
    'FIMAvanzado',
    'MonitorRed',
    'GestorCuarentenaAvanzado',
    'MonitorProcesos',
    'AnalizadoresUnificados'
]

