#!/usr/bin/env python3
"""
Copyright (c) 2025 DogSoulDev (https://github.com/DogSoulDev)
Todos los derechos reservados. Este código es propietario y confidencial.

Utilidades de Logging
"""

import logging
import os
from pathlib import Path
from datetime import datetime
from typing import Optional


def configurar_logger_principal(nombre_logger: str = "ares_aegis", 
                               nivel: int = logging.INFO,
                               archivo_log: Optional[str] = None) -> logging.Logger:
    """
    Configura el logger principal de Ares Aegis.
    
    Args:
        nombre_logger: Nombre del logger
        nivel: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        archivo_log: Ruta del archivo de log (opcional)
        
    Returns:
        logging.Logger: Logger configurado
    """
    logger = logging.getLogger(nombre_logger)
    
    # Evitar duplicar handlers si ya está configurado
    if logger.handlers:
        return logger
    
    logger.setLevel(nivel)
    
    # Formato de los mensajes
    formato = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para consola
    handler_consola = logging.StreamHandler()
    handler_consola.setLevel(nivel)
    handler_consola.setFormatter(formato)
    logger.addHandler(handler_consola)
    
    # Handler para archivo si se especifica
    if archivo_log:
        try:
            # Crear directorio si no existe
            Path(archivo_log).parent.mkdir(parents=True, exist_ok=True)
            
            handler_archivo = logging.FileHandler(archivo_log, encoding='utf-8')
            handler_archivo.setLevel(nivel)
            handler_archivo.setFormatter(formato)
            logger.addHandler(handler_archivo)
            
        except Exception as e:
            logger.warning(f"No se pudo configurar logging a archivo {archivo_log}: {e}")
    
    return logger


def configurar_logger_modulo(nombre_modulo: str, 
                           logger_padre: Optional[logging.Logger] = None) -> logging.Logger:
    """
    Configura un logger para un módulo específico.
    
    Args:
        nombre_modulo: Nombre del módulo
        logger_padre: Logger padre (opcional)
        
    Returns:
        logging.Logger: Logger del módulo
    """
    if logger_padre:
        nombre_completo = f"{logger_padre.name}.{nombre_modulo}"
    else:
        nombre_completo = f"ares_aegis.{nombre_modulo}"
    
    logger = logging.getLogger(nombre_completo)
    
    # Heredar configuración del padre si existe
    if logger_padre and not logger.handlers:
        logger.setLevel(logger_padre.level)
    
    return logger


def log_evento_seguridad(logger: logging.Logger, evento: str, detalles: str = ""):
    """
    Registra un evento de seguridad con formato especial.
    
    Args:
        logger: Logger a usar
        evento: Tipo de evento
        detalles: Detalles adicionales
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    mensaje = f"[SEGURIDAD] {evento}"
    if detalles:
        mensaje += f" - {detalles}"
    
    logger.warning(mensaje)


def log_amenaza_detectada(logger: logging.Logger, archivo: str, amenaza: str):
    """
    Registra la detección de una amenaza.
    
    Args:
        logger: Logger a usar
        archivo: Archivo donde se detectó la amenaza
        amenaza: Tipo de amenaza detectada
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    mensaje = f"[AMENAZA] Detectada en {archivo}: {amenaza}"
    
    logger.error(mensaje)


def log_inicio_escaneo(logger: logging.Logger, tipo_escaneo: str, objetivo: str):
    """
    Registra el inicio de un escaneo.
    
    Args:
        logger: Logger a usar
        tipo_escaneo: Tipo de escaneo (completo, personalizado, etc.)
        objetivo: Objetivo del escaneo (archivo, directorio, etc.)
    """
    mensaje = f"[ESCANEO] Iniciando {tipo_escaneo} en {objetivo}"
    logger.info(mensaje)


def log_fin_escaneo(logger: logging.Logger, tipo_escaneo: str, 
                   resultado: str, amenazas_encontradas: int = 0):
    """
    Registra la finalización de un escaneo.
    
    Args:
        logger: Logger a usar
        tipo_escaneo: Tipo de escaneo
        resultado: Resultado del escaneo
        amenazas_encontradas: Número de amenazas encontradas
    """
    mensaje = f"[ESCANEO] Finalizado {tipo_escaneo} - {resultado}"
    if amenazas_encontradas > 0:
        mensaje += f" - {amenazas_encontradas} amenaza(s) detectada(s)"
    
    if amenazas_encontradas > 0:
        logger.warning(mensaje)
    else:
        logger.info(mensaje)


def log_error_sistema(logger: logging.Logger, modulo: str, error: str):
    """
    Registra un error del sistema.
    
    Args:
        logger: Logger a usar
        modulo: Módulo donde ocurrió el error
        error: Descripción del error
    """
    mensaje = f"[ERROR] {modulo}: {error}"
    logger.error(mensaje)


def log_operacion_cuarentena(logger: logging.Logger, operacion: str, archivo: str):
    """
    Registra una operación de cuarentena.
    
    Args:
        logger: Logger a usar
        operacion: Tipo de operación (poner, restaurar, eliminar)
        archivo: Archivo afectado
    """
    mensaje = f"[CUARENTENA] {operacion.capitalize()}: {archivo}"
    logger.info(mensaje)


def obtener_ruta_log_por_defecto() -> str:
    """
    Obtiene la ruta por defecto para el archivo de log.
    
    Returns:
        str: Ruta del archivo de log
    """
    # Intentar usar directorio del sistema primero
    try:
        ruta_sistema = "/var/log/ares_aegis/ares_aegis.log"
        Path(ruta_sistema).parent.mkdir(parents=True, exist_ok=True)
        
        # Verificar permisos de escritura
        if os.access(Path(ruta_sistema).parent, os.W_OK):
            return ruta_sistema
    except Exception:
        pass
    
    # Si no se puede usar el directorio del sistema, usar directorio local
    return str(Path.cwd() / "ares_aegis.log")


def configurar_logging_completo(nivel: int = logging.INFO) -> logging.Logger:
    """
    Configura el sistema completo de logging para Ares Aegis.
    
    Args:
        nivel: Nivel de logging
        
    Returns:
        logging.Logger: Logger principal configurado
    """
    archivo_log = obtener_ruta_log_por_defecto()
    logger = configurar_logger_principal(
        nombre_logger="ares_aegis",
        nivel=nivel,
        archivo_log=archivo_log
    )
    
    logger.info("=" * 60)
    logger.info("Sistema de logging de Ares Aegis iniciado")
    logger.info(f"Archivo de log: {archivo_log}")
    logger.info("=" * 60)
    
    return logger
