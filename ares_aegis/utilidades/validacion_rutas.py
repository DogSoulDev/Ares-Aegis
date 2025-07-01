#!/usr/bin/env python3
"""
Validación de Rutas - Ares Aegis
Utilidades para validar rutas de archivos y directorios

Autor: DogSoulDev
Versión: 2.0.0
"""

import os
from pathlib import Path
from typing import Union, List, Tuple


def validar_ruta_archivo(ruta: Union[str, Path]) -> Tuple[bool, str]:
    """
    Valida si una ruta de archivo es válida y accesible.
    
    Args:
        ruta: Ruta del archivo a validar
        
    Returns:
        Tuple[bool, str]: (es_valida, mensaje)
    """
    try:
        path_obj = Path(ruta)
        
        # Verificar que la ruta no esté vacía
        if not str(ruta).strip():
            return False, "La ruta no puede estar vacía"
        
        # Verificar que el archivo existe
        if not path_obj.exists():
            return False, f"El archivo no existe: {ruta}"
        
        # Verificar que es un archivo (no directorio)
        if not path_obj.is_file():
            return False, f"La ruta no es un archivo: {ruta}"
        
        # Verificar permisos de lectura
        if not os.access(path_obj, os.R_OK):
            return False, f"Sin permisos de lectura: {ruta}"
        
        return True, "Archivo válido"
        
    except Exception as e:
        return False, f"Error validando archivo: {e}"


def validar_ruta_directorio(ruta: Union[str, Path]) -> Tuple[bool, str]:
    """
    Valida si una ruta de directorio es válida y accesible.
    
    Args:
        ruta: Ruta del directorio a validar
        
    Returns:
        Tuple[bool, str]: (es_valida, mensaje)
    """
    try:
        path_obj = Path(ruta)
        
        # Verificar que la ruta no esté vacía
        if not str(ruta).strip():
            return False, "La ruta no puede estar vacía"
        
        # Verificar que el directorio existe
        if not path_obj.exists():
            return False, f"El directorio no existe: {ruta}"
        
        # Verificar que es un directorio
        if not path_obj.is_dir():
            return False, f"La ruta no es un directorio: {ruta}"
        
        # Verificar permisos de lectura
        if not os.access(path_obj, os.R_OK):
            return False, f"Sin permisos de lectura: {ruta}"
        
        return True, "Directorio válido"
        
    except Exception as e:
        return False, f"Error validando directorio: {e}"


def validar_rutas_multiples(rutas: List[Union[str, Path]]) -> List[Tuple[str, bool, str]]:
    """
    Valida múltiples rutas (archivos o directorios).
    
    Args:
        rutas: Lista de rutas a validar
        
    Returns:
        List[Tuple[str, bool, str]]: Lista de (ruta, es_valida, mensaje)
    """
    resultados = []
    
    for ruta in rutas:
        ruta_str = str(ruta)
        path_obj = Path(ruta)
        
        if path_obj.exists():
            if path_obj.is_file():
                es_valida, mensaje = validar_ruta_archivo(ruta)
            elif path_obj.is_dir():
                es_valida, mensaje = validar_ruta_directorio(ruta)
            else:
                es_valida, mensaje = False, "Tipo de ruta desconocido"
        else:
            es_valida, mensaje = False, "La ruta no existe"
        
        resultados.append((ruta_str, es_valida, mensaje))
    
    return resultados


def es_ruta_segura(ruta: Union[str, Path]) -> bool:
    """
    Verifica si una ruta es segura para el acceso.
    Evita rutas que podrían ser peligrosas.
    
    Args:
        ruta: Ruta a verificar
        
    Returns:
        bool: True si la ruta es segura
    """
    try:
        path_obj = Path(ruta).resolve()
        ruta_str = str(path_obj).lower()
        
        # Rutas peligrosas en sistemas Linux/Unix
        rutas_peligrosas = [
            '/proc',
            '/sys',
            '/dev',
            '/boot',
            '/root',
            '/etc/shadow',
            '/etc/passwd',
            '/var/log/auth.log'
        ]
        
        # Verificar si la ruta está en áreas del sistema
        for ruta_peligrosa in rutas_peligrosas:
            if ruta_str.startswith(ruta_peligrosa.lower()):
                return False
        
        # Verificar caracteres peligrosos
        caracteres_peligrosos = ['..', '~/', '$']
        for caracter in caracteres_peligrosos:
            if caracter in str(ruta):
                return False
        
        return True
        
    except Exception:
        return False


def obtener_extension_archivo(ruta: Union[str, Path]) -> str:
    """
    Obtiene la extensión de un archivo.
    
    Args:
        ruta: Ruta del archivo
        
    Returns:
        str: Extensión del archivo (sin el punto)
    """
    try:
        return Path(ruta).suffix.lower().lstrip('.')
    except Exception:
        return ""


def es_archivo_ejecutable(ruta: Union[str, Path]) -> bool:
    """
    Verifica si un archivo es ejecutable basándose en su extensión.
    
    Args:
        ruta: Ruta del archivo
        
    Returns:
        bool: True si es ejecutable
    """
    extensiones_ejecutables = {
        'exe', 'bat', 'cmd', 'com', 'scr', 'pif', 'msi', 'msp',
        'sh', 'bash', 'zsh', 'csh', 'fish',
        'py', 'pl', 'rb', 'js', 'jar',
        'elf', 'bin', 'run'
    }
    
    extension = obtener_extension_archivo(ruta)
    return extension in extensiones_ejecutables


def filtrar_rutas_validas(rutas: List[Union[str, Path]]) -> List[str]:
    """
    Filtra una lista de rutas, devolviendo solo las válidas y seguras.
    
    Args:
        rutas: Lista de rutas a filtrar
        
    Returns:
        List[str]: Lista de rutas válidas
    """
    rutas_validas = []
    
    for ruta in rutas:
        # Verificar que sea segura
        if not es_ruta_segura(ruta):
            continue
        
        # Verificar que sea válida
        path_obj = Path(ruta)
        if path_obj.exists() and (path_obj.is_file() or path_obj.is_dir()):
            rutas_validas.append(str(path_obj))
    
    return rutas_validas


def obtener_tamano_archivo(ruta: Union[str, Path]) -> int:
    """
    Obtiene el tamaño de un archivo en bytes.
    
    Args:
        ruta: Ruta del archivo
        
    Returns:
        int: Tamaño en bytes, -1 si hay error
    """
    try:
        return Path(ruta).stat().st_size
    except Exception:
        return -1


def formatear_tamano_archivo(tamano_bytes: int) -> str:
    """
    Formatea el tamaño de un archivo en formato legible.
    
    Args:
        tamano_bytes: Tamaño en bytes
        
    Returns:
        str: Tamaño formateado (ej: "1.5 MB")
    """
    if tamano_bytes < 0:
        return "Desconocido"
    
    unidades = ['B', 'KB', 'MB', 'GB', 'TB']
    tamano = float(tamano_bytes)
    
    for unidad in unidades:
        if tamano < 1024.0:
            return f"{tamano:.1f} {unidad}"
        tamano /= 1024.0
    
    return f"{tamano:.1f} PB"
