#!/usr/bin/env python3
"""
Utils - Utilidades Simplificadas de Ares Aegis
Creado por DogSoulDev
Versión: 4.0.0 - Simplificado
"""

# Importaciones de logging
from .utils_ayuda_logging import (
    configurar_logging_completo,
    configurar_logger,
    configurar_logger_principal,
    configurar_logger_modulo,
    log_evento_seguridad,
    log_amenaza_detectada,
    log_inicio_escaneo,
    log_fin_escaneo,
    log_error_sistema,
    log_operacion_cuarentena,
    obtener_ruta_log_por_defecto
)

# Importaciones de validaciones
from .utils_validaciones import (
    validar_archivo,
    validar_directorio,
    validar_permisos_lectura,
    validar_permisos_escritura,
    es_ruta_segura,
    validar_hash
)

# Importaciones de rutas
from .utils_ayuda_rutas import (
    crear_ruta_segura,
    obtener_ruta_absoluta,
    obtener_tamaño_archivo,
    obtener_tamaño_directorio,
    listar_archivos_recursivo,
    copiar_archivo_seguro,
    mover_archivo_seguro,
    eliminar_archivo_seguro,
    obtener_rutas_sistema,
    crear_estructura_directorios_sistema,
    obtener_espacio_disco
)

# Importaciones de utilidades comunes
from .utils_imports_comunes import (
    configurar_logging_comun,
    UtilidadesComunes,
    ConstantesComunes,
    manejar_errores_ui,
    validar_kali_linux,
    requiere_permisos_admin,
    validar_archivo_existe,
    validar_directorio_existe
)

# Gestor de configuración
from .utils_gestor_configuracion import (
    gestor_configuracion,
    ConfiguracionGlobal,
    ConfiguracionSIEM,
    ConfiguracionEscaneador,
    ConfiguracionFIM,
    ConfiguracionMonitorRed,
    ConfiguracionCuarentena,
    ConfiguracionReportes,
    GestorConfiguracion
)

__all__ = [
    # Logging
    'configurar_logging_completo',
    'configurar_logger',
    'configurar_logger_principal', 
    'configurar_logger_modulo',
    'log_evento_seguridad',
    'log_amenaza_detectada',
    'log_inicio_escaneo',
    'log_fin_escaneo',
    'log_error_sistema',
    'log_operacion_cuarentena',
    'obtener_ruta_log_por_defecto',
    
    # Validaciones
    'validar_archivo',
    'validar_directorio',
    'validar_permisos_lectura',
    'validar_permisos_escritura',
    'es_ruta_segura',
    'validar_hash',
    
    # Rutas
    'crear_ruta_segura',
    'obtener_ruta_absoluta',
    'obtener_tamaño_archivo',
    'obtener_tamaño_directorio',
    'listar_archivos_recursivo',
    'copiar_archivo_seguro',
    'mover_archivo_seguro',
    'eliminar_archivo_seguro',
    'obtener_rutas_sistema',
    'crear_estructura_directorios_sistema',
    'obtener_espacio_disco',
    
    # Utilidades comunes
    'configurar_logging_comun',
    'UtilidadesComunes',
    'ConstantesComunes',
    'manejar_errores_ui',
    'validar_kali_linux',
    'requiere_permisos_admin',
    'validar_archivo_existe',
    'validar_directorio_existe',
    
    # Gestor de configuración
    'gestor_configuracion',
    'ConfiguracionGlobal',
    'ConfiguracionSIEM',
    'ConfiguracionEscaneador',
    'ConfiguracionFIM',
    'ConfiguracionMonitorRed',
    'ConfiguracionCuarentena',
    'ConfiguracionReportes',
    'GestorConfiguracion'
]


