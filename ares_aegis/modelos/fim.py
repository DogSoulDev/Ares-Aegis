#!/usr/bin/env python3
"""
Copyright (c) 2025 DogSoulDev (https://github.com/DogSoulDev)
Todos los derechos reservados. Este código es propietario y confidencial.

FIM - Monitoreo de Integridad de Archivos
"""

import os
import json
import hashlib
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
from stat import filemode

from .siem import SIEM, TipoEvento
from ..utilidades.validaciones import validar_ruta_directorio, validar_permisos_lectura
from ..utilidades.ayuda_rutas import (
    listar_archivos_recursivo, obtener_rutas_sistema, crear_ruta_segura
)
from ..utilidades.ayuda_logging import configurar_logger_modulo


class RegistroArchivoFIM:
    def __init__(self, ruta: str):
        self.ruta = ruta
        self.hash_md5 = ""
        self.hash_sha256 = ""
        self.tamaño = 0
        self.permisos = ""
        self.propietario = ""
        self.grupo = ""
        self.fecha_modificacion = ""
        self.fecha_acceso = ""
        self.fecha_creacion = ""
        self.timestamp_registro = datetime.now()
        
        self._calcular_atributos()
    
    def _calcular_atributos(self):
        try:
            stat_info = os.stat(self.ruta)
            
            self.tamaño = stat_info.st_size
            self.permisos = filemode(stat_info.st_mode)
            self.propietario = str(stat_info.st_uid)
            self.grupo = str(stat_info.st_gid)
            
            self.fecha_modificacion = datetime.fromtimestamp(stat_info.st_mtime).isoformat()
            self.fecha_acceso = datetime.fromtimestamp(stat_info.st_atime).isoformat()
            self.fecha_creacion = datetime.fromtimestamp(stat_info.st_ctime).isoformat()
            
            if os.path.isfile(self.ruta):
                with open(self.ruta, 'rb') as archivo:
                    contenido = archivo.read()
                    self.hash_md5 = hashlib.md5(contenido).hexdigest()
                    self.hash_sha256 = hashlib.sha256(contenido).hexdigest()
            
        except Exception:
            pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el registro a diccionario."""
        return {
            'ruta': self.ruta,
            'hash_md5': self.hash_md5,
            'hash_sha256': self.hash_sha256,
            'tamaño': self.tamaño,
            'permisos': self.permisos,
            'propietario': self.propietario,
            'grupo': self.grupo,
            'fecha_modificacion': self.fecha_modificacion,
            'fecha_acceso': self.fecha_acceso,
            'fecha_creacion': self.fecha_creacion,
            'timestamp_registro': self.timestamp_registro.isoformat()
        }
    
    def desde_dict(self, datos: Dict[str, Any]):
        """Carga el registro desde un diccionario."""
        self.ruta = datos.get('ruta', '')
        self.hash_md5 = datos.get('hash_md5', '')
        self.hash_sha256 = datos.get('hash_sha256', '')
        self.tamaño = datos.get('tamaño', 0)
        self.permisos = datos.get('permisos', '')
        self.propietario = datos.get('propietario', '')
        self.grupo = datos.get('grupo', '')
        self.fecha_modificacion = datos.get('fecha_modificacion', '')
        self.fecha_acceso = datos.get('fecha_acceso', '')
        self.fecha_creacion = datos.get('fecha_creacion', '')
        
        timestamp_str = datos.get('timestamp_registro', '')
        if timestamp_str:
            try:
                self.timestamp_registro = datetime.fromisoformat(timestamp_str)
            except Exception:
                self.timestamp_registro = datetime.now()
    
    def comparar_con(self, otro_registro: 'RegistroArchivoFIM') -> List[str]:
        """
        Compara este registro con otro y devuelve las diferencias.
        
        Args:
            otro_registro: Otro registro para comparar
            
        Returns:
            List[str]: Lista de diferencias encontradas
        """
        diferencias = []
        
        if self.hash_sha256 != otro_registro.hash_sha256:
            diferencias.append("contenido_modificado")
        
        if self.tamaño != otro_registro.tamaño:
            diferencias.append("tamaño_modificado")
        
        if self.permisos != otro_registro.permisos:
            diferencias.append("permisos_modificados")
        
        if self.propietario != otro_registro.propietario:
            diferencias.append("propietario_modificado")
        
        if self.grupo != otro_registro.grupo:
            diferencias.append("grupo_modificado")
        
        if self.fecha_modificacion != otro_registro.fecha_modificacion:
            diferencias.append("fecha_modificacion_cambiada")
        
        return diferencias


class CambioFIM:
    """Representa un cambio detectado por el FIM."""
    
    def __init__(self, ruta: str, tipo_cambio: str, detalles: Optional[Dict[str, Any]] = None):
        """
        Inicializa un cambio FIM.
        
        Args:
            ruta: Ruta del archivo modificado
            tipo_cambio: Tipo de cambio (creado, modificado, eliminado)
            detalles: Detalles adicionales del cambio
        """
        self.ruta = ruta
        self.tipo_cambio = tipo_cambio
        self.detalles = detalles or {}
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el cambio a diccionario."""
        return {
            'ruta': self.ruta,
            'tipo_cambio': self.tipo_cambio,
            'detalles': self.detalles,
            'timestamp': self.timestamp.isoformat()
        }
    
    def to_markdown(self) -> str:
        """Convierte el cambio a formato Markdown."""
        emoji_tipo = {
            'creado': '🆕',
            'modificado': '📝',
            'eliminado': '🗑️',
            'permisos_modificados': '🔒',
            'propietario_modificado': '👤'
        }.get(self.tipo_cambio, '📋')
        
        md = f"### {emoji_tipo} {self.tipo_cambio.upper()}\n\n"
        md += f"**Archivo:** `{self.ruta}`\n"
        md += f"**Fecha:** {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        if self.detalles:
            md += "\n**Detalles:**\n"
            for clave, valor in self.detalles.items():
                md += f"- **{clave}:** {valor}\n"
        
        md += "\n"
        return md


