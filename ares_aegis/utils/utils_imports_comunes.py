#!/usr/bin/env python3
"""
Módulo de Imports Comunes - Ares Aegis
Consolidación de imports frecuentemente utilizados para eliminar duplicación
"""

# ===== IMPORTS ESTÁNDAR PYTHON =====
import os
import sys
import re
import hashlib
import time
import json
import logging
import threading
import subprocess
import platform
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from abc import ABC, abstractmethod

# ===== IMPORTS TKINTER =====
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext

# ===== CONFIGURACIÓN DE LOGGING =====
def configurar_logging_comun(nombre_modulo):
    """Configurar logging estándar para módulos de Ares Aegis"""
    return logging.getLogger(nombre_modulo)

# ===== UTILIDADES COMUNES =====
class UtilidadesComunes:
    """Utilidades frecuentemente utilizadas en todo el proyecto"""
    
    @staticmethod
    def obtener_timestamp():
        """Obtener timestamp formateado estándar"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def es_kali_linux():
        """Verificar si el sistema es Kali Linux"""
        try:
            with open('/etc/os-release', 'r') as f:
                contenido = f.read()
                return 'kali' in contenido.lower()
        except:
            return False
    
    @staticmethod
    def es_windows():
        """Verificar si el sistema es Windows"""
        return platform.system().lower() == 'windows'
    
    @staticmethod
    def validar_permisos_root():
        """Verificar permisos de administrador/root"""
        if UtilidadesComunes.es_windows():
            import ctypes
            try:
                return ctypes.windll.shell32.IsUserAnAdmin()
            except:
                return False
        else:
            # Para sistemas Unix/Linux - usar método más compatible
            try:
                import getpass
                usuario_actual = getpass.getuser()
                return usuario_actual == 'root'
            except:
                # Si todo falla, asumir que no tiene permisos de root
                return False
    
    @staticmethod
    def ejecutar_comando_sistema(comando):
        """Ejecutar comando del sistema de forma segura"""
        try:
            resultado = subprocess.run(
                comando,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            return {
                'exito': resultado.returncode == 0,
                'salida': resultado.stdout,
                'error': resultado.stderr
            }
        except subprocess.TimeoutExpired:
            return {
                'exito': False,
                'salida': '',
                'error': 'Tiempo de espera agotado'
            }
        except Exception as e:
            return {
                'exito': False,
                'salida': '',
                'error': str(e)
            }
    
    @staticmethod
    def leer_archivo_seguro(ruta_archivo, encoding='utf-8'):
        """Leer archivo de forma segura con manejo de errores"""
        try:
            with open(ruta_archivo, 'r', encoding=encoding) as archivo:
                return {'exito': True, 'contenido': archivo.read(), 'error': None}
        except FileNotFoundError:
            return {'exito': False, 'contenido': None, 'error': 'Archivo no encontrado'}
        except PermissionError:
            return {'exito': False, 'contenido': None, 'error': 'Sin permisos de lectura'}
        except Exception as e:
            return {'exito': False, 'contenido': None, 'error': str(e)}
    
    @staticmethod
    def escribir_archivo_seguro(ruta_archivo, contenido, encoding='utf-8'):
        """Escribir archivo de forma segura con manejo de errores"""
        try:
            # Crear directorio padre si no existe
            Path(ruta_archivo).parent.mkdir(parents=True, exist_ok=True)
            
            with open(ruta_archivo, 'w', encoding=encoding) as archivo:
                archivo.write(contenido)
            return {'exito': True, 'error': None}
        except PermissionError:
            return {'exito': False, 'error': 'Sin permisos de escritura'}
        except Exception as e:
            return {'exito': False, 'error': str(e)}
    
    @staticmethod
    def generar_hash_archivo(ruta_archivo):
        """Generar hash SHA256 de un archivo"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(ruta_archivo, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return {'exito': True, 'hash': hash_sha256.hexdigest(), 'error': None}
        except Exception as e:
            return {'exito': False, 'hash': None, 'error': str(e)}

