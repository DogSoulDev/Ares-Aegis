#!/usr/bin/env python3
"""
Monitor de Integridad de Archivos (FIM) - Ares Aegis
Sistema de monitoreo de cambios en archivos críticos

Autor: DogSoulDev
Versión: 2.0.0
"""

import os
import hashlib
import json
import time
from pathlib import Path
from typing import Dict, List, Set, Any, Optional
from datetime import datetime


class RegistroArchivo:
    """Representa un archivo monitoreado."""
    
    def __init__(self, ruta: str):
        self.ruta = ruta
        self.hash_sha256 = ""
        self.tamaño = 0
        self.fecha_modificacion = 0
        self.permisos = ""
        self.fecha_registro = datetime.now()
        self.actualizar_metadatos()
    
    def actualizar_metadatos(self) -> bool:
        """Actualiza los metadatos del archivo."""
        try:
            ruta_archivo = Path(self.ruta)
            
            if not ruta_archivo.exists():
                return False
            
            stat_info = ruta_archivo.stat()
            self.tamaño = stat_info.st_size
            self.fecha_modificacion = stat_info.st_mtime
            self.permisos = oct(stat_info.st_mode)[-3:]
            
            # Calcular hash solo para archivos pequeños
            if self.tamaño < 50 * 1024 * 1024:  # 50MB
                with open(ruta_archivo, 'rb') as archivo:
                    self.hash_sha256 = hashlib.sha256(archivo.read()).hexdigest()
            else:
                self.hash_sha256 = "ARCHIVO_GRANDE"
            
            return True
            
        except Exception:
            return False
    
    def ha_cambiado(self) -> bool:
        """Verifica si el archivo ha cambiado."""
        estado_anterior = {
            'hash': self.hash_sha256,
            'tamaño': self.tamaño,
            'fecha_mod': self.fecha_modificacion,
            'permisos': self.permisos
        }
        
        self.actualizar_metadatos()
        
        estado_actual = {
            'hash': self.hash_sha256,
            'tamaño': self.tamaño,
            'fecha_mod': self.fecha_modificacion,
            'permisos': self.permisos
        }
        
        return estado_anterior != estado_actual
    
    def obtener_cambios(self, estado_anterior: Dict[str, Any]) -> List[str]:
        """Identifica qué cambios específicos ocurrieron."""
        cambios = []
        
        if estado_anterior.get('hash') != self.hash_sha256:
            cambios.append("contenido modificado")
        
        if estado_anterior.get('tamaño') != self.tamaño:
            cambios.append(f"tamaño cambió: {estado_anterior.get('tamaño', 0)} -> {self.tamaño}")
        
        if estado_anterior.get('fecha_mod') != self.fecha_modificacion:
            fecha_ant = datetime.fromtimestamp(estado_anterior.get('fecha_mod', 0))
            fecha_act = datetime.fromtimestamp(self.fecha_modificacion)
            cambios.append(f"fecha modificación: {fecha_ant} -> {fecha_act}")
        
        if estado_anterior.get('permisos') != self.permisos:
            cambios.append(f"permisos: {estado_anterior.get('permisos', '')} -> {self.permisos}")
        
        return cambios
    
    def a_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para serialización."""
        return {
            'ruta': self.ruta,
            'hash_sha256': self.hash_sha256,
            'tamaño': self.tamaño,
            'fecha_modificacion': self.fecha_modificacion,
            'permisos': self.permisos,
            'fecha_registro': self.fecha_registro.isoformat()
        }
    
    @classmethod
    def desde_dict(cls, datos: Dict[str, Any]) -> 'RegistroArchivo':
        """Crea instancia desde diccionario."""
        archivo = cls.__new__(cls)
        archivo.ruta = datos['ruta']
        archivo.hash_sha256 = datos['hash_sha256']
        archivo.tamaño = datos['tamaño']
        archivo.fecha_modificacion = datos['fecha_modificacion']
        archivo.permisos = datos['permisos']
        archivo.fecha_registro = datetime.fromisoformat(datos['fecha_registro'])
        return archivo


class MonitorIntegridad:
    """Monitor de integridad de archivos (FIM)."""
    
    def __init__(self, directorio_config: Optional[str] = None, siem=None):
        self.siem = siem
        
        if directorio_config:
            self.directorio_config = Path(directorio_config)
        else:
            self.directorio_config = Path.home() / ".ares_aegis" / "fim"
        
        self.directorio_config.mkdir(parents=True, exist_ok=True)
        
        self.archivo_base_datos = self.directorio_config / "base_datos_fim.json"
        self.archivo_configuracion = self.directorio_config / "configuracion_fim.json"
        
        self.archivos_monitoreados: Dict[str, RegistroArchivo] = {}
        self.rutas_monitoreadas: Set[str] = set()
        self.extensiones_monitoreadas: Set[str] = set()
        self.intervalos_verificacion = 300  # 5 minutos
        
        self._cargar_configuracion()
        self._cargar_base_datos()
        
        if self.siem:
            self.siem.log_evento('INFO', 'fim', 
                                     f'Monitor de integridad inicializado: {len(self.archivos_monitoreados)} archivos')
    
    def _cargar_configuracion(self):
        """Carga la configuración del monitor."""
        if self.archivo_configuracion.exists():
            try:
                with open(self.archivo_configuracion, 'r', encoding='utf-8') as archivo:
                    config = json.load(archivo)
                    
                    self.rutas_monitoreadas = set(config.get('rutas_monitoreadas', []))
                    self.extensiones_monitoreadas = set(config.get('extensiones_monitoreadas', []))
                    self.intervalos_verificacion = config.get('intervalo_verificacion', 300)
                
                if self.siem:
                    self.siem.log_evento('INFO', 'fim', 
                                             f'Configuración cargada: {len(self.rutas_monitoreadas)} rutas')
            except Exception as e:
                if self.siem:
                    self.siem.log_evento('ERROR', 'fim', f'Error cargando configuración: {e}')
                self._crear_configuracion_por_defecto()
        else:
            self._crear_configuracion_por_defecto()
    
    def _crear_configuracion_por_defecto(self):
        """Crea configuración por defecto."""
        self.rutas_monitoreadas = {
            '/etc/passwd',
            '/etc/shadow',
            '/etc/hosts',
            '/etc/crontab',
            '/etc/sudoers',
            '/boot/',
            '/usr/bin/',
            '/usr/sbin/',
        }
        
        self.extensiones_monitoreadas = {
            '.conf', '.config', '.ini', '.cfg', '.sh', '.py', '.pl',
            '.service', '.socket', '.timer'
        }
        
        self._guardar_configuracion()
    
    def _guardar_configuracion(self):
        """Guarda la configuración actual."""
        try:
            config = {
                'rutas_monitoreadas': list(self.rutas_monitoreadas),
                'extensiones_monitoreadas': list(self.extensiones_monitoreadas),
                'intervalo_verificacion': self.intervalos_verificacion
            }
            
            with open(self.archivo_configuracion, 'w', encoding='utf-8') as archivo:
                json.dump(config, archivo, indent=2, ensure_ascii=False)
            
            if self.siem:
                self.siem.log_evento('INFO', 'fim', 'Configuración guardada')
        except Exception as e:
            if self.siem:
                self.siem.log_evento('ERROR', 'fim', f'Error guardando configuración: {e}')
    
    def _cargar_base_datos(self):
        """Carga la base de datos de archivos monitoreados."""
        if self.archivo_base_datos.exists():
            try:
                with open(self.archivo_base_datos, 'r', encoding='utf-8') as archivo:
                    datos = json.load(archivo)
                    
                    self.archivos_monitoreados = {
                        ruta: RegistroArchivo.desde_dict(info)
                        for ruta, info in datos.items()
                    }
                
                if self.siem:
                    self.siem.log_evento('INFO', 'fim', 
                                             f'Base de datos cargada: {len(self.archivos_monitoreados)} archivos')
            except Exception as e:
                if self.siem:
                    self.siem.log_evento('ERROR', 'fim', f'Error cargando base de datos: {e}')
                self.archivos_monitoreados = {}
    
    def _guardar_base_datos(self):
        """Guarda la base de datos de archivos monitoreados."""
        try:
            datos = {
                ruta: archivo.a_dict()
                for ruta, archivo in self.archivos_monitoreados.items()
            }
            
            with open(self.archivo_base_datos, 'w', encoding='utf-8') as archivo:
                json.dump(datos, archivo, indent=2, ensure_ascii=False)
            
            if self.siem:
                self.siem.log_evento('INFO', 'fim', 
                                         f'Base de datos guardada: {len(self.archivos_monitoreados)} archivos')
        except Exception as e:
            if self.siem:
                self.siem.log_evento('ERROR', 'fim', f'Error guardando base de datos: {e}')
    
    def agregar_ruta_monitoreo(self, ruta: str):
        """Agrega una ruta al monitoreo."""
        ruta_normalizada = os.path.normpath(ruta)
        self.rutas_monitoreadas.add(ruta_normalizada)
        self._guardar_configuracion()
        
        if self.siem:
            self.siem.log_evento('INFO', 'fim', f'Ruta agregada al monitoreo: {ruta_normalizada}')
    
    def remover_ruta_monitoreo(self, ruta: str):
        """Remueve una ruta del monitoreo."""
        ruta_normalizada = os.path.normpath(ruta)
        self.rutas_monitoreadas.discard(ruta_normalizada)
        
        # Remover archivos de esta ruta de la base de datos
        archivos_a_remover = [
            archivo_ruta for archivo_ruta in self.archivos_monitoreados
            if archivo_ruta.startswith(ruta_normalizada)
        ]
        
        for archivo_ruta in archivos_a_remover:
            del self.archivos_monitoreados[archivo_ruta]
        
        self._guardar_configuracion()
        self._guardar_base_datos()
        
        if self.siem:
            self.siem.log_evento('INFO', 'fim', 
                                     f'Ruta removida del monitoreo: {ruta_normalizada} ({len(archivos_a_remover)} archivos)')
    
    def inicializar_base_datos(self) -> int:
        """Inicializa la base de datos escaneando todas las rutas monitoreadas."""
        archivos_agregados = 0
        
        for ruta in self.rutas_monitoreadas:
            archivos_agregados += self._escanear_ruta(ruta)
        
        self._guardar_base_datos()
        
        if self.siem:
            self.siem.log_evento('INFO', 'fim', 
                                     f'Base de datos inicializada: {archivos_agregados} archivos agregados')
        
        return archivos_agregados
    
    def _escanear_ruta(self, ruta: str) -> int:
        """Escanea una ruta y agrega archivos al monitoreo."""
        archivos_agregados = 0
        ruta_path = Path(ruta)
        
        try:
            if ruta_path.is_file():
                if self._debe_monitorear_archivo(str(ruta_path)):
                    if str(ruta_path) not in self.archivos_monitoreados:
                        self.archivos_monitoreados[str(ruta_path)] = RegistroArchivo(str(ruta_path))
                        archivos_agregados += 1
            elif ruta_path.is_dir():
                for archivo in ruta_path.rglob('*'):
                    if archivo.is_file() and self._debe_monitorear_archivo(str(archivo)):
                        if str(archivo) not in self.archivos_monitoreados:
                            self.archivos_monitoreados[str(archivo)] = RegistroArchivo(str(archivo))
                            archivos_agregados += 1
        except Exception as e:
            if self.siem:
                self.siem.log_evento('ERROR', 'fim', f'Error escaneando ruta {ruta}: {e}')
        
        return archivos_agregados
    
    def _debe_monitorear_archivo(self, ruta_archivo: str) -> bool:
        """Determina si un archivo debe ser monitoreado."""
        archivo_path = Path(ruta_archivo)
        
        # Verificar extensión
        if self.extensiones_monitoreadas:
            extension = archivo_path.suffix.lower()
            if extension not in self.extensiones_monitoreadas:
                return False
        
        # Excluir archivos temporales y de log
        nombre_archivo = archivo_path.name.lower()
        if (nombre_archivo.startswith('.') or 
            nombre_archivo.endswith(('.tmp', '.temp', '.log', '.bak', '.swp'))):
            return False
        
        # Limitar tamaño de archivo (100MB)
        try:
            if archivo_path.stat().st_size > 100 * 1024 * 1024:
                return False
        except:
            return False
        
        return True
    
    def verificar_integridad(self) -> List[Dict[str, Any]]:
        """Verifica la integridad de todos los archivos monitoreados."""
        cambios_detectados = []
        
        for ruta, registro in self.archivos_monitoreados.items():
            try:
                estado_anterior = {
                    'hash': registro.hash_sha256,
                    'tamaño': registro.tamaño,
                    'fecha_mod': registro.fecha_modificacion,
                    'permisos': registro.permisos
                }
                
                if registro.ha_cambiado():
                    cambios = registro.obtener_cambios(estado_anterior)
                    
                    cambio_detectado = {
                        'ruta': ruta,
                        'fecha_deteccion': datetime.now().isoformat(),
                        'cambios': cambios,
                        'estado_anterior': estado_anterior,
                        'estado_actual': {
                            'hash': registro.hash_sha256,
                            'tamaño': registro.tamaño,
                            'fecha_mod': registro.fecha_modificacion,
                            'permisos': registro.permisos
                        }
                    }
                    
                    cambios_detectados.append(cambio_detectado)
                    
                    if self.siem:
                        self.siem.log_evento('HIGH', 'fim', 
                                                 f'Cambio detectado en {ruta}: {", ".join(cambios)}')
            
            except Exception as e:
                if self.siem:
                    self.siem.log_evento('ERROR', 'fim', 
                                             f'Error verificando {ruta}: {e}')
        
        if cambios_detectados:
            self._guardar_base_datos()
        
        return cambios_detectados
    
    def buscar_archivos_nuevos(self) -> List[str]:
        """Busca archivos nuevos en las rutas monitoreadas."""
        archivos_nuevos = []
        
        for ruta in self.rutas_monitoreadas:
            try:
                archivos_nuevos.extend(self._buscar_nuevos_en_ruta(ruta))
            except Exception as e:
                if self.siem:
                    self.siem.log_evento('ERROR', 'fim', 
                                             f'Error buscando archivos nuevos en {ruta}: {e}')
        
        return archivos_nuevos
    
    def _buscar_nuevos_en_ruta(self, ruta: str) -> List[str]:
        """Busca archivos nuevos en una ruta específica."""
        archivos_nuevos = []
        ruta_path = Path(ruta)
        
        if ruta_path.is_file():
            if (self._debe_monitorear_archivo(str(ruta_path)) and 
                str(ruta_path) not in self.archivos_monitoreados):
                archivos_nuevos.append(str(ruta_path))
                self.archivos_monitoreados[str(ruta_path)] = RegistroArchivo(str(ruta_path))
        elif ruta_path.is_dir():
            for archivo in ruta_path.rglob('*'):
                if (archivo.is_file() and 
                    self._debe_monitorear_archivo(str(archivo)) and
                    str(archivo) not in self.archivos_monitoreados):
                    archivos_nuevos.append(str(archivo))
                    self.archivos_monitoreados[str(archivo)] = RegistroArchivo(str(archivo))
        
        return archivos_nuevos
    
    def buscar_archivos_eliminados(self) -> List[str]:
        """Busca archivos que han sido eliminados."""
        archivos_eliminados = []
        
        archivos_a_remover = []
        for ruta in self.archivos_monitoreados:
            if not Path(ruta).exists():
                archivos_eliminados.append(ruta)
                archivos_a_remover.append(ruta)
        
        # Remover archivos eliminados de la base de datos
        for ruta in archivos_a_remover:
            del self.archivos_monitoreados[ruta]
            if self.siem:
                self.siem.log_evento('MEDIUM', 'fim', f'Archivo eliminado detectado: {ruta}')
        
        if archivos_eliminados:
            self._guardar_base_datos()
        
        return archivos_eliminados
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas del monitor de integridad."""
        total_archivos = len(self.archivos_monitoreados)
        total_rutas = len(self.rutas_monitoreadas)
        
        # Agrupar por extensiones
        extensiones = {}
        for ruta in self.archivos_monitoreados:
            extension = Path(ruta).suffix.lower() or "sin_extension"
            extensiones[extension] = extensiones.get(extension, 0) + 1
        
        # Calcular espacio total monitoreado
        espacio_total = 0
        for registro in self.archivos_monitoreados.values():
            espacio_total += registro.tamaño
        
        return {
            'total_archivos': total_archivos,
            'total_rutas': total_rutas,
            'espacio_monitoreado': espacio_total,
            'archivos_por_extension': extensiones,
            'intervalo_verificacion': self.intervalos_verificacion
        }
    
    def generar_reporte_markdown(self, cambios_recientes: Optional[List[Dict[str, Any]]] = None) -> str:
        """Genera un reporte de integridad en formato Markdown."""
        estadisticas = self.obtener_estadisticas()
        
        reporte = "# Reporte de Integridad de Archivos - Ares Aegis\n\n"
        reporte += f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        reporte += "## Estadísticas Generales\n\n"
        reporte += f"- **Archivos monitoreados:** {estadisticas['total_archivos']}\n"
        reporte += f"- **Rutas monitoreadas:** {estadisticas['total_rutas']}\n"
        reporte += f"- **Espacio monitoreado:** {estadisticas['espacio_monitoreado'] / 1024 / 1024:.2f} MB\n"
        reporte += f"- **Intervalo de verificación:** {estadisticas['intervalo_verificacion']} segundos\n\n"
        
        if estadisticas['archivos_por_extension']:
            reporte += "## Archivos por Extensión\n\n"
            for extension, cantidad in sorted(estadisticas['archivos_por_extension'].items()):
                reporte += f"- **{extension}:** {cantidad} archivos\n"
            reporte += "\n"
        
        reporte += "## Rutas Monitoreadas\n\n"
        for ruta in sorted(self.rutas_monitoreadas):
            reporte += f"- `{ruta}`\n"
        reporte += "\n"
        
        if cambios_recientes:
            reporte += "## Cambios Detectados Recientemente\n\n"
            for cambio in cambios_recientes:
                reporte += f"### {cambio['ruta']}\n\n"
                reporte += f"- **Fecha de detección:** {cambio['fecha_deteccion']}\n"
                reporte += f"- **Cambios detectados:**\n"
                for detalle in cambio['cambios']:
                    reporte += f"  - {detalle}\n"
                reporte += "\n"
        
        return reporte
