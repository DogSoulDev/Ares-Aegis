#!/usr/bin/env python3
"""
Creado por DogSoulDev (https://github.com/DogSoulDev)
Todos los derechos reservados. Este código es propietario y confidencial.

Gestor de Cuarentena Avanzado - Ares Aegis
Sistema integral de cuarentena con análisis forense y restauración segura
"""

import os
import json
import shutil
import hashlib
import time
import threading
import zipfile
import tarfile
import subprocess
import mimetypes
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Union, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum
import tempfile
import stat

from .siem import SIEM, TipoEvento
from ..utils.validaciones import validar_ruta_archivo, validar_permisos_lectura
from ..utils.ayuda_rutas import crear_ruta_segura, obtener_rutas_sistema
from ..utils.ayuda_logging import configurar_logger_modulo


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
    ADWARE = "adware"
    SPYWARE = "spyware"
    RANSOMWARE = "ransomware"
    BOTNET = "botnet"
    EXPLOIT = "exploit"
    PHISHING = "phishing"
    SCRIPT_MALICIOSO = "script_malicioso"
    ARCHIVO_SOSPECHOSO = "archivo_sospechoso"
    CONFIGURACION_COMPROMETIDA = "configuracion_comprometida"
    FIRMA_INVALIDA = "firma_invalida"
    COMPORTAMIENTO_ANOMALO = "comportamiento_anomalo"
    DESCONOCIDO = "desconocido"


class NivelRiesgoCuarentena(Enum):
    """Niveles de riesgo para archivos en cuarentena."""
    CRITICO = "CRITICO"
    ALTO = "ALTO"
    MEDIO = "MEDIO"
    BAJO = "BAJO"
    MINIMO = "MINIMO"


class AccionCuarentena(Enum):
    """Acciones realizadas sobre archivos en cuarentena."""
    CUARENTENADO = "cuarentenado"
    ANALIZADO = "analizado"
    RESTAURADO = "restaurado"
    ELIMINADO = "eliminado"
    VALIDADO = "validado"
    MARCADO_SEGURO = "marcado_seguro"
    MARCADO_MALICIOSO = "marcado_malicioso"
    COPIA_SEGURIDAD = "copia_seguridad"
    ENVIADO_ANALISIS = "enviado_analisis"
    DESCOMPRIMIDO = "descomprimido"


