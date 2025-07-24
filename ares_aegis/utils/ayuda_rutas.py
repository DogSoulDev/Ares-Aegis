#!/usr/bin/env python3
"""
Creado por DogSoulDev
Todos los derechos reservados. Este código es propietario y confidencial.

Utilidades de Manejo de Rutas
"""

import os
import shutil
from pathlib import Path
from typing import Union, List, Optional


def crear_ruta_segura(ruta: Union[str, Path]) -> Path:
    ruta_path = Path(ruta)
    ruta_path.parent.mkdir(parents=True, exist_ok=True)
    return ruta_path


def obtener_ruta_absoluta(ruta: Union[str, Path]) -> Path:
    """
    Obtiene la ruta absoluta de forma segura.
    
    Args:
        ruta: Ruta relativa o absoluta
        
    Returns:
        Path: Ruta absoluta
    """
    return Path(ruta).resolve()


def obtener_tamaño_archivo(ruta: Union[str, Path]) -> int:
    """
    Obtiene el tamaño de un archivo en bytes.
    
    Args:
        ruta: Ruta del archivo
        
    Returns:
        int: Tamaño en bytes
        
    Raises:
        FileNotFoundError: Si el archivo no existe
        OSError: Si hay problemas de acceso
    """
    return Path(ruta).stat().st_size


def obtener_tamaño_directorio(ruta: Union[str, Path]) -> int:
    """
    Obtiene el tamaño total de un directorio en bytes.
    
    Args:
        ruta: Ruta del directorio
        
    Returns:
        int: Tamaño total en bytes
    """
    ruta_path = Path(ruta)
    tamaño_total = 0
    
    for archivo in ruta_path.rglob('*'):
        if archivo.is_file():
            try:
                tamaño_total += archivo.stat().st_size
            except (OSError, FileNotFoundError):
                # Saltar archivos que no se pueden leer
                continue
    
    return tamaño_total


def listar_archivos_recursivo(directorio: Union[str, Path], 
                            extensiones: Optional[List[str]] = None) -> List[Path]:
    """
    Lista archivos de forma recursiva en un directorio.
    
    Args:
        directorio: Directorio a explorar
        extensiones: Lista de extensiones a filtrar (opcional)
        
    Returns:
        List[Path]: Lista de archivos encontrados
    """
    directorio_path = Path(directorio)
    archivos = []
    
    for archivo in directorio_path.rglob('*'):
        if archivo.is_file():
            if extensiones is None:
                archivos.append(archivo)
            else:
                if archivo.suffix.lower() in [ext.lower() for ext in extensiones]:
                    archivos.append(archivo)
    
    return archivos


def copiar_archivo_seguro(origen: Union[str, Path], 
                         destino: Union[str, Path]) -> bool:
    """
    Copia un archivo de forma segura.
    
    Args:
        origen: Archivo origen
        destino: Archivo destino
        
    Returns:
        bool: True si la copia fue exitosa, False si falló
    """
    try:
        origen_path = Path(origen)
        destino_path = Path(destino)
        
        # Crear directorio destino si no existe
        destino_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Copiar archivo
        shutil.copy2(str(origen_path), str(destino_path))
        return True
        
    except Exception:
        return False


def mover_archivo_seguro(origen: Union[str, Path], 
                        destino: Union[str, Path]) -> bool:
    """
    Mueve un archivo de forma segura.
    
    Args:
        origen: Archivo origen
        destino: Archivo destino
        
    Returns:
        bool: True si el movimiento fue exitoso, False si falló
    """
    try:
        origen_path = Path(origen)
        destino_path = Path(destino)
        
        # Crear directorio destino si no existe
        destino_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Mover archivo
        shutil.move(str(origen_path), str(destino_path))
        return True
        
    except Exception:
        return False


def eliminar_archivo_seguro(ruta: Union[str, Path]) -> bool:
    """
    Elimina un archivo de forma segura.
    
    Args:
        ruta: Archivo a eliminar
        
    Returns:
        bool: True si la eliminación fue exitosa, False si falló
    """
    try:
        Path(ruta).unlink()
        return True
    except Exception:
        return False


def obtener_rutas_sistema() -> dict:
    """
    Obtiene las rutas importantes del sistema para Ares Aegis en Kali Linux.
    
    Returns:
        dict: Diccionario con las rutas del sistema
    """
    # Rutas optimizadas para Kali Linux
    rutas = {
        'directorio_base': '/usr/local/bin/ares_aegis',
        'directorio_config': '/etc/ares_aegis',
        'directorio_logs': '/var/log/ares_aegis',
        'directorio_datos': '/var/lib/ares_aegis',
        'directorio_cuarentena': '/var/ares_aegis_cuarentena',
        'directorio_recursos': '/usr/share/ares_aegis/recursos',
        'archivo_firmas': '/etc/ares_aegis/firmas.txt',
        'archivo_reglas_fim': '/etc/ares_aegis/reglas_fim_base.json',
        'archivo_log_principal': '/var/log/ares_aegis/ares_aegis.log',
        'archivo_log_siem': '/var/log/ares_aegis/eventos_siem.json'
    }
    
    return rutas


def crear_estructura_directorios_sistema() -> bool:
    """
    Crea la estructura de directorios del sistema para Ares Aegis.
    
    Returns:
        bool: True si se creó exitosamente, False si falló
    """
    try:
        rutas = obtener_rutas_sistema()
        
        # Crear directorios principales
        directorios = [
            rutas['directorio_base'],
            rutas['directorio_config'],
            rutas['directorio_logs'],
            rutas['directorio_cuarentena'],
            rutas['directorio_recursos']
        ]
        
        for directorio in directorios:
            Path(directorio).mkdir(parents=True, exist_ok=True)
            
        return True
        
    except Exception:
        return False


def obtener_espacio_disco(ruta: Union[str, Path]) -> dict:
    """
    Obtiene información del espacio en disco para una ruta.
    
    Args:
        ruta: Ruta a verificar
        
    Returns:
        dict: Información del espacio en disco
    """
    try:
        total, usado, libre = shutil.disk_usage(str(ruta))
        
        return {
            'total': total,
            'usado': usado,
            'libre': libre,
            'porcentaje_usado': round((usado / total) * 100, 2)
        }
        
    except Exception:
        return {
            'total': 0,
            'usado': 0,
            'libre': 0,
            'porcentaje_usado': 0
        }
