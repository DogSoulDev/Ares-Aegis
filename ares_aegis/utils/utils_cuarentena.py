"""
Utilidades para el gestor de cuarentena
Clases y funciones extraídas para reducir la complejidad del modelo principal
"""

import os
import json
import shutil
import hashlib
import time
import subprocess
import mimetypes
import tempfile
import stat
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Union, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
from enum import Enum

try:
    import pwd
    import grp
except ImportError:
    pwd = grp = None


class EstadoCuarentena(Enum):
    """Estados de los archivos en cuarentena."""
    PENDIENTE = "pendiente"
    EN_ANALISIS = "en_analisis"
    ANALIZADO = "analizado"
    SEGURO = "seguro"
    MALICIOSO = "malicioso"
    SOSPECHOSO = "sospechoso"
    RESTAURADO = "restaurado"
    ELIMINADO = "eliminado"
    ERROR = "error"


class TipoAmenazaCuarentena(Enum):
    """Tipos de amenazas detectadas en cuarentena."""
    VIRUS = "virus"
    TROYANO = "troyano"
    BACKDOOR = "backdoor"
    ROOTKIT = "rootkit"
    GUSANO = "gusano"
    SPYWARE = "spyware"
    ADWARE = "adware"
    RANSOMWARE = "ransomware"
    KEYLOGGER = "keylogger"
    BOTNET = "botnet"
    EXPLOIT = "exploit"
    MACRO_MALICIOSO = "macro_malicioso"
    SCRIPT_MALICIOSO = "script_malicioso"
    SOSPECHOSO = "sospechoso"
    DESCONOCIDO = "desconocido"


class NivelRiesgoCuarentena(Enum):
    """Niveles de riesgo de cuarentena."""
    CRITICO = "critico"
    ALTO = "alto"
    MEDIO = "medio"
    BAJO = "bajo"


class AccionCuarentena(Enum):
    """Acciones de cuarentena disponibles."""
    AISLAR = "aislar"
    ANALIZAR = "analizar"
    LIMPIAR = "limpiar"
    RESTAURAR = "restaurar"
    ELIMINAR = "eliminar"
    MANTENER = "mantener"
    NOTIFICAR = "notificar"
    BLOQUEAR = "bloquear"
    CUARENTENA_COMPLETA = "cuarentena_completa"


