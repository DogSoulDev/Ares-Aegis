"""
Controlador principal del Mini-SIEM para Ares Aegis
Orquesta la recolección, almacenamiento, análisis y alertas de eventos de seguridad
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from pathlib import Path
import threading
import queue
import json

from .recolector_logs import RecolectorRegistros
from .almacenamiento import AlmacenadorEventos
from .motor_correlacion import MotorCorrelacion, Alerta, SeveridadAlerta

logger = logging.getLogger(__name__)

class ControladorMiniSiem:
    """
    Controlador principal del Mini-SIEM
    Coordina todos los componentes del sistema de gestión de eventos de seguridad
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._cargar_configuracion(config_path)
        
        # Componentes principales
        self.recolector = RecolectorRegistros()
        self.almacenador = AlmacenadorEventos(self.config.get('db_path'))
        self.motor_correlacion = MotorCorrelacion()
        
        # Estado del sistema
        self.running = False
        self.task_recoleccion = None
        
        # Configurar callbacks
        self.recolector.agregar_callback(self.procesar_evento_entrante)
        self.motor_correlacion.agregar_callback_alerta(self.manejar_alerta)
        
        # Callbacks externos para notificaciones
        self.callbacks_alerta_externa = []
        self.callbacks_evento = []
        
        # Configuración de notificaciones
        self.notificaciones_activas = self.config.get('notificaciones', {
            'desktop': True,
            'terminal': True,
            'log': True
        })
        
        logger.info("Controlador Mini-SIEM inicializado")
        
    def _cargar_configuracion(self, config_path: Optional[str]) -> Dict:
        """Cargar configuración del Mini-SIEM"""
        config_default = {
            'db_path': None,
            'retention_days': 30,
            'batch_processing': True,
            'rules_file': None,
            'notificaciones': {
                'desktop': True,
                'terminal': True,
                'log': True
            }
        }
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_usuario = json.load(f)
                config_default.update(config_usuario)
            except Exception as e:
                logger.error(f"Error cargando configuración: {e}")
                
        return config_default
        
    async def iniciar(self):
        """Iniciar el Mini-SIEM"""
        if self.running:
            logger.warning("Mini-SIEM ya está ejecutándose")
            return
            
        logger.info("Iniciando Mini-SIEM...")
        self.running = True
        
        try:
            # Iniciar almacenamiento en batch
            if self.config.get('batch_processing', True):
                self.almacenador.iniciar_procesamiento_batch()
                
            # Cargar reglas personalizadas si existen
            if self.config.get('rules_file'):
                self.motor_correlacion.cargar_reglas_desde_archivo(
                    self.config['rules_file']
                )
                
            # Iniciar recolección de logs
            self.task_recoleccion = asyncio.create_task(
                self.recolector.iniciar_recoleccion()
            )
            
            # Programar limpieza periódica
            asyncio.create_task(self._tarea_limpieza_periodica())
            
            logger.info("Mini-SIEM iniciado exitosamente")
            
        except Exception as e:
            logger.error(f"Error iniciando Mini-SIEM: {e}")
            await self.detener()
            raise
            
    async def detener(self):
        """Detener el Mini-SIEM"""
        if not self.running:
            return
            
        logger.info("Deteniendo Mini-SIEM...")
        self.running = False
        
        try:
            # Detener recolección
            self.recolector.detener_recoleccion()
            
            if self.task_recoleccion:
                self.task_recoleccion.cancel()
                try:
                    await self.task_recoleccion
                except asyncio.CancelledError:
                    pass
                    
            # Detener almacenamiento
            self.almacenador.detener_procesamiento_batch()
            
            logger.info("Mini-SIEM detenido")
            
        except Exception as e:
            logger.error(f"Error deteniendo Mini-SIEM: {e}")
            
    async def procesar_evento_entrante(self, evento: Dict):
        """Procesar evento entrante del recolector"""
        try:
            # Almacenar evento
            self.almacenador.almacenar_evento(evento)
            
            # Procesar con motor de correlación
            await self.motor_correlacion.procesar_evento(evento)
            
            # Notificar a callbacks externos
            for callback in self.callbacks_evento:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(evento)
                    else:
                        callback(evento)
                except Exception as e:
                    logger.error(f"Error en callback de evento: {e}")
                    
        except Exception as e:
            logger.error(f"Error procesando evento: {e}")
            
    async def manejar_alerta(self, alerta: Alerta):
        """Manejar alerta generada por el motor de correlación"""
        try:
            # Log de la alerta
            if self.notificaciones_activas.get('log', True):
                logger.warning(f"ALERTA SIEM: {alerta.titulo} - {alerta.severidad.value}")
                
            # Notificación de escritorio
            if self.notificaciones_activas.get('desktop', True):
                await self._enviar_notificacion_desktop(alerta)
                
            # Notificación en terminal
            if self.notificaciones_activas.get('terminal', True):
                self._imprimir_alerta_terminal(alerta)
                
            # Notificar callbacks externos
            for callback in self.callbacks_alerta_externa:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(alerta)
                    else:
                        callback(alerta)
                except Exception as e:
                    logger.error(f"Error en callback de alerta: {e}")
                    
        except Exception as e:
            logger.error(f"Error manejando alerta: {e}")
            
    async def _enviar_notificacion_desktop(self, alerta: Alerta):
        """Enviar notificación de escritorio"""
        try:
            # Usar notify-send en sistemas Linux
            import subprocess
            
            # Mapear severidad a urgencia
            urgencia_map = {
                SeveridadAlerta.INFO: 'low',
                SeveridadAlerta.WARNING: 'normal',
                SeveridadAlerta.HIGH: 'critical',
                SeveridadAlerta.CRITICAL: 'critical'
            }
            
            urgencia = urgencia_map.get(alerta.severidad, 'normal')
            
            # Comando notify-send
            cmd = [
                'notify-send',
                '--urgency', urgencia,
                '--icon', 'security-high',
                f'ARES AEGIS - {alerta.severidad.value}',
                alerta.titulo
            ]
            
            # Ejecutar en background
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )
            await proc.wait()
            
        except Exception as e:
            logger.debug(f"No se pudo enviar notificación desktop: {e}")
            
    def _imprimir_alerta_terminal(self, alerta: Alerta):
        """Imprimir alerta en terminal con colores"""
        try:
            # Colores ANSI
            colores = {
                SeveridadAlerta.INFO: '\033[94m',      # Azul
                SeveridadAlerta.WARNING: '\033[93m',   # Amarillo
                SeveridadAlerta.HIGH: '\033[91m',      # Rojo
                SeveridadAlerta.CRITICAL: '\033[95m'   # Magenta
            }
            reset = '\033[0m'
            
            color = colores.get(alerta.severidad, '')
            timestamp = alerta.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            
            print(f"\n{color}[ALERTA SIEM] {timestamp}")
            print(f"Severidad: {alerta.severidad.value}")
            print(f"Título: {alerta.titulo}")
            print(f"Descripción: {alerta.descripcion}")
            print(f"Eventos relacionados: {len(alerta.eventos_relacionados)}{reset}\n")
            
        except Exception as e:
            logger.debug(f"Error imprimiendo alerta en terminal: {e}")
            
    async def _tarea_limpieza_periodica(self):
        """Tarea para limpieza periódica de datos antiguos"""
        while self.running:
            try:
                # Esperar 24 horas
                await asyncio.sleep(24 * 60 * 60)
                
                if not self.running:
                    break
                    
                # Limpiar eventos antiguos
                dias_retencion = self.config.get('retention_days', 30)
                self.almacenador.limpiar_eventos_antiguos(dias_retencion)
                
                # Reset estadísticas si es necesario
                # self.motor_correlacion.reset_estadisticas()
                
                logger.info(f"Limpieza periódica completada (retención: {dias_retencion} días)")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error en limpieza periódica: {e}")
                
    def agregar_callback_alerta(self, callback: Callable):
        """Agregar callback para alertas"""
        self.callbacks_alerta_externa.append(callback)
        
    def agregar_callback_evento(self, callback: Callable):
        """Agregar callback para eventos"""
        self.callbacks_evento.append(callback)
        
    def obtener_estadisticas_completas(self) -> Dict:
        """Obtener estadísticas completas del Mini-SIEM"""
        try:
            stats_correlacion = self.motor_correlacion.obtener_estadisticas()
            stats_almacenamiento = self.almacenador.obtener_metricas_rendimiento()
            stats_dashboard = self.almacenador.obtener_estadisticas_dashboard()
            
            return {
                'estado': 'activo' if self.running else 'inactivo',
                'timestamp': datetime.now().isoformat(),
                'correlacion': stats_correlacion,
                'almacenamiento': stats_almacenamiento,
                'dashboard': stats_dashboard,
                'configuracion': {
                    'retention_days': self.config.get('retention_days', 30),
                    'batch_processing': self.config.get('batch_processing', True),
                    'notificaciones': self.notificaciones_activas
                }
            }
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {'error': str(e)}
            
    def consultar_eventos_recientes(self, 
                                  limite: int = 50,
                                  categoria: Optional[str] = None,
                                  severidad: Optional[str] = None) -> List[Dict]:
        """Consultar eventos recientes"""
        try:
            return self.almacenador.consultar_eventos(
                limite=limite,
                categoria=categoria,
                severidad=severidad,
                desde=datetime.now() - timedelta(hours=24)
            )
        except Exception as e:
            logger.error(f"Error consultando eventos: {e}")
            return []
            
    def obtener_alertas_activas(self) -> List[Dict]:
        """Obtener alertas activas del sistema"""
        try:
            # Obtener eventos críticos recientes
            eventos_criticos = self.almacenador.consultar_eventos(
                limite=20,
                severidad='CRITICAL',
                desde=datetime.now() - timedelta(hours=1)
            )
            
            alertas_activas = []
            for evento in eventos_criticos:
                alertas_activas.append({
                    'id': evento.get('id'),
                    'timestamp': evento.get('timestamp'),
                    'severidad': evento.get('severity', 'UNKNOWN'),
                    'categoria': evento.get('event_category', 'unknown'),
                    'mensaje': evento.get('message', ''),
                    'origen': evento.get('source_type', 'unknown')
                })
                
            return alertas_activas
            
        except Exception as e:
            logger.error(f"Error obteniendo alertas activas: {e}")
            return []
            
    def exportar_informe_seguridad(self, archivo: str, 
                                 desde: Optional[datetime] = None,
                                 hasta: Optional[datetime] = None):
        """Exportar informe de seguridad a CSV"""
        try:
            if not desde:
                desde = datetime.now() - timedelta(days=7)
            if not hasta:
                hasta = datetime.now()
                
            filtros = {
                'desde': desde,
                'hasta': hasta
            }
            
            self.almacenador.exportar_eventos_csv(archivo, filtros)
            logger.info(f"Informe exportado a: {archivo}")
            
        except Exception as e:
            logger.error(f"Error exportando informe: {e}")
            raise
            
    def configurar_notificaciones(self, desktop: bool = True, 
                                terminal: bool = True, 
                                log: bool = True):
        """Configurar tipos de notificaciones"""
        self.notificaciones_activas = {
            'desktop': desktop,
            'terminal': terminal,
            'log': log
        }
        logger.info(f"Notificaciones configuradas: {self.notificaciones_activas}")
        
    def agregar_regla_personalizada(self, config_regla: Dict):
        """Agregar regla de correlación personalizada"""
        try:
            regla = self.motor_correlacion._crear_regla_desde_config(config_regla)
            if regla:
                self.motor_correlacion.agregar_regla(regla)
                logger.info(f"Regla personalizada agregada: {config_regla.get('nombre')}")
            else:
                logger.error("No se pudo crear la regla personalizada")
        except Exception as e:
            logger.error(f"Error agregando regla personalizada: {e}")
            
    def remover_regla(self, nombre_regla: str):
        """Remover regla de correlación"""
        self.motor_correlacion.remover_regla(nombre_regla)
        
    async def realizar_diagnostico(self) -> Dict:
        """Realizar diagnóstico del sistema Mini-SIEM"""
        diagnostico = {
            'timestamp': datetime.now().isoformat(),
            'estado_general': 'OK',
            'componentes': {},
            'problemas': []
        }
        
        try:
            # Verificar recolector
            diagnostico['componentes']['recolector'] = {
                'estado': 'activo' if self.running else 'inactivo',
                'fuentes_monitoreadas': len(self.recolector.fuentes_criticas)
            }
            
            # Verificar almacenamiento
            stats_db = self.almacenador.obtener_metricas_rendimiento()
            diagnostico['componentes']['almacenamiento'] = {
                'estado': 'OK',
                'total_eventos': stats_db.get('total_eventos', 0),
                'tamano_db_mb': stats_db.get('tamano_db_mb', 0)
            }
            
            # Verificar motor de correlación
            stats_motor = self.motor_correlacion.obtener_estadisticas()
            diagnostico['componentes']['correlacion'] = {
                'estado': 'OK',
                'reglas_activas': stats_motor.get('reglas_activas', 0),
                'eventos_procesados': stats_motor.get('eventos_procesados', 0),
                'alertas_generadas': stats_motor.get('alertas_generadas', 0)
            }
            
            # Verificar archivos de log críticos
            archivos_inaccesibles = []
            for nombre, ruta in self.recolector.fuentes_criticas.items():
                if not Path(ruta).exists():
                    archivos_inaccesibles.append(f"{nombre}: {ruta}")
                    
            if archivos_inaccesibles:
                diagnostico['problemas'].extend([
                    f"Archivo de log inaccesible: {archivo}" 
                    for archivo in archivos_inaccesibles
                ])
                
            # Verificar espacio en disco
            import shutil
            if hasattr(shutil, 'disk_usage'):
                _, _, espacio_libre = shutil.disk_usage('/')
                espacio_libre_gb = espacio_libre / (1024**3)
                
                if espacio_libre_gb < 1:  # Menos de 1GB libre
                    diagnostico['problemas'].append(
                        f"Poco espacio en disco: {espacio_libre_gb:.2f}GB disponibles"
                    )
                    
            if diagnostico['problemas']:
                diagnostico['estado_general'] = 'ADVERTENCIA'
                
        except Exception as e:
            diagnostico['estado_general'] = 'ERROR'
            diagnostico['problemas'].append(f"Error en diagnóstico: {e}")
            
        return diagnostico
