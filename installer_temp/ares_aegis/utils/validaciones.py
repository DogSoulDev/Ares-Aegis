#!/usr/bin/env python3
"""
Validaciones Simplificadas de Ares Aegis
Funciones básicas de validación

Creado por DogSoulDev
Versión: 4.0.0 - Simplificado
"""

import os
import re
from pathlib import Path
from typing import Union


def validar_archivo(ruta: Union[str, Path]) -> bool:
    """Validar que una ruta sea un archivo válido y existente"""
    try:
        ruta_path = Path(ruta)
        return ruta_path.exists() and ruta_path.is_file()
    except Exception:
        return False


def validar_directorio(ruta: Union[str, Path]) -> bool:
    """Validar que una ruta sea un directorio válido y existente"""
    try:
        ruta_path = Path(ruta)
        return ruta_path.exists() and ruta_path.is_dir()
    except Exception:
        return False


def validar_permisos_lectura(ruta: Union[str, Path]) -> bool:
    """Validar que se pueda leer un archivo o directorio"""
    try:
        return os.access(str(ruta), os.R_OK)
    except Exception:
        return False


def validar_permisos_escritura(ruta: Union[str, Path]) -> bool:
    """Validar que se pueda escribir en un archivo o directorio"""
    try:
        return os.access(str(ruta), os.W_OK)
    except Exception:
        return False


def es_ruta_segura(ruta: Union[str, Path]) -> bool:
    """Verificar que una ruta sea segura (sin path traversal)"""
    try:
        ruta_str = str(ruta)
        # Verificar que no contenga secuencias peligrosas
        if '..' in ruta_str or '~' in ruta_str:
            return False
        return True
    except:
        return False


def validar_hash(hash_str: str) -> bool:
    """Validar que una cadena sea un hash válido (MD5 o SHA256)"""
    if not hash_str:
        return False
    # MD5: 32 caracteres hexadecimales
    if len(hash_str) == 32 and re.match(r'^[a-fA-F0-9]{32}$', hash_str):
        return True
    # SHA256: 64 caracteres hexadecimales
    if len(hash_str) == 64 and re.match(r'^[a-fA-F0-9]{64}$', hash_str):
        return True
    return False


# Alias para compatibilidad con el código existente
validar_ruta_archivo = validar_archivo
validar_ruta_directorio = validar_directorio


