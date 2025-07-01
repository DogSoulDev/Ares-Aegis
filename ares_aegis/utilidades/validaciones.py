#!/usr/bin/env python3
"""
Utilidades de Validación - Ares Aegis
Funciones para validación de entradas de usuario

Autor: DogSoulDev
Versión: 2.0.0
"""

import os
import re
import ipaddress
from pathlib import Path
from typing import Union, Optional, List


def validar_ruta_archivo(ruta: Union[str, Path]) -> bool:
    """
    Valida que una ruta sea un archivo válido y existente.
    
    Args:
        ruta: Ruta del archivo a validar
        
    Returns:
        bool: True si es válida, False si no
    """
    try:
        ruta_path = Path(ruta)
        return ruta_path.exists() and ruta_path.is_file()
    except Exception:
        return False


def validar_ruta_directorio(ruta: Union[str, Path]) -> bool:
    """
    Valida que una ruta sea un directorio válido y existente.
    
    Args:
        ruta: Ruta del directorio a validar
        
    Returns:
        bool: True si es válida, False si no
    """
    try:
        ruta_path = Path(ruta)
        return ruta_path.exists() and ruta_path.is_dir()
    except Exception:
        return False


def validar_permisos_lectura(ruta: Union[str, Path]) -> bool:
    """
    Valida que se tengan permisos de lectura sobre una ruta.
    
    Args:
        ruta: Ruta a verificar
        
    Returns:
        bool: True si hay permisos, False si no
    """
    try:
        return os.access(str(ruta), os.R_OK)
    except Exception:
        return False


def validar_permisos_escritura(ruta: Union[str, Path]) -> bool:
    """
    Valida que se tengan permisos de escritura sobre una ruta.
    
    Args:
        ruta: Ruta a verificar
        
    Returns:
        bool: True si hay permisos, False si no
    """
    try:
        return os.access(str(ruta), os.W_OK)
    except Exception:
        return False


def validar_cadena_no_vacia(cadena: str) -> bool:
    """
    Valida que una cadena no esté vacía.
    
    Args:
        cadena: Cadena a validar
        
    Returns:
        bool: True si no está vacía, False si está vacía
    """
    return isinstance(cadena, str) and len(cadena.strip()) > 0


def validar_numero_entero(valor: str, minimo: Optional[int] = None, 
                         maximo: Optional[int] = None) -> bool:
    """
    Valida que un valor sea un número entero dentro de un rango.
    
    Args:
        valor: Valor a validar
        minimo: Valor mínimo permitido (opcional)
        maximo: Valor máximo permitido (opcional)
        
    Returns:
        bool: True si es válido, False si no
    """
    try:
        numero = int(valor)
        if minimo is not None and numero < minimo:
            return False
        if maximo is not None and numero > maximo:
            return False
        return True
    except (ValueError, TypeError):
        return False


def validar_extension_archivo(ruta: Union[str, Path], 
                            extensiones_permitidas: List[str]) -> bool:
    """
    Valida que un archivo tenga una extensión permitida.
    
    Args:
        ruta: Ruta del archivo
        extensiones_permitidas: Lista de extensiones permitidas (ej: ['.txt', '.log'])
        
    Returns:
        bool: True si la extensión es válida, False si no
    """
    try:
        ruta_path = Path(ruta)
        extension = ruta_path.suffix.lower()
        return extension in [ext.lower() for ext in extensiones_permitidas]
    except Exception:
        return False


def sanitizar_nombre_archivo(nombre: str) -> str:
    """
    Sanitiza un nombre de archivo eliminando caracteres peligrosos.
    
    Args:
        nombre: Nombre original del archivo
        
    Returns:
        str: Nombre sanitizado
    """
    # Eliminar caracteres peligrosos y reemplazar por guiones bajos
    nombre_limpio = re.sub(r'[<>:"/\\|?*]', '_', nombre)
    
    # Limitar longitud
    if len(nombre_limpio) > 255:
        nombre_limpio = nombre_limpio[:255]
    
    # Asegurar que no esté vacío
    if not nombre_limpio.strip():
        nombre_limpio = "archivo_sin_nombre"
    
    return nombre_limpio


def validar_direccion_ip(ip: str) -> bool:
    """
    Valida que una cadena sea una dirección IP válida.
    
    Args:
        ip: Dirección IP a validar
        
    Returns:
        bool: True si es válida, False si no
    """
    try:
        partes = ip.split('.')
        if len(partes) != 4:
            return False
        
        for parte in partes:
            numero = int(parte)
            if numero < 0 or numero > 255:
                return False
        
        return True
    except (ValueError, AttributeError):
        return False


def validar_puerto(puerto: Union[str, int]) -> bool:
    """
    Valida que un puerto sea válido (0-65535).
    
    Args:
        puerto: Puerto a validar
        
    Returns:
        bool: True si es válido, False si no
    """
    try:
        numero_puerto = int(puerto)
        return 0 <= numero_puerto <= 65535
    except (ValueError, TypeError):
        return False


def es_ruta_segura(ruta: Union[str, Path]) -> bool:
    """
    Verifica que una ruta sea segura (no contenga caracteres maliciosos).
    
    Args:
        ruta: Ruta a verificar
        
    Returns:
        bool: True si es segura, False si no
    """
    try:
        ruta_str = str(ruta)
        
        # Verificar caracteres peligrosos
        caracteres_peligrosos = ['..', '<', '>', '|', '&', ';', '`', '$']
        for caracter in caracteres_peligrosos:
            if caracter in ruta_str:
                return False
        
        # Verificar que no sea una ruta absoluta a directorios críticos del sistema
        rutas_criticas = ['/etc/passwd', '/etc/shadow', '/etc/sudoers']
        ruta_absoluta = os.path.abspath(ruta_str)
        
        for ruta_critica in rutas_criticas:
            if ruta_absoluta == ruta_critica:
                return False
        
        return True
    except Exception:
        return False


def validar_ip(ip: str) -> bool:
    """
    Valida si una cadena es una dirección IP válida (IPv4 o IPv6).
    
    Args:
        ip: Cadena a validar como dirección IP
        
    Returns:
        bool: True si es una IP válida
    """
    if not isinstance(ip, str):
        return False
    
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False