@dataclass
class MetadatosCuarentena:
    """Metadatos de un archivo en cuarentena."""
    ruta_original: str
    ruta_cuarentena: str
    fecha_cuarentena: datetime
    estado: EstadoCuarentena
    tipo_amenaza: TipoAmenazaCuarentena
    nivel_riesgo: NivelRiesgoCuarentena
    hash_md5: str
    hash_sha256: str
    tamaño_bytes: int
    permisos_originales: str
    propietario_original: str
    grupo_original: str
    mime_type: str
    motivo_cuarentena: str
    detalles_analisis: Dict[str, Any] = field(default_factory=dict)
    acciones_tomadas: List[AccionCuarentena] = field(default_factory=list)
    fecha_ultimo_analisis: Optional[datetime] = None
    resultado_analisis: Optional[str] = None
    firmas_detectadas: List[str] = field(default_factory=list)
    herramientas_usadas: List[str] = field(default_factory=list)
    notas_forenses: List[str] = field(default_factory=list)
    referencias_externas: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte los metadatos a diccionario."""
        return {
            'ruta_original': self.ruta_original,
            'ruta_cuarentena': self.ruta_cuarentena,
            'fecha_cuarentena': self.fecha_cuarentena.isoformat(),
            'estado': self.estado.value,
            'tipo_amenaza': self.tipo_amenaza.value,
            'nivel_riesgo': self.nivel_riesgo.value,
            'hash_md5': self.hash_md5,
            'hash_sha256': self.hash_sha256,
            'tamaño_bytes': self.tamaño_bytes,
            'permisos_originales': self.permisos_originales,
            'propietario_original': self.propietario_original,
            'grupo_original': self.grupo_original,
            'mime_type': self.mime_type,
            'motivo_cuarentena': self.motivo_cuarentena,
            'detalles_analisis': self.detalles_analisis,
            'acciones_tomadas': [accion.value for accion in self.acciones_tomadas],
            'fecha_ultimo_analisis': self.fecha_ultimo_analisis.isoformat() if self.fecha_ultimo_analisis else None,
            'resultado_analisis': self.resultado_analisis,
            'firmas_detectadas': self.firmas_detectadas,
            'herramientas_usadas': self.herramientas_usadas,
            'notas_forenses': self.notas_forenses,
            'referencias_externas': self.referencias_externas
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MetadatosCuarentena':
        """Crea metadatos desde un diccionario."""
        return cls(
            ruta_original=data['ruta_original'],
            ruta_cuarentena=data['ruta_cuarentena'],
            fecha_cuarentena=datetime.fromisoformat(data['fecha_cuarentena']),
            estado=EstadoCuarentena(data['estado']),
            tipo_amenaza=TipoAmenazaCuarentena(data['tipo_amenaza']),
            nivel_riesgo=NivelRiesgoCuarentena(data['nivel_riesgo']),
            hash_md5=data['hash_md5'],
            hash_sha256=data['hash_sha256'],
            tamaño_bytes=data['tamaño_bytes'],
            permisos_originales=data['permisos_originales'],
            propietario_original=data['propietario_original'],
            grupo_original=data['grupo_original'],
            mime_type=data['mime_type'],
            motivo_cuarentena=data['motivo_cuarentena'],
            detalles_analisis=data.get('detalles_analisis', {}),
            acciones_tomadas=[AccionCuarentena(accion) for accion in data.get('acciones_tomadas', [])],
            fecha_ultimo_analisis=datetime.fromisoformat(data['fecha_ultimo_analisis']) if data.get('fecha_ultimo_analisis') else None,
            resultado_analisis=data.get('resultado_analisis'),
            firmas_detectadas=data.get('firmas_detectadas', []),
            herramientas_usadas=data.get('herramientas_usadas', []),
            notas_forenses=data.get('notas_forenses', []),
            referencias_externas=data.get('referencias_externas', [])
        )


class UtilsCuarentena:
    """Utilidades generales para cuarentena"""
    
    @staticmethod
    def calcular_hash_archivo(ruta_archivo: str) -> Tuple[str, str]:
        """Calcula hashes MD5 y SHA256 de un archivo."""
        hash_md5 = hashlib.md5()
        hash_sha256 = hashlib.sha256()
        
        try:
            with open(ruta_archivo, 'rb') as archivo:
                for chunk in iter(lambda: archivo.read(4096), b""):
                    hash_md5.update(chunk)
                    hash_sha256.update(chunk)
        except Exception:
            return "", ""
        
        return hash_md5.hexdigest(), hash_sha256.hexdigest()
    
    @staticmethod
    def obtener_info_archivo(ruta_archivo: str) -> Dict[str, Any]:
        """Obtiene información detallada de un archivo."""
        try:
            stat_info = os.stat(ruta_archivo)
            
            # Obtener propietario y grupo si es posible
            propietario = ""
            grupo = ""
            if pwd and grp:
                try:
                    propietario = pwd.getpwuid(stat_info.st_uid).pw_name  # type: ignore
                    grupo = grp.getgrgid(stat_info.st_gid).gr_name  # type: ignore
                except:
                    propietario = str(stat_info.st_uid)
                    grupo = str(stat_info.st_gid)
            
            # Obtener tipo MIME
            mime_type, _ = mimetypes.guess_type(ruta_archivo)
            if not mime_type:
                mime_type = "application/octet-stream"
            
            return {
                'tamaño': stat_info.st_size,
                'permisos': oct(stat_info.st_mode)[-3:],
                'propietario': propietario,
                'grupo': grupo,
                'modificado': datetime.fromtimestamp(stat_info.st_mtime),
                'accedido': datetime.fromtimestamp(stat_info.st_atime),
                'creado': datetime.fromtimestamp(stat_info.st_ctime),
                'mime_type': mime_type
            }
        except Exception:
            return {}
    
    @staticmethod
    def es_archivo_ejecutable(ruta_archivo: str) -> bool:
        """Verifica si un archivo es ejecutable."""
        try:
            stat_info = os.stat(ruta_archivo)
            return bool(stat_info.st_mode & stat.S_IXUSR)
        except:
            return False
    
    @staticmethod
    def generar_nombre_cuarentena(ruta_original: str, hash_archivo: str) -> str:
        """Genera un nombre único para archivo en cuarentena."""
        timestamp = int(time.time())
        nombre_original = Path(ruta_original).name
        return f"{timestamp}_{hash_archivo[:8]}_{nombre_original}"


class AnalizadorForenseUtils:
    """Utilidades para análisis forense de archivos en cuarentena"""
    
    @staticmethod
    def verificar_herramientas_disponibles() -> Dict[str, bool]:
        """Verifica qué herramientas de análisis están disponibles."""
        herramientas = {
            'file': AnalizadorForenseUtils._comando_disponible('file'),
            'strings': AnalizadorForenseUtils._comando_disponible('strings'),
            'hexdump': AnalizadorForenseUtils._comando_disponible('hexdump'),
            'xxd': AnalizadorForenseUtils._comando_disponible('xxd'),
            'binwalk': AnalizadorForenseUtils._comando_disponible('binwalk'),
            'foremost': AnalizadorForenseUtils._comando_disponible('foremost'),
            'volatility': AnalizadorForenseUtils._comando_disponible('volatility'),
            'yara': AnalizadorForenseUtils._comando_disponible('yara'),
            'clamav': AnalizadorForenseUtils._comando_disponible('clamscan'),
            'exiftool': AnalizadorForenseUtils._comando_disponible('exiftool'),
            'strace': AnalizadorForenseUtils._comando_disponible('strace'),
            'ltrace': AnalizadorForenseUtils._comando_disponible('ltrace')
        }
        return herramientas
    
    @staticmethod
    def _comando_disponible(comando: str) -> bool:
        """Verifica si un comando está disponible en el sistema."""
        try:
            subprocess.run(['which', comando], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    @staticmethod
    def ejecutar_file(ruta_archivo: str) -> Dict[str, Any]:
        """Ejecuta el comando 'file' para identificar tipo de archivo."""
        try:
            resultado = subprocess.run(
                ['file', '-b', ruta_archivo],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if resultado.returncode == 0:
                return {
                    'comando': 'file',
                    'resultado': resultado.stdout.strip(),
                    'exitoso': True
                }
        except Exception as e:
            return {
                'comando': 'file',
                'error': str(e),
                'exitoso': False
            }
        
        return {'comando': 'file', 'exitoso': False}
    
    @staticmethod
    def ejecutar_strings(ruta_archivo: str, min_len: int = 4) -> Dict[str, Any]:
        """Ejecuta el comando 'strings' para extraer cadenas de texto."""
        try:
            resultado = subprocess.run(
                ['strings', '-n', str(min_len), ruta_archivo],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if resultado.returncode == 0:
                strings_encontrados = resultado.stdout.strip().split('\n')
                # Limitar a las primeras 100 strings para evitar salida masiva
                strings_limitados = strings_encontrados[:100]
                
                return {
                    'comando': 'strings',
                    'strings': strings_limitados,
                    'total_strings': len(strings_encontrados),
                    'exitoso': True
                }
        except Exception as e:
            return {
                'comando': 'strings',
                'error': str(e),
                'exitoso': False
            }
        
        return {'comando': 'strings', 'exitoso': False}
    
    @staticmethod
    def analizar_con_hexdump(ruta_archivo: str, bytes_max: int = 1024) -> Dict[str, Any]:
        """Analiza archivo con hexdump para obtener representación hexadecimal."""
        try:
            resultado = subprocess.run(
                ['hexdump', '-C', '-n', str(bytes_max), ruta_archivo],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if resultado.returncode == 0:
                return {
                    'comando': 'hexdump',
                    'hexdump': resultado.stdout.strip(),
                    'bytes_analizados': bytes_max,
                    'exitoso': True
                }
        except Exception as e:
            return {
                'comando': 'hexdump',
                'error': str(e),
                'exitoso': False
            }
        
        return {'comando': 'hexdump', 'exitoso': False}
    
    @staticmethod
    def cargar_patrones_malware() -> Dict[str, Union[List[str], List[bytes]]]:
        """Carga patrones para análisis de malware."""
        patrones = {
            'signatures_text': [
                'eval(',
                'exec(',
                'system(',
                'shell_exec(',
                'base64_decode(',
                'gzinflate(',
                'str_rot13(',
                '$GLOBALS',
                'php://input',
                '/bin/sh',
                '/bin/bash',
                'cmd.exe',
                'powershell.exe',
                'CreateProcess',
                'VirtualAlloc',
                'WriteProcessMemory',
                'CreateRemoteThread'
            ],
            'signatures_hex': [
                b'\x4d\x5a',  # MZ header (PE)
                b'\x7f\x45\x4c\x46',  # ELF header
                b'\xfe\xed\xfa\xce',  # Mach-O 32-bit
                b'\xfe\xed\xfa\xcf',  # Mach-O 64-bit
                b'\x50\x4b\x03\x04',  # ZIP header
                b'\x89\x50\x4e\x47',  # PNG header
                b'\xff\xd8\xff',  # JPEG header
                b'\x25\x50\x44\x46'  # PDF header
            ],
            'suspicious_patterns': [
                'root:',
                'shadow:',
                '/etc/passwd',
                '/etc/shadow',
                'HKEY_LOCAL_MACHINE',
                'HKEY_CURRENT_USER',
                'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run',
                'startup',
                'autorun',
                'persistence'
            ]
        }
        return patrones
    
    @staticmethod
    def buscar_patrones_en_archivo(ruta_archivo: str, patrones: Dict[str, Union[List[str], List[bytes]]]) -> Dict[str, Any]:
        """Busca patrones sospechosos en un archivo."""
        resultados = {
            'patrones_encontrados': [],
            'nivel_sospecha': 'bajo',
            'detalles': {}
        }
        
        try:
            with open(ruta_archivo, 'rb') as archivo:
                contenido = archivo.read(1024 * 1024)  # Leer hasta 1MB
                contenido_text = contenido.decode('utf-8', errors='ignore').lower()
                
                # Buscar patrones de texto
                patrones_texto_encontrados = []
                for patron in patrones.get('signatures_text', []):
                    if isinstance(patron, str) and patron.lower() in contenido_text:
                        patrones_texto_encontrados.append(patron)
                
                # Buscar patrones hexadecimales
                patrones_hex_encontrados = []
                for patron in patrones.get('signatures_hex', []):
                    if isinstance(patron, bytes) and patron in contenido:
                        patrones_hex_encontrados.append(patron.hex())
                
                # Buscar patrones sospechosos
                patrones_sospechosos_encontrados = []
                for patron in patrones.get('suspicious_patterns', []):
                    if isinstance(patron, str) and patron.lower() in contenido_text:
                        patrones_sospechosos_encontrados.append(patron)
                
                # Calcular nivel de sospecha
                total_patrones = len(patrones_texto_encontrados) + len(patrones_hex_encontrados) + len(patrones_sospechosos_encontrados)
                
                if total_patrones >= 5:
                    nivel_sospecha = 'critico'
                elif total_patrones >= 3:
                    nivel_sospecha = 'alto'
                elif total_patrones >= 1:
                    nivel_sospecha = 'medio'
                else:
                    nivel_sospecha = 'bajo'
                
                resultados.update({
                    'patrones_encontrados': patrones_texto_encontrados + patrones_hex_encontrados + patrones_sospechosos_encontrados,
                    'nivel_sospecha': nivel_sospecha,
                    'detalles': {
                        'patrones_texto': patrones_texto_encontrados,
                        'patrones_hex': patrones_hex_encontrados,
                        'patrones_sospechosos': patrones_sospechosos_encontrados,
                        'total_patrones': total_patrones
                    }
                })
                
        except Exception as e:
            resultados['error'] = str(e)
        
        return resultados


class GestorBackupCuarentena:
    """Gestor de copias de seguridad para archivos en cuarentena"""
    
    def __init__(self, directorio_backup: str):
        """Inicializa el gestor de backup."""
        self.directorio_backup = Path(directorio_backup)
        self.directorio_backup.mkdir(parents=True, exist_ok=True)
    
    def crear_backup(self, ruta_archivo: str, metadatos: MetadatosCuarentena) -> Optional[str]:
        """Crea una copia de seguridad de un archivo antes de la cuarentena."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nombre_backup = f"backup_{timestamp}_{metadatos.hash_sha256[:8]}_{Path(ruta_archivo).name}"
            ruta_backup = self.directorio_backup / nombre_backup
            
            # Copiar archivo
            shutil.copy2(ruta_archivo, ruta_backup)
            
            # Crear archivo de metadatos del backup
            metadatos_backup = {
                'archivo_original': ruta_archivo,
                'fecha_backup': timestamp,
                'metadatos_cuarentena': metadatos.to_dict()
            }
            
            ruta_metadatos = ruta_backup.with_suffix('.metadata.json')
            with open(ruta_metadatos, 'w', encoding='utf-8') as f:
                json.dump(metadatos_backup, f, indent=2, ensure_ascii=False)
            
            return str(ruta_backup)
            
        except Exception:
            return None
    
    def restaurar_desde_backup(self, ruta_backup: str, ruta_destino: str) -> bool:
        """Restaura un archivo desde su backup."""
        try:
            shutil.copy2(ruta_backup, ruta_destino)
            return True
        except Exception:
            return False
    
    def listar_backups(self) -> List[Dict[str, Any]]:
        """Lista todos los backups disponibles."""
        backups = []
        
        try:
            for archivo_backup in self.directorio_backup.glob('backup_*'):
                if archivo_backup.suffix != '.json':
                    metadatos_file = archivo_backup.with_suffix('.metadata.json')
                    
                    metadatos = {}
                    if metadatos_file.exists():
                        try:
                            with open(metadatos_file, 'r', encoding='utf-8') as f:
                                metadatos = json.load(f)
                        except:
                            pass
                    
                    backups.append({
                        'ruta_backup': str(archivo_backup),
                        'tamaño': archivo_backup.stat().st_size,
                        'fecha_creacion': datetime.fromtimestamp(archivo_backup.stat().st_ctime),
                        'metadatos': metadatos
                    })
        except Exception:
            pass
        
        return sorted(backups, key=lambda x: x['fecha_creacion'], reverse=True)