@dataclass
class MetadatosCuarentena:
    """Metadatos completos de un archivo en cuarentena."""
    archivo_id: str
    ruta_original: str
    ruta_cuarentena: str
    nombre_original: str
    extension: str
    tamaño_bytes: int
    hash_md5: str
    hash_sha1: str
    hash_sha256: str
    hash_sha512: str
    tipo_mime: str
    encoding: Optional[str]
    timestamp_cuarentena: datetime
    timestamp_ultimo_analisis: Optional[datetime]
    estado: EstadoCuarentena
    tipo_amenaza: Optional[TipoAmenazaCuarentena]
    nivel_riesgo: NivelRiesgoCuarentena
    origen_deteccion: str  # Módulo que detectó la amenaza
    razon_cuarentena: str
    permisos_originales: str
    propietario_original: str
    grupo_original: str
    resultado_analisis: Dict[str, Any] = field(default_factory=dict)
    acciones_realizadas: List[str] = field(default_factory=list)
    intentos_restauracion: int = 0
    comentarios: List[str] = field(default_factory=list)
    archivos_relacionados: List[str] = field(default_factory=list)
    es_falso_positivo: bool = False
    requiere_atencion_manual: bool = False
    
    def __post_init__(self):
        """Post-procesamiento de metadatos."""
        if not self.archivo_id:
            datos = f"{self.ruta_original}_{self.timestamp_cuarentena.timestamp()}"
            self.archivo_id = hashlib.sha256(datos.encode()).hexdigest()[:16]
        
        if isinstance(self.estado, str):
            self.estado = EstadoCuarentena(self.estado)
        
        if isinstance(self.nivel_riesgo, str):
            self.nivel_riesgo = NivelRiesgoCuarentena(self.nivel_riesgo)
        
        if isinstance(self.tipo_amenaza, str) and self.tipo_amenaza:
            self.tipo_amenaza = TipoAmenazaCuarentena(self.tipo_amenaza)
    
    @property
    def dias_en_cuarentena(self) -> int:
        """Calcula los días que lleva el archivo en cuarentena."""
        return (datetime.now() - self.timestamp_cuarentena).days
    
    @property
    def riesgo_numerico(self) -> int:
        """Convierte el nivel de riesgo a valor numérico."""
        return {
            NivelRiesgoCuarentena.CRITICO: 5,
            NivelRiesgoCuarentena.ALTO: 4,
            NivelRiesgoCuarentena.MEDIO: 3,
            NivelRiesgoCuarentena.BAJO: 2,
            NivelRiesgoCuarentena.MINIMO: 1
        }.get(self.nivel_riesgo, 0)
    
    def agregar_accion(self, accion: AccionCuarentena, detalles: str = ""):
        """Agrega una acción realizada al historial."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        entrada = f"[{timestamp}] {accion.value}"
        if detalles:
            entrada += f": {detalles}"
        self.acciones_realizadas.append(entrada)
    
    def agregar_comentario(self, comentario: str, usuario: str = "sistema"):
        """Agrega un comentario al archivo en cuarentena."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        entrada = f"[{timestamp}] {usuario}: {comentario}"
        self.comentarios.append(entrada)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte metadatos a diccionario."""
        return {
            'archivo_id': self.archivo_id,
            'ruta_original': self.ruta_original,
            'ruta_cuarentena': self.ruta_cuarentena,
            'nombre_original': self.nombre_original,
            'extension': self.extension,
            'tamaño_bytes': self.tamaño_bytes,
            'hash_md5': self.hash_md5,
            'hash_sha1': self.hash_sha1,
            'hash_sha256': self.hash_sha256,
            'hash_sha512': self.hash_sha512,
            'tipo_mime': self.tipo_mime,
            'encoding': self.encoding,
            'timestamp_cuarentena': self.timestamp_cuarentena.isoformat(),
            'timestamp_ultimo_analisis': self.timestamp_ultimo_analisis.isoformat() if self.timestamp_ultimo_analisis else None,
            'estado': self.estado.value,
            'tipo_amenaza': self.tipo_amenaza.value if self.tipo_amenaza else None,
            'nivel_riesgo': self.nivel_riesgo.value,
            'origen_deteccion': self.origen_deteccion,
            'razon_cuarentena': self.razon_cuarentena,
            'permisos_originales': self.permisos_originales,
            'propietario_original': self.propietario_original,
            'grupo_original': self.grupo_original,
            'resultado_analisis': self.resultado_analisis,
            'acciones_realizadas': self.acciones_realizadas,
            'intentos_restauracion': self.intentos_restauracion,
            'comentarios': self.comentarios,
            'archivos_relacionados': self.archivos_relacionados,
            'es_falso_positivo': self.es_falso_positivo,
            'requiere_atencion_manual': self.requiere_atencion_manual,
            'dias_en_cuarentena': self.dias_en_cuarentena,
            'riesgo_numerico': self.riesgo_numerico
        }


class AnalizadorForenseCuarentena:
    """Analizador forense para archivos en cuarentena."""
    
    def __init__(self):
        """Inicializa el analizador forense."""
        self.logger = configurar_logger_modulo("analizador_forense_cuarentena")
        
        # Herramientas de análisis disponibles
        self.herramientas_disponibles = self._verificar_herramientas()
        
        # Patrones de análisis
        self.patrones_malware = self._cargar_patrones_analisis()
        self.firmas_conocidas = self._cargar_firmas_conocidas()
        
        self.logger.info("Analizador forense de cuarentena inicializado")
    
    def _verificar_herramientas(self) -> Dict[str, bool]:
        """Verifica qué herramientas de análisis están disponibles."""
        herramientas = {
            'file': self._comando_disponible('file'),
            'strings': self._comando_disponible('strings'),
            'hexdump': self._comando_disponible('hexdump'),
            'xxd': self._comando_disponible('xxd'),
            'binwalk': self._comando_disponible('binwalk'),
            'foremost': self._comando_disponible('foremost'),
            'volatility': self._comando_disponible('volatility'),
            'yara': self._comando_disponible('yara'),
            'clamav': self._comando_disponible('clamscan'),
            'exiftool': self._comando_disponible('exiftool'),
            'strace': self._comando_disponible('strace'),
            'ltrace': self._comando_disponible('ltrace')
        }
        
        disponibles = sum(herramientas.values())
        self.logger.info(f"Herramientas de análisis disponibles: {disponibles}/{len(herramientas)}")
        
        return herramientas
    
    def _comando_disponible(self, comando: str) -> bool:
        """Verifica si un comando está disponible en el sistema."""
        try:
            subprocess.run(['which', comando], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def _cargar_patrones_analisis(self) -> Dict[str, Union[List[str], List[bytes]]]:
        """Carga patrones para análisis de malware."""
        return {
            'strings_sospechosos': [
                'eval(', 'exec(', 'system(', 'shell_exec(', 'passthru(',
                'base64_decode', 'gzinflate', 'str_rot13', 'chr(',
                '/bin/sh', 'bash -i', 'nc -e', 'python -c',
                'downloadstring', 'invoke-expression', 'bypass', 'hidden',
                'mimikatz', 'meterpreter', 'metasploit', 'payload',
                'shellcode', 'backdoor', 'keylogger', 'trojan'
            ],
            'extensiones_ejecutables': [
                '.exe', '.com', '.scr', '.pif', '.bat', '.cmd',
                '.vbs', '.js', '.jar', '.ps1', '.sh', '.py'
            ],
            'headers_maliciosos': [
                b'MZ',  # PE ejecutable
                b'\x7fELF',  # ELF ejecutable
                b'PK',  # ZIP/JAR
                b'\x1f\x8b',  # GZIP
                b'Rar!',  # RAR
                b'\x89PNG',  # PNG con posible steganografía
                b'\xff\xd8\xff'  # JPEG con posible steganografía
            ]
        }
    
    def _cargar_firmas_conocidas(self) -> Dict[str, str]:
        """Carga firmas conocidas de malware."""
        return {
            # Hashes conocidos de malware (ejemplos)
            'e2e7d3e3af6ed5c23e4e7b4f3e1d2a1b': 'Generic.Trojan',
            'a1b2c3d4e5f6789012345678901234567890abcd': 'Generic.Backdoor',
            'f1e2d3c4b5a6978564123098745612307896541230': 'Linux.Rootkit'
        }
    
    def analizar_archivo_completo(self, ruta_archivo: str, metadatos: MetadatosCuarentena) -> Dict[str, Any]:
        """
        Realiza un análisis forense completo del archivo.
        
        Args:
            ruta_archivo: Ruta al archivo en cuarentena
            metadatos: Metadatos del archivo
            
        Returns:
            Dict[str, Any]: Resultados del análisis forense
        """
        self.logger.info(f"Iniciando análisis forense completo: {metadatos.nombre_original}")
        
        resultado = {
            'timestamp_analisis': datetime.now().isoformat(),
            'archivo_analizado': metadatos.nombre_original,
            'hash_sha256': metadatos.hash_sha256,
            'analisis_basico': {},
            'analisis_strings': {},
            'analisis_headers': {},
            'analisis_herramientas': {},
            'detecciones': [],
            'nivel_amenaza': 'BAJO',
            'recomendaciones': [],
            'tiempo_analisis': 0
        }
        
        inicio_tiempo = time.time()
        
        try:
            # Análisis básico de archivo
            resultado['analisis_basico'] = self._analisis_basico(ruta_archivo, metadatos)
            
            # Análisis de strings sospechosos
            resultado['analisis_strings'] = self._analisis_strings(ruta_archivo)
            
            # Análisis de headers y estructura
            resultado['analisis_headers'] = self._analisis_headers(ruta_archivo)
            
            # Análisis con herramientas externas
            resultado['analisis_herramientas'] = self._analisis_herramientas_externas(ruta_archivo)
            
            # Verificación de firmas conocidas
            deteccion_firma = self._verificar_firmas_conocidas(metadatos.hash_sha256)
            if deteccion_firma:
                resultado['detecciones'].append({
                    'tipo': 'firma_conocida',
                    'descripcion': f"Hash conocido: {deteccion_firma}",
                    'severidad': 'ALTO'
                })
            
            # Evaluación del nivel de amenaza
            resultado['nivel_amenaza'] = self._evaluar_nivel_amenaza(resultado)
            
            # Generar recomendaciones
            resultado['recomendaciones'] = self._generar_recomendaciones(resultado, metadatos)
            
        except Exception as e:
            self.logger.error(f"Error en análisis forense: {e}")
            resultado['error'] = str(e)
        
        resultado['tiempo_analisis'] = time.time() - inicio_tiempo
        
        self.logger.info(f"Análisis forense completado en {resultado['tiempo_analisis']:.2f}s")
        
        return resultado
    
    def _analisis_basico(self, ruta_archivo: str, metadatos: MetadatosCuarentena) -> Dict[str, Any]:
        """Realiza análisis básico del archivo."""
        analisis = {
            'tamaño_archivo': metadatos.tamaño_bytes,
            'tipo_mime': metadatos.tipo_mime,
            'extension': metadatos.extension,
            'permisos_sospechosos': False,
            'tamaño_anormal': False,
            'nombre_sospechoso': False
        }
        
        # Verificar permisos sospechosos (ejecutable cuando no debería serlo)
        if metadatos.extension in ['.txt', '.doc', '.pdf', '.jpg', '.png']:
            if 'x' in metadatos.permisos_originales:
                analisis['permisos_sospechosos'] = True
        
        # Verificar tamaño anormal
        if metadatos.tamaño_bytes > 100 * 1024 * 1024:  # 100MB
            analisis['tamaño_anormal'] = True
        elif metadatos.tamaño_bytes == 0:
            analisis['tamaño_anormal'] = True
        
        # Verificar nombre sospechoso
        nombre_lower = metadatos.nombre_original.lower()
        strings_sospechosos = [patron for patron in self.patrones_malware['strings_sospechosos'][:10] if isinstance(patron, str)]
        if any(patron in nombre_lower for patron in strings_sospechosos):
            analisis['nombre_sospechoso'] = True
        
        return analisis
    
    def _analisis_strings(self, ruta_archivo: str) -> Dict[str, Any]:
        """Analiza strings en el archivo."""
        analisis = {
            'strings_sospechosos_encontrados': [],
            'urls_encontradas': [],
            'ips_encontradas': [],
            'comandos_sospechosos': [],
            'total_strings': 0
        }
        
        if not self.herramientas_disponibles.get('strings', False):
            return analisis
        
        try:
            # Ejecutar strings
            resultado = subprocess.run(
                ['strings', '-n', '4', ruta_archivo],
                capture_output=True, text=True, timeout=30
            )
            
            if resultado.returncode == 0:
                strings_encontrados = resultado.stdout.split('\n')
                analisis['total_strings'] = len(strings_encontrados)
                
                # Buscar patrones sospechosos
                for string in strings_encontrados:
                    string_lower = string.lower()
                    
                    # Strings sospechosos
                    for patron in self.patrones_malware['strings_sospechosos']:
                        if isinstance(patron, str) and patron in string_lower and string not in analisis['strings_sospechosos_encontrados']:
                            analisis['strings_sospechosos_encontrados'].append(string[:100])  # Limitar longitud
                    
                    # URLs
                    if 'http' in string_lower and string not in analisis['urls_encontradas']:
                        analisis['urls_encontradas'].append(string[:100])
                    
                    # IPs (búsqueda simple)
                    import re
                    ips = re.findall(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', string)
                    for ip in ips:
                        if ip not in analisis['ips_encontradas']:
                            analisis['ips_encontradas'].append(ip)
                    
                    # Comandos sospechosos de Linux
                    comandos_sospechosos = ['bash -i', 'nc -e', '/bin/sh', 'python -c', '/bin/', 'system(']
                    for cmd in comandos_sospechosos:
                        if cmd in string_lower and string not in analisis['comandos_sospechosos']:
                            analisis['comandos_sospechosos'].append(string[:100])
        
        except Exception as e:
            self.logger.warning(f"Error en análisis de strings: {e}")
        
        return analisis
    
    def _analisis_headers(self, ruta_archivo: str) -> Dict[str, Any]:
        """Analiza headers y estructura del archivo."""
        analisis = {
            'header_detectado': '',
            'tipo_archivo_real': '',
            'discrepancia_extension': False,
            'headers_sospechosos': [],
            'estructura_valida': True
        }
        
        try:
            # Leer primeros bytes para header
            with open(ruta_archivo, 'rb') as f:
                header = f.read(16)
            
            # Identificar tipo por header
            if header.startswith(b'MZ'):
                analisis['tipo_archivo_real'] = 'PE_Ejecutable'
            elif header.startswith(b'\x7fELF'):
                analisis['tipo_archivo_real'] = 'ELF_Ejecutable'
            elif header.startswith(b'PK'):
                analisis['tipo_archivo_real'] = 'ZIP_Archive'
            elif header.startswith(b'\x89PNG'):
                analisis['tipo_archivo_real'] = 'PNG_Image'
            elif header.startswith(b'\xff\xd8\xff'):
                analisis['tipo_archivo_real'] = 'JPEG_Image'
            elif header.startswith(b'%PDF'):
                analisis['tipo_archivo_real'] = 'PDF_Document'
            else:
                analisis['tipo_archivo_real'] = 'Desconocido'
            
            analisis['header_detectado'] = header.hex()[:32]
            
            # Verificar discrepancias
            ruta_path = Path(ruta_archivo)
            extension = ruta_path.suffix.lower()
            
            if extension == '.txt' and 'Ejecutable' in analisis['tipo_archivo_real']:
                analisis['discrepancia_extension'] = True
            elif extension == '.jpg' and analisis['tipo_archivo_real'] != 'JPEG_Image':
                analisis['discrepancia_extension'] = True
            elif extension == '.png' and analisis['tipo_archivo_real'] != 'PNG_Image':
                analisis['discrepancia_extension'] = True
            
            # Buscar headers maliciosos conocidos
            for header_malicioso in self.patrones_malware['headers_maliciosos']:
                if isinstance(header_malicioso, bytes) and header.startswith(header_malicioso):
                    analisis['headers_sospechosos'].append(header_malicioso.hex())
        
        except Exception as e:
            self.logger.warning(f"Error en análisis de headers: {e}")
            analisis['estructura_valida'] = False
        
        return analisis
    
    def _analisis_herramientas_externas(self, ruta_archivo: str) -> Dict[str, Any]:
        """Ejecuta herramientas externas de análisis."""
        analisis = {
            'file_output': '',
            'binwalk_output': '',
            'clamav_result': '',
            'exiftool_data': {},
            'herramientas_ejecutadas': []
        }
        
        # Análisis con 'file'
        if self.herramientas_disponibles.get('file', False):
            try:
                resultado = subprocess.run(
                    ['file', '-b', ruta_archivo],
                    capture_output=True, text=True, timeout=10
                )
                if resultado.returncode == 0:
                    analisis['file_output'] = resultado.stdout.strip()
                    analisis['herramientas_ejecutadas'].append('file')
            except Exception as e:
                self.logger.warning(f"Error ejecutando 'file': {e}")
        
        # Análisis con binwalk (si está disponible)
        if self.herramientas_disponibles.get('binwalk', False):
            try:
                resultado = subprocess.run(
                    ['binwalk', '-e', '-q', ruta_archivo],
                    capture_output=True, text=True, timeout=30
                )
                if resultado.returncode == 0:
                    analisis['binwalk_output'] = resultado.stdout[:1000]  # Limitar salida
                    analisis['herramientas_ejecutadas'].append('binwalk')
            except Exception as e:
                self.logger.warning(f"Error ejecutando binwalk: {e}")
        
        # Análisis con ClamAV (si está disponible)
        if self.herramientas_disponibles.get('clamav', False):
            try:
                resultado = subprocess.run(
                    ['clamscan', '--no-summary', ruta_archivo],
                    capture_output=True, text=True, timeout=30
                )
                analisis['clamav_result'] = resultado.stdout.strip()
                analisis['herramientas_ejecutadas'].append('clamav')
            except Exception as e:
                self.logger.warning(f"Error ejecutando ClamAV: {e}")
        
        return analisis
    
    def _verificar_firmas_conocidas(self, hash_sha256: str) -> Optional[str]:
        """Verifica si el hash corresponde a malware conocido."""
        return self.firmas_conocidas.get(hash_sha256)
    
    def _evaluar_nivel_amenaza(self, resultado_analisis: Dict[str, Any]) -> str:
        """Evalúa el nivel de amenaza basado en los resultados del análisis."""
        puntuacion = 0
        
        # Análisis básico
        analisis_basico = resultado_analisis.get('analisis_basico', {})
        if analisis_basico.get('permisos_sospechosos'):
            puntuacion += 2
        if analisis_basico.get('tamaño_anormal'):
            puntuacion += 1
        if analisis_basico.get('nombre_sospechoso'):
            puntuacion += 2
        
        # Análisis de strings
        analisis_strings = resultado_analisis.get('analisis_strings', {})
        puntuacion += len(analisis_strings.get('strings_sospechosos_encontrados', [])) * 2
        puntuacion += len(analisis_strings.get('comandos_sospechosos', []))
        
        # Análisis de headers
        analisis_headers = resultado_analisis.get('analisis_headers', {})
        if analisis_headers.get('discrepancia_extension'):
            puntuacion += 3
        if analisis_headers.get('headers_sospechosos'):
            puntuacion += 4
        
        # Detecciones específicas
        detecciones = resultado_analisis.get('detecciones', [])
        for deteccion in detecciones:
            if deteccion.get('severidad') == 'ALTO':
                puntuacion += 5
            elif deteccion.get('severidad') == 'MEDIO':
                puntuacion += 3
        
        # Evaluación final
        if puntuacion >= 10:
            return 'CRITICO'
        elif puntuacion >= 7:
            return 'ALTO'
        elif puntuacion >= 4:
            return 'MEDIO'
        elif puntuacion >= 2:
            return 'BAJO'
        else:
            return 'MINIMO'
    
    def _generar_recomendaciones(self, resultado_analisis: Dict[str, Any], metadatos: MetadatosCuarentena) -> List[str]:
        """Genera recomendaciones basadas en el análisis."""
        recomendaciones = []
        
        nivel_amenaza = resultado_analisis.get('nivel_amenaza', 'BAJO')
        
        if nivel_amenaza in ['CRITICO', 'ALTO']:
            recomendaciones.append("🚨 ELIMINAR INMEDIATAMENTE - Alto riesgo de seguridad")
            recomendaciones.append("🔍 Realizar análisis forense completo del sistema")
            recomendaciones.append("🛡️ Verificar integridad de archivos críticos")
        
        elif nivel_amenaza == 'MEDIO':
            recomendaciones.append("⚠️ Mantener en cuarentena para análisis adicional")
            recomendaciones.append("🔬 Realizar análisis en entorno aislado")
            recomendaciones.append("📊 Monitorear actividad del sistema")
        
        elif nivel_amenaza == 'BAJO':
            recomendaciones.append("ℹ️ Posible falso positivo - Revisar manualmente")
            recomendaciones.append("✅ Considerar restauración después de validación")
        
        else:
            recomendaciones.append("✅ Archivo probablemente seguro")
            recomendaciones.append("🔄 Candidato para restauración automática")
        
        # Recomendaciones específicas
        analisis_headers = resultado_analisis.get('analisis_headers', {})
        if analisis_headers.get('discrepancia_extension'):
            recomendaciones.append("⚠️ Discrepancia entre extensión y contenido real")
        
        analisis_strings = resultado_analisis.get('analisis_strings', {})
        if analisis_strings.get('strings_sospechosos_encontrados'):
            recomendaciones.append("🔍 Contiene strings potencialmente maliciosos")
        
        if metadatos.dias_en_cuarentena > 30:
            recomendaciones.append("🗂️ Archivo lleva más de 30 días en cuarentena - Considerar eliminación")
        
        return recomendaciones


class GestorCuarentenaAvanzado:
    def obtener_lista_cuarentena(self):
        """Devuelve una lista de metadatos de archivos en cuarentena (activos)."""
        return [m for m in self.base_datos.values() if getattr(m, 'estado', None) and getattr(m.estado, 'value', None) == 'ACTIVO']

    def restaurar_archivo(self, hash_sha256: str) -> bool:
        """Restaura un archivo de la cuarentena a su ubicación original usando el hash."""
        for metadatos in self.base_datos.values():
            if getattr(metadatos, 'hash_sha256', None) == hash_sha256 and getattr(metadatos, 'estado', None) and getattr(metadatos.estado, 'value', None) == 'ACTIVO':
                try:
                    ruta_backup = getattr(metadatos, 'ruta_backup', None)
                    ruta_original = getattr(metadatos, 'ruta_original', None)
                    if ruta_backup and ruta_original and os.path.exists(ruta_backup):
                        import shutil
                        shutil.copy2(ruta_backup, ruta_original)
                        metadatos.estado = type(metadatos.estado)("RESTAURADO")
                        self._guardar_base_datos()
                        self.archivos_restaurados += 1
                        self.logger.info(f"Archivo restaurado: {ruta_original}")
                        return True
                except Exception as e:
                    self.logger.error(f"Error restaurando archivo: {e}")
                    return False
        return False

    def eliminar_archivo(self, hash_sha256: str) -> bool:
        """Elimina un archivo de la cuarentena y su backup usando el hash."""
        for metadatos in self.base_datos.values():
            if getattr(metadatos, 'hash_sha256', None) == hash_sha256 and getattr(metadatos, 'estado', None) and getattr(metadatos.estado, 'value', None) == 'ACTIVO':
                try:
                    ruta_cuarentena = getattr(metadatos, 'ruta_cuarentena', None)
                    ruta_backup = getattr(metadatos, 'ruta_backup', None)
                    if ruta_cuarentena and os.path.exists(ruta_cuarentena):
                        os.remove(ruta_cuarentena)
                    if ruta_backup and os.path.exists(ruta_backup):
                        os.remove(ruta_backup)
                    metadatos.estado = type(metadatos.estado)("ELIMINADO")
                    self._guardar_base_datos()
                    self.logger.info(f"Archivo eliminado: {hash_sha256}")
                    return True
                except Exception as e:
                    self.logger.error(f"Error eliminando archivo: {e}")
                    return False
        return False
    """Sistema avanzado de gestión de cuarentena."""
    
    def __init__(self, siem: SIEM):
        """
        Inicializa el gestor de cuarentena avanzado.
        
        Args:
            siem: Instancia del SIEM para registro de eventos
        """
        self.siem = siem
        self.logger = configurar_logger_modulo("gestor_cuarentena")
        
        # Componentes del sistema
        self.analizador_forense = AnalizadorForenseCuarentena()
        
        # Configuración de directorios
        self.directorio_cuarentena = self._configurar_directorio_cuarentena()
        self.directorio_activos = os.path.join(self.directorio_cuarentena, "activos")
        self.directorio_backups = os.path.join(self.directorio_cuarentena, "backups")
        self.directorio_logs = os.path.join(self.directorio_cuarentena, "logs")
        self.directorio_temp = os.path.join(self.directorio_cuarentena, "temp")
        
        # Base de datos de cuarentena
        self.base_datos: Dict[str, MetadatosCuarentena] = {}
        self.archivo_base_datos = os.path.join(self.directorio_cuarentena, "cuarentena_db.json")
        
        # Configuración
        self.tamaño_maximo_archivo = 500 * 1024 * 1024  # 500MB
        self.dias_retencion = 90  # Días antes de eliminar automáticamente
        self.analisis_automatico = True
        self.compresion_habilitada = True
        
        # Estado del sistema
        self.archivos_procesados = 0
        self.amenazas_detectadas = 0
        self.falsos_positivos = 0
        self.archivos_restaurados = 0
        
        # Inicializar sistema
        self._crear_estructura_directorios()
        self._cargar_base_datos()
        
        self.logger.info("Gestor de Cuarentena Avanzado inicializado correctamente")
        self.siem.registrar_evento(
            TipoEvento.SISTEMA_INICIADO,
            "Sistema de Cuarentena Avanzado inicializado correctamente",
            {
                'directorio_cuarentena': self.directorio_cuarentena,
                'archivos_en_cuarentena': len(self.base_datos),
                'analisis_automatico': self.analisis_automatico
            },
            "MEDIO"
        )
    
    def _configurar_directorio_cuarentena(self) -> str:
        """Configura y retorna el directorio de cuarentena unificado (solo cuarentena_avanzada)."""
        try:
            rutas_sistema = obtener_rutas_sistema()
            directorio = os.path.join(rutas_sistema['directorio_datos'], "cuarentena_avanzada")
        except Exception:
            directorio = str(Path.cwd() / "cuarentena_avanzada")
        # Eliminar carpeta antigua si existe (limpieza)
        carpeta_antigua = Path.cwd() / "cuarentena"
        if carpeta_antigua.exists() and carpeta_antigua.is_dir():
            try:
                import shutil
                shutil.rmtree(carpeta_antigua)
            except Exception:
                pass
        return directorio
    
    def _crear_estructura_directorios(self):
        """Crea la estructura de directorios necesaria."""
        directorios = [
            self.directorio_cuarentena,
            self.directorio_activos,
            self.directorio_backups,
            self.directorio_logs,
            self.directorio_temp
        ]
        
        for directorio in directorios:
            try:
                # Crear directorio usando os.makedirs en lugar de crear_ruta_segura
                os.makedirs(directorio, mode=0o700, exist_ok=True)
                # Establecer permisos restrictivos
                os.chmod(directorio, 0o700)
            except Exception as e:
                self.logger.error(f"Error creando directorio {directorio}: {e}")
    
    def _cargar_base_datos(self):
        """Carga la base de datos de cuarentena."""
        try:
            if os.path.exists(self.archivo_base_datos):
                with open(self.archivo_base_datos, 'r', encoding='utf-8') as archivo:
                    datos = json.load(archivo)
                    
                    for archivo_id, datos_metadatos in datos.items():
                        metadatos = MetadatosCuarentena(
                            archivo_id=archivo_id,
                            ruta_original="",
                            ruta_cuarentena="",
                            nombre_original="",
                            extension="",
                            tamaño_bytes=0,
                            hash_md5="", hash_sha1="", hash_sha256="", hash_sha512="",
                            tipo_mime="", encoding=None,
                            timestamp_cuarentena=datetime.now(),
                            timestamp_ultimo_analisis=None,
                            estado=EstadoCuarentena.PENDIENTE,
                            tipo_amenaza=None,
                            nivel_riesgo=NivelRiesgoCuarentena.BAJO,
                            origen_deteccion="", razon_cuarentena="",
                            permisos_originales="", propietario_original="", grupo_original=""
                        )
                        
                        # Cargar datos desde diccionario
                        metadatos.__dict__.update(datos_metadatos)
                        
                        # Convertir fechas
                        if isinstance(metadatos.timestamp_cuarentena, str):
                            metadatos.timestamp_cuarentena = datetime.fromisoformat(metadatos.timestamp_cuarentena)
                        
                        if metadatos.timestamp_ultimo_analisis and isinstance(metadatos.timestamp_ultimo_analisis, str):
                            metadatos.timestamp_ultimo_analisis = datetime.fromisoformat(metadatos.timestamp_ultimo_analisis)
                        
                        # Convertir enums desde strings
                        if isinstance(metadatos.estado, str):
                            metadatos.estado = EstadoCuarentena(metadatos.estado)
                        
                        if isinstance(metadatos.nivel_riesgo, str):
                            metadatos.nivel_riesgo = NivelRiesgoCuarentena(metadatos.nivel_riesgo)
                        
                        if isinstance(metadatos.tipo_amenaza, str) and metadatos.tipo_amenaza:
                            metadatos.tipo_amenaza = TipoAmenazaCuarentena(metadatos.tipo_amenaza)
                        
                        self.base_datos[archivo_id] = metadatos
                
                self.logger.info(f"Base de datos de cuarentena cargada: {len(self.base_datos)} archivos")
        
        except Exception as e:
            self.logger.warning(f"Error cargando base de datos de cuarentena: {e}")
    
    def _guardar_base_datos(self):
        """Guarda la base de datos de cuarentena."""
        try:
            datos = {}
            for archivo_id, metadatos in self.base_datos.items():
                datos[archivo_id] = metadatos.to_dict()
            
            with open(self.archivo_base_datos, 'w', encoding='utf-8') as archivo:
                json.dump(datos, archivo, ensure_ascii=False, indent=2)
            
            self.logger.debug("Base de datos de cuarentena guardada")
        
        except Exception as e:
            self.logger.error(f"Error guardando base de datos de cuarentena: {e}")
    
    def poner_en_cuarentena(self, ruta_archivo: str, origen_deteccion: str, 
                           razon: str, tipo_amenaza: Optional[TipoAmenazaCuarentena] = None,
                           nivel_riesgo: NivelRiesgoCuarentena = NivelRiesgoCuarentena.MEDIO) -> Optional[str]:
        """
        Pone un archivo en cuarentena.
        
        Args:
            ruta_archivo: Ruta del archivo a poner en cuarentena
            origen_deteccion: Módulo que detectó la amenaza
            razon: Razón para poner en cuarentena
            tipo_amenaza: Tipo de amenaza detectada
            nivel_riesgo: Nivel de riesgo del archivo
            
        Returns:
            Optional[str]: ID del archivo en cuarentena o None si falló
        """
        try:
            self.logger.info(f"Iniciando proceso de cuarentena para: {ruta_archivo}")
            
            # Validaciones
            if not os.path.exists(ruta_archivo):
                self.logger.error(f"El archivo no existe: {ruta_archivo}")
                return None
            
            if not validar_permisos_lectura(ruta_archivo):
                self.logger.error(f"Permisos de lectura insuficientes para: {ruta_archivo}")
                return None
            
            # Verificar tamaño
            tamaño_archivo = os.path.getsize(ruta_archivo)
            if tamaño_archivo > self.tamaño_maximo_archivo:
                self.logger.warning(f"El archivo excede el tamaño máximo permitido para cuarentena: {tamaño_archivo} bytes")
                return None
            
            # Generar metadatos
            metadatos = self._generar_metadatos_archivo(ruta_archivo, origen_deteccion, razon, tipo_amenaza, nivel_riesgo)
            
            # Crear ruta en cuarentena
            nombre_cuarentena = f"{metadatos.archivo_id}_{metadatos.nombre_original}"
            ruta_cuarentena = os.path.join(self.directorio_activos, nombre_cuarentena)
            
            # Crear backup antes de mover
            if self._crear_backup_archivo(ruta_archivo, metadatos):
                metadatos.agregar_accion(AccionCuarentena.COPIA_SEGURIDAD, "Backup creado exitosamente")
            
            # Mover archivo a cuarentena
            if self.compresion_habilitada:
                ruta_cuarentena += ".zip"
                self._comprimir_archivo(ruta_archivo, ruta_cuarentena)
            else:
                shutil.move(ruta_archivo, ruta_cuarentena)
            
            metadatos.ruta_cuarentena = ruta_cuarentena
            metadatos.agregar_accion(AccionCuarentena.CUARENTENADO, f"Movido desde {ruta_archivo}")
            
            # Establecer permisos restrictivos
            os.chmod(ruta_cuarentena, 0o600)
            
            # Guardar en base de datos
            self.base_datos[metadatos.archivo_id] = metadatos
            self._guardar_base_datos()
            
            # Registrar evento
            self.siem.registrar_evento(
                TipoEvento.AMENAZA_DETECTADA,
                f"Archivo puesto en cuarentena: {metadatos.nombre_original}",
                {
                    'archivo_id': metadatos.archivo_id,
                    'ruta_original': ruta_archivo,
                    'origen_deteccion': origen_deteccion,
                    'razon': razon,
                    'tipo_amenaza': tipo_amenaza.value if tipo_amenaza else None,
                    'nivel_riesgo': nivel_riesgo.value,
                    'hash_sha256': metadatos.hash_sha256
                },
                "ALTO" if nivel_riesgo in [NivelRiesgoCuarentena.CRITICO, NivelRiesgoCuarentena.ALTO] else "MEDIO"
            )
            
            # Iniciar análisis automático si está habilitado
            if self.analisis_automatico:
                threading.Thread(
                    target=self._analizar_archivo_automatico,
                    args=(metadatos.archivo_id,),
                    daemon=True
                ).start()
            
            self.archivos_procesados += 1
            self.logger.info(f"Archivo puesto en cuarentena correctamente: {metadatos.archivo_id}")
            
            return metadatos.archivo_id
        
        except Exception as e:
            self.logger.error(f"Error al poner archivo en cuarentena: {e}")
            return None
    
    def _generar_metadatos_archivo(self, ruta_archivo: str, origen_deteccion: str, razon: str,
                                  tipo_amenaza: Optional[TipoAmenazaCuarentena],
                                  nivel_riesgo: NivelRiesgoCuarentena) -> MetadatosCuarentena:
        """Genera metadatos completos para un archivo."""
        ruta_path = Path(ruta_archivo)
        # Obtener tipo MIME
        try:
            # Usar mimetypes estándar de Python
            tipo_mime, encoding = mimetypes.guess_type(ruta_archivo)
            if not tipo_mime:
                tipo_mime = "application/octet-stream"
        except Exception:
            tipo_mime = "application/octet-stream"
            encoding = None
        
        # Obtener información del archivo
        stat_info = os.stat(ruta_archivo)
        hashes = self._calcular_hashes_archivo(ruta_archivo)
        
        # Obtener información de propietario
        try:
            import pwd, grp
            propietario = pwd.getpwuid(stat_info.st_uid).pw_name
            grupo = grp.getgrgid(stat_info.st_gid).gr_name
        except Exception:
            propietario = str(stat_info.st_uid)
            grupo = str(stat_info.st_gid)
        
        return MetadatosCuarentena(
            archivo_id="",  # Se generará automáticamente
            ruta_original=ruta_archivo,
            ruta_cuarentena="",  # Se establecerá después
            nombre_original=ruta_path.name,
            extension=ruta_path.suffix.lower(),
            tamaño_bytes=stat_info.st_size,
            hash_md5=hashes['md5'],
            hash_sha1=hashes['sha1'],
            hash_sha256=hashes['sha256'],
            hash_sha512=hashes['sha512'],
            tipo_mime=tipo_mime,
            encoding=encoding,
            timestamp_cuarentena=datetime.now(),
            timestamp_ultimo_analisis=None,
            estado=EstadoCuarentena.PENDIENTE,
            tipo_amenaza=tipo_amenaza,
            nivel_riesgo=nivel_riesgo,
            origen_deteccion=origen_deteccion,
            razon_cuarentena=razon,
            permisos_originales=oct(stat_info.st_mode)[-3:],
            propietario_original=propietario,
            grupo_original=grupo
        )
    
    def _calcular_hashes_archivo(self, ruta_archivo: str) -> Dict[str, str]:
        """Calcula múltiples hashes del archivo."""
        hashes = {'md5': '', 'sha1': '', 'sha256': '', 'sha512': ''}
        
        try:
            with open(ruta_archivo, 'rb') as archivo:
                contenido = archivo.read()
                
                hashes['md5'] = hashlib.md5(contenido).hexdigest()
                hashes['sha1'] = hashlib.sha1(contenido).hexdigest()
                hashes['sha256'] = hashlib.sha256(contenido).hexdigest()
                hashes['sha512'] = hashlib.sha512(contenido).hexdigest()
        
        except Exception as e:
            self.logger.warning(f"Error calculando hashes: {e}")
        
        return hashes
    
    def _crear_backup_archivo(self, ruta_archivo: str, metadatos: MetadatosCuarentena) -> bool:
        """Crea un backup del archivo antes de moverlo a cuarentena."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nombre_backup = f"{metadatos.nombre_original}_{timestamp}_backup{metadatos.extension}"
            ruta_backup = os.path.join(self.directorio_backups, nombre_backup)
            
            shutil.copy2(ruta_archivo, ruta_backup)
            os.chmod(ruta_backup, 0o600)
            
            self.logger.debug(f"Backup creado: {ruta_backup}")
            return True
        
        except Exception as e:
            self.logger.warning(f"Error creando backup: {e}")
            return False
    
    def _comprimir_archivo(self, ruta_origen: str, ruta_destino: str):
        """Comprime un archivo usando ZIP."""
        try:
            with zipfile.ZipFile(ruta_destino, 'w', zipfile.ZIP_DEFLATED) as archivo_zip:
                archivo_zip.write(ruta_origen, os.path.basename(ruta_origen))
            
            # Eliminar archivo original
            os.remove(ruta_origen)
            
            self.logger.debug(f"Archivo comprimido: {ruta_destino}")
        
        except Exception as e:
            self.logger.error(f"Error comprimiendo archivo: {e}")
            # Fallback: mover sin comprimir
            shutil.move(ruta_origen, ruta_destino.replace('.zip', ''))
    
    def _analizar_archivo_automatico(self, archivo_id: str):
        """Analiza automáticamente un archivo en cuarentena."""
        try:
            if archivo_id not in self.base_datos:
                return
            
            metadatos = self.base_datos[archivo_id]
            metadatos.estado = EstadoCuarentena.EN_ANALISIS
            self._guardar_base_datos()
            
            # Descomprimir si es necesario
            ruta_analisis = self._preparar_archivo_para_analisis(metadatos)
            
            # Ejecutar análisis forense
            resultado_analisis = self.analizador_forense.analizar_archivo_completo(ruta_analisis, metadatos)
            
            # Actualizar metadatos con resultados
            metadatos.resultado_analisis = resultado_analisis
            metadatos.timestamp_ultimo_analisis = datetime.now()
            metadatos.agregar_accion(AccionCuarentena.ANALIZADO, f"Análisis completado - Nivel: {resultado_analisis['nivel_amenaza']}")
            
            # Actualizar estado basado en análisis
            nivel_amenaza = resultado_analisis.get('nivel_amenaza', 'BAJO')
            if nivel_amenaza in ['CRITICO', 'ALTO']:
                metadatos.estado = EstadoCuarentena.MALICIOSO
                metadatos.tipo_amenaza = TipoAmenazaCuarentena.ARCHIVO_SOSPECHOSO
                self.amenazas_detectadas += 1
            elif nivel_amenaza == 'MEDIO':
                metadatos.estado = EstadoCuarentena.SOSPECHOSO
                metadatos.requiere_atencion_manual = True
            else:
                metadatos.estado = EstadoCuarentena.SEGURO
            
            # Limpiar archivo temporal
            if ruta_analisis != metadatos.ruta_cuarentena:
                try:
                    os.remove(ruta_analisis)
                except Exception:
                    pass
            
            self._guardar_base_datos()
            
            # Registrar resultado
            self.siem.registrar_evento(
                TipoEvento.ANALISIS_COMPLETADO,
                f"Análisis automático completado: {metadatos.nombre_original}",
                {
                    'archivo_id': archivo_id,
                    'nivel_amenaza': nivel_amenaza,
                    'estado_final': metadatos.estado.value,
                    'tiempo_analisis': resultado_analisis.get('tiempo_analisis', 0)
                },
                "ALTO" if nivel_amenaza in ['CRITICO', 'ALTO'] else "MEDIO"
            )
            
            self.logger.info(f"Análisis automático completado: {archivo_id} - {nivel_amenaza}")
        
        except Exception as e:
            self.logger.error(f"Error en análisis automático: {e}")
            if archivo_id in self.base_datos:
                self.base_datos[archivo_id].estado = EstadoCuarentena.ERROR
                self._guardar_base_datos()
    
    def _preparar_archivo_para_analisis(self, metadatos: MetadatosCuarentena) -> str:
        """Prepara un archivo para análisis (descomprime si es necesario)."""
        if metadatos.ruta_cuarentena.endswith('.zip'):
            # Descomprimir temporalmente
            ruta_temp = os.path.join(self.directorio_temp, f"analisis_{metadatos.archivo_id}")
            
            try:
                with zipfile.ZipFile(metadatos.ruta_cuarentena, 'r') as archivo_zip:
                    archivo_zip.extractall(ruta_temp)
                
                # Buscar el archivo extraído
                archivos_extraidos = os.listdir(ruta_temp)
                if archivos_extraidos:
                    return os.path.join(ruta_temp, archivos_extraidos[0])
            
            except Exception as e:
                self.logger.warning(f"Error descomprimiendo para análisis: {e}")
        
        return metadatos.ruta_cuarentena
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas del sistema de cuarentena."""
        total_archivos = len(self.base_datos)
        archivos_por_estado = defaultdict(int)
        archivos_por_riesgo = defaultdict(int)
        archivos_por_tipo_amenaza = defaultdict(int)
        
        for metadatos in self.base_datos.values():
            archivos_por_estado[metadatos.estado.value] += 1
            archivos_por_riesgo[metadatos.nivel_riesgo.value] += 1
            if metadatos.tipo_amenaza:
                archivos_por_tipo_amenaza[metadatos.tipo_amenaza.value] += 1
        
        return {
            'total_archivos_cuarentena': total_archivos,
            'archivos_procesados': self.archivos_procesados,
            'amenazas_detectadas': self.amenazas_detectadas,
            'falsos_positivos': self.falsos_positivos,
            'archivos_restaurados': self.archivos_restaurados,
            'archivos_por_estado': dict(archivos_por_estado),
            'archivos_por_riesgo': dict(archivos_por_riesgo),
            'archivos_por_tipo_amenaza': dict(archivos_por_tipo_amenaza),
            'directorio_cuarentena': self.directorio_cuarentena,
            'analisis_automatico': self.analisis_automatico,
            'herramientas_forenses': len([k for k, v in self.analizador_forense.herramientas_disponibles.items() if v])
        }


# Alias para compatibilidad
GestorCuarentena = GestorCuarentenaAvanzado

