#!/usr/bin/env python3
"""
Creado por DogSoulDev (https://github.com/DogSoulDev)
Todos los derechos reservados. Este código es propietario y confidencial.

Modelos MVC - Arquitectura Simplificada
"""

# Modelos principales simplificados
from .modelo_siem import SIEM, TipoEvento
from .modelo_escaneador import EscaneadorMalware
from .modelo_fim import FIM
from .modelo_monitor_red import MonitorRed
from .modelo_gestor_cuarentena import GestorCuarentenaAvanzado
from .modelo_monitor_procesos import MonitorProcesos
from .modelo_analizadores import AnalizadoresUnificados

__all__ = [
    'SIEM',
    'TipoEvento',
    'EscaneadorMalware',
    'FIM',
    'MonitorRed',
    'GestorCuarentenaAvanzado',
    'MonitorProcesos',
    'AnalizadoresUnificados'
]