class FIM:
    """Sistema de Monitoreo de Integridad de Archivos."""
    
    def __init__(self, siem: SIEM):
        """
        Inicializa el sistema FIM.
        
        Args:
            siem: Instancia del SIEM para registro de eventos
        """
        self.siem = siem
        self.logger = configurar_logger_modulo("fim")
        
        # Base de datos de archivos
        self.base_datos: Dict[str, RegistroArchivoFIM] = {}
        
        # Configuración
        self.archivo_base_datos = self._determinar_ruta_base_datos()
        self.rutas_monitoreadas: Set[str] = set()
        self.rutas_excluidas: Set[str] = set()
        
        # Cargar configuración por defecto
        self._cargar_configuracion_por_defecto()
        
        # Cargar base de datos existente
        self._cargar_base_datos()
        
        self.logger.info("FIM inicializado correctamente")
        self.siem.registrar_evento(
            TipoEvento.SISTEMA_INICIADO,
            "Sistema FIM inicializado",
            {'archivo_base_datos': self.archivo_base_datos},
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
        # Rutas críticas del sistema a monitorear
        rutas_criticas = [
            '/etc/passwd',
            '/etc/shadow',
            '/etc/group',
            '/etc/sudoers',
            '/etc/hosts',
            '/etc/crontab',
            '/etc/ssh/sshd_config',
            '/usr/bin',
            '/usr/sbin',
            '/bin',
            '/sbin'
        ]
        
        # Agregar rutas que existan
        for ruta in rutas_criticas:
            if os.path.exists(ruta):
                self.rutas_monitoreadas.add(ruta)
        
        # Rutas a excluir por defecto
        rutas_excluidas = [
            '/proc',
            '/sys',
            '/dev',
            '/tmp',
            '/var/tmp',
            '/var/log'
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
                        registro = RegistroArchivoFIM(ruta)
                        registro.desde_dict(datos_archivo)
                        self.base_datos[ruta] = registro
                
                self.logger.info(f"Base de datos FIM cargada: {len(self.base_datos)} archivos")
        
        except Exception as e:
            self.logger.warning(f"Error cargando base de datos FIM: {e}")
    
    def _guardar_base_datos(self):
        """Guarda la base de datos de archivos al archivo."""
        try:
            crear_ruta_segura(self.archivo_base_datos)
            
            datos = {}
            for ruta, registro in self.base_datos.items():
                datos[ruta] = registro.to_dict()
            
            with open(self.archivo_base_datos, 'w', encoding='utf-8') as archivo:
                json.dump(datos, archivo, ensure_ascii=False, indent=2)
            
            self.logger.debug("Base de datos FIM guardada correctamente")
        
        except Exception as e:
            self.logger.error(f"Error guardando base de datos FIM: {e}")
    
    def agregar_ruta_monitoreo(self, ruta: str):
        """
        Agrega una ruta al monitoreo FIM.
        
        Args:
            ruta: Ruta a agregar al monitoreo
        """
        if validar_ruta_directorio(ruta) or os.path.isfile(ruta):
            self.rutas_monitoreadas.add(os.path.abspath(ruta))
            self.logger.info(f"Ruta agregada al monitoreo FIM: {ruta}")
        else:
            self.logger.warning(f"Ruta no válida para monitoreo FIM: {ruta}")
    
    def remover_ruta_monitoreo(self, ruta: str):
        """
        Remueve una ruta del monitoreo FIM.
        
        Args:
            ruta: Ruta a remover del monitoreo
        """
        ruta_absoluta = os.path.abspath(ruta)
        if ruta_absoluta in self.rutas_monitoreadas:
            self.rutas_monitoreadas.remove(ruta_absoluta)
            self.logger.info(f"Ruta removida del monitoreo FIM: {ruta}")
    
    def crear_baseline(self, rutas_adicionales: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Crea una línea base de integridad.
        
        Args:
            rutas_adicionales: Rutas adicionales a incluir en la línea base
            
        Returns:
            Dict[str, Any]: Estadísticas de la creación de línea base
        """
        self.logger.info("Iniciando creación de línea base FIM")
        self.siem.registrar_evento(
            TipoEvento.SISTEMA_INICIADO,
            "Creación de línea base FIM iniciada",
            nivel_criticidad="MEDIO"
        )
        
        inicio_tiempo = time.time()
        archivos_procesados = 0
        errores = 0
        
        # Agregar rutas adicionales si se proporcionan
        if rutas_adicionales:
            for ruta in rutas_adicionales:
                self.agregar_ruta_monitoreo(ruta)
        
        # Procesar todas las rutas monitoreadas
        for ruta in self.rutas_monitoreadas.copy():
            try:
                if os.path.isfile(ruta):
                    # Es un archivo individual
                    if validar_permisos_lectura(ruta):
                        registro = RegistroArchivoFIM(ruta)
                        self.base_datos[ruta] = registro
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
                                registro = RegistroArchivoFIM(ruta_archivo)
                                self.base_datos[ruta_archivo] = registro
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
            'timestamp': datetime.now().isoformat()
        }
        
        self.siem.registrar_evento(
            TipoEvento.SISTEMA_INICIADO,
            "Línea base FIM creada exitosamente",
            estadisticas,
            "MEDIO"
        )
        
        self.logger.info(f"Línea base FIM creada: {archivos_procesados} archivos en {tiempo_total:.2f}s")
        
        return estadisticas
    
    def verificar_integridad(self) -> List[CambioFIM]:
        """
        Verifica la integridad de archivos monitoreados.
        
        Returns:
            List[CambioFIM]: Lista de cambios detectados
        """
        self.logger.info("Iniciando verificación de integridad FIM")
        self.siem.registrar_evento(
            TipoEvento.SISTEMA_INICIADO,
            "Verificación de integridad FIM iniciada",
            nivel_criticidad="MEDIO"
        )
        
        cambios_detectados = []
        archivos_verificados = 0
        
        # Verificar archivos existentes en la base de datos
        for ruta, registro_original in self.base_datos.items():
            try:
                if os.path.exists(ruta):
                    # El archivo aún existe, verificar cambios
                    registro_actual = RegistroArchivoFIM(ruta)
                    diferencias = registro_original.comparar_con(registro_actual)
                    
                    if diferencias:
                        cambio = CambioFIM(
                            ruta,
                            "modificado",
                            {
                                'diferencias': diferencias,
                                'hash_original': registro_original.hash_sha256,
                                'hash_actual': registro_actual.hash_sha256,
                                'tamaño_original': registro_original.tamaño,
                                'tamaño_actual': registro_actual.tamaño
                            }
                        )
                        cambios_detectados.append(cambio)
                        
                        # Actualizar registro en base de datos
                        self.base_datos[ruta] = registro_actual
                        
                        # Registrar en SIEM
                        self.siem.registrar_evento(
                            TipoEvento.INTEGRIDAD_VIOLADA,
                            f"Integridad violada: {ruta}",
                            {
                                'ruta': ruta,
                                'diferencias': diferencias,
                                'hash_original': registro_original.hash_sha256[:16],
                                'hash_actual': registro_actual.hash_sha256[:16]
                            },
                            "ALTO"
                        )
                
                else:
                    # El archivo fue eliminado
                    cambio = CambioFIM(
                        ruta,
                        "eliminado",
                        {
                            'hash_original': registro_original.hash_sha256,
                            'tamaño_original': registro_original.tamaño
                        }
                    )
                    cambios_detectados.append(cambio)
                    
                    # Remover de la base de datos
                    del self.base_datos[ruta]
                    
                    # Registrar en SIEM
                    self.siem.registrar_evento(
                        TipoEvento.INTEGRIDAD_VIOLADA,
                        f"Archivo eliminado: {ruta}",
                        {'ruta': ruta, 'hash_original': registro_original.hash_sha256[:16]},
                        "ALTO"
                    )
                
                archivos_verificados += 1
                
                # Log de progreso
                if archivos_verificados % 1000 == 0:
                    self.logger.info(f"Progreso verificación: {archivos_verificados} archivos verificados")
            
            except Exception as e:
                self.logger.warning(f"Error verificando archivo {ruta}: {e}")
        
        # Buscar archivos nuevos en las rutas monitoreadas
        for ruta in self.rutas_monitoreadas:
            if os.path.isdir(ruta):
                try:
                    archivos_actuales = listar_archivos_recursivo(ruta)
                    
                    for archivo in archivos_actuales:
                        ruta_archivo = str(archivo)
                        
                        # Verificar si está en rutas excluidas
                        if any(exclusion in ruta_archivo for exclusion in self.rutas_excluidas):
                            continue
                        
                        if ruta_archivo not in self.base_datos:
                            # Archivo nuevo detectado
                            tamaño = 0
                            if os.path.isfile(ruta_archivo):
                                try:
                                    tamaño = os.path.getsize(ruta_archivo)
                                except Exception:
                                    tamaño = 0
                            
                            cambio = CambioFIM(
                                ruta_archivo,
                                "creado",
                                {'tamaño': tamaño}
                            )
                            cambios_detectados.append(cambio)
                            
                            # Agregar a la base de datos
                            try:
                                registro_nuevo = RegistroArchivoFIM(ruta_archivo)
                                self.base_datos[ruta_archivo] = registro_nuevo
                            except Exception as e:
                                self.logger.warning(f"Error creando registro para archivo nuevo {ruta_archivo}: {e}")
                            
                            # Registrar en SIEM
                            self.siem.registrar_evento(
                                TipoEvento.INTEGRIDAD_VIOLADA,
                                f"Archivo nuevo detectado: {ruta_archivo}",
                                {'ruta': ruta_archivo},
                                "MEDIO"
                            )
                
                except Exception as e:
                    self.logger.warning(f"Error buscando archivos nuevos en {ruta}: {e}")
        
        # Guardar cambios en la base de datos
        if cambios_detectados:
            self._guardar_base_datos()
        
        # Registrar finalización
        self.siem.registrar_evento(
            TipoEvento.SISTEMA_INICIADO,
            "Verificación de integridad FIM completada",
            {
                'archivos_verificados': archivos_verificados,
                'cambios_detectados': len(cambios_detectados)
            },
            "MEDIO" if len(cambios_detectados) == 0 else "ALTO"
        )
        
        self.logger.info(f"Verificación FIM completada: {archivos_verificados} archivos, "
                        f"{len(cambios_detectados)} cambios detectados")
        
        return cambios_detectados
    
    def generar_reporte_markdown(self, cambios: List[CambioFIM]) -> str:
        """
        Genera un reporte de cambios en formato Markdown.
        
        Args:
            cambios: Lista de cambios detectados
            
        Returns:
            str: Reporte en formato Markdown
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        md = f"# Reporte de Integridad de Archivos (FIM)\n\n"
        md += f"**Fecha:** {timestamp}\n"
        md += f"**Total de cambios detectados:** {len(cambios)}\n\n"
        
        if not cambios:
            md += "## ✅ Sin Cambios Detectados\n\n"
            md += "La verificación de integridad no detectó cambios en los archivos monitoreados.\n\n"
            return md
        
        # Agrupar cambios por tipo
        cambios_por_tipo = {}
        for cambio in cambios:
            tipo = cambio.tipo_cambio
            if tipo not in cambios_por_tipo:
                cambios_por_tipo[tipo] = []
            cambios_por_tipo[tipo].append(cambio)
        
        # Mostrar cambios por tipo
        for tipo, lista_cambios in cambios_por_tipo.items():
            emoji_tipo = {
                'creado': '🆕',
                'modificado': '📝',
                'eliminado': '🗑️'
            }.get(tipo, '📋')
            
            md += f"## {emoji_tipo} Archivos {tipo.upper()}S ({len(lista_cambios)})\n\n"
            
            for cambio in lista_cambios:
                md += cambio.to_markdown()
                md += "---\n\n"
        
        return md
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del sistema FIM.
        
        Returns:
            Dict[str, Any]: Estadísticas del FIM
        """
        return {
            'archivos_en_base_datos': len(self.base_datos),
            'rutas_monitoreadas': len(self.rutas_monitoreadas),
            'rutas_excluidas': len(self.rutas_excluidas),
            'archivo_base_datos': self.archivo_base_datos,
            'lista_rutas_monitoreadas': list(self.rutas_monitoreadas)
        }
