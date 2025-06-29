#!/usr/bin/env python3
"""
Cuarentena - Ares Aegis
Módulo para gestión de archivos en cuarentena

Autor: DogSoulDev
Versión: 2.0.0
"""

import os
import shutil
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime


class ArchivoEnCuarentena:
    """Representa un archivo en cuarentena."""
    
    def __init__(self, ruta_original: str, ruta_cuarentena: str, 
                 razon: str = "", hash_archivo: str = ""):
        self.ruta_original = ruta_original
        self.ruta_cuarentena = ruta_cuarentena
        self.razon = razon
        self.hash_archivo = hash_archivo
        self.fecha_cuarentena = datetime.now()
        self.id_cuarentena = self._generar_id()
    
    def _generar_id(self) -> str:
        """Genera un ID único para el archivo en cuarentena."""
        datos = f"{self.ruta_original}{self.fecha_cuarentena.isoformat()}"
        return hashlib.md5(datos.encode()).hexdigest()[:8]
    
    def a_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para serialización."""
        return {
            'id_cuarentena': self.id_cuarentena,
            'ruta_original': self.ruta_original,
            'ruta_cuarentena': self.ruta_cuarentena,
            'razon': self.razon,
            'hash_archivo': self.hash_archivo,
            'fecha_cuarentena': self.fecha_cuarentena.isoformat()
        }
    
    @classmethod
    def desde_dict(cls, datos: Dict[str, Any]) -> 'ArchivoEnCuarentena':
        """Crea instancia desde diccionario."""
        archivo = cls(
            datos['ruta_original'],
            datos['ruta_cuarentena'],
            datos['razon'],
            datos['hash_archivo']
        )
        archivo.id_cuarentena = datos['id_cuarentena']
        archivo.fecha_cuarentena = datetime.fromisoformat(datos['fecha_cuarentena'])
        return archivo


class GestorCuarentena:
    """Gestor para el manejo de archivos en cuarentena."""
    
    def __init__(self, directorio_cuarentena: Optional[str] = None, siem=None):
        self.siem = siem
        
        if directorio_cuarentena:
            self.directorio_cuarentena = Path(directorio_cuarentena)
        else:
            self.directorio_cuarentena = Path.home() / ".ares_aegis" / "cuarentena"
        
        self.directorio_cuarentena.mkdir(parents=True, exist_ok=True)
        
        self.archivo_registro = self.directorio_cuarentena / "registro.json"
        self.archivos_cuarentena: List[ArchivoEnCuarentena] = []
        
        self._cargar_registro()
        
        if self.siem:
            self.siem.registrar_evento('INFO', 'cuarentena', 
                                     f'Gestor de cuarentena inicializado: {self.directorio_cuarentena}')
    
    def _cargar_registro(self):
        """Carga el registro de archivos en cuarentena."""
        if self.archivo_registro.exists():
            try:
                with open(self.archivo_registro, 'r', encoding='utf-8') as archivo:
                    datos = json.load(archivo)
                    self.archivos_cuarentena = [
                        ArchivoEnCuarentena.desde_dict(item) for item in datos
                    ]
                
                if self.siem:
                    self.siem.registrar_evento('INFO', 'cuarentena', 
                                             f'Registro cargado: {len(self.archivos_cuarentena)} archivos')
            except Exception as e:
                if self.siem:
                    self.siem.registrar_evento('ERROR', 'cuarentena', 
                                             f'Error cargando registro: {e}')
                self.archivos_cuarentena = []
    
    def _guardar_registro(self):
        """Guarda el registro de archivos en cuarentena."""
        try:
            datos = [archivo.a_dict() for archivo in self.archivos_cuarentena]
            with open(self.archivo_registro, 'w', encoding='utf-8') as archivo:
                json.dump(datos, archivo, indent=2, ensure_ascii=False)
            
            if self.siem:
                self.siem.registrar_evento('INFO', 'cuarentena', 
                                         f'Registro guardado: {len(self.archivos_cuarentena)} archivos')
        except Exception as e:
            if self.siem:
                self.siem.registrar_evento('ERROR', 'cuarentena', 
                                         f'Error guardando registro: {e}')
    
    def poner_en_cuarentena(self, ruta_archivo: str, razon: str = "") -> bool:
        """
        Mueve un archivo a cuarentena.
        
        Args:
            ruta_archivo: Ruta del archivo a poner en cuarentena
            razon: Razón por la cual se pone en cuarentena
            
        Returns:
            True si se movió exitosamente, False en caso contrario
        """
        archivo_original = Path(ruta_archivo)
        
        if not archivo_original.exists():
            if self.siem:
                self.siem.registrar_evento('WARNING', 'cuarentena', 
                                         f'Archivo no encontrado para cuarentena: {ruta_archivo}')
            return False
        
        try:
            # Calcular hash del archivo
            with open(archivo_original, 'rb') as f:
                hash_archivo = hashlib.sha256(f.read()).hexdigest()
            
            # Generar nombre único para cuarentena
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_cuarentena = f"{timestamp}_{hash_archivo[:8]}_{archivo_original.name}"
            ruta_cuarentena = self.directorio_cuarentena / nombre_cuarentena
            
            # Mover archivo a cuarentena
            shutil.move(str(archivo_original), str(ruta_cuarentena))
            
            # Crear registro
            archivo_cuarentena = ArchivoEnCuarentena(
                str(archivo_original),
                str(ruta_cuarentena),
                razon,
                hash_archivo
            )
            
            self.archivos_cuarentena.append(archivo_cuarentena)
            self._guardar_registro()
            
            if self.siem:
                self.siem.registrar_evento('HIGH', 'cuarentena', 
                                         f'Archivo puesto en cuarentena: {ruta_archivo} -> {ruta_cuarentena}')
            
            return True
            
        except Exception as e:
            if self.siem:
                self.siem.registrar_evento('ERROR', 'cuarentena', 
                                         f'Error poniendo archivo en cuarentena {ruta_archivo}: {e}')
            return False
    
    def restaurar_archivo(self, id_cuarentena: str) -> bool:
        """
        Restaura un archivo desde cuarentena a su ubicación original.
        
        Args:
            id_cuarentena: ID del archivo en cuarentena
            
        Returns:
            True si se restauró exitosamente, False en caso contrario
        """
        archivo_cuarentena = self._buscar_por_id(id_cuarentena)
        
        if not archivo_cuarentena:
            if self.siem:
                self.siem.registrar_evento('WARNING', 'cuarentena', 
                                         f'Archivo con ID {id_cuarentena} no encontrado en cuarentena')
            return False
        
        try:
            archivo_en_cuarentena = Path(archivo_cuarentena.ruta_cuarentena)
            ruta_original = Path(archivo_cuarentena.ruta_original)
            
            if not archivo_en_cuarentena.exists():
                if self.siem:
                    self.siem.registrar_evento('ERROR', 'cuarentena', 
                                             f'Archivo en cuarentena no existe: {archivo_cuarentena.ruta_cuarentena}')
                return False
            
            # Crear directorio padre si no existe
            ruta_original.parent.mkdir(parents=True, exist_ok=True)
            
            # Mover archivo de vuelta
            shutil.move(str(archivo_en_cuarentena), str(ruta_original))
            
            # Remover de la lista
            self.archivos_cuarentena.remove(archivo_cuarentena)
            self._guardar_registro()
            
            if self.siem:
                self.siem.registrar_evento('INFO', 'cuarentena', 
                                         f'Archivo restaurado: {archivo_cuarentena.ruta_cuarentena} -> {ruta_original}')
            
            return True
            
        except Exception as e:
            if self.siem:
                self.siem.registrar_evento('ERROR', 'cuarentena', 
                                         f'Error restaurando archivo {id_cuarentena}: {e}')
            return False
    
    def eliminar_definitivamente(self, id_cuarentena: str) -> bool:
        """
        Elimina definitivamente un archivo de cuarentena.
        
        Args:
            id_cuarentena: ID del archivo en cuarentena
            
        Returns:
            True si se eliminó exitosamente, False en caso contrario
        """
        archivo_cuarentena = self._buscar_por_id(id_cuarentena)
        
        if not archivo_cuarentena:
            if self.siem:
                self.siem.registrar_evento('WARNING', 'cuarentena', 
                                         f'Archivo con ID {id_cuarentena} no encontrado para eliminación')
            return False
        
        try:
            archivo_en_cuarentena = Path(archivo_cuarentena.ruta_cuarentena)
            
            if archivo_en_cuarentena.exists():
                archivo_en_cuarentena.unlink()
            
            # Remover de la lista
            self.archivos_cuarentena.remove(archivo_cuarentena)
            self._guardar_registro()
            
            if self.siem:
                self.siem.registrar_evento('HIGH', 'cuarentena', 
                                         f'Archivo eliminado definitivamente: {archivo_cuarentena.ruta_original}')
            
            return True
            
        except Exception as e:
            if self.siem:
                self.siem.registrar_evento('ERROR', 'cuarentena', 
                                         f'Error eliminando archivo {id_cuarentena}: {e}')
            return False
    
    def _buscar_por_id(self, id_cuarentena: str) -> Optional[ArchivoEnCuarentena]:
        """Busca un archivo en cuarentena por su ID."""
        for archivo in self.archivos_cuarentena:
            if archivo.id_cuarentena == id_cuarentena:
                return archivo
        return None
    
    def listar_archivos(self) -> List[ArchivoEnCuarentena]:
        """Lista todos los archivos en cuarentena."""
        return self.archivos_cuarentena.copy()
    
    def buscar_por_hash(self, hash_archivo: str) -> List[ArchivoEnCuarentena]:
        """Busca archivos en cuarentena por hash."""
        return [archivo for archivo in self.archivos_cuarentena 
                if archivo.hash_archivo == hash_archivo]
    
    def buscar_por_ruta_original(self, ruta: str) -> List[ArchivoEnCuarentena]:
        """Busca archivos en cuarentena por ruta original."""
        return [archivo for archivo in self.archivos_cuarentena 
                if ruta in archivo.ruta_original]
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas de la cuarentena."""
        total_archivos = len(self.archivos_cuarentena)
        
        if total_archivos == 0:
            return {
                'total_archivos': 0,
                'espacio_utilizado': 0,
                'archivos_por_razon': {},
                'archivos_por_fecha': {}
            }
        
        # Calcular espacio utilizado
        espacio_total = 0
        for archivo in self.archivos_cuarentena:
            try:
                ruta_archivo = Path(archivo.ruta_cuarentena)
                if ruta_archivo.exists():
                    espacio_total += ruta_archivo.stat().st_size
            except:
                continue
        
        # Agrupar por razón
        razones = {}
        for archivo in self.archivos_cuarentena:
            razon = archivo.razon or "Sin especificar"
            razones[razon] = razones.get(razon, 0) + 1
        
        # Agrupar por fecha (por día)
        fechas = {}
        for archivo in self.archivos_cuarentena:
            fecha = archivo.fecha_cuarentena.strftime('%Y-%m-%d')
            fechas[fecha] = fechas.get(fecha, 0) + 1
        
        return {
            'total_archivos': total_archivos,
            'espacio_utilizado': espacio_total,
            'archivos_por_razon': razones,
            'archivos_por_fecha': fechas
        }
    
    def limpiar_cuarentena_antigua(self, dias: int = 30) -> int:
        """
        Limpia archivos de cuarentena más antiguos que el número especificado de días.
        
        Args:
            dias: Número de días. Archivos más antiguos serán eliminados
            
        Returns:
            Número de archivos eliminados
        """
        from datetime import timedelta
        
        fecha_limite = datetime.now() - timedelta(days=dias)
        archivos_eliminados = 0
        
        archivos_a_eliminar = []
        for archivo in self.archivos_cuarentena:
            if archivo.fecha_cuarentena < fecha_limite:
                archivos_a_eliminar.append(archivo)
        
        for archivo in archivos_a_eliminar:
            if self.eliminar_definitivamente(archivo.id_cuarentena):
                archivos_eliminados += 1
        
        if self.siem and archivos_eliminados > 0:
            self.siem.registrar_evento('INFO', 'cuarentena', 
                                     f'Limpieza automática: {archivos_eliminados} archivos eliminados')
        
        return archivos_eliminados
    
    def generar_reporte_markdown(self) -> str:
        """Genera un reporte de cuarentena en formato Markdown."""
        estadisticas = self.obtener_estadisticas()
        
        reporte = "# Reporte de Cuarentena - Ares Aegis\n\n"
        reporte += f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        reporte += "## Estadísticas Generales\n\n"
        reporte += f"- **Total de archivos en cuarentena:** {estadisticas['total_archivos']}\n"
        reporte += f"- **Espacio utilizado:** {estadisticas['espacio_utilizado'] / 1024 / 1024:.2f} MB\n"
        reporte += f"- **Directorio de cuarentena:** `{self.directorio_cuarentena}`\n\n"
        
        if estadisticas['archivos_por_razon']:
            reporte += "## Archivos por Razón de Cuarentena\n\n"
            for razon, cantidad in estadisticas['archivos_por_razon'].items():
                reporte += f"- **{razon}:** {cantidad} archivos\n"
            reporte += "\n"
        
        if estadisticas['archivos_por_fecha']:
            reporte += "## Archivos por Fecha\n\n"
            for fecha, cantidad in sorted(estadisticas['archivos_por_fecha'].items(), reverse=True):
                reporte += f"- **{fecha}:** {cantidad} archivos\n"
            reporte += "\n"
        
        if self.archivos_cuarentena:
            reporte += "## Detalle de Archivos en Cuarentena\n\n"
            for archivo in sorted(self.archivos_cuarentena, 
                                key=lambda x: x.fecha_cuarentena, reverse=True):
                reporte += f"### ID: {archivo.id_cuarentena}\n\n"
                reporte += f"- **Archivo original:** `{archivo.ruta_original}`\n"
                reporte += f"- **Razón:** {archivo.razon}\n"
                reporte += f"- **Fecha de cuarentena:** {archivo.fecha_cuarentena.strftime('%Y-%m-%d %H:%M:%S')}\n"
                reporte += f"- **Hash SHA256:** `{archivo.hash_archivo}`\n\n"
        
        return reporte
