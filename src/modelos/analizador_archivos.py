#!/usr/bin/env python3
"""
Analizador de Archivos
Módulo para análisis detallado de metadatos de archivos y cálculo de hashes criptográficos.

Autor: DogSoulDev
Versión: 2.0.0
"""

import os
import hashlib
import mimetypes
import stat
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


class MetadatosArchivo:
    """Contenedor para metadatos detallados de un archivo."""
    
    def __init__(self, ruta_archivo: str):
        """
        Inicializa los metadatos de un archivo.
        
        Args:
            ruta_archivo: Ruta al archivo a analizar
        """
        self.ruta_archivo = Path(ruta_archivo)
        self.existe = self.ruta_archivo.exists()
        
        if self.existe:
            self._extraer_metadatos()
        else:
            self._inicializar_vacio()
    
    def _extraer_metadatos(self):
        """Extrae todos los metadatos disponibles del archivo."""
        try:
            stat_info = self.ruta_archivo.stat()
            
            # Información básica
            self.nombre = self.ruta_archivo.name
            self.extension = self.ruta_archivo.suffix.lower()
            self.directorio_padre = str(self.ruta_archivo.parent)
            self.ruta_absoluta = str(self.ruta_archivo.absolute())
            
            # Tamaños
            self.tamaño_bytes = stat_info.st_size
            self.tamaño_kb = round(self.tamaño_bytes / 1024, 2)
            self.tamaño_mb = round(self.tamaño_bytes / (1024 * 1024), 2)
            
            # Fechas y tiempos
            self.fecha_modificacion = datetime.fromtimestamp(stat_info.st_mtime)
            self.fecha_acceso = datetime.fromtimestamp(stat_info.st_atime)
            self.fecha_creacion = datetime.fromtimestamp(stat_info.st_ctime)
            
            # Permisos y propietario
            self.permisos_octal = oct(stat_info.st_mode)[-3:]
            self.permisos_legibles = stat.filemode(stat_info.st_mode)
            self.uid_propietario = stat_info.st_uid
            self.gid_grupo = stat_info.st_gid
            
            # Información del tipo de archivo
            self.es_archivo_regular = stat.S_ISREG(stat_info.st_mode)
            self.es_directorio = stat.S_ISDIR(stat_info.st_mode)
            self.es_enlace_simbolico = stat.S_ISLNK(stat_info.st_mode)
            self.es_ejecutable = os.access(self.ruta_archivo, os.X_OK)
            self.es_legible = os.access(self.ruta_archivo, os.R_OK)
            self.es_escribible = os.access(self.ruta_archivo, os.W_OK)
            
            # Tipo MIME
            self.tipo_mime, self.codificacion = mimetypes.guess_type(str(self.ruta_archivo))
            
            # Información específica del sistema
            self.numero_inodo = stat_info.st_ino
            self.numero_enlaces = stat_info.st_nlink
            self.dispositivo = stat_info.st_dev
            
        except (OSError, PermissionError) as e:
            self.error_acceso = str(e)
            self._inicializar_vacio()
    
    def _inicializar_vacio(self):
        """Inicializa valores por defecto cuando no se puede acceder al archivo."""
        self.nombre = ""
        self.extension = ""
        self.directorio_padre = ""
        self.ruta_absoluta = ""
        self.tamaño_bytes = 0
        self.tamaño_kb = 0
        self.tamaño_mb = 0
        self.fecha_modificacion = None
        self.fecha_acceso = None
        self.fecha_creacion = None
        self.permisos_octal = ""
        self.permisos_legibles = ""
        self.uid_propietario = 0
        self.gid_grupo = 0
        self.es_archivo_regular = False
        self.es_directorio = False
        self.es_enlace_simbolico = False
        self.es_ejecutable = False
        self.es_legible = False
        self.es_escribible = False
        self.tipo_mime = None
        self.codificacion = None
        self.numero_inodo = 0
        self.numero_enlaces = 0
        self.dispositivo = 0
        self.error_acceso = "Archivo no accesible"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte los metadatos a un diccionario."""
        return {
            'ruta_archivo': str(self.ruta_archivo),
            'existe': self.existe,
            'nombre': self.nombre,
            'extension': self.extension,
            'directorio_padre': self.directorio_padre,
            'ruta_absoluta': self.ruta_absoluta,
            'tamaño': {
                'bytes': self.tamaño_bytes,
                'kb': self.tamaño_kb,
                'mb': self.tamaño_mb
            },
            'fechas': {
                'modificacion': self.fecha_modificacion.isoformat() if self.fecha_modificacion else None,
                'acceso': self.fecha_acceso.isoformat() if self.fecha_acceso else None,
                'creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None
            },
            'permisos': {
                'octal': self.permisos_octal,
                'legibles': self.permisos_legibles,
                'es_ejecutable': self.es_ejecutable,
                'es_legible': self.es_legible,
                'es_escribible': self.es_escribible
            },
            'propietario': {
                'uid': self.uid_propietario,
                'gid': self.gid_grupo
            },
            'tipo_archivo': {
                'es_archivo_regular': self.es_archivo_regular,
                'es_directorio': self.es_directorio,
                'es_enlace_simbolico': self.es_enlace_simbolico,
                'tipo_mime': self.tipo_mime,
                'codificacion': self.codificacion
            },
            'sistema': {
                'inodo': self.numero_inodo,
                'enlaces': self.numero_enlaces,
                'dispositivo': self.dispositivo
            }
        }


class HashesArchivo:
    """Calculadora de hashes criptográficos para archivos."""
    
    def __init__(self, ruta_archivo: str):
        """
        Inicializa el calculador de hashes.
        
        Args:
            ruta_archivo: Ruta al archivo a analizar
        """
        self.ruta_archivo = Path(ruta_archivo)
        self.hashes = {}
        self.tiempo_calculo = 0
        self.error = None
    
    def calcular_todos_los_hashes(self, chunk_size: int = 8192) -> Dict[str, str]:
        """
        Calcula MD5, SHA1, SHA256 y SHA512 del archivo.
        
        Args:
            chunk_size: Tamaño del chunk para lectura del archivo
            
        Returns:
            Dict con todos los hashes calculados
        """
        inicio = datetime.now()
        
        try:
            # Inicializar algoritmos de hash
            md5_hash = hashlib.md5()
            sha1_hash = hashlib.sha1()
            sha256_hash = hashlib.sha256()
            sha512_hash = hashlib.sha512()
            
            # Leer archivo en chunks y actualizar hashes
            with open(self.ruta_archivo, 'rb') as archivo:
                while chunk := archivo.read(chunk_size):
                    md5_hash.update(chunk)
                    sha1_hash.update(chunk)
                    sha256_hash.update(chunk)
                    sha512_hash.update(chunk)
            
            # Obtener valores hexadecimales
            self.hashes = {
                'md5': md5_hash.hexdigest(),
                'sha1': sha1_hash.hexdigest(),
                'sha256': sha256_hash.hexdigest(),
                'sha512': sha512_hash.hexdigest()
            }
            
        except (OSError, PermissionError) as e:
            self.error = str(e)
            self.hashes = {
                'md5': '',
                'sha1': '',
                'sha256': '',
                'sha512': ''
            }
        
        fin = datetime.now()
        self.tiempo_calculo = (fin - inicio).total_seconds()
        
        return self.hashes
    
    def calcular_hash_especifico(self, algoritmo: str) -> str:
        """
        Calcula un hash específico del archivo.
        
        Args:
            algoritmo: Algoritmo a usar ('md5', 'sha1', 'sha256', 'sha512')
            
        Returns:
            Hash hexadecimal del archivo
        """
        algoritmo = algoritmo.lower()
        algoritmos_soportados = {
            'md5': hashlib.md5,
            'sha1': hashlib.sha1,
            'sha256': hashlib.sha256,
            'sha512': hashlib.sha512
        }
        
        if algoritmo not in algoritmos_soportados:
            raise ValueError(f"Algoritmo no soportado: {algoritmo}")
        
        try:
            hasher = algoritmos_soportados[algoritmo]()
            
            with open(self.ruta_archivo, 'rb') as archivo:
                while chunk := archivo.read(8192):
                    hasher.update(chunk)
            
            return hasher.hexdigest()
            
        except (OSError, PermissionError) as e:
            self.error = str(e)
            return ""


class AnalizadorArchivos:
    """Analizador completo de archivos con metadatos y hashes."""
    
    def __init__(self, siem=None):
        """
        Inicializa el analizador de archivos.
        
        Args:
            siem: Sistema SIEM para logging (opcional)
        """
        self.siem = siem
    
    def analizar_archivo_completo(self, ruta_archivo: str) -> Dict[str, Any]:
        """
        Realiza un análisis completo de un archivo.
        
        Args:
            ruta_archivo: Ruta al archivo a analizar
            
        Returns:
            Dict con análisis completo (metadatos + hashes)
        """
        if self.siem:
            self.siem.log_evento('INFO', 'analizador_archivos', 
                               f'Iniciando análisis completo de {ruta_archivo}')
        
        # Extraer metadatos
        metadatos = MetadatosArchivo(ruta_archivo)
        
        # Calcular hashes (solo para archivos regulares)
        hashes_resultado = {}
        if metadatos.es_archivo_regular and metadatos.existe:
            calculador_hashes = HashesArchivo(ruta_archivo)
            hashes_resultado = calculador_hashes.calcular_todos_los_hashes()
            
            if self.siem and calculador_hashes.error:
                self.siem.log_evento('WARNING', 'analizador_archivos', 
                                   f'Error calculando hashes: {calculador_hashes.error}')
        
        # Combinar resultados
        resultado = {
            'timestamp_analisis': datetime.now().isoformat(),
            'metadatos': metadatos.to_dict(),
            'hashes': hashes_resultado,
            'analisis_completado': metadatos.existe and metadatos.es_archivo_regular
        }
        
        if self.siem:
            self.siem.log_evento('INFO', 'analizador_archivos', 
                               f'Análisis completado para {ruta_archivo}')
        
        return resultado
    
    def analizar_directorio(self, ruta_directorio: str, recursivo: bool = False) -> List[Dict[str, Any]]:
        """
        Analiza todos los archivos en un directorio.
        
        Args:
            ruta_directorio: Ruta al directorio a analizar
            recursivo: Si debe analizar subdirectorios
            
        Returns:
            Lista de análisis de archivos
        """
        if self.siem:
            self.siem.log_evento('INFO', 'analizador_archivos', 
                               f'Iniciando análisis de directorio {ruta_directorio}')
        
        directorio = Path(ruta_directorio)
        if not directorio.exists() or not directorio.is_dir():
            if self.siem:
                self.siem.log_evento('ERROR', 'analizador_archivos', 
                                   f'Directorio no válido: {ruta_directorio}')
            return []
        
        resultados = []
        patron = "**/*" if recursivo else "*"
        
        try:
            for archivo in directorio.glob(patron):
                if archivo.is_file():
                    analisis = self.analizar_archivo_completo(str(archivo))
                    resultados.append(analisis)
        
        except PermissionError as e:
            if self.siem:
                self.siem.log_evento('ERROR', 'analizador_archivos', 
                                   f'Sin permisos para acceder a {ruta_directorio}: {e}')
        
        if self.siem:
            self.siem.log_evento('INFO', 'analizador_archivos', 
                               f'Análisis de directorio completado: {len(resultados)} archivos')
        
        return resultados
    
    def comparar_hashes(self, hash1: str, hash2: str) -> bool:
        """
        Compara dos hashes para verificar si son idénticos.
        
        Args:
            hash1: Primer hash a comparar
            hash2: Segundo hash a comparar
            
        Returns:
            True si los hashes son idénticos
        """
        return hash1.lower() == hash2.lower()
    
    def verificar_archivo_contra_hash(self, ruta_archivo: str, hash_esperado: str, 
                                    algoritmo: str = 'sha256') -> bool:
        """
        Verifica la integridad de un archivo contra un hash conocido.
        
        Args:
            ruta_archivo: Ruta al archivo a verificar
            hash_esperado: Hash esperado para comparación
            algoritmo: Algoritmo de hash a usar
            
        Returns:
            True si el archivo coincide con el hash esperado
        """
        calculador = HashesArchivo(ruta_archivo)
        hash_calculado = calculador.calcular_hash_especifico(algoritmo)
        
        resultado = self.comparar_hashes(hash_calculado, hash_esperado)
        
        if self.siem:
            estado = "COINCIDE" if resultado else "NO_COINCIDE"
            self.siem.log_evento('INFO', 'analizador_archivos', 
                               f'Verificación de integridad {estado}: {ruta_archivo}')
        
        return resultado
    
    def generar_reporte_markdown(self, analisis: Dict[str, Any]) -> str:
        """
        Genera un reporte en formato Markdown del análisis.
        
        Args:
            analisis: Resultado del análisis completo
            
        Returns:
            String con el reporte en formato Markdown
        """
        metadatos = analisis['metadatos']
        hashes = analisis['hashes']
        
        reporte = f"""# Análisis de Archivo: {metadatos['nombre']}

