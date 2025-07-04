#!/usr/bin/env python3
"""
Copyright (c) 2025 DogSoulDev (https://github.com/DogSoulDev)
Todos los derechos reservados. Este código es propietario y confidencial.

Gestor de Cuarentena
"""

import os
import json
import shutil
import gzip
import time
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

from .siem import SIEM, TipoEvento
from ..utilidades.validaciones import validar_ruta_archivo, validar_permisos_lectura
from ..utilidades.ayuda_rutas import crear_ruta_segura, obtener_rutas_sistema
from ..utilidades.ayuda_logging import configurar_logger_modulo


@dataclass
class ArchivoEnCuarentena:
    ruta_original: str
    ruta_cuarentena: str
    hash_md5: str
    hash_sha256: str
    tamaño_original: int
    fecha_cuarentena: datetime
    motivo_cuarentena: str
    amenaza_detectada: str
    hash_contenido_cuarentena: str
    comprimido: bool
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el objeto a diccionario."""
        data = asdict(self)
        data['fecha_cuarentena'] = self.fecha_cuarentena.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ArchivoEnCuarentena':
        """Crea un objeto desde un diccionario."""
        data['fecha_cuarentena'] = datetime.fromisoformat(data['fecha_cuarentena'])
        return cls(**data)
    
    def obtener_nombre_archivo(self) -> str:
        """Obtiene el nombre del archivo original."""
        return Path(self.ruta_original).name
    
    def obtener_tamaño_mb(self) -> float:
        """Obtiene el tamaño en megabytes."""
        return self.tamaño_original / (1024 * 1024)
    
    def dias_en_cuarentena(self) -> int:
        """Calcula los días que lleva en cuarentena."""
        return (datetime.now() - self.fecha_cuarentena).days


class Cuarentena:
    """Sistema de cuarentena para archivos maliciosos."""
    
    def __init__(self, siem: SIEM):
        """
        Inicializa el sistema de cuarentena.
        
        Args:
            siem: Instancia del SIEM para registro de eventos
        """
        self.siem = siem
        self.logger = configurar_logger_modulo("cuarentena")
        
        # Configuración de rutas
        self.directorio_cuarentena = self._determinar_directorio_cuarentena()
        self.archivo_indice = os.path.join(self.directorio_cuarentena, "indice_cuarentena.json")
        
        # Base de datos de archivos en cuarentena
        self.archivos_cuarentena: Dict[str, ArchivoEnCuarentena] = {}
        
        # Configuración
        self.compresion_habilitada = True
        self.dias_retencion = 30  # Días para mantener archivos en cuarentena
        self.tamaño_maximo_archivo_mb = 100  # MB
        
        # Crear directorio de cuarentena si no existe
        self._crear_estructura_directorios()
        
        # Cargar archivos existentes
        self._cargar_indice()
        
        self.logger.info(f"Sistema de cuarentena inicializado en: {self.directorio_cuarentena}")
        self.siem.registrar_evento(
            TipoEvento.SISTEMA_INICIADO,
            "Sistema de cuarentena inicializado",
            {
                'directorio_cuarentena': self.directorio_cuarentena,
                'archivos_en_cuarentena': len(self.archivos_cuarentena)
            },
            "MEDIO"
        )
    
    def _determinar_directorio_cuarentena(self) -> str:
        """Determina el directorio para la cuarentena."""
        try:
            rutas_sistema = obtener_rutas_sistema()
            directorio_base = rutas_sistema['directorio_config']
            directorio_cuarentena = os.path.join(directorio_base, "cuarentena")
            
            # Verificar permisos
            Path(directorio_base).mkdir(parents=True, exist_ok=True)
            if os.access(directorio_base, os.W_OK):
                return directorio_cuarentena
        except Exception:
            pass
        
        # Usar directorio local como respaldo
        return os.path.join(str(Path.cwd()), "cuarentena")
    
    def _crear_estructura_directorios(self):
        """Crea la estructura de directorios necesaria."""
        try:
            # Directorio principal de cuarentena
            Path(self.directorio_cuarentena).mkdir(parents=True, exist_ok=True)
            
            # Subdirectorios organizados por fecha
            subdirectorios = ['activos', 'logs', 'temp']
            for subdir in subdirectorios:
                Path(self.directorio_cuarentena, subdir).mkdir(parents=True, exist_ok=True)
            
            self.logger.debug("Estructura de directorios de cuarentena creada")
        
        except Exception as e:
            self.logger.error(f"Error creando estructura de directorios: {e}")
            raise
    
    def _cargar_indice(self):
        """Carga el índice de archivos en cuarentena."""
        try:
            if os.path.exists(self.archivo_indice):
                with open(self.archivo_indice, 'r', encoding='utf-8') as archivo:
                    datos = json.load(archivo)
                    
                    for hash_archivo, datos_archivo in datos.items():
                        archivo_cuarentena = ArchivoEnCuarentena.from_dict(datos_archivo)
                        self.archivos_cuarentena[hash_archivo] = archivo_cuarentena
                
                self.logger.info(f"Índice de cuarentena cargado: {len(self.archivos_cuarentena)} archivos")
        
        except Exception as e:
            self.logger.warning(f"Error cargando índice de cuarentena: {e}")
    
    def _guardar_indice(self):
        """Guarda el índice de archivos en cuarentena."""
        try:
            crear_ruta_segura(self.archivo_indice)
            
            datos = {}
            for hash_archivo, archivo_cuarentena in self.archivos_cuarentena.items():
                datos[hash_archivo] = archivo_cuarentena.to_dict()
            
            with open(self.archivo_indice, 'w', encoding='utf-8') as archivo:
                json.dump(datos, archivo, ensure_ascii=False, indent=2)
            
            self.logger.debug("Índice de cuarentena guardado")
        
        except Exception as e:
            self.logger.error(f"Error guardando índice de cuarentena: {e}")
    
    def _calcular_hash_archivo(self, ruta_archivo: str) -> tuple[str, str]:
        """
        Calcula hashes MD5 y SHA256 de un archivo.
        
        Args:
            ruta_archivo: Ruta del archivo
            
        Returns:
            tuple[str, str]: Hash MD5 y SHA256
        """
        hash_md5 = hashlib.md5()
        hash_sha256 = hashlib.sha256()
        
        with open(ruta_archivo, 'rb') as archivo:
            while chunk := archivo.read(8192):
                hash_md5.update(chunk)
                hash_sha256.update(chunk)
        
        return hash_md5.hexdigest(), hash_sha256.hexdigest()
    
    def _generar_nombre_cuarentena(self, ruta_original: str, hash_sha256: str) -> str:
        """
        Genera un nombre único para el archivo en cuarentena.
        
        Args:
            ruta_original: Ruta original del archivo
            hash_sha256: Hash SHA256 del archivo
            
        Returns:
            str: Nombre único para cuarentena
        """
        timestamp = int(time.time())
        nombre_original = Path(ruta_original).name
        extension = ".qtn"  # Extensión para archivos en cuarentena
        
        if self.compresion_habilitada:
            extension = ".qtn.gz"
        
        nombre_cuarentena = f"{timestamp}_{hash_sha256[:16]}_{nombre_original}{extension}"
        return os.path.join(self.directorio_cuarentena, "activos", nombre_cuarentena)
    
    def poner_en_cuarentena(self, ruta_archivo: str, motivo: str, amenaza_detectada: str = "") -> bool:
        """
        Pone un archivo en cuarentena.
        
        Args:
            ruta_archivo: Ruta del archivo a poner en cuarentena
            motivo: Motivo de la cuarentena
            amenaza_detectada: Tipo de amenaza detectada
            
        Returns:
            bool: True si se puso en cuarentena exitosamente
        """
        try:
            # Validaciones
            if not validar_ruta_archivo(ruta_archivo):
                self.logger.warning(f"Archivo no válido para cuarentena: {ruta_archivo}")
                return False
            
            if not validar_permisos_lectura(ruta_archivo):
                self.logger.warning(f"Sin permisos para leer archivo: {ruta_archivo}")
                return False
            
            # Verificar tamaño del archivo
            tamaño_archivo = os.path.getsize(ruta_archivo)
            if tamaño_archivo > (self.tamaño_maximo_archivo_mb * 1024 * 1024):
                self.logger.warning(f"Archivo demasiado grande para cuarentena: {ruta_archivo}")
                return False
            
            # Calcular hashes
            hash_md5, hash_sha256 = self._calcular_hash_archivo(ruta_archivo)
            
            # Verificar si ya está en cuarentena
            if hash_sha256 in self.archivos_cuarentena:
                self.logger.info(f"Archivo ya está en cuarentena: {ruta_archivo}")
                return True
            
            # Generar ruta de cuarentena
            ruta_cuarentena = self._generar_nombre_cuarentena(ruta_archivo, hash_sha256)
            
            # Copiar y procesar archivo
            if self.compresion_habilitada:
                # Comprimir archivo en cuarentena
                with open(ruta_archivo, 'rb') as archivo_origen:
                    with gzip.open(ruta_cuarentena, 'wb') as archivo_destino:
                        shutil.copyfileobj(archivo_origen, archivo_destino)
            else:
                # Copiar archivo sin comprimir
                shutil.copy2(ruta_archivo, ruta_cuarentena)
            
            # Calcular hash del contenido en cuarentena
            hash_contenido_cuarentena = hashlib.sha256()
            with open(ruta_cuarentena, 'rb') as archivo:
                while chunk := archivo.read(8192):
                    hash_contenido_cuarentena.update(chunk)
            
            # Crear registro de cuarentena
            archivo_cuarentena = ArchivoEnCuarentena(
                ruta_original=os.path.abspath(ruta_archivo),
                ruta_cuarentena=ruta_cuarentena,
                hash_md5=hash_md5,
                hash_sha256=hash_sha256,
                tamaño_original=tamaño_archivo,
                fecha_cuarentena=datetime.now(),
                motivo_cuarentena=motivo,
                amenaza_detectada=amenaza_detectada,
                hash_contenido_cuarentena=hash_contenido_cuarentena.hexdigest(),
                comprimido=self.compresion_habilitada
            )
            
            # Agregar al índice
            self.archivos_cuarentena[hash_sha256] = archivo_cuarentena
            
            # Guardar índice
            self._guardar_indice()
            
            # Registrar en SIEM
            self.siem.registrar_evento(
                TipoEvento.ARCHIVO_CUARENTENA,
                f"Archivo puesto en cuarentena: {ruta_archivo}",
                {
                    'ruta_original': ruta_archivo,
                    'ruta_cuarentena': ruta_cuarentena,
                    'hash_sha256': hash_sha256,
                    'motivo': motivo,
                    'amenaza_detectada': amenaza_detectada,
                    'tamaño_mb': round(tamaño_archivo / (1024 * 1024), 2)
                },
                "ALTO"
            )
            
            self.logger.info(f"Archivo puesto en cuarentena exitosamente: {ruta_archivo}")
            
            # Eliminar archivo original si está fuera del directorio de cuarentena
            try:
                if not ruta_archivo.startswith(self.directorio_cuarentena):
                    os.remove(ruta_archivo)
                    self.logger.info(f"Archivo original eliminado: {ruta_archivo}")
            except Exception as e:
                self.logger.warning(f"No se pudo eliminar archivo original {ruta_archivo}: {e}")
            
            return True
        
        except Exception as e:
            self.logger.error(f"Error poniendo archivo en cuarentena {ruta_archivo}: {e}")
            return False
    
    def restaurar_archivo(self, hash_sha256: str, ruta_destino: Optional[str] = None) -> bool:
        """
        Restaura un archivo de la cuarentena.
        
        Args:
            hash_sha256: Hash SHA256 del archivo a restaurar
            ruta_destino: Ruta de destino opcional, si no se especifica usa la original
            
        Returns:
            bool: True si se restauró exitosamente
        """
        try:
            if hash_sha256 not in self.archivos_cuarentena:
                self.logger.warning(f"Archivo no encontrado en cuarentena: {hash_sha256}")
                return False
            
            archivo_cuarentena = self.archivos_cuarentena[hash_sha256]
            
            # Determinar ruta de destino
            if ruta_destino is None:
                ruta_destino = archivo_cuarentena.ruta_original
            
            # Verificar que el archivo en cuarentena existe
            if not os.path.exists(archivo_cuarentena.ruta_cuarentena):
                self.logger.error(f"Archivo en cuarentena no encontrado: {archivo_cuarentena.ruta_cuarentena}")
                return False
            
            # Crear directorio de destino si no existe
            crear_ruta_segura(ruta_destino)
            
            # Restaurar archivo
            if archivo_cuarentena.comprimido:
                # Descomprimir archivo
                with gzip.open(archivo_cuarentena.ruta_cuarentena, 'rb') as archivo_origen:
                    with open(ruta_destino, 'wb') as archivo_destino:
                        shutil.copyfileobj(archivo_origen, archivo_destino)
            else:
                # Copiar archivo sin descomprimir
                shutil.copy2(archivo_cuarentena.ruta_cuarentena, ruta_destino)
            
            # Verificar integridad del archivo restaurado
            hash_md5_restaurado, hash_sha256_restaurado = self._calcular_hash_archivo(ruta_destino)
            
            if hash_sha256_restaurado != hash_sha256:
                self.logger.error(f"Error de integridad al restaurar archivo: {hash_sha256}")
                os.remove(ruta_destino)
                return False
            
            # Registrar en SIEM
            self.siem.registrar_evento(
                TipoEvento.ARCHIVO_RESTAURADO,
                f"Archivo restaurado de cuarentena: {ruta_destino}",
                {
                    'ruta_original': archivo_cuarentena.ruta_original,
                    'ruta_destino': ruta_destino,
                    'hash_sha256': hash_sha256,
                    'fecha_cuarentena': archivo_cuarentena.fecha_cuarentena.isoformat()
                },
                "MEDIO"
            )
            
            self.logger.info(f"Archivo restaurado exitosamente: {ruta_destino}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error restaurando archivo {hash_sha256}: {e}")
            return False
    
    def eliminar_de_cuarentena(self, hash_sha256: str) -> bool:
        """
        Elimina permanentemente un archivo de la cuarentena.
        
        Args:
            hash_sha256: Hash SHA256 del archivo a eliminar
            
        Returns:
            bool: True si se eliminó exitosamente
        """
        try:
            if hash_sha256 not in self.archivos_cuarentena:
                self.logger.warning(f"Archivo no encontrado en cuarentena: {hash_sha256}")
                return False
            
            archivo_cuarentena = self.archivos_cuarentena[hash_sha256]
            
            # Eliminar archivo físico
            if os.path.exists(archivo_cuarentena.ruta_cuarentena):
                os.remove(archivo_cuarentena.ruta_cuarentena)
            
            # Eliminar del índice
            del self.archivos_cuarentena[hash_sha256]
            
            # Guardar índice
            self._guardar_indice()
            
            # Registrar en SIEM
            self.siem.registrar_evento(
                TipoEvento.INFORMACION,
                f"Archivo eliminado permanentemente de cuarentena",
                {
                    'ruta_original': archivo_cuarentena.ruta_original,
                    'hash_sha256': hash_sha256,
                    'fecha_cuarentena': archivo_cuarentena.fecha_cuarentena.isoformat()
                },
                "MEDIO"
            )
            
            self.logger.info(f"Archivo eliminado de cuarentena: {hash_sha256}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error eliminando archivo de cuarentena {hash_sha256}: {e}")
            return False
    
    def limpiar_archivos_antiguos(self) -> Dict[str, Any]:
        """
        Limpia archivos antiguos de la cuarentena según la política de retención.
        
        Returns:
            Dict[str, Any]: Estadísticas de la limpieza
        """
        archivos_eliminados = 0
        errores = 0
        
        fecha_limite = datetime.now().timestamp() - (self.dias_retencion * 24 * 3600)
        
        archivos_a_eliminar = []
        
        for hash_sha256, archivo_cuarentena in self.archivos_cuarentena.items():
            if archivo_cuarentena.fecha_cuarentena.timestamp() < fecha_limite:
                archivos_a_eliminar.append(hash_sha256)
        
        for hash_sha256 in archivos_a_eliminar:
            if self.eliminar_de_cuarentena(hash_sha256):
                archivos_eliminados += 1
            else:
                errores += 1
        
        estadisticas = {
            'archivos_eliminados': archivos_eliminados,
            'errores': errores,
            'dias_retencion': self.dias_retencion,
            'timestamp': datetime.now().isoformat()
        }
        
        if archivos_eliminados > 0:
            self.siem.registrar_evento(
                TipoEvento.INFORMACION,
                f"Limpieza de cuarentena completada",
                estadisticas,
                "MEDIO"
            )
        
        self.logger.info(f"Limpieza de cuarentena: {archivos_eliminados} archivos eliminados")
        
        return estadisticas
    
    def listar_archivos_cuarentena(self) -> List[ArchivoEnCuarentena]:
        """
        Lista todos los archivos en cuarentena.
        
        Returns:
            List[ArchivoEnCuarentena]: Lista de archivos en cuarentena
        """
        return list(self.archivos_cuarentena.values())
    
    def buscar_archivo(self, termino_busqueda: str) -> List[ArchivoEnCuarentena]:
        """
        Busca archivos en cuarentena por nombre o ruta.
        
        Args:
            termino_busqueda: Término de búsqueda
            
        Returns:
            List[ArchivoEnCuarentena]: Archivos que coinciden con la búsqueda
        """
        resultados = []
        termino_lower = termino_busqueda.lower()
        
        for archivo in self.archivos_cuarentena.values():
            if (termino_lower in archivo.ruta_original.lower() or
                termino_lower in archivo.amenaza_detectada.lower() or
                termino_lower in archivo.motivo_cuarentena.lower()):
                resultados.append(archivo)
        
        return resultados
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del sistema de cuarentena.
        
        Returns:
            Dict[str, Any]: Estadísticas de la cuarentena
        """
        if not self.archivos_cuarentena:
            return {
                'total_archivos': 0,
                'tamaño_total_mb': 0,
                'directorio_cuarentena': self.directorio_cuarentena,
                'compresion_habilitada': self.compresion_habilitada,
                'dias_retencion': self.dias_retencion
            }
        
        tamaño_total = sum(archivo.tamaño_original for archivo in self.archivos_cuarentena.values())
        
        # Agrupar por amenaza
        amenazas = {}
        for archivo in self.archivos_cuarentena.values():
            amenaza = archivo.amenaza_detectada or "No especificada"
            amenazas[amenaza] = amenazas.get(amenaza, 0) + 1
        
        # Archivo más antiguo
        archivo_mas_antiguo = min(
            self.archivos_cuarentena.values(),
            key=lambda x: x.fecha_cuarentena
        )
        
        return {
            'total_archivos': len(self.archivos_cuarentena),
            'tamaño_total_mb': round(tamaño_total / (1024 * 1024), 2),
            'directorio_cuarentena': self.directorio_cuarentena,
            'compresion_habilitada': self.compresion_habilitada,
            'dias_retencion': self.dias_retencion,
            'amenazas_detectadas': amenazas,
            'archivo_mas_antiguo': {
                'nombre': archivo_mas_antiguo.obtener_nombre_archivo(),
                'fecha_cuarentena': archivo_mas_antiguo.fecha_cuarentena.isoformat(),
                'dias_en_cuarentena': archivo_mas_antiguo.dias_en_cuarentena()
            }
        }
    
    def generar_reporte_markdown(self) -> str:
        """
        Genera un reporte de cuarentena en formato Markdown.
        
        Returns:
            str: Reporte en formato Markdown
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        estadisticas = self.obtener_estadisticas()
        
        md = f"# Reporte del Sistema de Cuarentena\n\n"
        md += f"**Fecha:** {timestamp}\n"
        md += f"**Directorio:** `{self.directorio_cuarentena}`\n\n"
        
        # Estadísticas generales
        md += "## 📊 Estadísticas Generales\n\n"
        md += f"- **Total de archivos:** {estadisticas['total_archivos']}\n"
        md += f"- **Tamaño total:** {estadisticas['tamaño_total_mb']} MB\n"
        md += f"- **Compresión habilitada:** {'✅ Sí' if estadisticas['compresion_habilitada'] else '❌ No'}\n"
        md += f"- **Días de retención:** {estadisticas['dias_retencion']}\n\n"
        
        if estadisticas['total_archivos'] == 0:
            md += "## ✅ Sin Archivos en Cuarentena\n\n"
            md += "Actualmente no hay archivos en cuarentena.\n\n"
            return md
        
        # Amenazas detectadas
        if 'amenazas_detectadas' in estadisticas:
            md += "## 🦠 Amenazas Detectadas\n\n"
            md += "| Tipo de Amenaza | Cantidad |\n"
            md += "|-----------------|----------|\n"
            
            for amenaza, cantidad in estadisticas['amenazas_detectadas'].items():
                md += f"| {amenaza} | {cantidad} |\n"
            
            md += "\n"
        
        # Archivos en cuarentena (últimos 20)
        archivos = sorted(
            self.archivos_cuarentena.values(),
            key=lambda x: x.fecha_cuarentena,
            reverse=True
        )[:20]
        
        if archivos:
            md += "## 📋 Archivos en Cuarentena (Últimos 20)\n\n"
            md += "| Archivo | Amenaza | Fecha | Tamaño (MB) | Días |\n"
            md += "|---------|---------|--------|-------------|------|\n"
            
            for archivo in archivos:
                nombre = archivo.obtener_nombre_archivo()[:30] + "..." if len(archivo.obtener_nombre_archivo()) > 30 else archivo.obtener_nombre_archivo()
                amenaza = archivo.amenaza_detectada[:20] + "..." if len(archivo.amenaza_detectada) > 20 else archivo.amenaza_detectada
                fecha = archivo.fecha_cuarentena.strftime('%Y-%m-%d')
                tamaño_mb = round(archivo.obtener_tamaño_mb(), 2)
                dias = archivo.dias_en_cuarentena()
                
                md += f"| `{nombre}` | {amenaza} | {fecha} | {tamaño_mb} | {dias} |\n"
            
            md += "\n"
        
        return md
