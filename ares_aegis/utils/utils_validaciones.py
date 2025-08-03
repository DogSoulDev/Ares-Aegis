import os
import re
from pathlib import Path
from typing import Union

def validar_archivo(ruta: Union[str, Path]) -> bool:
    try: return Path(ruta).exists() and Path(ruta).is_file()
    except: return False

def validar_directorio(ruta: Union[str, Path]) -> bool:
    try: return Path(ruta).exists() and Path(ruta).is_dir()
    except: return False

def validar_permisos_lectura(ruta: Union[str, Path]) -> bool:
    try: return os.access(str(ruta), os.R_OK)
    except: return False

def validar_permisos_escritura(ruta: Union[str, Path]) -> bool:
    try: return os.access(str(ruta), os.W_OK)
    except: return False

def es_ruta_segura(ruta: Union[str, Path]) -> bool:
    try: return '..' not in str(ruta) and '~' not in str(ruta)
    except: return False

def validar_hash(hash_str: str) -> bool:
    if not hash_str: return False
    return bool((len(hash_str) == 32 and re.match(r'^[a-fA-F0-9]{32}$', hash_str)) or (len(hash_str) == 64 and re.match(r'^[a-fA-F0-9]{64}$', hash_str)))

validar_ruta_archivo = validar_archivo
validar_ruta_directorio = validar_directorio


