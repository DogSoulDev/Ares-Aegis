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

from .modelo_fim_utilidades import (
    TipoArchivo, NivelCriticidadFIM, TipoCambio, EstadoMonitoreo, 
    TipoAmenazaFIM, MetadatosArchivoAvanzados, UtilsFIM, 
    AnalizadorAmenazasFIM, GeneradorReportesFIM, OptimizadorRendimientoFIM
)
from ..utils.utils_validaciones import validar_ruta_directorio, validar_permisos_lectura
from ..utils.utils_ayuda_rutas import (
    listar_archivos_recursivo, obtener_rutas_sistema, crear_ruta_segura
)
from ..utils.utils_ayuda_logging import configurar_logger_modulo


@dataclass
class AlertaFIM:
    """Alerta avanzada del sistema FIM."""
    id_alerta: str
    tipo_cambio: TipoCambio
    tipo_amenaza: Optional[TipoAmenazaFIM]
    archivo_afectado: str
    metadatos_anteriores: Optional[MetadatosArchivoAvanzados]
    metadatos_actuales: Optional[MetadatosArchivoAvanzados]
    timestamp: datetime
    nivel_criticidad: NivelCriticidadFIM
    descripcion: str
    detalles_cambio: Dict[str, Any]
    contexto_seguridad: Dict[str, Any] = field(default_factory=dict)
    acciones_recomendadas: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Post procesamiento de la alerta."""
        if isinstance(self.tipo_cambio, str):
            self.tipo_cambio = TipoCambio(self.tipo_cambio)
        
        if isinstance(self.tipo_amenaza, str):
            self.tipo_amenaza = TipoAmenazaFIM(self.tipo_amenaza)
        
        if isinstance(self.nivel_criticidad, str):
            self.nivel_criticidad = NivelCriticidadFIM(self.nivel_criticidad)
        
        self._generar_acciones_recomendadas()
    
    def _generar_acciones_recomendadas(self):
        """Genera acciones recomendadas basadas en el tipo de amenaza."""
        if not self.acciones_recomendadas:
            if self.tipo_amenaza == TipoAmenazaFIM.MALWARE_DETECTADO:
                self.acciones_recomendadas = [
                    "Aislar archivo inmediatamente",
                    "Ejecutar análisis antivirus completo",
                    "Verificar integridad del sistema"
                ]
            elif self.tipo_amenaza == TipoAmenazaFIM.ARCHIVO_SISTEMA_MODIFICADO:
                self.acciones_recomendadas = [
                    "Verificar la legitimidad del cambio",
                    "Revisar logs de sistema",
                    "Considerar restaurar desde backup"
                ]
            elif self.tipo_amenaza == TipoAmenazaFIM.ESCALACION_PRIVILEGIOS:
                self.acciones_recomendadas = [
                    "Investigar causa del cambio de permisos",
                    "Verificar legitimidad del propietario",
                    "Revisar actividad de usuarios privilegiados"
                ]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la alerta a diccionario."""
        return {
            'id_alerta': self.id_alerta,
            'tipo_cambio': self.tipo_cambio.value,
            'tipo_amenaza': self.tipo_amenaza.value if self.tipo_amenaza else None,
            'archivo_afectado': self.archivo_afectado,
            'metadatos_anteriores': self.metadatos_anteriores.to_dict() if self.metadatos_anteriores else None,
            'metadatos_actuales': self.metadatos_actuales.to_dict() if self.metadatos_actuales else None,
            'timestamp': self.timestamp.isoformat(),
            'nivel_criticidad': self.nivel_criticidad.value,
            'descripcion': self.descripcion,
            'detalles_cambio': self.detalles_cambio,
            'contexto_seguridad': self.contexto_seguridad,
            'acciones_recomendadas': self.acciones_recomendadas
        }


