#!/usr/bin/env python3
"""
Configuración Simplificada de Ares Aegis
Configuraciones centralizadas del sistema

Creado por DogSoulDev
Versión: 4.0.0 - Simplificado
"""

import os
from pathlib import Path

# Rutas principales del proyecto
RUTA_RAIZ = Path(__file__).parent.parent
RUTA_CONFIGURACION = RUTA_RAIZ / "configuracion"
RUTA_RECURSOS = RUTA_RAIZ / "recursos"
RUTA_CUARENTENA = RUTA_RAIZ / "cuarentena"
RUTA_REPORTES = RUTA_RAIZ / "reportes"
RUTA_LOGS = RUTA_RAIZ / "logs"

# Configuraciones de seguridad
CONFIGURACION_SEGURIDAD = {
    "extensiones_peligrosas": {
        '.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', 
        '.js', '.jar', '.ps1', '.sh', '.bin', '.dll', '.msi'
    },
    "tamaño_max_analisis": 50 * 1024 * 1024,  # 50MB
    "tiempo_timeout_analisis": 30,  # segundos
    "limite_procesos_monitoreados": 50
}

# Configuraciones de la interfaz
CONFIGURACION_UI = {
    "tema": "oscuro",
    "tamaño_ventana": "1400x900",
    "tamaño_minimo": "1200x800",
    "actualizacion_automatica": 5000,  # milisegundos
    "colores": {
        "bg_principal": "#0d1421",
        "bg_secundario": "#16213e", 
        "acento": "#1a73e8",
        "texto": "#ffffff",
        "texto_secundario": "#b3b3b3"
    }
}

# Configuraciones del sistema
CONFIGURACION_SISTEMA = {
    "intervalo_monitoreo_red": 10,  # segundos
    "intervalo_monitoreo_procesos": 30,  # segundos
    "intervalo_fim": 60,  # segundos
    "limite_alertas_recientes": 100,
    "backup_automatico": True,
    "logs_detallados": True
}

# Configuraciones de archivos
ARCHIVOS_CONFIGURACION = {
    "firmas": RUTA_CONFIGURACION / "firmas.txt",
    "ips_maliciosas": RUTA_RECURSOS / "ips_maliciosas_local.txt",
    "reglas_respuesta": RUTA_RECURSOS / "reglas_respuesta.json",
    "notificaciones": RUTA_CONFIGURACION / "notificaciones.json"
}

def crear_directorios_necesarios():
    """Crear directorios necesarios si no existen"""
    directorios = [
        RUTA_CONFIGURACION,
        RUTA_RECURSOS,
        RUTA_CUARENTENA,
        RUTA_REPORTES,
        RUTA_LOGS,
        RUTA_CUARENTENA / "backups"
    ]
    
    for directorio in directorios:
        directorio.mkdir(parents=True, exist_ok=True)

def obtener_configuracion_completa():
    """Obtener toda la configuración del sistema"""
    return {
        "seguridad": CONFIGURACION_SEGURIDAD,
        "ui": CONFIGURACION_UI,
        "sistema": CONFIGURACION_SISTEMA,
        "archivos": ARCHIVOS_CONFIGURACION,
        "rutas": {
            "raiz": RUTA_RAIZ,
            "configuracion": RUTA_CONFIGURACION,
            "recursos": RUTA_RECURSOS,
            "cuarentena": RUTA_CUARENTENA,
            "reportes": RUTA_REPORTES,
            "logs": RUTA_LOGS
        }
    }

# Inicializar directorios al importar el módulo
crear_directorios_necesarios()
