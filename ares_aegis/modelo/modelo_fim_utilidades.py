#!/usr/bin/env python3
"""
Ares Aegis - Utilidades FIM
Clases auxiliares y utilidades para el sistema de monitoreo de integridad de archivos

Creado por DogSoulDev (https://github.com/DogSoulDev)
Todos los derechos reservados. Este código es propietario y confidencial.

Versión: 4.0.0
"""

import os
import hashlib
import mimetypes
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field

try:
    import pwd
    import grp
except ImportError:
    pwd = grp = None
from collections import defaultdict
from enum import Enum
from stat import filemode

from ..utils.utils_ayuda_logging import configurar_logger_modulo


class TipoArchivo(Enum):
    EJECUTABLE = "ejecutable"
    BIBLIOTECA = "biblioteca"
    CONFIGURACION = "configuracion"
    SCRIPT = "script"
    BINARIO = "binario"
    TEXTO = "texto"
    SISTEMA = "sistema"
    LOG = "log"
    TEMPORAL = "temporal"
    COMPRIMIDO = "comprimido"
    MULTIMEDIA = "multimedia"
    DOCUMENTO = "documento"
    CERTIFICADO = "certificado"
    CLAVE = "clave"
    BASE_DATOS = "base_datos"
    DESCONOCIDO = "desconocido"


class NivelCriticidadFIM(Enum):
    """Niveles de criticidad para archivos monitoreados."""
    CRITICO = "CRITICO"
    ALTO = "ALTO"
    MEDIO = "MEDIO"
    BAJO = "BAJO"
    INFO = "INFO"


class TipoCambio(Enum):
    CREADO = "creado"
    MODIFICADO = "modificado"
    ELIMINADO = "eliminado"
    MOVIDO = "movido"
    PERMISOS_MODIFICADOS = "permisos_modificados"
    PROPIETARIO_MODIFICADO = "propietario_modificado"
    GRUPO_MODIFICADO = "grupo_modificado"
    TAMAÑO_MODIFICADO = "tamaño_modificado"
    HASH_MODIFICADO = "hash_modificado"
    TIMESTAMP_MODIFICADO = "timestamp_modificado"
    ATRIBUTOS_MODIFICADOS = "atributos_modificados"


class EstadoMonitoreo(Enum):
    ACTIVO = "activo"
    INACTIVO = "inactivo"
    PAUSADO = "pausado"
    ERROR = "error"
    INICIALIZANDO = "inicializando"
    FINALIZANDO = "finalizando"


class TipoAmenazaFIM(Enum):
    MALWARE_DETECTADO = "malware_detectado"
    ARCHIVO_SISTEMA_MODIFICADO = "archivo_sistema_modificado"
    CONFIGURACION_ALTERADA = "configuracion_alterada"
    EJECUTABLE_SOSPECHOSO = "ejecutable_sospechoso"
    BACKDOOR_POTENCIAL = "backdoor_potencial"
    ROOTKIT_DETECTADO = "rootkit_detectado"
    ARCHIVO_CRITICO_ELIMINADO = "archivo_critico_eliminado"
    PERMISOS_PELIGROSOS = "permisos_peligrosos"
    ESCALACION_PRIVILEGIOS = "escalacion_privilegios"
    INYECCION_CODIGO = "inyeccion_codigo"
    FIRMA_INVALIDA = "firma_invalida"
    TAMAÑO_ANORMAL = "tamaño_anormal"