@dataclass
class ReporteFIM:
    """Reporte de monitoreo FIM."""
    periodo_inicio: datetime
    periodo_fin: datetime
    total_archivos_monitoreados: int
    total_cambios_detectados: int
    alertas_por_nivel: Dict[NivelCriticidadFIM, int]
    cambios_por_tipo: Dict[TipoCambio, int]
    amenazas_detectadas: Dict[TipoAmenazaFIM, int]
    archivos_mas_modificados: List[Tuple[str, int]]
    resumen_estadisticas: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def generar_desde_alertas(cls, alertas: List[AlertaFIM], periodo_inicio: datetime, periodo_fin: datetime) -> 'ReporteFIM':
        """Genera reporte desde lista de alertas."""
        alertas_periodo = [a for a in alertas if periodo_inicio <= a.timestamp <= periodo_fin]
        
        alertas_por_nivel = defaultdict(int)
        cambios_por_tipo = defaultdict(int)
        amenazas_detectadas = defaultdict(int)
        archivos_modificaciones = defaultdict(int)
        
        for alerta in alertas_periodo:
            alertas_por_nivel[alerta.nivel_criticidad] += 1
            cambios_por_tipo[alerta.tipo_cambio] += 1
            if alerta.tipo_amenaza:
                amenazas_detectadas[alerta.tipo_amenaza] += 1
            archivos_modificaciones[alerta.archivo_afectado] += 1
        
        archivos_mas_modificados = sorted(
            archivos_modificaciones.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return cls(
            periodo_inicio=periodo_inicio,
            periodo_fin=periodo_fin,
            total_archivos_monitoreados=0,  # Se calcula en el FIM principal
            total_cambios_detectados=len(alertas_periodo),
            alertas_por_nivel=dict(alertas_por_nivel),
            cambios_por_tipo=dict(cambios_por_tipo),
            amenazas_detectadas=dict(amenazas_detectadas),
            archivos_mas_modificados=archivos_mas_modificados
        )


class FIM:
    """Sistema de Monitoreo de Integridad de Archivos (FIM) Avanzado."""
    
    def __init__(self, config: Dict[str, Any]):
        """Inicializa el FIM con configuración."""
        self.config = config
        self.logger = configurar_logger_modulo(__name__)
        
        # Configuración básica
        self.rutas_monitoreadas: Set[str] = set(config.get('rutas_monitoreadas', []))
        self.rutas_excluidas: Set[str] = set(config.get('rutas_excluidas', []))
        self.extensiones_monitoreadas: Set[str] = set(config.get('extensiones_monitoreadas', []))
        self.profundidad_maxima: int = config.get('profundidad_maxima', 10)
        self.intervalo_escaneo: int = config.get('intervalo_escaneo', 300)
        
        # Estados del sistema
        self.estado: EstadoMonitoreo = EstadoMonitoreo.INACTIVO
        self.baseline: Dict[str, MetadatosArchivoAvanzados] = {}
        self.alertas: List[AlertaFIM] = []
        self.estadisticas: Dict[str, Any] = {}
        
        # Hilos y control
        self._hilo_monitoreo: Optional[threading.Thread] = None
        self._detener_monitoreo = threading.Event()
        self._lock_baseline = threading.Lock()
        self._lock_alertas = threading.Lock()
        
        # Componentes especializados
        self.utils_fim = UtilsFIM()
        self.analizador_amenazas = AnalizadorAmenazasFIM()
        self.generador_reportes = GeneradorReportesFIM()
        self.optimizador = OptimizadorRendimientoFIM()
        
        # SIEM integrado
        self.siem: Optional[Any] = None
        if config.get('habilitar_siem', False):
            try:
                from .modelo_siem import SIEM
                self.siem = SIEM(config.get('config_siem', {}))
            except ImportError:
                self.logger.warning("SIEM no disponible")
        
        self.logger.info("FIM inicializado correctamente")
    
    def establecer_baseline(self, forzar_recalculo: bool = False) -> bool:
        """Establece la línea base de archivos monitoreados."""
        try:
            if self.baseline and not forzar_recalculo:
                self.logger.info("Baseline ya establecida")
                return True
            
            self.estado = EstadoMonitoreo.INICIALIZANDO
            self.logger.info("Estableciendo baseline...")
            
            archivos_encontrados = 0
            baseline_temporal = {}
            
            for ruta_base in self.rutas_monitoreadas:
                if not os.path.exists(ruta_base):
                    self.logger.warning(f"Ruta no existe: {ruta_base}")
                    continue
                
                for archivo in self._escanear_directorio(ruta_base):
                    if self._debe_monitorear_archivo(archivo):
                        try:
                            metadatos = MetadatosArchivoAvanzados.desde_archivo(archivo)
                            baseline_temporal[archivo] = metadatos
                            archivos_encontrados += 1
                            
                            if archivos_encontrados % 1000 == 0:
                                self.logger.info(f"Procesados {archivos_encontrados} archivos...")
                        
                        except Exception as e:
                            self.logger.error(f"Error procesando {archivo}: {e}")
            
            with self._lock_baseline:
                self.baseline = baseline_temporal
            
            self.estado = EstadoMonitoreo.ACTIVO
            self.logger.info(f"Baseline establecida: {len(self.baseline)} archivos")
            
            # Actualizar estadísticas
            self.estadisticas['total_archivos_baseline'] = len(self.baseline)
            self.estadisticas['fecha_ultima_baseline'] = datetime.now()
            
            return True
        
        except Exception as e:
            self.logger.error(f"Error estableciendo baseline: {e}")
            self.estado = EstadoMonitoreo.ERROR
            return False
    
    def iniciar_monitoreo(self) -> bool:
        """Inicia el monitoreo continuo."""
        try:
            if self.estado == EstadoMonitoreo.ACTIVO and self._hilo_monitoreo:
                self.logger.warning("Monitoreo ya activo")
                return True
            
            if not self.baseline:
                self.logger.info("Estableciendo baseline antes de iniciar monitoreo...")
                if not self.establecer_baseline():
                    return False
            
            self._detener_monitoreo.clear()
            self._hilo_monitoreo = threading.Thread(target=self._ciclo_monitoreo, daemon=True)
            self._hilo_monitoreo.start()
            
            self.estado = EstadoMonitoreo.ACTIVO
            self.logger.info("Monitoreo FIM iniciado")
            
            return True
        
        except Exception as e:
            self.logger.error(f"Error iniciando monitoreo: {e}")
            self.estado = EstadoMonitoreo.ERROR
            return False
    
    def detener_monitoreo(self) -> bool:
        """Detiene el monitoreo."""
        try:
            self.estado = EstadoMonitoreo.FINALIZANDO
            self._detener_monitoreo.set()
            
            if self._hilo_monitoreo and self._hilo_monitoreo.is_alive():
                self._hilo_monitoreo.join(timeout=30)
            
            self.estado = EstadoMonitoreo.INACTIVO
            self.logger.info("Monitoreo FIM detenido")
            
            return True
        
        except Exception as e:
            self.logger.error(f"Error deteniendo monitoreo: {e}")
            return False
    
    def _ciclo_monitoreo(self):
        """Ciclo principal de monitoreo."""
        while not self._detener_monitoreo.is_set():
            try:
                inicio_ciclo = time.time()
                cambios_detectados = self._escanear_cambios()
                
                if cambios_detectados:
                    self.logger.info(f"Detectados {len(cambios_detectados)} cambios")
                    self._procesar_cambios(cambios_detectados)
                
                # Optimización del rendimiento
                self.optimizador.optimizar_ciclo(self.baseline, self.estadisticas)
                
                # Esperar hasta el próximo ciclo
                tiempo_transcurrido = time.time() - inicio_ciclo
                tiempo_espera = max(0, self.intervalo_escaneo - tiempo_transcurrido)
                
                if self._detener_monitoreo.wait(tiempo_espera):
                    break
            
            except Exception as e:
                self.logger.error(f"Error en ciclo de monitoreo: {e}")
                time.sleep(10)  # Pausa antes de reintentar
    
    def _escanear_cambios(self) -> List[Tuple[str, TipoCambio, Optional[MetadatosArchivoAvanzados], Optional[MetadatosArchivoAvanzados]]]:
        """Escanea cambios desde la última baseline."""
        cambios = []
        archivos_actuales = set()
        
        # Escanear archivos actuales
        for ruta_base in self.rutas_monitoreadas:
            for archivo in self._escanear_directorio(ruta_base):
                if self._debe_monitorear_archivo(archivo):
                    archivos_actuales.add(archivo)
                    
                    try:
                        metadatos_actuales = MetadatosArchivoAvanzados.desde_archivo(archivo)
                        
                        if archivo in self.baseline:
                            # Archivo existente - verificar cambios
                            metadatos_anteriores = self.baseline[archivo]
                            cambios_archivo = metadatos_actuales.comparar_con(metadatos_anteriores)
                            
                            if cambios_archivo:
                                for tipo_cambio in cambios_archivo:
                                    cambios.append((archivo, tipo_cambio, metadatos_actuales, metadatos_anteriores))
                        else:
                            # Archivo nuevo
                            cambios.append((archivo, TipoCambio.CREADO, metadatos_actuales, None))
                    
                    except Exception as e:
                        self.logger.error(f"Error escaneando {archivo}: {e}")
        
        # Detectar archivos eliminados
        with self._lock_baseline:
            archivos_baseline = set(self.baseline.keys())
        
        archivos_eliminados = archivos_baseline - archivos_actuales
        for archivo_eliminado in archivos_eliminados:
            metadatos_anteriores = self.baseline[archivo_eliminado]
            cambios.append((archivo_eliminado, TipoCambio.ELIMINADO, None, metadatos_anteriores))
        
        return cambios
    
    def _procesar_cambios(self, cambios: List[Tuple[str, TipoCambio, Optional[MetadatosArchivoAvanzados], Optional[MetadatosArchivoAvanzados]]]):
        """Procesa los cambios detectados."""
        for archivo, tipo_cambio, metadatos_actuales, metadatos_anteriores in cambios:
            try:
                # Analizar amenaza
                tipo_amenaza = self.analizador_amenazas.analizar_cambio(
                    archivo, tipo_cambio, metadatos_actuales, metadatos_anteriores
                )
                
                # Determinar nivel de criticidad
                if metadatos_actuales:
                    nivel_criticidad = metadatos_actuales.nivel_criticidad
                elif metadatos_anteriores:
                    nivel_criticidad = metadatos_anteriores.nivel_criticidad
                else:
                    nivel_criticidad = NivelCriticidadFIM.INFO
                
                # Crear alerta
                alerta = AlertaFIM(
                    id_alerta=f"FIM_{int(time.time()*1000)}_{hash(archivo) % 10000}",
                    tipo_cambio=tipo_cambio,
                    tipo_amenaza=tipo_amenaza,
                    archivo_afectado=archivo,
                    metadatos_anteriores=metadatos_anteriores,
                    metadatos_actuales=metadatos_actuales,
                    timestamp=datetime.now(),
                    nivel_criticidad=nivel_criticidad,
                    descripcion=self._generar_descripcion_cambio(archivo, tipo_cambio, tipo_amenaza),
                    detalles_cambio=self._generar_detalles_cambio(metadatos_actuales, metadatos_anteriores)
                )
                
                # Registrar alerta
                with self._lock_alertas:
                    self.alertas.append(alerta)
                
                # Enviar a SIEM si está disponible
                if self.siem:
                    self.siem.procesar_evento({
                        'tipo': 'FIM_CAMBIO',
                        'archivo': archivo,
                        'cambio': tipo_cambio.value,
                        'amenaza': tipo_amenaza.value if tipo_amenaza else None,
                        'criticidad': nivel_criticidad.value,
                        'timestamp': alerta.timestamp.isoformat()
                    })
                
                # Actualizar baseline si es necesario
                if tipo_cambio != TipoCambio.ELIMINADO and metadatos_actuales:
                    with self._lock_baseline:
                        self.baseline[archivo] = metadatos_actuales
                elif tipo_cambio == TipoCambio.ELIMINADO:
                    with self._lock_baseline:
                        self.baseline.pop(archivo, None)
                
                self.logger.info(f"Procesado cambio: {archivo} - {tipo_cambio.value}")
            
            except Exception as e:
                self.logger.error(f"Error procesando cambio en {archivo}: {e}")
    
    def _escanear_directorio(self, ruta: str) -> List[str]:
        """Escanea directorio recursivamente."""
        archivos = []
        
        try:
            for ruta_archivo in listar_archivos_recursivo(ruta, None):
                archivos.append(ruta_archivo)
        except Exception as e:
            self.logger.error(f"Error escaneando directorio {ruta}: {e}")
        
        return archivos
    
    def _debe_monitorear_archivo(self, archivo: str) -> bool:
        """Determina si un archivo debe ser monitoreado."""
        # Verificar exclusiones
        for exclusion in self.rutas_excluidas:
            if exclusion in archivo:
                return False
        
        # Verificar extensiones si están configuradas
        if self.extensiones_monitoreadas:
            extension = Path(archivo).suffix.lower()
            if extension not in self.extensiones_monitoreadas:
                return False
        
        # Verificar permisos de lectura
        if not validar_permisos_lectura(archivo):
            return False
        
        return True
    
    def _generar_descripcion_cambio(self, archivo: str, tipo_cambio: TipoCambio, tipo_amenaza: Optional[TipoAmenazaFIM]) -> str:
        """Genera descripción del cambio."""
        descripcion_base = f"Archivo {archivo} - {tipo_cambio.value}"
        
        if tipo_amenaza:
            descripcion_base += f" - Amenaza detectada: {tipo_amenaza.value}"
        
        return descripcion_base
    
    def _generar_detalles_cambio(self, metadatos_actuales: Optional[MetadatosArchivoAvanzados], metadatos_anteriores: Optional[MetadatosArchivoAvanzados]) -> Dict[str, Any]:
        """Genera detalles específicos del cambio."""
        detalles = {}
        
        if metadatos_anteriores and metadatos_actuales:
            # Cambios específicos
            if metadatos_actuales.hash_sha256 != metadatos_anteriores.hash_sha256:
                detalles['hash_cambio'] = {
                    'anterior': metadatos_anteriores.hash_sha256,
                    'actual': metadatos_actuales.hash_sha256
                }
            
            if metadatos_actuales.tamaño_bytes != metadatos_anteriores.tamaño_bytes:
                detalles['tamaño_cambio'] = {
                    'anterior': metadatos_anteriores.tamaño_bytes,
                    'actual': metadatos_actuales.tamaño_bytes,
                    'diferencia': metadatos_actuales.tamaño_bytes - metadatos_anteriores.tamaño_bytes
                }
            
            if metadatos_actuales.permisos_texto != metadatos_anteriores.permisos_texto:
                detalles['permisos_cambio'] = {
                    'anterior': metadatos_anteriores.permisos_texto,
                    'actual': metadatos_actuales.permisos_texto
                }
        
        return detalles
    
    def obtener_alertas(self, filtros: Optional[Dict[str, Any]] = None) -> List[AlertaFIM]:
        """Obtiene alertas con filtros opcionales."""
        with self._lock_alertas:
            alertas = self.alertas.copy()
        
        if not filtros:
            return alertas
        
        # Aplicar filtros
        if 'nivel_criticidad' in filtros:
            nivel = filtros['nivel_criticidad']
            if isinstance(nivel, str):
                nivel = NivelCriticidadFIM(nivel)
            alertas = [a for a in alertas if a.nivel_criticidad == nivel]
        
        if 'tipo_cambio' in filtros:
            tipo = filtros['tipo_cambio']
            if isinstance(tipo, str):
                tipo = TipoCambio(tipo)
            alertas = [a for a in alertas if a.tipo_cambio == tipo]
        
        if 'fecha_desde' in filtros:
            fecha_desde = filtros['fecha_desde']
            alertas = [a for a in alertas if a.timestamp >= fecha_desde]
        
        if 'fecha_hasta' in filtros:
            fecha_hasta = filtros['fecha_hasta']
            alertas = [a for a in alertas if a.timestamp <= fecha_hasta]
        
        return alertas
    
    def generar_reporte(self, periodo_horas: int = 24) -> ReporteFIM:
        """Genera reporte de las últimas horas."""
        fin = datetime.now()
        inicio = fin - timedelta(hours=periodo_horas)
        
        alertas_periodo = self.obtener_alertas({
            'fecha_desde': inicio,
            'fecha_hasta': fin
        })
        
        reporte = ReporteFIM.generar_desde_alertas(alertas_periodo, inicio, fin)
        reporte.total_archivos_monitoreados = len(self.baseline)
        
        return reporte
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas del sistema."""
        with self._lock_alertas:
            total_alertas = len(self.alertas)
        
        with self._lock_baseline:
            total_archivos = len(self.baseline)
        
        estadisticas = {
            'estado': self.estado.value,
            'total_archivos_monitoreados': total_archivos,
            'total_alertas_generadas': total_alertas,
            'rutas_monitoreadas': list(self.rutas_monitoreadas),
            'rutas_excluidas': list(self.rutas_excluidas),
            'intervalo_escaneo': self.intervalo_escaneo,
            'ultima_actualizacion': datetime.now().isoformat()
        }
        
        estadisticas.update(self.estadisticas)
        
        return estadisticas
    
    def limpiar_alertas_antiguas(self, dias_retencion: int = 30):
        """Limpia alertas más antiguas que el período especificado."""
        fecha_limite = datetime.now() - timedelta(days=dias_retencion)
        
        with self._lock_alertas:
            alertas_anteriores = len(self.alertas)
            self.alertas = [a for a in self.alertas if a.timestamp > fecha_limite]
            alertas_eliminadas = alertas_anteriores - len(self.alertas)
        
        if alertas_eliminadas > 0:
            self.logger.info(f"Limpiadas {alertas_eliminadas} alertas antiguas")
    
    def exportar_configuracion(self) -> Dict[str, Any]:
        """Exporta la configuración actual."""
        return {
            'rutas_monitoreadas': list(self.rutas_monitoreadas),
            'rutas_excluidas': list(self.rutas_excluidas),
            'extensiones_monitoreadas': list(self.extensiones_monitoreadas),
            'profundidad_maxima': self.profundidad_maxima,
            'intervalo_escaneo': self.intervalo_escaneo,
            'config': self.config
        }
    
    def importar_configuracion(self, config: Dict[str, Any]) -> bool:
        """Importa configuración."""
        try:
            self.rutas_monitoreadas = set(config.get('rutas_monitoreadas', []))
            self.rutas_excluidas = set(config.get('rutas_excluidas', []))
            self.extensiones_monitoreadas = set(config.get('extensiones_monitoreadas', []))
            self.profundidad_maxima = config.get('profundidad_maxima', 10)
            self.intervalo_escaneo = config.get('intervalo_escaneo', 300)
            
            self.logger.info("Configuración importada correctamente")
            return True
        
        except Exception as e:
            self.logger.error(f"Error importando configuración: {e}")
            return False
