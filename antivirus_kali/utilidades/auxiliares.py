"""
Funciones auxiliares genéricas para el proyecto.
Incluye helpers reutilizables y utilidades varias.

Uso:
    from antivirus_kali.utilidades import auxiliares
    # Llama a funciones auxiliares aquí
"""

import os
import hashlib
import json
import psutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime


def obtener_hash_archivo(ruta_archivo: Union[str, Path], algoritmo: str = 'sha256') -> Optional[str]:
    """
    Calcula el hash de un archivo usando el algoritmo especificado.
    
    Args:
        ruta_archivo: Ruta al archivo
        algoritmo: Algoritmo de hash (md5, sha1, sha256, sha512)
        
    Returns:
        Hash del archivo o None si hay error
    """
    try:
        ruta = Path(ruta_archivo)
        if not ruta.exists() or not ruta.is_file():
            return None
            
        hash_obj = hashlib.new(algoritmo)
        with open(ruta, 'rb') as archivo:
            for chunk in iter(lambda: archivo.read(4096), b""):
                hash_obj.update(chunk)
        
        return hash_obj.hexdigest()
        
    except Exception:
        return None


def formatear_tamaño(bytes_size: int) -> str:
    """
    Convierte bytes a formato legible (KB, MB, GB, etc.).
    
    Args:
        bytes_size: Tamaño en bytes
        
    Returns:
        String formateado con el tamaño
    """
    if bytes_size == 0:
        return "0 B"
    
    size = float(bytes_size)
    for unidad in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.1f} {unidad}"
        size /= 1024.0
    
    return f"{size:.1f} PB"


def obtener_info_sistema() -> Dict[str, Any]:
    """
    Obtiene información básica del sistema.
    
    Returns:
        Diccionario con información del sistema
    """
    try:
        info = {
            'sistema_operativo': psutil.LINUX and 'Linux' or 'Otro',
            'arquitectura': os.uname().machine,
            'memoria_total': psutil.virtual_memory().total,
            'memoria_disponible': psutil.virtual_memory().available,
            'uso_cpu': psutil.cpu_percent(interval=1),
            'num_cpus': psutil.cpu_count(),
            'uptime': datetime.now() - datetime.fromtimestamp(psutil.boot_time()),
            'procesos_activos': len(psutil.pids())
        }
        return info
    except Exception:
        return {}


def validar_permisos_archivo(ruta_archivo: Union[str, Path], 
                           lectura: bool = True, 
                           escritura: bool = False, 
                           ejecucion: bool = False) -> bool:
    """
    Valida si el usuario actual tiene los permisos especificados sobre un archivo.
    
    Args:
        ruta_archivo: Ruta al archivo
        lectura: Verificar permiso de lectura
        escritura: Verificar permiso de escritura
        ejecucion: Verificar permiso de ejecución
        
    Returns:
        True si tiene todos los permisos especificados
    """
    try:
        ruta = Path(ruta_archivo)
        if not ruta.exists():
            return False
            
        permisos = [
            not lectura or os.access(ruta, os.R_OK),
            not escritura or os.access(ruta, os.W_OK),
            not ejecucion or os.access(ruta, os.X_OK)
        ]
        
        return all(permisos)
        
    except Exception:
        return False


def guardar_json(datos: Dict[str, Any], ruta_archivo: Union[str, Path]) -> bool:
    """
    Guarda datos en formato JSON.
    
    Args:
        datos: Diccionario con los datos a guardar
        ruta_archivo: Ruta donde guardar el archivo
        
    Returns:
        True si se guardó correctamente
    """
    try:
        ruta = Path(ruta_archivo)
        ruta.parent.mkdir(parents=True, exist_ok=True)
        
        with open(ruta, 'w', encoding='utf-8') as archivo:
            json.dump(datos, archivo, indent=2, ensure_ascii=False, default=str)
        
        return True
        
    except Exception:
        return False


def cargar_json(ruta_archivo: Union[str, Path]) -> Optional[Dict[str, Any]]:
    """
    Carga datos desde un archivo JSON.
    
    Args:
        ruta_archivo: Ruta al archivo JSON
        
    Returns:
        Diccionario con los datos o None si hay error
    """
    try:
        ruta = Path(ruta_archivo)
        if not ruta.exists():
            return None
            
        with open(ruta, 'r', encoding='utf-8') as archivo:
            return json.load(archivo)
            
    except Exception:
        return None


def buscar_archivos(directorio: Union[str, Path], 
                   patron: str = "*", 
                   recursivo: bool = True,
                   solo_archivos: bool = True) -> List[Path]:
    """
    Busca archivos en un directorio con un patrón específico.
    
    Args:
        directorio: Directorio donde buscar
        patron: Patrón de búsqueda (ej: "*.py", "test_*")
        recursivo: Buscar en subdirectorios
        solo_archivos: Solo devolver archivos (no directorios)
        
    Returns:
        Lista de rutas encontradas
    """
    try:
        ruta_dir = Path(directorio)
        if not ruta_dir.exists() or not ruta_dir.is_dir():
            return []
            
        if recursivo:
            resultados = list(ruta_dir.rglob(patron))
        else:
            resultados = list(ruta_dir.glob(patron))
            
        if solo_archivos:
            resultados = [r for r in resultados if r.is_file()]
            
        return sorted(resultados)
        
    except Exception:
        return []


def limpiar_directorio_temporal(directorio: Union[str, Path], 
                              max_antigüedad_horas: int = 24) -> int:
    """
    Limpia archivos temporales antiguos de un directorio.
    
    Args:
        directorio: Directorio a limpiar
        max_antigüedad_horas: Máxima antigüedad en horas para conservar archivos
        
    Returns:
        Número de archivos eliminados
    """
    try:
        ruta_dir = Path(directorio)
        if not ruta_dir.exists():
            return 0
            
        archivos_eliminados = 0
        limite_tiempo = datetime.now().timestamp() - (max_antigüedad_horas * 3600)
        
        for archivo in ruta_dir.rglob("*"):
            if archivo.is_file():
                try:
                    if archivo.stat().st_mtime < limite_tiempo:
                        archivo.unlink()
                        archivos_eliminados += 1
                except Exception:
                    continue
                    
        return archivos_eliminados
        
    except Exception:
        return 0


def verificar_conectividad_red(host: str = "8.8.8.8", puerto: int = 53, timeout: int = 3) -> bool:
    """
    Verifica conectividad de red básica.
    
    Args:
        host: Host para probar conectividad
        puerto: Puerto para la conexión
        timeout: Timeout en segundos
        
    Returns:
        True si hay conectividad
    """
    try:
        import socket
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        
        resultado = sock.connect_ex((host, puerto))
        sock.close()
        
        return resultado == 0
        
    except Exception:
        return False