class ValidadorCuarentena:
    """Validador de archivos para cuarentena"""
    
    @staticmethod
    def validar_archivo_para_cuarentena(ruta_archivo: str) -> Tuple[bool, str]:
        """Valida si un archivo puede ser puesto en cuarentena."""
        try:
            # Verificar que el archivo existe
            if not os.path.exists(ruta_archivo):
                return False, "El archivo no existe"
            
            # Verificar que es un archivo (no directorio)
            if not os.path.isfile(ruta_archivo):
                return False, "La ruta no corresponde a un archivo"
            
            # Verificar permisos de lectura
            if not os.access(ruta_archivo, os.R_OK):
                return False, "Sin permisos de lectura"
            
            # Verificar que no es un archivo del sistema crítico
            archivos_criticos = [
                '/bin/', '/sbin/', '/usr/bin/', '/usr/sbin/',
                '/etc/passwd', '/etc/shadow', '/etc/fstab',
                '/boot/', '/lib/', '/lib64/'
            ]
            
            ruta_absoluta = os.path.abspath(ruta_archivo)
            for critico in archivos_criticos:
                if ruta_absoluta.startswith(critico):
                    return False, f"Archivo del sistema crítico: {critico}"
            
            return True, ""
            
        except Exception as e:
            return False, f"Error validando archivo: {str(e)}"
    
    @staticmethod
    def calcular_nivel_riesgo(metadatos: MetadatosCuarentena, analisis_forense: Dict[str, Any]) -> NivelRiesgoCuarentena:
        """Calcula el nivel de riesgo basado en metadatos y análisis."""
        puntuacion_riesgo = 0
        
        # Puntuación por tipo de amenaza
        puntuacion_amenaza = {
            TipoAmenazaCuarentena.RANSOMWARE: 10,
            TipoAmenazaCuarentena.ROOTKIT: 9,
            TipoAmenazaCuarentena.BACKDOOR: 8,
            TipoAmenazaCuarentena.TROYANO: 7,
            TipoAmenazaCuarentena.VIRUS: 6,
            TipoAmenazaCuarentena.GUSANO: 6,
            TipoAmenazaCuarentena.KEYLOGGER: 5,
            TipoAmenazaCuarentena.SPYWARE: 4,
            TipoAmenazaCuarentena.ADWARE: 2,
            TipoAmenazaCuarentena.SOSPECHOSO: 3
        }
        
        puntuacion_riesgo += puntuacion_amenaza.get(metadatos.tipo_amenaza, 1)
        
        # Puntuación por patrones encontrados en análisis forense
        if analisis_forense.get('nivel_sospecha') == 'critico':
            puntuacion_riesgo += 5
        elif analisis_forense.get('nivel_sospecha') == 'alto':
            puntuacion_riesgo += 3
        elif analisis_forense.get('nivel_sospecha') == 'medio':
            puntuacion_riesgo += 1
        
        # Puntuación por archivo ejecutable
        if UtilsCuarentena.es_archivo_ejecutable(metadatos.ruta_original):
            puntuacion_riesgo += 2
        
        # Determinar nivel de riesgo
        if puntuacion_riesgo >= 12:
            return NivelRiesgoCuarentena.CRITICO
        elif puntuacion_riesgo >= 8:
            return NivelRiesgoCuarentena.ALTO
        elif puntuacion_riesgo >= 4:
            return NivelRiesgoCuarentena.MEDIO
        else:
            return NivelRiesgoCuarentena.BAJO
