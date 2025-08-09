#!/usr/bin/env python3
"""
Ares Aegis - Controlador FIM
Controlador especializado para gestionar operaciones de integridad de archivos

Creado por DogSoulDev (https://github.com/DogSoulDev)
Todos los derechos reservados. Este código es propietario y confidencial.
La copia, distribución o modificación no autorizada está estrictamente prohibida.

Versión: 4.0.0
"""

import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path

from ..modelo.modelo_fim import FIM
from ..modelo.modelo_siem import SIEM, TipoEvento
from ..utils.utils_ayuda_logging import configurar_logger_modulo


class ControladorFIM:
    """Controlador especializado para operaciones de FIM (File Integrity Monitoring)."""
    
    def __init__(self, fim: FIM, siem: SIEM):
        """
        Inicializar el controlador FIM.
        
        Args:
            fim: Instancia del FIM avanzado
            siem: Instancia del SIEM para registro de eventos
        """
        self.fim = fim
        self.siem = siem
        self.logger = configurar_logger_modulo("controlador_fim")
        
        # Estado del controlador
        self.monitoreando = False
        self.ultimo_baseline = None
        self.cambios_detectados = []
        self.archivos_criticos = set()
        self.lock = threading.Lock()
        
        # Configuración de monitoreo
        self.configuracion = {
            'rutas_monitoreadas': [
                '/etc',
                '/usr/bin',
                '/usr/sbin',
                '/home',
                '/var/log'
            ],
            'extensiones_criticas': ['.conf', '.cfg', '.ini', '.config', '.sh', '.py', '.exe'],
            'intervalo_verificacion_segundos': 300,  # 5 minutos
            'crear_baseline_automatico': True
        }
        
        self.logger.info("Controlador FIM inicializado")
    
    def iniciar_monitoreo(self) -> bool:
        """
        Iniciar el monitoreo de integridad de archivos.
        
        Returns:
            bool: True si se inició exitosamente
        """
        try:
            with self.lock:
                if self.monitoreando:
                    self.logger.warning("El monitoreo FIM ya está activo")
                    return True
                
                self.monitoreando = True
            
            # Registrar evento
            if self.siem:
                self.siem.registrar_evento(
                    TipoEvento.SERVICIO_INICIADO,
                    "Monitoreo FIM iniciado desde controlador",
                    {'componente': 'fim'},
                    "MEDIO"
                )
            
            self.logger.info("Monitoreo FIM iniciado exitosamente")
            return True
        
        except Exception as e:
            self.logger.error(f"Error iniciando monitoreo FIM: {e}")
            if self.siem:
                self.siem.registrar_evento(
                    TipoEvento.ERROR_SISTEMA,
                    f"Error iniciando monitoreo FIM: {e}",
                    {'componente': 'fim', 'error': str(e)},
                    "ALTO"
                )
            return False
    
    def detener_monitoreo(self) -> bool:
        """
        Detener el monitoreo de integridad de archivos.
        
        Returns:
            bool: True si se detuvo exitosamente
        """
        try:
            with self.lock:
                if not self.monitoreando:
                    self.logger.warning("El monitoreo FIM ya está inactivo")
                    return True
                
                self.monitoreando = False
            
            # Registrar evento
            if self.siem:
                self.siem.registrar_evento(
                    TipoEvento.SERVICIO_DETENIDO,
                    "Monitoreo FIM detenido desde controlador",
                    {'componente': 'fim'},
                    "MEDIO"
                )
            
            self.logger.info("Monitoreo FIM detenido exitosamente")
            return True
        
        except Exception as e:
            self.logger.error(f"Error deteniendo monitoreo FIM: {e}")
            if self.siem:
                self.siem.registrar_evento(
                    TipoEvento.ERROR_SISTEMA,
                    f"Error deteniendo monitoreo FIM: {e}",
                    {'componente': 'fim', 'error': str(e)},
                    "ALTO"
                )
            return False
    
    def crear_baseline(self, rutas_personalizadas: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Crear una línea base de integridad de archivos.
        
        Args:
            rutas_personalizadas: Rutas específicas para el baseline (opcional)
            
        Returns:
            Dict[str, Any]: Resultados de la creación del baseline
        """
        try:
            self.logger.info("Iniciando creación de baseline FIM")
            
            inicio_tiempo = time.time()
            
            # Usar rutas personalizadas o configuradas
            rutas = rutas_personalizadas or self.configuracion['rutas_monitoreadas']
            
            # Crear baseline usando el FIM
            resultado_fim = self.fim.establecer_baseline(forzar_recalculo=True)
            
            tiempo_total = time.time() - inicio_tiempo
            
            # Construir resultado del controlador
            resultado = {
                'timestamp': datetime.now().isoformat(),
                'rutas_procesadas': rutas,
                'archivos_procesados': 0,  # Información no disponible directamente
                'tiempo_creacion': tiempo_total,
                'baseline_creado': resultado_fim,
                'errores': []
            }
            
            # Guardar como último baseline
            with self.lock:
                self.ultimo_baseline = resultado
            
            # Registrar evento
            if self.siem:
                self.siem.registrar_evento(
                    TipoEvento.CONFIGURACION_MODIFICADA,
                    f"Baseline FIM creado: {resultado['archivos_procesados']} archivos procesados",
                    resultado,
                    "MEDIO"
                )
            
            self.logger.info(f"Baseline FIM creado exitosamente en {tiempo_total:.2f}s")
            return resultado
        
        except Exception as e:
            self.logger.error(f"Error creando baseline FIM: {e}")
            resultado_error = {
                'timestamp': datetime.now().isoformat(),
                'baseline_creado': False,
                'error': str(e)
            }
            
            if self.siem:
                self.siem.registrar_evento(
                    TipoEvento.ERROR_SISTEMA,
                    f"Error creando baseline FIM: {e}",
                    resultado_error,
                    "ALTO"
                )
            
            return resultado_error
    
    def verificar_integridad(self) -> Dict[str, Any]:
        """
        Verificar la integridad de archivos contra la línea base.
        
        Returns:
            Dict[str, Any]: Resultados de la verificación
        """
        try:
            self.logger.info("Iniciando verificación de integridad FIM")
            
            inicio_tiempo = time.time()
            
            # Obtener alertas recientes como verificación de integridad
            cambios = self.fim.obtener_alertas()
            
            tiempo_total = time.time() - inicio_tiempo
            
            # Procesar cambios detectados
            cambios_criticos = []
            cambios_menores = []
            
            for cambio in cambios:
                # Convertir cambio a diccionario si es necesario
                if hasattr(cambio, 'to_dict'):
                    cambio_dict = cambio.to_dict()
                elif isinstance(cambio, dict):
                    cambio_dict = cambio
                else:
                    # Si no se puede convertir, crear diccionario básico
                    cambio_dict = {'tipo_cambio': str(cambio), 'ruta_archivo': 'desconocido'}
                
                # Clasificar cambios por criticidad
                if self._es_cambio_critico(cambio_dict):
                    cambios_criticos.append(cambio_dict)
                else:
                    cambios_menores.append(cambio_dict)
                
                # Registrar cambio individual en SIEM
                self._registrar_cambio_siem(cambio_dict)
            
            # Actualizar lista de cambios detectados
            with self.lock:
                self.cambios_detectados.extend([c for c in cambios if hasattr(c, 'to_dict')])
                
                # Mantener solo los últimos 1000 cambios
                if len(self.cambios_detectados) > 1000:
                    self.cambios_detectados = self.cambios_detectados[-1000:]
            
            resultado = {
                'timestamp': datetime.now().isoformat(),
                'tiempo_verificacion': tiempo_total,
                'total_cambios': len(cambios),
                'cambios_criticos': len(cambios_criticos),
                'cambios_menores': len(cambios_menores),
                'cambios_detectados': [c.to_dict() if hasattr(c, 'to_dict') else c for c in cambios]
            }
            
            # Registrar resultado general
            nivel_criticidad = "CRITICO" if cambios_criticos else "ALTO" if cambios else "BAJO"
            
            if self.siem:
                self.siem.registrar_evento(
                    TipoEvento.ANALISIS_COMPLETADO,
                    f"Verificación FIM completada: {len(cambios)} cambios detectados ({len(cambios_criticos)} críticos)",
                    resultado,
                    nivel_criticidad
                )
            
            if cambios:
                self.logger.warning(f"Verificación FIM completada: {len(cambios)} cambios detectados ({len(cambios_criticos)} críticos)")
            else:
                self.logger.info("Verificación FIM completada: Sin cambios detectados")
            
            return resultado
        
        except Exception as e:
            self.logger.error(f"Error en verificación de integridad: {e}")
            resultado_error = {
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'verificacion_completada': False
            }
            
            if self.siem:
                self.siem.registrar_evento(
                    TipoEvento.ERROR_SISTEMA,
                    f"Error en verificación FIM: {e}",
                    resultado_error,
                    "ALTO"
                )
            
            return resultado_error
    
    def _es_cambio_critico(self, cambio: Dict[str, Any]) -> bool:
        """
        Determinar si un cambio es crítico.
        
        Args:
            cambio: Datos del cambio detectado
            
        Returns:
            bool: True si el cambio es crítico
        """
        ruta = cambio.get('ruta_archivo', '')
        tipo_cambio = cambio.get('tipo_cambio', '')
        
        # Archivos en directorios críticos
        rutas_criticas = ['/etc', '/usr/bin', '/usr/sbin', '/boot']
        if any(ruta.startswith(ruta_critica) for ruta_critica in rutas_criticas):
            return True
        
        # Archivos ejecutables
        if ruta.endswith(('.exe', '.sh', '.py', '.bin')):
            return True
        
        # Cambios de permisos en archivos importantes
        if tipo_cambio in ['permisos_modificados', 'propietario_modificado'] and ruta.startswith('/etc'):
            return True
        
        # Archivos de configuración críticos
        archivos_criticos = ['passwd', 'shadow', 'sudoers', 'hosts', 'resolv.conf']
        if any(archivo_critico in ruta for archivo_critico in archivos_criticos):
            return True
        
        return False
    
    def _registrar_cambio_siem(self, cambio: Dict[str, Any]):
        """
        Registrar un cambio individual en el SIEM.
        
        Args:
            cambio: Datos del cambio detectado
        """
        if not self.siem:
            return
        
        ruta = cambio.get('ruta_archivo', 'desconocido')
        tipo_cambio = cambio.get('tipo_cambio', 'desconocido')
        
        # Determinar tipo de evento SIEM
        if tipo_cambio == 'creado':
            tipo_evento = TipoEvento.ARCHIVO_CREADO
        elif tipo_cambio == 'modificado':
            tipo_evento = TipoEvento.ARCHIVO_MODIFICADO
        elif tipo_cambio == 'eliminado':
            tipo_evento = TipoEvento.ARCHIVO_ELIMINADO
        elif tipo_cambio == 'permisos_modificados':
            tipo_evento = TipoEvento.PERMISOS_MODIFICADOS
        else:
            tipo_evento = TipoEvento.INTEGRIDAD_VIOLADA
        
        # Determinar nivel de criticidad
        nivel = "CRITICO" if self._es_cambio_critico(cambio) else "MEDIO"
        
        self.siem.registrar_evento(
            tipo_evento,
            f"Cambio FIM detectado: {tipo_cambio} en {ruta}",
            cambio,
            nivel
        )
    
    def obtener_estado_fim(self) -> Dict[str, Any]:
        """
        Obtener el estado actual del FIM.
        
        Returns:
            Dict[str, Any]: Estado del FIM
        """
        try:
            stats_fim = self.fim.obtener_estadisticas()
            
            with self.lock:
                cambios_recientes = len([c for c in self.cambios_detectados
                                       if c.get('timestamp', datetime.min) > datetime.now() - timedelta(hours=24)])
            
            return {
                'monitoreando': self.monitoreando,
                'archivos_en_baseline': stats_fim.get('archivos_en_base_datos', 0),
                'ultimo_baseline': self.ultimo_baseline,
                'cambios_detectados_24h': cambios_recientes,
                'total_cambios_historicos': len(self.cambios_detectados),
                'archivos_criticos': len(self.archivos_criticos),
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            self.logger.error(f"Error obteniendo estado FIM: {e}")
            return {
                'monitoreando': self.monitoreando,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def obtener_cambios_recientes(self, limite: int = 100, solo_criticos: bool = False) -> List[Dict[str, Any]]:
        """
        Obtener cambios detectados recientemente.
        
        Args:
            limite: Número máximo de cambios a devolver
            solo_criticos: Si True, solo devolver cambios críticos
            
        Returns:
            List[Dict[str, Any]]: Lista de cambios
        """
        with self.lock:
            cambios = self.cambios_detectados.copy()
        
        # Filtrar solo críticos si se solicita
        if solo_criticos:
            cambios = [c for c in cambios if self._es_cambio_critico(c)]
        
        # Ordenar por timestamp descendente y limitar
        cambios.sort(key=lambda x: x.get('timestamp', datetime.min), reverse=True)
        return cambios[:limite]
    
    def agregar_ruta_monitoreo(self, ruta: str) -> bool:
        """
        Agregar una ruta al monitoreo FIM.
        
        Args:
            ruta: Ruta a agregar al monitoreo
            
        Returns:
            bool: True si se agregó exitosamente
        """
        try:
            if not Path(ruta).exists():
                raise ValueError(f"La ruta no existe: {ruta}")
            
            with self.lock:
                if ruta not in self.configuracion['rutas_monitoreadas']:
                    self.configuracion['rutas_monitoreadas'].append(ruta)
                    
                    # Marcar como crítico si es directorio del sistema
                    if ruta.startswith(('/etc', '/usr/bin', '/usr/sbin', '/boot')):
                        self.archivos_criticos.add(ruta)
            
            # Registrar cambio de configuración
            if self.siem:
                self.siem.registrar_evento(
                    TipoEvento.CONFIGURACION_MODIFICADA,
                    f"Ruta agregada al monitoreo FIM: {ruta}",
                    {'ruta': ruta, 'accion': 'agregar'},
                    "MEDIO"
                )
            
            self.logger.info(f"Ruta agregada al monitoreo FIM: {ruta}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error agregando ruta al monitoreo: {e}")
            return False
    
    def remover_ruta_monitoreo(self, ruta: str) -> bool:
        """
        Remover una ruta del monitoreo FIM.
        
        Args:
            ruta: Ruta a remover del monitoreo
            
        Returns:
            bool: True si se removió exitosamente
        """
        try:
            with self.lock:
                if ruta in self.configuracion['rutas_monitoreadas']:
                    self.configuracion['rutas_monitoreadas'].remove(ruta)
                    self.archivos_criticos.discard(ruta)
            
            # Registrar cambio de configuración
            if self.siem:
                self.siem.registrar_evento(
                    TipoEvento.CONFIGURACION_MODIFICADA,
                    f"Ruta removida del monitoreo FIM: {ruta}",
                    {'ruta': ruta, 'accion': 'remover'},
                    "MEDIO"
                )
            
            self.logger.info(f"Ruta removida del monitoreo FIM: {ruta}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error removiendo ruta del monitoreo: {e}")
            return False
    
    def obtener_rutas_monitoreadas(self) -> List[str]:
        """
        Obtener lista de rutas actualmente monitoreadas.
        
        Returns:
            List[str]: Lista de rutas monitoreadas
        """
        with self.lock:
            return self.configuracion['rutas_monitoreadas'].copy()
    
    def configurar_fim(self, config: Dict[str, Any]):
        """
        Configurar parámetros del FIM.
        
        Args:
            config: Diccionario con configuración
        """
        with self.lock:
            self.configuracion.update(config)
        
        self.logger.info(f"Configuración FIM actualizada: {config}")
        
        if self.siem:
            self.siem.registrar_evento(
                TipoEvento.CONFIGURACION_MODIFICADA,
                "Configuración FIM actualizada",
                config,
                "MEDIO"
            )
    
    def generar_reporte_fim(self) -> str:
        """
        Generar reporte de FIM en formato Markdown.
        
        Returns:
            str: Reporte en formato Markdown
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        estado = self.obtener_estado_fim()
        cambios_recientes = self.obtener_cambios_recientes(20, solo_criticos=False)
        cambios_criticos = self.obtener_cambios_recientes(10, solo_criticos=True)
        
        md = f"# Reporte de FIM (File Integrity Monitoring)\n\n"
        md += f"**Fecha de generación:** {timestamp}\n\n"
        
        # Estado del FIM
        md += "##  Estado del FIM\n\n"
        md += f"- **Estado:** {' Activo' if estado['monitoreando'] else ' Inactivo'}\n"
        md += f"- **Archivos en baseline:** {estado.get('archivos_en_baseline', 0)}\n"
        md += f"- **Cambios detectados (24h):** {estado.get('cambios_detectados_24h', 0)}\n"
        md += f"- **Total cambios históricos:** {estado.get('total_cambios_historicos', 0)}\n"
        md += f"- **Archivos críticos:** {estado.get('archivos_criticos', 0)}\n\n"
        
        # Último baseline
        if estado.get('ultimo_baseline'):
            baseline = estado['ultimo_baseline']
            md += "## [STATS] Último Baseline\n\n"
            md += f"- **Fecha:** {baseline.get('timestamp', 'N/A')}\n"
            md += f"- **Archivos procesados:** {baseline.get('archivos_procesados', 0)}\n"
            md += f"- **Tiempo de creación:** {baseline.get('tiempo_creacion', 0):.2f}s\n\n"
        
        # Cambios críticos recientes
        md += "##  Cambios Críticos Recientes\n\n"
        if cambios_criticos:
            for cambio in cambios_criticos:
                timestamp_cambio = cambio.get('timestamp', 'N/A')
                if isinstance(timestamp_cambio, datetime):
                    timestamp_cambio = timestamp_cambio.strftime('%H:%M:%S')
                md += f"- **{timestamp_cambio}:** {cambio.get('tipo_cambio', 'N/A')} - {cambio.get('ruta_archivo', 'N/A')}\n"
        else:
            md += "No hay cambios críticos recientes.\n"
        
        md += "\n##  Cambios Recientes (Todos)\n\n"
        if cambios_recientes:
            for cambio in cambios_recientes[:10]:
                timestamp_cambio = cambio.get('timestamp', 'N/A')
                if isinstance(timestamp_cambio, datetime):
                    timestamp_cambio = timestamp_cambio.strftime('%H:%M:%S')
                md += f"- **{timestamp_cambio}:** {cambio.get('tipo_cambio', 'N/A')} - {cambio.get('ruta_archivo', 'N/A')}\n"
        else:
            md += "No hay cambios recientes.\n"
        
        md += "\n---\n"
        md += "*Reporte generado automáticamente por Ares Aegis*\n"
        
        return md
    
    def limpiar_cambios_antiguos(self, dias_retencion: int = 30):
        """
        Limpiar cambios antiguos para liberar memoria.
        
        Args:
            dias_retencion: Días de retención de cambios
        """
        limite_tiempo = datetime.now() - timedelta(days=dias_retencion)
        
        with self.lock:
            cambios_nuevos = [c for c in self.cambios_detectados
                            if c.get('timestamp', datetime.min) >= limite_tiempo]
            cambios_removidos = len(self.cambios_detectados) - len(cambios_nuevos)
            self.cambios_detectados = cambios_nuevos
        
        self.logger.info(f"Limpieza FIM completada: {cambios_removidos} cambios antiguos removidos")


