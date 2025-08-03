import os
import shutil
from pathlib import Path
from typing import Union, List, Optional

def crear_ruta_segura(ruta: Union[str, Path]) -> Path:
    ruta_path = Path(ruta)
    ruta_path.parent.mkdir(parents=True, exist_ok=True)
    return ruta_path

def obtener_ruta_absoluta(ruta: Union[str, Path]) -> Path:
    return Path(ruta).resolve()

def obtener_tamaño_archivo(ruta: Union[str, Path]) -> int:
    return Path(ruta).stat().st_size

def obtener_tamaño_directorio(ruta: Union[str, Path]) -> int:
    ruta_path = Path(ruta)
    tamaño_total = 0
    for archivo in ruta_path.rglob('*'):
        if archivo.is_file():
            try: tamaño_total += archivo.stat().st_size
            except: continue
    return tamaño_total

def listar_archivos_recursivo(directorio: Union[str, Path], extensiones: Optional[List[str]] = None) -> List[Path]:
    directorio_path = Path(directorio)
    archivos = []
    for archivo in directorio_path.rglob('*'):
        if archivo.is_file():
            if extensiones is None or archivo.suffix.lower() in [ext.lower() for ext in extensiones]:
                archivos.append(archivo)
    return archivos


def copiar_archivo_seguro(origen: Union[str, Path], destino: Union[str, Path]) -> bool:
    try:
        destino_path = Path(destino)
        destino_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(origen), str(destino_path))
        return True
    except: return False

def mover_archivo_seguro(origen: Union[str, Path], destino: Union[str, Path]) -> bool:
    try:
        destino_path = Path(destino)
        destino_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(origen), str(destino_path))
        return True
    except: return False

def eliminar_archivo_seguro(ruta: Union[str, Path]) -> bool:
    try: Path(ruta).unlink(); return True
    except: return False

def obtener_rutas_sistema() -> dict:
    return {
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

def crear_estructura_directorios_sistema() -> bool:
    try:
        rutas = obtener_rutas_sistema()
        for directorio in [rutas['directorio_base'], rutas['directorio_config'], rutas['directorio_logs'], rutas['directorio_cuarentena'], rutas['directorio_recursos']]:
            Path(directorio).mkdir(parents=True, exist_ok=True)
        return True
    except: return False

def obtener_espacio_disco(ruta: Union[str, Path]) -> dict:
    try:
        total, usado, libre = shutil.disk_usage(str(ruta))
        return {'total': total, 'usado': usado, 'libre': libre, 'porcentaje_usado': round((usado / total) * 100, 2)}
    except: return {'total': 0, 'usado': 0, 'libre': 0, 'porcentaje_usado': 0}