## Información General
- **Ruta completa:** `{metadatos['ruta_absoluta']}`
- **Existe:** {'✅ Sí' if metadatos['existe'] else '❌ No'}
- **Tipo:** {metadatos['tipo_archivo']['tipo_mime'] or 'Desconocido'}
- **Extensión:** `{metadatos['extension'] or 'Sin extensión'}`

## Tamaño
- **Bytes:** {metadatos['tamaño']['bytes']:,}
- **KB:** {metadatos['tamaño']['kb']}
- **MB:** {metadatos['tamaño']['mb']}

## Fechas y Tiempos
- **Modificación:** {metadatos['fechas']['modificacion'] or 'N/A'}
- **Acceso:** {metadatos['fechas']['acceso'] or 'N/A'}
- **Creación:** {metadatos['fechas']['creacion'] or 'N/A'}

## Permisos y Seguridad
- **Permisos:** `{metadatos['permisos']['legibles']}` ({metadatos['permisos']['octal']})
- **Propietario UID:** {metadatos['propietario']['uid']}
- **Grupo GID:** {metadatos['propietario']['gid']}
- **Ejecutable:** {'✅ Sí' if metadatos['permisos']['es_ejecutable'] else '❌ No'}
- **Legible:** {'✅ Sí' if metadatos['permisos']['es_legible'] else '❌ No'}
- **Escribible:** {'✅ Sí' if metadatos['permisos']['es_escribible'] else '❌ No'}

## Hashes Criptográficos
"""

        if hashes:
            for algoritmo, valor in hashes.items():
                if valor:
                    reporte += f"- **{algoritmo.upper()}:** `{valor}`\n"
        else:
            reporte += "- *No se calcularon hashes (archivo no regular o no accesible)*\n"

        reporte += f"""
## Información del Sistema
- **Inodo:** {metadatos['sistema']['inodo']}
- **Enlaces duros:** {metadatos['sistema']['enlaces']}
- **Dispositivo:** {metadatos['sistema']['dispositivo']}

---
*Análisis realizado el {analisis['timestamp_analisis']} por Ares Aegis*
"""
        
        return reporte
