#!/usr/bin/env python3
"""
Copyright (c) 2025 DogSoulDev (https://github.com/DogSoulDev)
Todos los derechos reservados. Este código es propietario y confidencial.

FIM - Monitor de Integridad de Archivos Avanzado - Ares Aegis
Sistema integral de monitoreo de integridad con detección de amenazas y análisis comportamental
"""

import os
import json
import hashlib
import time
import threading
import subprocess
import re
import mimetypes
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Union, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum
from stat import filemode

from .siem import SIEM, TipoEvento
from ..utilidades.validaciones import validar_ruta_directorio, validar_permisos_lectura
from ..utilidades.ayuda_rutas import (
    listar_archivos_recursivo, obtener_rutas_sistema, crear_ruta_segura
)
from ..utilidades.ayuda_logging import configurar_logger_modulo


class TipoArchivo(Enum):
    """Tipos de archivos en el sistema."""
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
    """Tipos de cambios detectados por FIM."""
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
    """Estados del monitoreo FIM."""
    ACTIVO = "activo"
    INACTIVO = "inactivo"
    PAUSADO = "pausado"
    ERROR = "error"
    INICIALIZANDO = "inicializando"
    FINALIZANDO = "finalizando"


class TipoAmenazaFIM(Enum):
    """Tipos de amenazas detectadas por FIM."""
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
    """Metadatos avanzados de archivo para FIM."""
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
        """Obtiene el nombre de usuario por UID."""
        try:
            import pwd
            return pwd.getpwuid(uid).pw_name
        except Exception:
            return str(uid)
    
    @staticmethod
    def _obtener_nombre_grupo(gid: int) -> str:
        """Obtiene el nombre del grupo por GID."""
        try:
            import grp
            return grp.getgrgid(gid).gr_name
        except Exception:
            return str(gid)
    
    def _evaluar_criticidad(self):
        """Evalúa automáticamente el nivel de criticidad."""
        ruta_lower = self.ruta.lower()
        
        # Archivos críticos del sistema
        if any(critico in ruta_lower for critico in ['/etc/passwd', '/etc/shadow', '/etc/sudoers', '/boot/']):
            self.nivel_criticidad = NivelCriticidadFIM.CRITICO
        
        # Ejecutables del sistema
        elif self.tipo_archivo == TipoArchivo.EJECUTABLE and ('/bin/' in ruta_lower or '/sbin/' in ruta_lower):
            self.nivel_criticidad = NivelCriticidadFIM.ALTO
        
        # Configuraciones importantes
        elif self.tipo_archivo == TipoArchivo.CONFIGURACION and '/etc/' in ruta_lower:
            self.nivel_criticidad = NivelCriticidadFIM.ALTO
        
        # Certificados y claves
        elif self.tipo_archivo in [TipoArchivo.CERTIFICADO, TipoArchivo.CLAVE]:
            self.nivel_criticidad = NivelCriticidadFIM.ALTO
        
        # Archivos con permisos SUID/SGID
        elif 's' in self.permisos_texto:
            self.nivel_criticidad = NivelCriticidadFIM.ALTO
        
        # Bibliotecas del sistema
        elif self.tipo_archivo == TipoArchivo.BIBLIOTECA:
            self.nivel_criticidad = NivelCriticidadFIM.MEDIO
        
        # Scripts ejecutables
        elif self.tipo_archivo == TipoArchivo.SCRIPT and 'x' in self.permisos_texto:
            self.nivel_criticidad = NivelCriticidadFIM.MEDIO
    
    def _detectar_marcadores_seguridad(self):
        """Detecta marcadores de seguridad relevantes."""
        # Permisos especiales
        if 's' in self.permisos_texto:
            self.marcadores_seguridad.append("SUID_SGID")
        
        if 't' in self.permisos_texto:
            self.marcadores_seguridad.append("STICKY_BIT")
        
        # Archivos ocultos
        if self.nombre_archivo.startswith('.'):
            self.marcadores_seguridad.append("ARCHIVO_OCULTO")
        
        # Archivos temporales
        if self.tipo_archivo == TipoArchivo.TEMPORAL:
            self.marcadores_seguridad.append("ARCHIVO_TEMPORAL")
        
        # Ejecutables en ubicaciones no estándar
        if self.tipo_archivo == TipoArchivo.EJECUTABLE and not any(
            std in self.ruta.lower() for std in ['/bin/', '/sbin/', '/usr/bin/', '/usr/sbin/']
        ):
            self.marcadores_seguridad.append("EJECUTABLE_UBICACION_INUSUAL")
        
        # Archivos grandes
        if self.tamaño_bytes > 100 * 1024 * 1024:  # 100MB
            self.marcadores_seguridad.append("ARCHIVO_GRANDE")
        
        # Enlaces simbólicos
        if self.es_enlace_simbolico:
            self.marcadores_seguridad.append("ENLACE_SIMBOLICO")
    
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
        """Convierte metadatos a diccionario."""
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