@dataclass
class MetadatosArchivoAvanzados:
    ruta: str
    nombre_archivo: str
    extension: str
    tipo_archivo: TipoArchivo
    tamaño_bytes: int
    hash_md5: str
    hash_sha1: str
    hash_sha256: str
    hash_sha512: str
    permisos_octal: str
    permisos_texto: str
    propietario_uid: int
    propietario_nombre: str
    grupo_gid: int
    grupo_nombre: str
    fecha_creacion: datetime
    fecha_modificacion: datetime
    fecha_acceso: datetime
    fecha_cambio_metadatos: datetime
    timestamp_registro: datetime
    es_enlace_simbolico: bool = False
    destino_enlace: Optional[str] = None
    numero_inodo: int = 0
    numero_enlaces: int = 0
    dispositivo: int = 0
    tipo_mime: Optional[str] = None
    encoding: Optional[str] = None
    firma_digital: Optional[str] = None
    version_archivo: Optional[str] = None
    comentarios: List[str] = field(default_factory=list)
    marcadores_seguridad: List[str] = field(default_factory=list)
    nivel_criticidad: NivelCriticidadFIM = NivelCriticidadFIM.INFO
    
    def __post_init__(self):
        """Post-procesamiento de metadatos."""
        if isinstance(self.tipo_archivo, str):
            try:
                self.tipo_archivo = TipoArchivo(self.tipo_archivo)
            except ValueError:
                self.tipo_archivo = TipoArchivo.DESCONOCIDO
        
        if isinstance(self.nivel_criticidad, str):
            try:
                self.nivel_criticidad = NivelCriticidadFIM(self.nivel_criticidad)
            except ValueError:
                self.nivel_criticidad = NivelCriticidadFIM.INFO
        
        self._evaluar_criticidad()
        self._detectar_marcadores_seguridad()
    
    @classmethod
    def desde_archivo(cls, ruta: str) -> 'MetadatosArchivoAvanzados':
        """Crea metadatos desde un archivo del sistema."""
        try:
            ruta_path = Path(ruta)
            stat_info = os.stat(ruta)
            
            # Información básica
            nombre = ruta_path.name
            extension = ruta_path.suffix.lower()
            tipo_archivo = cls._determinar_tipo_archivo(ruta, extension)
            
            # Hashes (solo para archivos regulares y pequeños)
            hashes = {'md5': '', 'sha1': '', 'sha256': '', 'sha512': ''}
            if os.path.isfile(ruta) and stat_info.st_size < 100 * 1024 * 1024:  # 100MB límite
                hashes = cls._calcular_hashes(ruta)
            
            # Propietario y grupo
            propietario_nombre = cls._obtener_nombre_usuario(stat_info.st_uid)
            grupo_nombre = cls._obtener_nombre_grupo(stat_info.st_gid)
            
            # Tipo MIME
            tipo_mime, encoding = mimetypes.guess_type(ruta)
            
            # Enlaces simbólicos
            es_enlace = os.path.islink(ruta)
            destino_enlace = os.readlink(ruta) if es_enlace else None
            
            return cls(
                ruta=ruta,
                nombre_archivo=nombre,
                extension=extension,
                tipo_archivo=tipo_archivo,
                tamaño_bytes=stat_info.st_size,
                hash_md5=hashes['md5'],
                hash_sha1=hashes['sha1'],
                hash_sha256=hashes['sha256'],
                hash_sha512=hashes['sha512'],
                permisos_octal=oct(stat_info.st_mode)[-3:],
                permisos_texto=filemode(stat_info.st_mode),
                propietario_uid=stat_info.st_uid,
                propietario_nombre=propietario_nombre,
                grupo_gid=stat_info.st_gid,
                grupo_nombre=grupo_nombre,
                fecha_creacion=datetime.fromtimestamp(stat_info.st_ctime),
                fecha_modificacion=datetime.fromtimestamp(stat_info.st_mtime),
                fecha_acceso=datetime.fromtimestamp(stat_info.st_atime),
                fecha_cambio_metadatos=datetime.fromtimestamp(stat_info.st_ctime),
                timestamp_registro=datetime.now(),
                es_enlace_simbolico=es_enlace,
                destino_enlace=destino_enlace,
                numero_inodo=stat_info.st_ino,
                numero_enlaces=stat_info.st_nlink,
                dispositivo=stat_info.st_dev,
                tipo_mime=tipo_mime,
                encoding=encoding
            )
        
        except Exception:
            # En caso de error, retornar metadatos básicos
            return cls(
                ruta=ruta,
                nombre_archivo=os.path.basename(ruta),
                extension="",
                tipo_archivo=TipoArchivo.DESCONOCIDO,
                tamaño_bytes=0,
                hash_md5="",
                hash_sha1="",
                hash_sha256="",
                hash_sha512="",
                permisos_octal="000",
                permisos_texto="----------",
                propietario_uid=0,
                propietario_nombre="unknown",
                grupo_gid=0,
                grupo_nombre="unknown",
                fecha_creacion=datetime.now(),
                fecha_modificacion=datetime.now(),
                fecha_acceso=datetime.now(),
                fecha_cambio_metadatos=datetime.now(),
                timestamp_registro=datetime.now()
            )
    
    @staticmethod
    def _determinar_tipo_archivo(ruta: str, extension: str) -> TipoArchivo:
        """Determina el tipo de archivo basado en la ruta y extensión."""
        extension = extension.lower()
        ruta_lower = ruta.lower()
        
        # Ejecutables
        if extension in ['.exe', '.bin', '.com', '.bat', '.cmd', '.sh', '.run'] or '/bin/' in ruta_lower or '/sbin/' in ruta_lower:
            return TipoArchivo.EJECUTABLE
        
        # Bibliotecas
        if extension in ['.so', '.dll', '.dylib', '.a', '.lib']:
            return TipoArchivo.BIBLIOTECA
        
        # Configuración
        if extension in ['.conf', '.cfg', '.ini', '.yaml', '.yml', '.json', '.xml', '.toml'] or '/etc/' in ruta_lower:
            return TipoArchivo.CONFIGURACION
        
        # Scripts
        if extension in ['.py', '.js', '.php', '.pl', '.rb', '.sh', '.ps1', '.vbs']:
            return TipoArchivo.SCRIPT
        
        # Logs
        if extension in ['.log', '.out', '.err'] or '/var/log/' in ruta_lower:
            return TipoArchivo.LOG
        
        # Temporales
        if extension in ['.tmp', '.temp', '.cache'] or '/tmp/' in ruta_lower or '/var/tmp/' in ruta_lower:
            return TipoArchivo.TEMPORAL
        
        # Comprimidos
        if extension in ['.zip', '.tar', '.gz', '.bz2', '.xz', '.7z', '.rar']:
            return TipoArchivo.COMPRIMIDO
        
        # Certificados y claves
        if extension in ['.pem', '.crt', '.cer', '.key', '.p12', '.pfx']:
            return TipoArchivo.CERTIFICADO
        
        if extension in ['.key', '.priv', '.pub', '.rsa', '.dsa']:
            return TipoArchivo.CLAVE
        
        # Base de datos
        if extension in ['.db', '.sqlite', '.sqlite3', '.mdb', '.accdb']:
            return TipoArchivo.BASE_DATOS
        
        # Sistema
        if '/proc/' in ruta_lower or '/sys/' in ruta_lower or '/dev/' in ruta_lower:
            return TipoArchivo.SISTEMA
        
        # Verificar si es ejecutable por permisos
        try:
            if os.access(ruta, os.X_OK) and os.path.isfile(ruta):
                return TipoArchivo.EJECUTABLE
        except Exception:
            pass
        
        return TipoArchivo.DESCONOCIDO
    
    @staticmethod
    def _calcular_hashes(ruta: str) -> Dict[str, str]:
        """Calcula múltiples hashes del archivo."""
        hashes = {'md5': '', 'sha1': '', 'sha256': '', 'sha512': ''}
        
        try:
            with open(ruta, 'rb') as archivo:
                contenido = archivo.read()
                
                hashes['md5'] = hashlib.md5(contenido).hexdigest()
                hashes['sha1'] = hashlib.sha1(contenido).hexdigest()
                hashes['sha256'] = hashlib.sha256(contenido).hexdigest()
                hashes['sha512'] = hashlib.sha512(contenido).hexdigest()
        
        except Exception:
            pass
        
        return hashes
    
    @staticmethod
    def _obtener_nombre_usuario(uid: int) -> str:
        """Obtiene el nombre del usuario por UID."""
        try:
            return pwd.getpwuid(uid).pw_name  # type: ignore
        except (KeyError, ImportError):
            return str(uid)
    
    @staticmethod
    def _obtener_nombre_grupo(gid: int) -> str:
        """Obtiene el nombre del grupo por GID."""
        try:
            return grp.getgrgid(gid).gr_name  # type: ignore
        except (KeyError, ImportError):
            return str(gid)
    
    def _evaluar_criticidad(self):
        """Evalúa la criticidad del archivo basado en su ubicación y tipo."""
        ruta_lower = self.ruta.lower()
        
        # Archivos críticos del sistema
        if any(critica in ruta_lower for critica in ['/boot/', '/etc/', '/bin/', '/sbin/', '/usr/bin/', '/usr/sbin/']):
            self.nivel_criticidad = NivelCriticidadFIM.CRITICO
        
        # Archivos de configuración importantes
        elif any(config in ruta_lower for config in ['/etc/passwd', '/etc/shadow', '/etc/sudoers', '/etc/ssh/']):
            self.nivel_criticidad = NivelCriticidadFIM.CRITICO
        
        # Archivos ejecutables
        elif self.tipo_archivo == TipoArchivo.EJECUTABLE:
            self.nivel_criticidad = NivelCriticidadFIM.ALTO
        
        # Archivos de configuración general
        elif self.tipo_archivo == TipoArchivo.CONFIGURACION:
            self.nivel_criticidad = NivelCriticidadFIM.MEDIO
        
        # Certificados y claves
        elif self.tipo_archivo in [TipoArchivo.CERTIFICADO, TipoArchivo.CLAVE]:
            self.nivel_criticidad = NivelCriticidadFIM.ALTO
    
    def _detectar_marcadores_seguridad(self):
        """Detecta marcadores de seguridad en el archivo."""
        if self.tipo_archivo == TipoArchivo.EJECUTABLE:
            self.marcadores_seguridad.append("executable")
        
        if 'x' in self.permisos_texto and self.tamaño_bytes > 0:
            self.marcadores_seguridad.append("executable_permissions")
        
        if self.propietario_uid == 0:
            self.marcadores_seguridad.append("root_owned")
        
        if '4' in self.permisos_octal[0] or '2' in self.permisos_octal[0]:
            self.marcadores_seguridad.append("setuid_setgid")
    
    def comparar_con(self, otros_metadatos: 'MetadatosArchivoAvanzados') -> List[TipoCambio]:
        """Compara estos metadatos con otros y devuelve las diferencias."""
        cambios = []
        
        if self.hash_sha256 != otros_metadatos.hash_sha256:
            cambios.append(TipoCambio.HASH_MODIFICADO)
        
        if self.tamaño_bytes != otros_metadatos.tamaño_bytes:
            cambios.append(TipoCambio.TAMAÑO_MODIFICADO)
        
        if self.permisos_texto != otros_metadatos.permisos_texto:
            cambios.append(TipoCambio.PERMISOS_MODIFICADOS)
        
        if self.propietario_uid != otros_metadatos.propietario_uid:
            cambios.append(TipoCambio.PROPIETARIO_MODIFICADO)
        
        if self.grupo_gid != otros_metadatos.grupo_gid:
            cambios.append(TipoCambio.GRUPO_MODIFICADO)
        
        if self.fecha_modificacion != otros_metadatos.fecha_modificacion:
            cambios.append(TipoCambio.TIMESTAMP_MODIFICADO)
        
        return cambios
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte los metadatos a diccionario."""
        return {
            'ruta': self.ruta,
            'nombre_archivo': self.nombre_archivo,
            'extension': self.extension,
            'tipo_archivo': self.tipo_archivo.value,
            'tamaño_bytes': self.tamaño_bytes,
            'hash_md5': self.hash_md5,
            'hash_sha1': self.hash_sha1,
            'hash_sha256': self.hash_sha256,
            'hash_sha512': self.hash_sha512,
            'permisos_octal': self.permisos_octal,
            'permisos_texto': self.permisos_texto,
            'propietario_uid': self.propietario_uid,
            'propietario_nombre': self.propietario_nombre,
            'grupo_gid': self.grupo_gid,
            'grupo_nombre': self.grupo_nombre,
            'fecha_creacion': self.fecha_creacion.isoformat(),
            'fecha_modificacion': self.fecha_modificacion.isoformat(),
            'fecha_acceso': self.fecha_acceso.isoformat(),
            'fecha_cambio_metadatos': self.fecha_cambio_metadatos.isoformat(),
            'timestamp_registro': self.timestamp_registro.isoformat(),
            'es_enlace_simbolico': self.es_enlace_simbolico,
            'destino_enlace': self.destino_enlace,
            'numero_inodo': self.numero_inodo,
            'numero_enlaces': self.numero_enlaces,
            'dispositivo': self.dispositivo,
            'tipo_mime': self.tipo_mime,
            'encoding': self.encoding,
            'firma_digital': self.firma_digital,
            'version_archivo': self.version_archivo,
            'comentarios': self.comentarios,
            'marcadores_seguridad': self.marcadores_seguridad,
            'nivel_criticidad': self.nivel_criticidad.value
        }


class UtilsFIM:
    """Utilidades generales para el sistema FIM."""
    
    @staticmethod
    def determinar_tipo_archivo(ruta: str, extension: str) -> TipoArchivo:
        """Wrapper para determinar tipo de archivo."""
        return MetadatosArchivoAvanzados._determinar_tipo_archivo(ruta, extension)
    
    @staticmethod
    def calcular_hashes(ruta: str) -> Dict[str, str]:
        """Wrapper para calcular hashes."""
        return MetadatosArchivoAvanzados._calcular_hashes(ruta)
    
    @staticmethod
    def es_archivo_critico(ruta: str) -> bool:
        """Determina si un archivo es crítico para el sistema."""
        rutas_criticas = [
            '/boot/', '/etc/', '/bin/', '/sbin/', '/usr/bin/', '/usr/sbin/',
            '/lib/', '/usr/lib/', '/var/lib/', '/usr/share/'
        ]
        
        archivos_criticos = [
            '/etc/passwd', '/etc/shadow', '/etc/group', '/etc/sudoers',
            '/etc/fstab', '/etc/hosts', '/etc/ssh/sshd_config'
        ]
        
        ruta_lower = ruta.lower()
        
        # Verificar archivos específicos críticos
        if any(critico in ruta_lower for critico in archivos_criticos):
            return True
        
        # Verificar directorios críticos
        if any(critica in ruta_lower for critica in rutas_criticas):
            return True
        
        return False
    
    @staticmethod
    def obtener_nivel_criticidad(ruta: str, tipo_archivo: TipoArchivo) -> NivelCriticidadFIM:
        """Obtiene el nivel de criticidad de un archivo."""
        if UtilsFIM.es_archivo_critico(ruta):
            return NivelCriticidadFIM.CRITICO
        
        if tipo_archivo == TipoArchivo.EJECUTABLE:
            return NivelCriticidadFIM.ALTO
        
        if tipo_archivo == TipoArchivo.CONFIGURACION:
            return NivelCriticidadFIM.MEDIO
        
        if tipo_archivo in [TipoArchivo.CERTIFICADO, TipoArchivo.CLAVE]:
            return NivelCriticidadFIM.ALTO
        
        return NivelCriticidadFIM.BAJO


class AnalizadorAmenazasFIM:
    """Analizador de amenazas para el sistema FIM optimizado para Kali Linux."""
    
    def __init__(self):
        """Inicializa el analizador de amenazas."""
        self.logger = configurar_logger_modulo("analizador_amenazas_fim")
        
        # Patrones de amenazas optimizados para Kali Linux
        self.patrones_malware = self._cargar_patrones_malware_kali()
        self.rutas_criticas = self._cargar_rutas_criticas_kali()
        self.extensiones_sospechosas = self._cargar_extensiones_sospechosas_kali()
        
        # Umbrales de detección optimizados
        self.tamaño_minimo_sospechoso = 1024 * 1024  # 1MB
        self.tamaño_maximo_normal = 100 * 1024 * 1024  # 100MB
        
        self.logger.info("Analizador de amenazas FIM inicializado para Kali Linux")
    
    def _cargar_patrones_malware_kali(self) -> Dict[str, List[str]]:
        """Carga patrones específicos de Kali Linux."""
        return {
            'nombres_sospechosos': [
                # Herramientas de pentesting maliciosas
                'backdoor', 'trojan', 'keylogger', 'rootkit', 'botnet',
                'mimikatz', 'cobalt', 'empire', 'powersploit', 'bloodhound',
                'lazagne', 'secretsdump', 'procdump', 'lsadump',
                'webshell', 'php-reverse-shell', 'nc.exe', 'netcat', 'socat',
                'obfuscated', 'encoded', 'packed', 'crypted', 'polymorphic'
            ],
            'extensiones_malware': [
                '.exe', '.com', '.scr', '.pif', '.bat', '.cmd', '.vbs', '.ps1',
                '.zip', '.rar', '.7z', '.tar.gz', '.doc', '.docm', '.xls', '.xlsm'
            ],
            'directorios_sospechosos': [
                '/tmp/.', '/dev/shm/.', '/var/tmp/.', '/.hidden',
                '/home/*/.hidden/', '/root/.hidden/', '/usr/local/hidden/',
                '/tmp/metasploit*/', '/tmp/msfvenom*/', '/tmp/beef*/'
            ]
        }
    
    def _cargar_rutas_criticas_kali(self) -> Set[str]:
        """Carga rutas críticas específicas de Kali Linux."""
        return {
            # Sistema base crítico
            '/etc/passwd', '/etc/shadow', '/etc/group', '/etc/sudoers',
            '/etc/hosts', '/etc/ssh/sshd_config', '/etc/fstab',
            '/boot/', '/usr/bin/', '/usr/sbin/', '/bin/', '/sbin/',
            
            # Configuraciones de Kali específicas
            '/etc/apt/sources.list', '/etc/proxychains.conf', '/etc/tor/torrc',
            '/usr/share/metasploit-framework/config/',
            '/usr/share/beef-xss/config.yaml',
            
            # Herramientas de seguridad críticas
            '/usr/share/nmap/scripts/', '/usr/share/yara/rules/',
            '/usr/share/wordlists/', '/etc/fail2ban/',
            
            # Configuraciones de red y firewall
            '/etc/iptables/rules.v4', '/etc/ufw/user.rules',
            '/etc/NetworkManager/', '/etc/systemd/network/'
        }
    
    def _cargar_extensiones_sospechosas_kali(self) -> Set[str]:
        """Carga extensiones sospechosas optimizadas para Kali."""
        return {
            '.tmp', '.temp', '.bak', '.old', '.hidden', '.suspect',
            '.b64', '.base64', '.encoded', '.obfuscated', '.packed',
            '.msf', '.rc', '.resource', '.exploit', '.payload',
            '.dump', '.dmp', '.mem', '.core', '.pcap.bak', '.sql.bak'
        }
    
    def es_archivo_sospechoso(self, ruta: str, nombre: str, extension: str) -> bool:
        """
        Determina si un archivo es sospechoso basado en patrones optimizados.
        
        Args:
            ruta: Ruta completa del archivo
            nombre: Nombre del archivo
            extension: Extensión del archivo
        
        Returns:
            bool: True si el archivo es sospechoso
        """
        nombre_lower = nombre.lower()
        ruta_lower = ruta.lower()
        
        # Verificar nombres sospechosos
        if any(patron in nombre_lower for patron in self.patrones_malware['nombres_sospechosos']):
            return True
        
        # Verificar extensiones maliciosas
        if extension in self.patrones_malware['extensiones_malware']:
            return True
        
        # Verificar directorios sospechosos
        if any(directorio in ruta_lower for directorio in self.patrones_malware['directorios_sospechosos']):
            return True
        
        # Archivos ocultos en ubicaciones críticas
        if nombre.startswith('.') and any(critica in ruta for critica in self.rutas_criticas):
            return True
        
        return False
    
    def evaluar_criticidad_cambio(self, ruta: str, tipo_cambio: str) -> str:
        """
        Evalúa la criticidad de un cambio basado en la ruta y tipo.
        
        Args:
            ruta: Ruta del archivo modificado
            tipo_cambio: Tipo de cambio detectado
        
        Returns:
            str: Nivel de criticidad (CRITICO, ALTO, MEDIO, BAJO)
        """
        # Archivos críticos del sistema
        if any(critica in ruta for critica in self.rutas_criticas):
            return "CRITICO"
        
        # Cambios en ejecutables del sistema
        if any(ejecutable in ruta for ejecutable in ['/bin/', '/sbin/', '/usr/bin/', '/usr/sbin/']):
            return "ALTO"
        
        # Cambios en configuraciones
        if any(config in ruta for config in ['/etc/', '.conf', '.cfg', '.ini']):
            return "ALTO"
        
        # Eliminación de archivos importantes
        if tipo_cambio == "eliminado" and not ruta.startswith('/tmp/'):
            return "MEDIO"
        
        return "BAJO"
    
    def analizar_cambio(self, archivo: str, tipo_cambio: TipoCambio, 
                       metadatos_actuales: Optional['MetadatosArchivoAvanzados'], 
                       metadatos_anteriores: Optional['MetadatosArchivoAvanzados']) -> Optional[TipoAmenazaFIM]:
        """
        Analiza un cambio de archivo para detectar amenazas.
        
        Args:
            archivo: Ruta del archivo
            tipo_cambio: Tipo de cambio detectado
            metadatos_actuales: Metadatos actuales (si existen)
            metadatos_anteriores: Metadatos anteriores (si existen)
        
        Returns:
            TipoAmenazaFIM o None si no se detecta amenaza
        """
        try:
            # Archivos críticos del sistema
            if archivo in self.rutas_criticas:
                if tipo_cambio == TipoCambio.MODIFICADO:
                    return TipoAmenazaFIM.ARCHIVO_SISTEMA_MODIFICADO
                elif tipo_cambio == TipoCambio.ELIMINADO:
                    return TipoAmenazaFIM.ARCHIVO_CRITICO_ELIMINADO
            
            # Ejecutables sospechosos
            if metadatos_actuales and metadatos_actuales.tipo_archivo == TipoArchivo.EJECUTABLE:
                # Ejecutable en ubicación inusual
                if not any(ruta in archivo.lower() for ruta in ['/bin/', '/sbin/', '/usr/bin/', '/usr/sbin/']):
                    return TipoAmenazaFIM.EJECUTABLE_SOSPECHOSO
            
            # Cambios de permisos peligrosos
            if (metadatos_actuales and metadatos_anteriores and 
                metadatos_actuales.permisos_texto != metadatos_anteriores.permisos_texto):
                # SUID/SGID agregado
                if ('s' in metadatos_actuales.permisos_texto and 
                    's' not in metadatos_anteriores.permisos_texto):
                    return TipoAmenazaFIM.ESCALACION_PRIVILEGIOS
            
            # Archivos con nombres sospechosos
            nombre_archivo = os.path.basename(archivo).lower()
            for patron in self.patrones_malware['nombres_sospechosos']:
                if patron in nombre_archivo:
                    return TipoAmenazaFIM.MALWARE_DETECTADO
            
            # Archivos de configuración alterados
            if (metadatos_actuales and metadatos_actuales.tipo_archivo == TipoArchivo.CONFIGURACION):
                if '/etc/' in archivo or '.conf' in archivo:
                    return TipoAmenazaFIM.CONFIGURACION_ALTERADA
            
            # Sin amenazas detectadas
            return None
        
        except Exception as e:
            self.logger.error(f"Error analizando cambio en {archivo}: {e}")
            return None


class GeneradorReportesFIM:
    """Generador de reportes optimizado para análisis en Kali Linux."""
    
    def __init__(self):
        """Inicializa el generador de reportes."""
        self.logger = configurar_logger_modulo("generador_reportes_fim")
    
    def generar_reporte_markdown(self, alertas: List[Any], estadisticas: Dict[str, Any]) -> str:
        """
        Genera un reporte detallado en formato Markdown.
        
        Args:
            alertas: Lista de alertas FIM
            estadisticas: Estadísticas del sistema
        
        Returns:
            str: Reporte en formato Markdown
        """
        md = "# 🛡️ Reporte de Integridad FIM - Kali Linux\n\n"
        md += f"**Generado:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # Resumen estadístico
        md += "## 📊 Resumen Estadístico\n\n"
        md += f"- **Archivos monitoreados:** {estadisticas.get('archivos_monitoreados', 0):,}\n"
        md += f"- **Verificaciones realizadas:** {estadisticas.get('verificaciones_realizadas', 0):,}\n"
        md += f"- **Cambios detectados:** {estadisticas.get('cambios_detectados', 0):,}\n"
        md += f"- **Amenazas detectadas:** {estadisticas.get('amenazas_detectadas', 0):,}\n"
        md += f"- **Tiempo activo:** {estadisticas.get('tiempo_activo_segundos', 0):,}s\n\n"
        
        # Alertas críticas
        alertas_criticas = [a for a in alertas if hasattr(a, 'nivel_criticidad') and 
                           a.nivel_criticidad.value == 'CRITICO']
        
        if alertas_criticas:
            md += "## 🚨 Alertas Críticas\n\n"
            for alerta in alertas_criticas[:10]:  # Mostrar solo las primeras 10
                if hasattr(alerta, 'generar_reporte_markdown'):
                    md += alerta.generar_reporte_markdown()
                else:
                    md += f"- **Archivo:** {getattr(alerta, 'archivo_afectado', 'N/A')}\n"
                    md += f"  **Descripción:** {getattr(alerta, 'descripcion', 'N/A')}\n\n"
        
        # Recomendaciones para Kali Linux
        md += "## 🔧 Recomendaciones para Kali Linux\n\n"
        md += "- Verificar regularmente la integridad de herramientas de pentesting\n"
        md += "- Monitorear cambios en configuraciones de proxy y TOR\n"
        md += "- Validar actualizaciones de bases de datos de exploits\n"
        md += "- Revisar logs de sistemas críticos diariamente\n\n"
        
        return md
    
    def generar_resumen_ejecutivo(self, alertas: List[Any], estadisticas: Dict[str, Any]) -> str:
        """
        Genera un resumen ejecutivo conciso.
        
        Args:
            alertas: Lista de alertas
            estadisticas: Estadísticas del sistema
        
        Returns:
            str: Resumen ejecutivo
        """
        total_alertas = len(alertas)
        alertas_criticas = len([a for a in alertas if hasattr(a, 'nivel_criticidad') and 
                               a.nivel_criticidad.value == 'CRITICO'])
        
        resumen = f"**Estado del Sistema FIM:**\n"
        resumen += f"- Total de alertas: {total_alertas}\n"
        resumen += f"- Alertas críticas: {alertas_criticas}\n"
        resumen += f"- Archivos monitoreados: {estadisticas.get('archivos_monitoreados', 0):,}\n"
        
        if alertas_criticas > 0:
            resumen += f"\n⚠️ **ATENCIÓN:** {alertas_criticas} alertas críticas requieren investigación inmediata.\n"
        elif total_alertas > 0:
            resumen += f"\n📋 **INFO:** {total_alertas} cambios detectados para revisión.\n"
        else:
            resumen += f"\n✅ **OK:** Sistema sin cambios críticos detectados.\n"
        
        return resumen


class OptimizadorRendimientoFIM:
    """Optimizador de rendimiento específico para Kali Linux."""
    
    def __init__(self):
        """Inicializa el optimizador."""
        self.logger = configurar_logger_modulo("optimizador_fim")
        self.cache_metadatos = {}
        self.rutas_optimizadas = set()
    
    def optimizar_rutas_monitoreo(self, rutas: Set[str]) -> Set[str]:
        """
        Optimiza las rutas de monitoreo para mejor rendimiento en Kali.
        
        Args:
            rutas: Conjunto de rutas a optimizar
        
        Returns:
            Set[str]: Rutas optimizadas
        """
        rutas_optimizadas = set()
        
        # Priorizar rutas críticas de Kali
        rutas_prioritarias = {
            '/etc/', '/usr/bin/', '/usr/sbin/', '/bin/', '/sbin/',
            '/usr/share/metasploit-framework/', '/usr/share/wordlists/',
            '/root/.ssh/', '/etc/ssh/'
        }
        
        for ruta in rutas:
            # Incluir rutas prioritarias
            if any(prioritaria in ruta for prioritaria in rutas_prioritarias):
                if os.path.exists(ruta):
                    rutas_optimizadas.add(ruta)
            
            # Excluir rutas que cambian frecuentemente y no son críticas
            elif not any(excluir in ruta for excluir in ['/tmp/', '/var/tmp/', '/proc/', '/sys/']):
                if os.path.exists(ruta):
                    rutas_optimizadas.add(ruta)
        
        self.logger.info(f"Rutas optimizadas: {len(rutas_optimizadas)} de {len(rutas)} originales")
        return rutas_optimizadas
    
    def cache_metadatos_archivo(self, ruta: str, metadatos: Any) -> None:
        """
        Cachea metadatos para mejorar rendimiento.
        
        Args:
            ruta: Ruta del archivo
            metadatos: Metadatos a cachear
        """
        self.cache_metadatos[ruta] = {
            'metadatos': metadatos,
            'timestamp_cache': datetime.now()
        }
    
    def optimizar_ciclo(self, baseline: Dict[str, Any], estadisticas: Dict[str, Any]) -> None:
        """
        Optimiza el ciclo de monitoreo basado en estadísticas.
        
        Args:
            baseline: Línea base actual
            estadisticas: Estadísticas del sistema
        """
        # Limpiar cache si es necesario
        if len(self.cache_metadatos) > 10000:
            self.limpiar_cache_antiguo()
        
        # Actualizar estadísticas
        estadisticas['cache_metadatos_size'] = len(self.cache_metadatos)
        estadisticas['rutas_optimizadas'] = len(self.rutas_optimizadas)
        
        self.logger.debug("Ciclo de optimización completado")
    
    def limpiar_cache_antiguo(self, horas_limite: int = 24) -> None:
        """
        Limpia entradas del cache más antiguas que el límite especificado.
        
        Args:
            horas_limite: Horas límite para mantener cache
        """
        limite = datetime.now() - timedelta(hours=horas_limite)
        
        rutas_eliminar = []
        for ruta, data in self.cache_metadatos.items():
            if data['timestamp_cache'] < limite:
                rutas_eliminar.append(ruta)
        
        for ruta in rutas_eliminar:
            del self.cache_metadatos[ruta]
        
        if rutas_eliminar:
            self.logger.info(f"Limpiadas {len(rutas_eliminar)} entradas del cache")
        
        # Limpiar cache si es muy grande
        if len(self.cache_metadatos) > 10000:
            self._limpiar_cache_antiguo()
    
    def obtener_metadatos_cache(self, ruta: str) -> Optional[Any]:
        """
        Obtiene metadatos del cache si están disponibles.
        
        Args:
            ruta: Ruta del archivo
        
        Returns:
            Optional[Any]: Metadatos cacheados o None
        """
        if ruta in self.cache_metadatos:
            cache_entry = self.cache_metadatos[ruta]
            # Cache válido por 5 minutos
            if (datetime.now() - cache_entry['timestamp_cache']).seconds < 300:
                return cache_entry['metadatos']
        
        return None
    
    def _limpiar_cache_antiguo(self):
        """Limpia entradas antiguas del cache."""
        ahora = datetime.now()
        rutas_a_eliminar = []
        
        for ruta, cache_entry in self.cache_metadatos.items():
            if (ahora - cache_entry['timestamp_cache']).seconds > 600:  # 10 minutos
                rutas_a_eliminar.append(ruta)
        
        for ruta in rutas_a_eliminar:
            del self.cache_metadatos[ruta]
        
        self.logger.debug(f"Cache limpiado: {len(rutas_a_eliminar)} entradas eliminadas")
    
    def recomendar_configuracion_kali(self) -> Dict[str, Any]:
        """
        Recomienda configuración optimizada para Kali Linux.
        
        Returns:
            Dict[str, Any]: Configuración recomendada
        """
        return {
            'intervalo_verificacion': 300,  # 5 minutos para entornos activos
            'max_archivos_por_verificacion': 5000,  # Límite para evitar sobrecarga
            'cache_habilitado': True,
            'compresion_logs': True,
            'retencion_alertas_dias': 30,
            'rutas_excluir_por_defecto': [
                '/tmp/', '/var/tmp/', '/proc/', '/sys/', '/dev/',
                '/var/log/', '/var/cache/', '/root/.cache/',
                '/tmp/metasploit*/', '/tmp/beef*/', '/tmp/sqlmap*/'
            ],
            'extensiones_priorizar': [
                '.conf', '.cfg', '.ini', '.sh', '.py', '.pl', '.rb',
                '.key', '.pem', '.crt', '.p12', '.pfx'
            ]
        }
