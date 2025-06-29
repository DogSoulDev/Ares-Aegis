"""
Módulo de Gestión de Cuarentena
Sistema para aislar y gestionar archivos sospechosos o maliciosos.

Este módulo permite mover archivos a cuarentena, listarlos, restaurarlos
y eliminarlos permanentemente, manteniendo metadatos de cada archivo.
"""

import os
import json
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import hashlib

from .siem import SIEM, TipoEvento


class ArchivoEnCuarentena:
    """Clase para representar un archivo en cuarentena."""
    
    def __init__(self, ruta_original: str, motivo: str, hash_archivo: Optional[str] = None):
        """
        Inicializa un archivo en cuarentena.
        
        Args:
            ruta_original: Ruta original del archivo antes de la cuarentena
            motivo: Motivo por el cual fue puesto en cuarentena
            hash_archivo: Hash SHA256 del archivo (se calcula si no se proporciona)
        """
        self.ruta_original = ruta_original
        self.nombre_original = os.path.basename(ruta_original)
        self.motivo = motivo
        self.timestamp_cuarentena = datetime.now()
        self.hash_sha256 = hash_archivo or ""
        self.id_cuarentena = self._generar_id()
        self.tamano_bytes = 0
        
        # Si el archivo original aún existe, obtener información adicional
        if os.path.isfile(ruta_original):
            try:
                stat_info = os.stat(ruta_original)
                self.tamano_bytes = stat_info.st_size
                if not self.hash_sha256:
                    self.hash_sha256 = self._calcular_hash(ruta_original)
            except Exception:
                pass
    
    def _generar_id(self) -> str:
        """Genera un ID único para el archivo en cuarentena."""
        timestamp_str = self.timestamp_cuarentena.strftime('%Y%m%d_%H%M%S')
        hash_ruta = hashlib.md5(self.ruta_original.encode()).hexdigest()[:8]
        return f"Q_{timestamp_str}_{hash_ruta}"
    
    def _calcular_hash(self, ruta: str) -> str:
        """Calcula el hash SHA256 del archivo."""
        try:
            with open(ruta, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el archivo a diccionario para serialización."""
        return {
            "id_cuarentena": self.id_cuarentena,
            "ruta_original": self.ruta_original,
            "nombre_original": self.nombre_original,
            "motivo": self.motivo,
            "timestamp_cuarentena": self.timestamp_cuarentena.isoformat(),
            "hash_sha256": self.hash_sha256,
            "tamano_bytes": self.tamano_bytes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ArchivoEnCuarentena':
        """Crea una instancia desde un diccionario."""
        archivo = cls.__new__(cls)
        archivo.id_cuarentena = data["id_cuarentena"]
        archivo.ruta_original = data["ruta_original"]
        archivo.nombre_original = data["nombre_original"]
        archivo.motivo = data["motivo"]
        archivo.timestamp_cuarentena = datetime.fromisoformat(data["timestamp_cuarentena"])
        archivo.hash_sha256 = data["hash_sha256"]
        archivo.tamano_bytes = data["tamano_bytes"]
        return archivo
    
    def to_markdown(self) -> str:
        """Convierte la información del archivo a formato Markdown."""
        timestamp_str = self.timestamp_cuarentena.strftime('%Y-%m-%d %H:%M:%S')
        tamano_mb = self.tamano_bytes / (1024 * 1024) if self.tamano_bytes > 0 else 0
        
        markdown = f"### Archivo en Cuarentena: `{self.nombre_original}`\n\n"
        markdown += f"- **ID:** `{self.id_cuarentena}`\n"
        markdown += f"- **Ruta Original:** `{self.ruta_original}`\n"
        markdown += f"- **Motivo:** {self.motivo}\n"
        markdown += f"- **Fecha de Cuarentena:** {timestamp_str}\n"
        markdown += f"- **Tamaño:** {tamano_mb:.2f} MB ({self.tamano_bytes} bytes)\n"
        
        if self.hash_sha256:
            markdown += f"- **Hash SHA256:** `{self.hash_sha256}`\n"
        
        markdown += "\n"
        return markdown


class GestorCuarentena:
    """Gestor para el manejo de archivos en cuarentena."""
    
    def __init__(self, siem: SIEM, directorio_cuarentena: Optional[Path] = None):
        """
        Inicializa el gestor de cuarentena.
        
        Args:
            siem: Instancia del SIEM para logging
            directorio_cuarentena: Directorio para almacenar archivos en cuarentena
        """
        self.siem = siem
        self.logger = logging.getLogger(__name__)
        
        # Configurar directorio de cuarentena
        if directorio_cuarentena is None:
            try:
                self.directorio_cuarentena = Path("/var/ares_aegis_cuarentena")
                self.directorio_cuarentena.mkdir(parents=True, exist_ok=True, mode=0o700)
            except PermissionError:
                # Fallback para desarrollo
                self.directorio_cuarentena = Path.home() / ".ares_aegis" / "cuarentena"
                self.directorio_cuarentena.mkdir(parents=True, exist_ok=True, mode=0o700)
        else:
            self.directorio_cuarentena = directorio_cuarentena
            self.directorio_cuarentena.mkdir(parents=True, exist_ok=True, mode=0o700)
        
        # Archivo de metadatos
        self.archivo_metadatos = self.directorio_cuarentena / "metadatos.json"
        
        # Diccionario de archivos en cuarentena
        self.archivos_cuarentena: Dict[str, ArchivoEnCuarentena] = {}
        
        self._cargar_metadatos()
        self.siem.log_evento(TipoEvento.SISTEMA_EVENTO, "Gestor de cuarentena inicializado",
                           {"directorio": str(self.directorio_cuarentena)})
    
    def poner_en_cuarentena(self, ruta_archivo: str, motivo: str) -> str:
        """
        Mueve un archivo a cuarentena.
        
        Args:
            ruta_archivo: Ruta del archivo a poner en cuarentena
            motivo: Motivo de la cuarentena
            
        Returns:
            ID del archivo en cuarentena
            
        Raises:
            FileNotFoundError: Si el archivo no existe
            PermissionError: Si no hay permisos para mover el archivo
        """
        if not os.path.isfile(ruta_archivo):
            raise FileNotFoundError(f"El archivo no existe: {ruta_archivo}")
        
        self.logger.info(f"Poniendo en cuarentena: {ruta_archivo}")
        
        # Crear objeto de archivo en cuarentena
        archivo_cuarentena = ArchivoEnCuarentena(ruta_archivo, motivo)
        
        # Definir ruta en cuarentena
        nombre_cuarentena = f"{archivo_cuarentena.id_cuarentena}_{archivo_cuarentena.nombre_original}"
        ruta_cuarentena = self.directorio_cuarentena / nombre_cuarentena
        
        try:
            # Mover archivo a cuarentena
            shutil.move(ruta_archivo, ruta_cuarentena)
            
            # Cambiar permisos para evitar ejecución accidental
            os.chmod(ruta_cuarentena, 0o600)
            
            # Agregar a la lista de archivos en cuarentena
            self.archivos_cuarentena[archivo_cuarentena.id_cuarentena] = archivo_cuarentena
            
            # Guardar metadatos
            self._guardar_metadatos()
            
            # Log del evento
            self.siem.log_evento(TipoEvento.ARCHIVO_CUARENTENA,
                               f"Archivo puesto en cuarentena: {ruta_archivo}",
                               {"id": archivo_cuarentena.id_cuarentena, "motivo": motivo})
            
            return archivo_cuarentena.id_cuarentena
            
        except Exception as e:
            error_msg = f"Error moviendo archivo a cuarentena {ruta_archivo}: {e}"
            self.logger.error(error_msg)
            self.siem.log_evento(TipoEvento.ERROR, error_msg)
            raise
    
    def listar_archivos_cuarentena(self) -> List[ArchivoEnCuarentena]:
        """
        Lista todos los archivos en cuarentena.
        
        Returns:
            Lista de archivos en cuarentena
        """
        return list(self.archivos_cuarentena.values())
    
    def obtener_archivo_cuarentena(self, id_cuarentena: str) -> Optional[ArchivoEnCuarentena]:
        """
        Obtiene información de un archivo específico en cuarentena.
        
        Args:
            id_cuarentena: ID del archivo en cuarentena
            
        Returns:
            Información del archivo o None si no existe
        """
        return self.archivos_cuarentena.get(id_cuarentena)
    
    def restaurar_archivo(self, id_cuarentena: str, 
                         ruta_destino: Optional[str] = None) -> bool:
        """
        Restaura un archivo desde la cuarentena.
        
        Args:
            id_cuarentena: ID del archivo en cuarentena
            ruta_destino: Ruta de destino (opcional, usa la original si no se especifica)
            
        Returns:
            True si se restauró exitosamente, False en caso contrario
        """
        if id_cuarentena not in self.archivos_cuarentena:
            self.logger.error(f"Archivo en cuarentena no encontrado: {id_cuarentena}")
            return False
        
        archivo_cuarentena = self.archivos_cuarentena[id_cuarentena]
        
        # Determinar ruta de destino
        if ruta_destino is None:
            ruta_destino = archivo_cuarentena.ruta_original
        
        # Verificar si la ruta de destino ya existe
        if os.path.exists(ruta_destino):
            self.logger.warning(f"El archivo de destino ya existe: {ruta_destino}")
            return False
        
        # Construir ruta del archivo en cuarentena
        nombre_cuarentena = f"{id_cuarentena}_{archivo_cuarentena.nombre_original}"
        ruta_cuarentena = self.directorio_cuarentena / nombre_cuarentena
        
        if not ruta_cuarentena.exists():
            self.logger.error(f"Archivo físico en cuarentena no encontrado: {ruta_cuarentena}")
            return False
        
        try:
            # Crear directorio de destino si no existe
            os.makedirs(os.path.dirname(ruta_destino), exist_ok=True)
            
            # Mover archivo de vuelta
            shutil.move(str(ruta_cuarentena), ruta_destino)
            
            # Restaurar permisos (básicos)
            os.chmod(ruta_destino, 0o644)
            
            # Eliminar de la lista de cuarentena
            del self.archivos_cuarentena[id_cuarentena]
            
            # Guardar metadatos actualizados
            self._guardar_metadatos()
            
            # Log del evento
            self.siem.log_evento(TipoEvento.ARCHIVO_CUARENTENA,
                               f"Archivo restaurado desde cuarentena: {ruta_destino}",
                               {"id": id_cuarentena, "ruta_original": archivo_cuarentena.ruta_original})
            
            self.logger.info(f"Archivo restaurado exitosamente: {id_cuarentena} -> {ruta_destino}")
            return True
            
        except Exception as e:
            error_msg = f"Error restaurando archivo {id_cuarentena}: {e}"
            self.logger.error(error_msg)
            self.siem.log_evento(TipoEvento.ERROR, error_msg)
            return False
    
    def eliminar_permanentemente(self, id_cuarentena: str) -> bool:
        """
        Elimina permanentemente un archivo de la cuarentena.
        
        Args:
            id_cuarentena: ID del archivo en cuarentena
            
        Returns:
            True si se eliminó exitosamente, False en caso contrario
        """
        if id_cuarentena not in self.archivos_cuarentena:
            self.logger.error(f"Archivo en cuarentena no encontrado: {id_cuarentena}")
            return False
        
        archivo_cuarentena = self.archivos_cuarentena[id_cuarentena]
        
        # Construir ruta del archivo en cuarentena
        nombre_cuarentena = f"{id_cuarentena}_{archivo_cuarentena.nombre_original}"
        ruta_cuarentena = self.directorio_cuarentena / nombre_cuarentena
        
        try:
            # Eliminar archivo físico si existe
            if ruta_cuarentena.exists():
                os.remove(ruta_cuarentena)
            
            # Eliminar de la lista de cuarentena
            del self.archivos_cuarentena[id_cuarentena]
            
            # Guardar metadatos actualizados
            self._guardar_metadatos()
            
            # Log del evento
            self.siem.log_evento(TipoEvento.ARCHIVO_CUARENTENA,
                               f"Archivo eliminado permanentemente de cuarentena",
                               {"id": id_cuarentena, "ruta_original": archivo_cuarentena.ruta_original})
            
            self.logger.info(f"Archivo eliminado permanentemente: {id_cuarentena}")
            return True
            
        except Exception as e:
            error_msg = f"Error eliminando archivo {id_cuarentena}: {e}"
            self.logger.error(error_msg)
            self.siem.log_evento(TipoEvento.ERROR, error_msg)
            return False
    
    def limpiar_cuarentena_antigua(self, dias: int = 30) -> int:
        """
        Elimina archivos en cuarentena más antiguos que el número de días especificado.
        
        Args:
            dias: Número de días para conservar archivos en cuarentena
            
        Returns:
            Número de archivos eliminados
        """
        fecha_limite = datetime.now().timestamp() - (dias * 24 * 3600)
        archivos_eliminados = 0
        
        archivos_a_eliminar = []
        for id_cuarentena, archivo in self.archivos_cuarentena.items():
            if archivo.timestamp_cuarentena.timestamp() < fecha_limite:
                archivos_a_eliminar.append(id_cuarentena)
        
        for id_cuarentena in archivos_a_eliminar:
            if self.eliminar_permanentemente(id_cuarentena):
                archivos_eliminados += 1
        
        if archivos_eliminados > 0:
            self.siem.log_evento(TipoEvento.SISTEMA_EVENTO,
                               f"Limpieza automática de cuarentena: {archivos_eliminados} archivos eliminados")
        
        return archivos_eliminados
    
    def _cargar_metadatos(self):
        """Carga los metadatos de archivos en cuarentena."""
        try:
            if self.archivo_metadatos.exists():
                with open(self.archivo_metadatos, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for archivo_data in data.get("archivos", []):
                    archivo = ArchivoEnCuarentena.from_dict(archivo_data)
                    self.archivos_cuarentena[archivo.id_cuarentena] = archivo
                
                self.logger.info(f"Metadatos de cuarentena cargados: {len(self.archivos_cuarentena)} archivos")
        except Exception as e:
            self.logger.error(f"Error cargando metadatos de cuarentena: {e}")
    
    def _guardar_metadatos(self):
        """Guarda los metadatos de archivos en cuarentena."""
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "directorio_cuarentena": str(self.directorio_cuarentena),
                "archivos": [archivo.to_dict() for archivo in self.archivos_cuarentena.values()]
            }
            
            with open(self.archivo_metadatos, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            self.logger.error(f"Error guardando metadatos de cuarentena: {e}")
    
    def generar_reporte_markdown(self) -> str:
        """
        Genera un reporte en Markdown de los archivos en cuarentena.
        
        Returns:
            String con el reporte en formato Markdown
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        markdown = f"# Reporte de Cuarentena\n\n"
        markdown += f"**Fecha:** {timestamp}\n"
        markdown += f"**Directorio de Cuarentena:** `{self.directorio_cuarentena}`\n"
        markdown += f"**Archivos en Cuarentena:** {len(self.archivos_cuarentena)}\n\n"
        
        if not self.archivos_cuarentena:
            markdown += "## ✅ Estado: CUARENTENA VACÍA\n\n"
            markdown += "No hay archivos actualmente en cuarentena.\n\n"
        else:
            markdown += "## 📋 Archivos en Cuarentena\n\n"
            
            # Calcular estadísticas
            total_tamano = sum(archivo.tamano_bytes for archivo in self.archivos_cuarentena.values())
            total_mb = total_tamano / (1024 * 1024)
            
            markdown += f"**Espacio total ocupado:** {total_mb:.2f} MB\n\n"
            
            # Listar archivos ordenados por fecha (más recientes primero)
            archivos_ordenados = sorted(self.archivos_cuarentena.values(),
                                      key=lambda x: x.timestamp_cuarentena, reverse=True)
            
            for archivo in archivos_ordenados:
                markdown += archivo.to_markdown()
        
        return markdown
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas de la cuarentena."""
        total_tamano = sum(archivo.tamano_bytes for archivo in self.archivos_cuarentena.values())
        
        return {
            "total_archivos": len(self.archivos_cuarentena),
            "espacio_ocupado_bytes": total_tamano,
            "espacio_ocupado_mb": total_tamano / (1024 * 1024),
            "directorio_cuarentena": str(self.directorio_cuarentena),
            "archivo_metadatos": str(self.archivo_metadatos)
        }