@dataclass
class AlertaFIM:
    """Alerta avanzada del sistema FIM."""
    id_alerta: str
    tipo_cambio: TipoCambio
    tipo_amenaza: Optional[TipoAmenazaFIM]
    archivo_afectado: str
    descripcion: str
    nivel_criticidad: NivelCriticidadFIM
    metadatos_anteriores: Optional[MetadatosArchivoAvanzados]
    metadatos_actuales: Optional[MetadatosArchivoAvanzados]
    diferencias_detectadas: List[str]
    evidencia: Dict[str, Any]
    timestamp: datetime
    accion_automatica: Optional[str] = None
    falso_positivo: bool = False
    confirmada: bool = False
    investigada: bool = False
    
    def __post_init__(self):
        """Post-procesamiento de la alerta."""
        if not self.id_alerta:
            datos = f"{self.tipo_cambio.value}_{self.archivo_afectado}_{self.timestamp.timestamp()}"
            self.id_alerta = hashlib.sha256(datos.encode()).hexdigest()[:16]
        
        if isinstance(self.tipo_cambio, str):
            self.tipo_cambio = TipoCambio(self.tipo_cambio)
        
        if isinstance(self.nivel_criticidad, str):
            self.nivel_criticidad = NivelCriticidadFIM(self.nivel_criticidad)
        
        if isinstance(self.tipo_amenaza, str):
            self.tipo_amenaza = TipoAmenazaFIM(self.tipo_amenaza)
    
    @property
    def severidad_numerica(self) -> int:
        """Convierte nivel de criticidad a valor numérico."""
        return {
            NivelCriticidadFIM.CRITICO: 4,
            NivelCriticidadFIM.ALTO: 3,
            NivelCriticidadFIM.MEDIO: 2,
            NivelCriticidadFIM.BAJO: 1,
            NivelCriticidadFIM.INFO: 0
        }.get(self.nivel_criticidad, 0)
    
    def generar_reporte_markdown(self) -> str:
        """Genera un reporte detallado en Markdown."""
        emoji_tipo = {
            TipoCambio.CREADO: '🆕',
            TipoCambio.MODIFICADO: '📝',
            TipoCambio.ELIMINADO: '🗑️',
            TipoCambio.MOVIDO: '🔄',
            TipoCambio.PERMISOS_MODIFICADOS: '🔒'
        }.get(self.tipo_cambio, '📋')
        
        emoji_criticidad = {
            NivelCriticidadFIM.CRITICO: '🚨',
            NivelCriticidadFIM.ALTO: '⚠️',
            NivelCriticidadFIM.MEDIO: '🔔',
            NivelCriticidadFIM.BAJO: 'ℹ️',
            NivelCriticidadFIM.INFO: '📄'
        }.get(self.nivel_criticidad, '📋')
        
        md = f"### {emoji_tipo} {emoji_criticidad} Alerta FIM: {self.tipo_cambio.value.upper()}\n\n"
        md += f"**ID Alerta:** `{self.id_alerta}`\n"
        md += f"**Archivo:** `{self.archivo_afectado}`\n"
        md += f"**Descripción:** {self.descripcion}\n"
        md += f"**Nivel de Criticidad:** {self.nivel_criticidad.value}\n"
        md += f"**Timestamp:** {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        if self.tipo_amenaza:
            md += f"**Tipo de Amenaza:** {self.tipo_amenaza.value}\n"
        
        if self.diferencias_detectadas:
            md += f"\n**Diferencias Detectadas:**\n"
            for diff in self.diferencias_detectadas:
                md += f"- {diff}\n"
        
        if self.evidencia:
            md += f"\n**Evidencia:**\n"
            for clave, valor in self.evidencia.items():
                md += f"- **{clave}:** {valor}\n"
        
        if self.accion_automatica:
            md += f"\n**Acción Automática:** {self.accion_automatica}\n"
        
        md += f"\n**Estado:** "
        if self.falso_positivo:
            md += "🟡 Falso Positivo"
        elif self.confirmada:
            md += "🔴 Confirmada"
        elif self.investigada:
            md += "🔍 Investigada"
        else:
            md += "🟠 Pendiente de Investigación"
        
        md += "\n\n---\n\n"
        return md
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la alerta a diccionario."""
        return {
            'id_alerta': self.id_alerta,
            'tipo_cambio': self.tipo_cambio.value,
            'tipo_amenaza': self.tipo_amenaza.value if self.tipo_amenaza else None,
            'archivo_afectado': self.archivo_afectado,
            'descripcion': self.descripcion,
            'nivel_criticidad': self.nivel_criticidad.value,
            'metadatos_anteriores': self.metadatos_anteriores.to_dict() if self.metadatos_anteriores else None,
            'metadatos_actuales': self.metadatos_actuales.to_dict() if self.metadatos_actuales else None,
            'diferencias_detectadas': self.diferencias_detectadas,
            'evidencia': self.evidencia,
            'timestamp': self.timestamp.isoformat(),
            'accion_automatica': self.accion_automatica,
            'falso_positivo': self.falso_positivo,
            'confirmada': self.confirmada,
            'investigada': self.investigada,
            'severidad_numerica': self.severidad_numerica
        }


class AnalizadorAmenazasFIM:
    """Analizador de amenazas para el sistema FIM."""
    
    def __init__(self):
        """Inicializa el analizador de amenazas."""
        self.logger = configurar_logger_modulo("analizador_amenazas_fim")
        
        # Patrones de amenazas
        self.patrones_malware = self._cargar_patrones_malware()
        self.rutas_criticas = self._cargar_rutas_criticas()
        self.extensiones_sospechosas = self._cargar_extensiones_sospechosas()
        
        # Umbrales de detección
        self.tamaño_minimo_sospechoso = 1024 * 1024  # 1MB
        self.tamaño_maximo_normal = 100 * 1024 * 1024  # 100MB
        
        self.logger.info("Analizador de amenazas FIM inicializado")
    
    def _cargar_patrones_malware(self) -> Dict[str, List[str]]:
        """Carga patrones conocidos de malware (expandido para Kali Linux)."""
        return {
            'nombres_sospechosos': [
                # Patrones básicos de malware
                'backdoor', 'trojan', 'keylogger', 'rootkit', 'botnet',
                'worm', 'virus', 'malware', 'exploit', 'payload',
                'shell', 'reverse', 'bind', 'meterpreter', 'stager',
                
                # Patrones específicos de herramientas de pentesting maliciosas
                'mimikatz', 'cobalt', 'empire', 'powersploit',
                'bloodhound', 'sharphound', 'rubeus', 'ghostpack',
                'lazagne', 'secretsdump', 'procdump', 'lsadump',
                
                # Patrones de herramientas de post-explotación
                'persistence', 'lateral', 'escalation', 'exfiltration',
                'credential', 'dump', 'hash', 'password', 'crack',
                
                # Patrones de shells y backdoors
                'webshell', 'php-reverse-shell', 'nc.exe', 'netcat',
                'socat', 'telnet-backdoor', 'ssh-backdoor',
                
                # Patrones de herramientas de evasión
                'obfuscated', 'encoded', 'packed', 'crypted',
                'polymorphic', 'metamorphic', 'steganography',
                
                # Patrones específicos de APT y malware avanzado
                'apt', 'stuxnet', 'wannacry', 'petya', 'notpetya',
                'emotet', 'trickbot', 'qakbot', 'dridex',
                
                # Patrones de herramientas de reconocimiento maliciosas
                'scanner', 'enum', 'bruteforce', 'dictionary',
                'wordlist', 'fuzzer', 'dirb', 'gobuster'
            ],
            'extensiones_malware': [
                # Extensiones ejecutables estándar
                '.exe', '.com', '.scr', '.pif', '.bat', '.cmd',
                '.vbs', '.vbe', '.js', '.jse', '.wsf', '.wsh',
                
                # Extensiones de scripts maliciosos
                '.ps1', '.ps2', '.psc1', '.psc2', '.msh', '.msh1',
                '.msh2', '.mshxml', '.msh1xml', '.msh2xml',
                
                # Extensiones de archivos comprimidos sospechosos
                '.zip', '.rar', '.7z', '.tar.gz', '.tar.bz2',
                
                # Extensiones de documentos con macros
                '.doc', '.docm', '.xls', '.xlsm', '.ppt', '.pptm',
                '.pdf', '.rtf', '.odt', '.ods', '.odp',
                
                # Extensiones de archivos de configuración sospechosos
                '.conf', '.cfg', '.ini', '.reg', '.dat',
                
                # Extensiones específicas de herramientas de pentesting
                '.rc', '.msf', '.nse', '.xml', '.json',
                '.payload', '.shellcode', '.bin', '.raw'
            ],
            'directorios_sospechosos': [
                # Directorios temporales comunes para malware
                '/tmp/.', '/dev/shm/.', '/var/tmp/.', '/.hidden',
                '/proc/self/', '/sys/kernel/', '/run/shm/.',
                
                # Directorios de usuario sospechosos
                '/home/*/.hidden/', '/root/.hidden/', '/home/*/...',
                '/root/.../', '/home/*/.config/.', '/root/.config/.',
                
                # Directorios de sistema inusuales
                '/usr/local/hidden/', '/opt/.hidden/', '/var/.hidden/',
                '/etc/.hidden/', '/lib/.hidden/', '/bin/.hidden/',
                
                # Directorios específicos de Kali que pueden ser abusados
                '/usr/share/metasploit-framework/modules/payloads/singles/',
                '/usr/share/metasploit-framework/modules/exploits/',
                '/tmp/metasploit*/', '/tmp/msfvenom*/',
                
                # Directorios de herramientas de pentesting que pueden ocultar malware
                '/tmp/beef*/', '/tmp/sqlmap*/', '/tmp/nikto*/',
                '/tmp/nmap*/', '/tmp/gobuster*/', '/tmp/dirb*/',
                
                # Directorios de logs que pueden ser comprometidos
                '/var/log/.', '/var/run/.', '/var/spool/.',
                
                # Directorios de web que pueden contener webshells
                '/var/www/html/.', '/var/www/.', '/usr/share/nginx/html/.',
                '/opt/lampp/htdocs/.', '/home/*/public_html/.',
                
                # Directorios de bases de datos comprometidas
                '/var/lib/mysql/.', '/var/lib/postgresql/.',
                '/var/lib/mongodb/.', '/var/lib/redis/.',
                
                # Directorios de servicios que pueden ser comprometidos
                '/etc/cron.d/.', '/etc/systemd/system/.',
                '/home/*/.config/autostart/.', '/root/.config/autostart/.'
            ],
            'patrones_archivos_sistema': [
                # Archivos críticos que nunca deberían ser modificados por malware
                'passwd', 'shadow', 'group', 'sudoers', 'hosts',
                'fstab', 'crontab', 'sshd_config', 'ssh_config',
                
                # Archivos de configuración de servicios críticos
                'apache2.conf', 'nginx.conf', 'my.cnf', 'redis.conf',
                'mongodb.conf', 'torrc', 'proxychains.conf',
                
                # Archivos de inicio del sistema
                'rc.local', 'inittab', 'grub.cfg', 'menu.lst',
                
                # Archivos de configuración de red
                'interfaces', 'resolv.conf', 'nsswitch.conf',
                'dhcpcd.conf', 'wpa_supplicant.conf',
                
                # Archivos de kernels y módulos
                'modules', 'modprobe.conf', 'sysctl.conf',
                'udev.rules', 'fstab'
            ]
        }
    
    def _cargar_rutas_criticas(self) -> Set[str]:
        """Carga rutas críticas del sistema (expandido para Kali Linux)."""
        return {
            # Archivos críticos de autenticación básicos
            '/etc/passwd', '/etc/shadow', '/etc/group', '/etc/gshadow',
            '/etc/sudoers', '/etc/security/limits.conf',
            
            # Configuraciones de red críticas
            '/etc/hosts', '/etc/hosts.allow', '/etc/hosts.deny',
            '/etc/resolv.conf', '/etc/nsswitch.conf',
            
            # Servicios críticos del sistema
            '/etc/crontab', '/etc/ssh/sshd_config', '/etc/fstab',
            
            # Directorios críticos de ejecutables
            '/boot/', '/usr/bin/', '/usr/sbin/', '/bin/', '/sbin/',
            
            # Configuraciones de servicios de red
            '/etc/systemd/', '/etc/init.d/', '/etc/rc.d/',
            '/etc/apache2/apache2.conf', '/etc/nginx/nginx.conf',
            '/etc/mysql/my.cnf', '/etc/postgresql/',
            
            # Configuraciones específicas de Kali Linux
            '/etc/apt/sources.list', '/etc/apt/sources.list.d/',
            '/etc/update-motd.d/', '/etc/profile',
            
            # Herramientas de pentesting críticas
            '/usr/share/metasploit-framework/config/',
            '/usr/share/beef-xss/config.yaml',
            '/etc/proxychains.conf', '/etc/tor/torrc',
            
            # Configuraciones de seguridad
            '/etc/fail2ban/', '/etc/aide/aide.conf',
            '/etc/audit/auditd.conf', '/etc/rsyslog.conf',
            
            # Configuraciones de firewall
            '/etc/iptables/rules.v4', '/etc/iptables/rules.v6',
            '/etc/ufw/user.rules', '/etc/ufw/user6.rules',
            
            # Configuraciones críticas de SSH y certificados
            '/etc/ssh/', '/etc/ssl/certs/', '/etc/pki/',
            '/root/.ssh/authorized_keys', '/root/.ssh/id_rsa',
            
            # Configuraciones de kernels y módulos
            '/etc/modules', '/etc/modprobe.d/',
            '/etc/sysctl.conf', '/etc/sysctl.d/',
            
            # Configuraciones de servicios de base de datos
            '/etc/redis/redis.conf', '/etc/mongodb.conf',
            '/var/lib/mysql/mysql/', '/var/lib/postgresql/',
            
            # Configuraciones de virtualización
            '/etc/docker/daemon.json', '/etc/libvirt/',
            '/etc/qemu/', '/etc/vbox/',
            
            # Archivos de configuración de herramientas forenses
            '/usr/share/autopsy/case/', '/usr/share/sleuthkit/',
            '/usr/share/volatility/plugins/',
            
            # Configuraciones de herramientas de análisis
            '/usr/share/yara/rules/', '/usr/share/clamav/',
            '/usr/share/nmap/scripts/',
            
            # Configuraciones de desarrollo
            '/etc/ld.so.conf', '/etc/ld.so.conf.d/',
            '/usr/include/linux/', '/usr/src/linux-headers*/',
            
            # Configuraciones de monitoreo
            '/etc/nagios/', '/etc/zabbix/', '/etc/collectd/',
            '/etc/munin/', '/etc/cacti/',
            
            # Configuraciones de servicios web especializados
            '/etc/burpsuite/', '/etc/zaproxy/',
            '/usr/share/burpsuite/burpsuite.jar',
            
            # Archivos de configuración de herramientas de red
            '/etc/wireshark/', '/etc/tcpdump/',
            '/usr/share/nmap/nmap-services',
            '/usr/share/masscan/masscan.conf'
        }
    
    def _cargar_extensiones_sospechosas(self) -> Set[str]:
        """Carga extensiones de archivos sospechosas (expandido para Kali Linux)."""
        return {
            # Extensiones de archivos temporales básicos
            '.tmp', '.temp', '.bak', '.old', '.orig', '.swp', '.~',
            '.backup', '.save', '.copy',
            
            # Extensiones relacionadas con malware
            '.hidden', '.suspect', '.malware', '.infected', '.virus',
            '.trojan', '.backdoor', '.rootkit', '.keylog',
            
            # Extensiones de archivos compilados sospechosos
            '.o', '.so.bak', '.dll.bak', '.exe.bak', '.bin.bak',
            
            # Extensiones de scripts codificados o ofuscados
            '.b64', '.base64', '.encoded', '.obfuscated', '.packed',
            '.crypted', '.enc', '.crypt',
            
            # Extensiones de archivos de configuración modificados
            '.conf.bak', '.cfg.old', '.ini.save', '.config.tmp',
            
            # Extensiones específicas de herramientas de pentesting
            '.msf', '.rc', '.resource', '.exploit', '.payload',
            '.shellcode', '.asm', '.nasm',
            
            # Extensiones de archivos de volcado y dump
            '.dump', '.dmp', '.mem', '.core', '.crash',
            '.lsass', '.sam', '.system', '.security',
            
            # Extensiones de logs y rastros
            '.log.bak', '.access.old', '.error.tmp', '.audit.save',
            
            # Extensiones de archivos de red sospechosos
            '.pcap.bak', '.cap.old', '.tcpdump', '.wireshark',
            
            # Extensiones de archivos de base de datos comprometidas
            '.sql.bak', '.db.tmp', '.sqlite.old', '.mysql.save',
            
            # Extensiones de archivos web sospechosos
            '.php.bak', '.jsp.old', '.asp.tmp', '.aspx.save',
            '.cgi.bak', '.pl.old', '.py.tmp',
            
            # Extensiones de archivos de certificados comprometidos
            '.pem.bak', '.key.old', '.crt.tmp', '.p12.save',
            '.pfx.bak', '.jks.old',
            
            # Extensiones de archivos de sistema comprometidos
            '.passwd.bak', '.shadow.old', '.sudoers.tmp',
            '.hosts.save', '.fstab.bak',
            
            # Extensiones de archivos de herramientas específicas
            '.nmap.bak', '.masscan.old', '.nikto.tmp',
            '.dirb.save', '.gobuster.bak', '.sqlmap.old'
        }
    
    def analizar_cambio(self, metadatos_anteriores: Optional[MetadatosArchivoAvanzados], 
                       metadatos_actuales: Optional[MetadatosArchivoAvanzados],
                       tipo_cambio: TipoCambio) -> List[TipoAmenazaFIM]:
        """
        Analiza un cambio para detectar amenazas.
        
        Args:
            metadatos_anteriores: Metadatos anteriores del archivo
            metadatos_actuales: Metadatos actuales del archivo
            tipo_cambio: Tipo de cambio detectado
            
        Returns:
            Lista de amenazas detectadas
        """
        amenazas = []
        
        # Determinar archivo a analizar
        metadatos = metadatos_actuales or metadatos_anteriores
        if not metadatos:
            return amenazas
        
        # Análisis por tipo de cambio
        if tipo_cambio == TipoCambio.CREADO and metadatos_actuales:
            amenazas.extend(self._analizar_archivo_nuevo(metadatos_actuales))
        
        elif tipo_cambio == TipoCambio.MODIFICADO and metadatos_anteriores and metadatos_actuales:
            amenazas.extend(self._analizar_archivo_modificado(metadatos_anteriores, metadatos_actuales))
        
        elif tipo_cambio == TipoCambio.ELIMINADO and metadatos_anteriores:
            amenazas.extend(self._analizar_archivo_eliminado(metadatos_anteriores))
        
        elif tipo_cambio == TipoCambio.PERMISOS_MODIFICADOS and metadatos_anteriores and metadatos_actuales:
            amenazas.extend(self._analizar_cambio_permisos(metadatos_anteriores, metadatos_actuales))
        
        # Análisis general de seguridad
        amenazas.extend(self._analizar_seguridad_general(metadatos))
        
        return list(set(amenazas))  # Eliminar duplicados
    
    def _analizar_archivo_nuevo(self, metadatos: MetadatosArchivoAvanzados) -> List[TipoAmenazaFIM]:
        """Analiza un archivo recién creado."""
        amenazas = []
        
        # Verificar si es ejecutable en ubicación sospechosa
        if metadatos.tipo_archivo == TipoArchivo.EJECUTABLE:
            if any(sospechoso in metadatos.ruta.lower() for sospechoso in self.patrones_malware['directorios_sospechosos']):
                amenazas.append(TipoAmenazaFIM.EJECUTABLE_SOSPECHOSO)
        
        # Verificar nombres sospechosos
        nombre_lower = metadatos.nombre_archivo.lower()
        if any(patron in nombre_lower for patron in self.patrones_malware['nombres_sospechosos']):
            amenazas.append(TipoAmenazaFIM.MALWARE_DETECTADO)
        
        # Verificar extensiones sospechosas
        if metadatos.extension in self.extensiones_sospechosas:
            amenazas.append(TipoAmenazaFIM.ARCHIVO_SISTEMA_MODIFICADO)
        
        # Archivos ocultos en ubicaciones críticas
        if metadatos.nombre_archivo.startswith('.') and any(critica in metadatos.ruta for critica in self.rutas_criticas):
            amenazas.append(TipoAmenazaFIM.BACKDOOR_POTENCIAL)
        
        return amenazas
    
    def _analizar_archivo_modificado(self, anteriores: MetadatosArchivoAvanzados, 
                                   actuales: MetadatosArchivoAvanzados) -> List[TipoAmenazaFIM]:
        """Analiza un archivo modificado."""
        amenazas = []
        
        # Verificar si es archivo crítico del sistema
        if any(critica in actuales.ruta for critica in self.rutas_criticas):
            amenazas.append(TipoAmenazaFIM.ARCHIVO_SISTEMA_MODIFICADO)
        
        # Cambios de tamaño anormales
        cambio_tamaño = abs(actuales.tamaño_bytes - anteriores.tamaño_bytes)
        if cambio_tamaño > self.tamaño_maximo_normal:
            amenazas.append(TipoAmenazaFIM.TAMAÑO_ANORMAL)
        
        # Cambio de tipo de archivo (posible inyección)
        if actuales.tipo_archivo != anteriores.tipo_archivo:
            amenazas.append(TipoAmenazaFIM.INYECCION_CODIGO)
        
        return amenazas
    
    def _analizar_archivo_eliminado(self, anteriores: MetadatosArchivoAvanzados) -> List[TipoAmenazaFIM]:
        """Analiza un archivo eliminado."""
        amenazas = []
        
        # Archivo crítico eliminado
        if any(critica in anteriores.ruta for critica in self.rutas_criticas):
            amenazas.append(TipoAmenazaFIM.ARCHIVO_CRITICO_ELIMINADO)
        
        # Ejecutable del sistema eliminado
        if anteriores.tipo_archivo == TipoArchivo.EJECUTABLE and anteriores.nivel_criticidad == NivelCriticidadFIM.CRITICO:
            amenazas.append(TipoAmenazaFIM.ROOTKIT_DETECTADO)
        
        return amenazas
    
    def _analizar_cambio_permisos(self, anteriores: MetadatosArchivoAvanzados, 
                                 actuales: MetadatosArchivoAvanzados) -> List[TipoAmenazaFIM]:
        """Analiza cambios de permisos."""
        amenazas = []
        
        # Escalación de privilegios (agregó SUID/SGID)
        if 's' in actuales.permisos_texto and 's' not in anteriores.permisos_texto:
            amenazas.append(TipoAmenazaFIM.ESCALACION_PRIVILEGIOS)
        
        # Permisos peligrosos (777)
        if actuales.permisos_octal == '777':
            amenazas.append(TipoAmenazaFIM.PERMISOS_PELIGROSOS)
        
        # Cambio de propietario a root
        if actuales.propietario_uid == 0 and anteriores.propietario_uid != 0:
            amenazas.append(TipoAmenazaFIM.ESCALACION_PRIVILEGIOS)
        
        return amenazas
    
    def _analizar_seguridad_general(self, metadatos: MetadatosArchivoAvanzados) -> List[TipoAmenazaFIM]:
        """Análisis general de seguridad."""
        amenazas = []
        
        # Archivos con SUID/SGID en ubicaciones inusuales
        if 's' in metadatos.permisos_texto and not any(
            estandar in metadatos.ruta for estandar in ['/bin/', '/sbin/', '/usr/bin/', '/usr/sbin/']
        ):
            amenazas.append(TipoAmenazaFIM.ESCALACION_PRIVILEGIOS)
        
        # Ejecutables en directorios de escritura mundial
        if metadatos.tipo_archivo == TipoArchivo.EJECUTABLE and any(
            temp in metadatos.ruta for temp in ['/tmp/', '/var/tmp/', '/dev/shm/']
        ):
            amenazas.append(TipoAmenazaFIM.EJECUTABLE_SOSPECHOSO)
        
        return amenazas


class FIMAvanzado:
    """Sistema avanzado de Monitoreo de Integridad de Archivos."""
    
    def __init__(self, siem: SIEM):
        """
        Inicializa el sistema FIM avanzado.
        
        Args:
            siem: Instancia del SIEM para registro de eventos
        """
        self.siem = siem
        self.logger = configurar_logger_modulo("fim")
        
        # Componentes del sistema
        self.analizador_amenazas = AnalizadorAmenazasFIM()
        
        # Base de datos de archivos
        self.base_datos: Dict[str, MetadatosArchivoAvanzados] = {}
        
        # Estado del sistema
        self.estado_monitoreo = EstadoMonitoreo.INACTIVO
        self.hilo_monitoreo: Optional[threading.Thread] = None
        
        # Configuración
        self.archivo_base_datos = self._determinar_ruta_base_datos()
        self.rutas_monitoreadas: Set[str] = set()
        self.rutas_excluidas: Set[str] = set()
        self.intervalo_verificacion = 300  # 5 minutos
        
        # Alertas y estadísticas
        self.alertas_generadas: deque = deque(maxlen=10000)
        self.estadisticas = {
            "inicio_monitoreo": None,
            "archivos_monitoreados": 0,
            "verificaciones_realizadas": 0,
            "cambios_detectados": 0,
            "amenazas_detectadas": 0,
            "falsos_positivos": 0,
            "tiempo_ultima_verificacion": None,
            "tiempo_activo_segundos": 0
        }
        
        # Cargar configuración por defecto
        self._cargar_configuracion_por_defecto()
        
        # Cargar base de datos existente
        self._cargar_base_datos()
        
        self.logger.info("FIM avanzado inicializado correctamente")
        self.siem.registrar_evento(
            TipoEvento.SISTEMA_INICIADO,
            "Sistema FIM avanzado inicializado",
            {
                'archivo_base_datos': self.archivo_base_datos,
                'rutas_monitoreadas': len(self.rutas_monitoreadas),
                'archivos_en_base_datos': len(self.base_datos)
            },
            "MEDIO"
        )
    
    def _determinar_ruta_base_datos(self) -> str:
        """Determina la ruta del archivo de base de datos FIM."""
        try:
            rutas_sistema = obtener_rutas_sistema()
            ruta_sistema = rutas_sistema['directorio_config'] + "/fim_base_datos.json"
            crear_ruta_segura(ruta_sistema)
            
            if os.access(Path(ruta_sistema).parent, os.W_OK):
                return ruta_sistema
        except Exception:
            pass
        
        # Usar directorio local si no se puede usar el del sistema
        return str(Path.cwd() / "fim_base_datos.json")
    
    def _cargar_configuracion_por_defecto(self):
        """Carga la configuración por defecto del FIM."""
        # Rutas críticas del sistema a monitorear (expandido para Kali Linux)
        rutas_criticas = [
            # Archivos críticos de autenticación y usuarios
            '/etc/passwd', '/etc/shadow', '/etc/group', '/etc/gshadow',
            '/etc/sudoers', '/etc/sudoers.d/', '/etc/security/',
            '/etc/pam.d/', '/etc/login.defs', '/etc/default/useradd',
            
            # Configuraciones de red críticas
            '/etc/hosts', '/etc/hosts.allow', '/etc/hosts.deny',
            '/etc/resolv.conf', '/etc/nsswitch.conf', '/etc/network/',
            '/etc/NetworkManager/', '/etc/systemd/network/',
            '/etc/netplan/', '/etc/iptables/', '/etc/ufw/',
            
            # Servicios y demonios críticos
            '/etc/crontab', '/etc/cron.d/', '/etc/cron.daily/',
            '/etc/cron.hourly/', '/etc/cron.monthly/', '/etc/cron.weekly/',
            '/var/spool/cron/', '/etc/systemd/', '/etc/init.d/',
            '/etc/rc.d/', '/etc/rc.local', '/etc/rc.conf',
            '/lib/systemd/', '/usr/lib/systemd/',
            
            # SSH y servicios remotos
            '/etc/ssh/', '/etc/ssh/sshd_config', '/etc/ssh/ssh_config',
            '/root/.ssh/', '/home/*/.ssh/', '/etc/ssl/',
            '/etc/pki/', '/usr/share/ca-certificates/',
            
            # Configuraciones de sistema críticas
            '/etc/fstab', '/etc/mtab', '/etc/modules',
            '/etc/modprobe.d/', '/etc/sysctl.conf', '/etc/sysctl.d/',
            '/etc/kernel/', '/etc/initramfs-tools/', '/etc/grub.d/',
            '/boot/', '/boot/grub/', '/boot/efi/',
            
            # Binarios ejecutables críticos
            '/bin/', '/sbin/', '/usr/bin/', '/usr/sbin/',
            '/usr/local/bin/', '/usr/local/sbin/', '/opt/bin/',
            
            # Bibliotecas críticas del sistema
            '/lib/', '/lib64/', '/usr/lib/', '/usr/lib64/',
            '/usr/local/lib/', '/lib/x86_64-linux-gnu/',
            '/usr/lib/x86_64-linux-gnu/',
            
            # Directorios de configuración críticos
            '/etc/apache2/', '/etc/nginx/', '/etc/httpd/',
            '/etc/mysql/', '/etc/postgresql/', '/etc/redis/',
            '/etc/mongodb/', '/etc/docker/', '/etc/kubernetes/',
            
            # Configuraciones específicas de Kali Linux
            '/etc/apt/', '/etc/dpkg/', '/var/lib/dpkg/',
            '/etc/update-motd.d/', '/etc/profile', '/etc/profile.d/',
            '/etc/bash.bashrc', '/etc/environment', '/etc/locale.conf',
            '/etc/timezone', '/etc/localtime',
            
            # Herramientas de pentesting y seguridad (Kali específico)
            '/usr/share/metasploit-framework/',
            '/usr/share/wordlists/', '/usr/share/nmap/',
            '/usr/share/burpsuite/', '/usr/share/sqlmap/',
            '/usr/share/aircrack-ng/', '/usr/share/john/',
            '/usr/share/hashcat/', '/usr/share/hydra/',
            '/usr/share/nikto/', '/usr/share/dirb/',
            '/usr/share/dirbuster/', '/usr/share/gobuster/',
            '/usr/share/wfuzz/', '/usr/share/amass/',
            '/usr/share/recon-ng/', '/usr/share/theharvester/',
            
            # Configuraciones de servicios de pentesting
            '/etc/beef-xss/', '/etc/armitage/', '/etc/msfconsole/',
            '/root/.msf4/', '/root/.beef/', '/root/.recon-ng/',
            
            # Configuraciones de proxy y herramientas web
            '/etc/proxychains.conf', '/etc/tor/', '/etc/i2p/',
            '/etc/privoxy/', '/etc/polipo/',
            
            # Bases de datos y archivos de configuración de herramientas
            '/var/lib/mlocate/', '/var/lib/updatedb/',
            '/usr/share/exploitdb/', '/usr/share/payloads/',
            '/usr/share/SET/', '/usr/share/social-engineer-toolkit/',
            
            # Configuraciones de monitoreo y logging
            '/etc/rsyslog.conf', '/etc/rsyslog.d/', '/etc/logrotate.conf',
            '/etc/logrotate.d/', '/etc/audit/', '/etc/auditd/',
            '/var/log/auth.log', '/var/log/secure', '/var/log/messages',
            '/var/log/syslog', '/var/log/kern.log',
            
            # Configuraciones de firewall y seguridad de red
            '/etc/fail2ban/', '/etc/psad/', '/etc/snort/',
            '/etc/suricata/', '/etc/bro/', '/etc/zeek/',
            '/etc/aide/', '/etc/tripwire/', '/etc/samhain/',
            
            # Configuraciones de virtualización y contenedores
            '/etc/libvirt/', '/etc/qemu/', '/etc/vbox/',
            '/etc/vmware/', '/var/lib/docker/', '/etc/containerd/',
            
            # Configuraciones de desarrollo y compilación
            '/etc/ld.so.conf', '/etc/ld.so.conf.d/',
            '/usr/include/', '/usr/src/', '/lib/modules/',
            
            # Configuraciones específicas de servicios críticos
            '/etc/dnsmasq.conf', '/etc/dhcp/', '/etc/bind/',
            '/etc/postfix/', '/etc/dovecot/', '/etc/exim4/',
            '/etc/samba/', '/etc/cups/', '/etc/avahi/',
            
            # Directorios de usuario críticos
            '/root/', '/home/', '/etc/skel/',
            
            # Configuraciones de X11 y display
            '/etc/X11/', '/usr/share/X11/', '/etc/gdm3/',
            '/etc/lightdm/', '/etc/sddm.conf',
            
            # Configuraciones de kernels y módulos
            '/etc/modules-load.d/', '/etc/modprobe.d/',
            '/etc/udev/', '/lib/udev/', '/usr/lib/udev/',
            
            # Archivos de configuración de hardware
            '/etc/acpi/', '/etc/alsa/', '/etc/pulse/',
            '/etc/bluetooth/', '/etc/cups/',
            
            # Configuraciones de seguridad adicionales
            '/etc/apparmor/', '/etc/apparmor.d/',
            '/etc/selinux/', '/etc/grsecurity/',
            '/etc/pax/', '/etc/hardening/',
            
            # Herramientas forenses y análisis (Kali específico)
            '/usr/share/autopsy/', '/usr/share/sleuthkit/',
            '/usr/share/volatility/', '/usr/share/binwalk/',
            '/usr/share/foremost/', '/usr/share/scalpel/',
            '/usr/share/ddrescue/', '/usr/share/testdisk/',
            
            # Herramientas de ingeniería inversa
            '/usr/share/radare2/', '/usr/share/ghidra/',
            '/usr/share/ida/', '/usr/share/gdb/',
            '/usr/share/ollydbg/', '/usr/share/x64dbg/',
            
            # Herramientas de análisis de malware
            '/usr/share/yara/', '/usr/share/clamav/',
            '/usr/share/virustotal/', '/usr/share/viper/',
            '/usr/share/malware-traffic-analysis/',
            
            # Configuraciones de bases de datos especializadas
            '/var/lib/locate/', '/var/lib/mlocate/',
            '/usr/share/nmap/scripts/', '/usr/share/nse/',
            '/usr/share/masscan/', '/usr/share/zmap/'
        ]
        
        # Agregar rutas que existan
        for ruta in rutas_criticas:
            if os.path.exists(ruta):
                self.rutas_monitoreadas.add(os.path.abspath(ruta))
        
        # Rutas a excluir por defecto (expandido para evitar falsos positivos)
        rutas_excluidas = [
            # Directorios del sistema que cambian constantemente
            '/proc/', '/sys/', '/dev/', '/run/', '/tmp/', '/var/tmp/',
            
            # Logs y cachés que cambian frecuentemente
            '/var/log/', '/var/cache/', '/var/spool/', '/var/run/',
            '/var/lock/', '/var/backups/', '/var/crash/',
            
            # Medios removibles y montajes temporales
            '/media/', '/mnt/', '/lost+found', '/cdrom/',
            '/floppy/', '/auto/', '/misc/',
            
            # Directorios de usuario que pueden generar muchos cambios
            '/home/*/.cache/', '/home/*/.local/share/Trash/',
            '/home/*/.mozilla/firefox/*/Cache/',
            '/home/*/.chrome/Default/Cache/',
            '/home/*/.config/google-chrome/Default/Cache/',
            '/root/.cache/', '/root/.local/share/Trash/',
            
            # Archivos temporales del sistema
            '/var/tmp/', '/usr/tmp/', '/var/spool/cups/',
            '/var/lib/dhcp/', '/var/lib/NetworkManager/',
            
            # Archivos de swap y memoria virtual
            '/swap.img', '/swapfile', '/hiberfil.sys',
            '/pagefile.sys', '/var/swap/',
            
            # Directorios de compilación temporal
            '/usr/src/linux*/.tmp_versions/',
            '/usr/src/*/.git/', '/tmp/.*/',
            
            # Cachés de paquetes y actualizaciones
            '/var/lib/apt/lists/', '/var/cache/apt/',
            '/var/cache/debconf/', '/var/lib/dpkg/updates/',
            
            # Archivos de sesión y PID
            '/var/run/user/', '/run/user/', '/run/systemd/',
            '/run/udev/', '/var/lib/systemd/',
            
            # Directorios de impresión temporal
            '/var/spool/cups-pdf/', '/var/spool/lpd/',
            
            # Archivos de base de datos que cambian constantemente
            '/var/lib/mysql/ib_logfile*', '/var/lib/postgresql/*/main/pg_xlog/',
            
            # Archivos de logs rotativos específicos
            '/var/log/*.old', '/var/log/*.gz', '/var/log/*.[0-9]*',
            
            # Directorios de herramientas que generan archivos temporales
            '/tmp/metasploit*/', '/tmp/msfvenom*/', '/tmp/beef*/',
            '/tmp/sqlmap*/', '/tmp/nikto*/', '/tmp/nmap*/',
            
            # Cachés específicos de Kali
            '/var/lib/locate/', '/var/lib/mlocate/',
            '/usr/share/exploitdb/.git/', '/usr/share/wordlists/.git/',
            
            # Archivos de configuración temporal de herramientas
            '/root/.msf4/logs/', '/root/.msf4/loot/',
            '/root/.beef/logs/', '/root/.sqlmap/output/',
        ]
        
        self.rutas_excluidas.update(rutas_excluidas)
        
        self.logger.info(f"Configuración cargada: {len(self.rutas_monitoreadas)} rutas monitoreadas")
    
    def _cargar_base_datos(self):
        """Carga la base de datos de archivos desde el archivo."""
        try:
            if os.path.exists(self.archivo_base_datos):
                with open(self.archivo_base_datos, 'r', encoding='utf-8') as archivo:
                    datos = json.load(archivo)
                    
                    for ruta, datos_archivo in datos.items():
                        metadatos = MetadatosArchivoAvanzados(
                            ruta=ruta,
                            nombre_archivo="",
                            extension="",
                            tipo_archivo=TipoArchivo.DESCONOCIDO,
                            tamaño_bytes=0,
                            hash_md5="", hash_sha1="", hash_sha256="", hash_sha512="",
                            permisos_octal="", permisos_texto="",
                            propietario_uid=0, propietario_nombre="",
                            grupo_gid=0, grupo_nombre="",
                            fecha_creacion=datetime.now(),
                            fecha_modificacion=datetime.now(),
                            fecha_acceso=datetime.now(),
                            fecha_cambio_metadatos=datetime.now(),
                            timestamp_registro=datetime.now()
                        )
                        
                        # Cargar datos desde diccionario
                        metadatos.__dict__.update(datos_archivo)
                        
                        # Convertir fechas string a datetime
                        for campo_fecha in ['fecha_creacion', 'fecha_modificacion', 'fecha_acceso', 
                                          'fecha_cambio_metadatos', 'timestamp_registro']:
                            if isinstance(getattr(metadatos, campo_fecha), str):
                                try:
                                    setattr(metadatos, campo_fecha, datetime.fromisoformat(getattr(metadatos, campo_fecha)))
                                except Exception:
                                    setattr(metadatos, campo_fecha, datetime.now())
                        
                        self.base_datos[ruta] = metadatos
                
                self.estadisticas["archivos_monitoreados"] = len(self.base_datos)
                self.logger.info(f"Base de datos FIM cargada: {len(self.base_datos)} archivos")
        
        except Exception as e:
            self.logger.warning(f"Error cargando base de datos FIM: {e}")
    
    def _guardar_base_datos(self):
        """Guarda la base de datos de archivos al archivo."""
        try:
            crear_ruta_segura(self.archivo_base_datos)
            
            datos = {}
            for ruta, metadatos in self.base_datos.items():
                datos[ruta] = metadatos.to_dict()
            
            with open(self.archivo_base_datos, 'w', encoding='utf-8') as archivo:
                json.dump(datos, archivo, ensure_ascii=False, indent=2)
            
            self.logger.debug("Base de datos FIM guardada correctamente")
        
        except Exception as e:
            self.logger.error(f"Error guardando base de datos FIM: {e}")
    
    def crear_baseline_avanzada(self, rutas_adicionales: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Crea una línea base avanzada de integridad.
        
        Args:
            rutas_adicionales: Rutas adicionales a incluir en la línea base
            
        Returns:
            Dict[str, Any]: Estadísticas de la creación de línea base
        """
        self.logger.info("Iniciando creación de línea base FIM avanzada")
        
        inicio_tiempo = time.time()
        archivos_procesados = 0
        errores = 0
        tipos_archivo = defaultdict(int)
        
        # Agregar rutas adicionales si se proporcionan
        if rutas_adicionales:
            for ruta in rutas_adicionales:
                if os.path.exists(ruta):
                    self.rutas_monitoreadas.add(os.path.abspath(ruta))
        
        # Procesar todas las rutas monitoreadas
        for ruta in self.rutas_monitoreadas.copy():
            try:
                if os.path.isfile(ruta):
                    # Es un archivo individual
                    if validar_permisos_lectura(ruta):
                        metadatos = MetadatosArchivoAvanzados.desde_archivo(ruta)
                        self.base_datos[ruta] = metadatos
                        tipos_archivo[metadatos.tipo_archivo.value] += 1
                        archivos_procesados += 1
                    else:
                        self.logger.warning(f"Sin permisos de lectura: {ruta}")
                        errores += 1
                
                elif os.path.isdir(ruta):
                    # Es un directorio
                    archivos = listar_archivos_recursivo(ruta)
                    
                    for archivo in archivos:
                        ruta_archivo = str(archivo)
                        
                        # Verificar si está en rutas excluidas
                        if any(exclusion in ruta_archivo for exclusion in self.rutas_excluidas):
                            continue
                        
                        try:
                            if validar_permisos_lectura(ruta_archivo):
                                metadatos = MetadatosArchivoAvanzados.desde_archivo(ruta_archivo)
                                self.base_datos[ruta_archivo] = metadatos
                                tipos_archivo[metadatos.tipo_archivo.value] += 1
                                archivos_procesados += 1
                            else:
                                errores += 1
                        
                        except Exception as e:
                            self.logger.warning(f"Error procesando archivo {ruta_archivo}: {e}")
                            errores += 1
                        
                        # Log de progreso cada 1000 archivos
                        if archivos_procesados % 1000 == 0:
                            self.logger.info(f"Progreso línea base: {archivos_procesados} archivos procesados")
            
            except Exception as e:
                self.logger.error(f"Error procesando ruta {ruta}: {e}")
                errores += 1
        
        # Guardar base de datos
        self._guardar_base_datos()
        
        tiempo_total = time.time() - inicio_tiempo
        
        estadisticas = {
            'archivos_procesados': archivos_procesados,
            'errores': errores,
            'tiempo_total': tiempo_total,
            'rutas_monitoreadas': len(self.rutas_monitoreadas),
            'tipos_archivo': dict(tipos_archivo),
            'timestamp': datetime.now().isoformat()
        }
        
        self.estadisticas["archivos_monitoreados"] = archivos_procesados
        
        self.siem.registrar_evento(
            TipoEvento.SISTEMA_INICIADO,
            "Línea base FIM avanzada creada exitosamente",
            estadisticas,
            "MEDIO"
        )
        
        self.logger.info(f"Línea base FIM avanzada creada: {archivos_procesados} archivos en {tiempo_total:.2f}s")
        
        return estadisticas
    
    def verificar_integridad_completa(self) -> List[AlertaFIM]:
        """
        Verifica la integridad completa de archivos monitoreados.
        
        Returns:
            List[AlertaFIM]: Lista de alertas generadas
        """
        self.logger.info("Iniciando verificación de integridad completa")
        
        alertas_generadas = []
        archivos_verificados = 0
        
        # Verificar archivos existentes en la base de datos
        for ruta, metadatos_originales in list(self.base_datos.items()):
            try:
                if os.path.exists(ruta):
                    # El archivo aún existe, verificar cambios
                    metadatos_actuales = MetadatosArchivoAvanzados.desde_archivo(ruta)
                    cambios = metadatos_originales.comparar_con(metadatos_actuales)
                    
                    if cambios:
                        # Analizar amenazas
                        for tipo_cambio in cambios:
                            amenazas = self.analizador_amenazas.analizar_cambio(
                                metadatos_originales, metadatos_actuales, tipo_cambio
                            )
                            
                            # Crear alerta
                            alerta = AlertaFIM(
                                id_alerta="",
                                tipo_cambio=tipo_cambio,
                                tipo_amenaza=amenazas[0] if amenazas else None,
                                archivo_afectado=ruta,
                                descripcion=f"Archivo {tipo_cambio.value}: {ruta}",
                                nivel_criticidad=metadatos_actuales.nivel_criticidad,
                                metadatos_anteriores=metadatos_originales,
                                metadatos_actuales=metadatos_actuales,
                                diferencias_detectadas=[cambio.value for cambio in cambios],
                                evidencia={
                                    "amenazas_detectadas": [a.value for a in amenazas],
                                    "hash_anterior": metadatos_originales.hash_sha256[:16],
                                    "hash_actual": metadatos_actuales.hash_sha256[:16],
                                    "tamaño_anterior": metadatos_originales.tamaño_bytes,
                                    "tamaño_actual": metadatos_actuales.tamaño_bytes
                                },
                                timestamp=datetime.now()
                            )
                            alertas_generadas.append(alerta)
                        
                        # Actualizar metadatos en base de datos
                        self.base_datos[ruta] = metadatos_actuales
                
                else:
                    # El archivo fue eliminado
                    amenazas = self.analizador_amenazas.analizar_cambio(
                        metadatos_originales, None, TipoCambio.ELIMINADO
                    )
                    
                    alerta = AlertaFIM(
                        id_alerta="",
                        tipo_cambio=TipoCambio.ELIMINADO,
                        tipo_amenaza=amenazas[0] if amenazas else None,
                        archivo_afectado=ruta,
                        descripcion=f"Archivo eliminado: {ruta}",
                        nivel_criticidad=metadatos_originales.nivel_criticidad,
                        metadatos_anteriores=metadatos_originales,
                        metadatos_actuales=None,
                        diferencias_detectadas=["archivo_eliminado"],
                        evidencia={
                            "amenazas_detectadas": [a.value for a in amenazas],
                            "hash_original": metadatos_originales.hash_sha256[:16],
                            "tamaño_original": metadatos_originales.tamaño_bytes
                        },
                        timestamp=datetime.now()
                    )
                    alertas_generadas.append(alerta)
                    
                    # Remover de la base de datos
                    del self.base_datos[ruta]
                
                archivos_verificados += 1
            
            except Exception as e:
                self.logger.warning(f"Error verificando archivo {ruta}: {e}")
        
        # Guardar cambios en la base de datos
        if alertas_generadas:
            self._guardar_base_datos()
        
        # Actualizar estadísticas
        self.estadisticas["cambios_detectados"] += len(alertas_generadas)
        self.estadisticas["amenazas_detectadas"] += sum(1 for a in alertas_generadas if a.tipo_amenaza)
        
        self.logger.info(f"Verificación FIM completada: {archivos_verificados} archivos, "
                        f"{len(alertas_generadas)} alertas generadas")
        
        return alertas_generadas
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas completas del FIM."""
        return {
            **self.estadisticas,
            "estado_monitoreo": self.estado_monitoreo.value,
            "archivos_en_base_datos": len(self.base_datos),
            "rutas_monitoreadas_total": len(self.rutas_monitoreadas),
            "rutas_excluidas_total": len(self.rutas_excluidas),
            "alertas_pendientes": len(self.alertas_generadas)
        }


# Alias para compatibilidad
FIM = FIMAvanzado
