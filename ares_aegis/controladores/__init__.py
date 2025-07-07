"""
Copyright (c) 2025 DogSoulDev (https://github.com/DogSoulDev)
Todos los derechos reservados. Este código es propietario y confidencial.

Controladores MVC - Arquitectura Especializada
"""

# Controlador principal
from .controlador_principal import ControladorPrincipal

# Controladores especializados
from .controlador_escaneador import ControladorEscaneador
from .controlador_siem import ControladorSIEM
from .controlador_monitor_red import ControladorMonitorRed
from .controlador_fim import ControladorFIM
from .controlador_cuarentena import ControladorCuarentena
from .controlador_reportes import ControladorReportes
from .controlador_vulnerabilidades import ControladorVulnerabilidades
from .controlador_analisis import ControladorAnalisis
from .controlador_respuesta_automatizada import ControladorRespuestaAutomatizada
from .controlador_incidentes import ControladorIncidentes

__all__ = [
    'ControladorPrincipal',
    'ControladorEscaneador',
    'ControladorSIEM',
    'ControladorMonitorRed',
    'ControladorFIM',
    'ControladorCuarentena',
    'ControladorReportes',
    'ControladorVulnerabilidades',
    'ControladorAnalisis',
    'ControladorRespuestaAutomatizada',
    'ControladorIncidentes'
]