# ===== CONSTANTES COMUNES =====
class ConstantesComunes:
    """Constantes utilizadas frecuentemente en el proyecto"""
    
    # Rutas comunes
    DIRECTORIO_BASE = Path(__file__).parent.parent.parent
    DIRECTORIO_CONFIGURACION = DIRECTORIO_BASE / 'configuracion'
    DIRECTORIO_LOGS = Path('/var/log/ares_aegis') if not UtilidadesComunes.es_windows() else DIRECTORIO_BASE / 'logs'
    DIRECTORIO_RECURSOS = DIRECTORIO_BASE / 'recursos'
    DIRECTORIO_DATA = DIRECTORIO_BASE / 'data'
    
    # Archivos de configuración
    ARCHIVO_CONFIG_PRINCIPAL = DIRECTORIO_CONFIGURACION / 'ares_aegis_config.json'
    ARCHIVO_FIRMAS = DIRECTORIO_RECURSOS / 'firmas.txt'
    ARCHIVO_CHEATSHEETS = DIRECTORIO_RECURSOS / 'cheatsheets'
    
    # Configuración de logging
    FORMATO_LOG = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ARCHIVO_LOG_PRINCIPAL = DIRECTORIO_LOGS / 'ares_aegis.log'
    
    # Configuración de interfaz
    ANCHO_VENTANA_DEFECTO = 1200
    ALTO_VENTANA_DEFECTO = 800
    
    # Timeouts y límites
    TIMEOUT_COMANDO_DEFECTO = 30
    TAMANO_MAXIMO_LOG = 10 * 1024 * 1024  # 10MB
    LINEAS_MAXIMAS_TEXTO = 1000

# ===== DECORADORES COMUNES =====
def manejar_errores_ui(func):
    """Decorador para manejar errores en funciones de UI"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger = configurar_logging_comun(func.__module__)
            logger.error(f"Error en {func.__name__}: {str(e)}")
            messagebox.showerror("Error", f"Error inesperado: {str(e)}")
    return wrapper

def validar_kali_linux(func):
    """Decorador para funciones que requieren Kali Linux"""
    def wrapper(*args, **kwargs):
        if not UtilidadesComunes.es_kali_linux():
            logger = configurar_logging_comun(func.__module__)
            logger.warning(f"Función {func.__name__} optimizada para Kali Linux")
        return func(*args, **kwargs)
    return wrapper

def requiere_permisos_admin(func):
    """Decorador para funciones que requieren permisos de administrador"""
    def wrapper(*args, **kwargs):
        if not UtilidadesComunes.validar_permisos_root():
            logger = configurar_logging_comun(func.__module__)
            logger.warning(f"Función {func.__name__} requiere permisos de administrador")
        return func(*args, **kwargs)
    return wrapper

# ===== FUNCIONES DE VALIDACIÓN COMUNES =====
def validar_archivo_existe(ruta_archivo):
    """Validar que un archivo existe"""
    return Path(ruta_archivo).exists()

def validar_directorio_existe(ruta_directorio):
    """Validar que un directorio existe"""
    return Path(ruta_directorio).is_dir()

def validar_permisos_lectura(ruta):
    """Validar permisos de lectura"""
    return os.access(ruta, os.R_OK)

def validar_permisos_escritura(ruta):
    """Validar permisos de escritura"""
    return os.access(ruta, os.W_OK)

# ===== EXPORTACIONES =====
__all__ = [
    # Módulos estándar
    'os', 'sys', 're', 'hashlib', 'time', 'json', 'logging', 'threading',
    'subprocess', 'platform', 'Path', 'defaultdict', 'Counter', 'datetime',
    'timedelta', 'ABC', 'abstractmethod',
    
    # Tkinter
    'tk', 'ttk', 'messagebox', 'filedialog', 'scrolledtext',
    
    # Clases y utilidades
    'UtilidadesComunes', 'ConstantesComunes',
    
    # Funciones
    'configurar_logging_comun', 'validar_archivo_existe', 'validar_directorio_existe',
    'validar_permisos_lectura', 'validar_permisos_escritura',
    
    # Decoradores
    'manejar_errores_ui', 'validar_kali_linux', 'requiere_permisos_admin'
]
