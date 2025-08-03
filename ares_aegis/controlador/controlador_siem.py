#!/usr/bin/env python3
"""
Ares Aegis - Controlador SIEM Optimizado
Controlador especializado para gestionar eventos y correlaciones del SIEM

Creado por DogSoulDev (https://github.com/DogSoulDev)
Todos los derechos reservados. Este código es propietario y confidencial.
La copia, distribución o modificación no autorizada está estrictamente prohibida.

Versión: 4.0.0 - Arquitectura Optimizada
"""

import asyncio
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Set
from collections import defaultdict
from pathlib import Path

from ..modelo.modelo_siem import SIEM, TipoEvento, EventoSIEM
from ..utils.utils_ayuda_logging import configurar_logger_modulo
from .controlador_base import ControladorBase
from ..utils.utils_gestor_configuracion import gestor_configuracion


class ControladorSIEM(ControladorBase):
    """Controlador especializado para operaciones del SIEM con arquitectura optimizada."""
    
    def __init__(self, siem: SIEM):
        """
        Inicializar el controlador SIEM.
        
        Args:
            siem: Instancia del SIEM
        """
        super().__init__("siem")
        
        self.siem = siem
        self.configuracion = gestor_configuracion.obtener_config_controlador("siem")
        
        # Estado del controlador
        self.correlaciones_activas = {}
        self.alertas_criticas = []
        self.eventos_recientes = []
        self.patrones_detectados = defaultdict(int)
        self.lock = threading.Lock()  # Agregar lock faltante
        
        # Configuración de correlación con valores por defecto
        if self.configuracion:
            self.configuracion_correlacion = {
                'ventana_tiempo': self.configuracion.ventana_tiempo,
                'umbral_eventos_similares': self.configuracion.umbral_eventos_similares,
                'tipos_eventos_criticos': self.configuracion.tipos_eventos_criticos or [
                    'AMENAZA_DETECTADA',
                    'MALWARE_DETECTADO'
                ]
            }
        else:
            self.configuracion_correlacion = {
                'ventana_tiempo': 300,
                'umbral_eventos_similares': 5,
                'tipos_eventos_criticos': [
                    'AMENAZA_DETECTADA',
                    'MALWARE_DETECTADO'
                ]
            }
        
        self.logger.info("Controlador SIEM inicializado con nueva arquitectura")
    
    async def _inicializar_impl(self) -> bool:
        """Implementación de inicialización del controlador SIEM"""
        try:
            # Inicializar correlación de eventos
            await self._inicializar_correlacion()
            
            # Configurar monitoreo automático
            asyncio.create_task(self._monitoreo_continuo_eventos())
            
            return True
        except Exception as e:
            self.logger.error(f"Error inicializando controlador SIEM: {e}")
            return False
    
    async def _finalizar_impl(self) -> bool:
        """Implementación de finalización del controlador SIEM"""
        try:
            # Limpiar correlaciones activas
            self.correlaciones_activas.clear()
            self.logger.info("Controlador SIEM finalizado")
            return True
        except Exception as e:
            self.logger.error(f"Error finalizando controlador SIEM: {e}")
            return False
    
    async def _inicializar_correlacion(self):
        """Inicializar sistema de correlación de eventos"""
        self.logger.info("Sistema de correlación de eventos inicializado")
    
    async def _monitoreo_continuo_eventos(self):
        """Monitoreo continuo de eventos para correlación"""
        while self.activo:
            try:
                async with self.operacion_segura("monitoreo_eventos"):
                    await self._procesar_eventos_recientes()
                    await self._detectar_patrones()
                
                await asyncio.sleep(30)  # Verificar cada 30 segundos
                
            except Exception as e:
                self.logger.error(f"Error en monitoreo continuo: {e}")
                await asyncio.sleep(60)
    
    async def _procesar_eventos_recientes(self):
        """Procesar eventos recientes para correlación"""
        if not self.siem:
            return
        
        try:
            # Obtener eventos recientes del SIEM
            eventos = self.siem.obtener_eventos_recientes(limite=100)
            self.eventos_recientes = eventos[-50:]  # Mantener solo los últimos 50
            
            # Procesar para correlación
            for evento in eventos:
                await self._correlacionar_evento(evento)
                
        except Exception as e:
            self.logger.error(f"Error procesando eventos recientes: {e}")
    
    async def _correlacionar_evento(self, evento: dict):
        """Correlacionar un evento individual"""
        try:
            tipo_evento = evento.get('tipo', '')
            
            # Incrementar contador de patrón
            self.patrones_detectados[tipo_evento] += 1
            
            # Verificar si es un evento crítico
            if tipo_evento in self.configuracion_correlacion['tipos_eventos_criticos']:
                await self._procesar_evento_critico(evento)
                
        except Exception as e:
            self.logger.error(f"Error correlacionando evento: {e}")
    
    async def _procesar_evento_critico(self, evento: dict):
        """Procesar evento crítico"""
        try:
            alerta = {
                'timestamp': datetime.now(),
                'evento': evento,
                'nivel': 'CRITICO',
                'procesado': False
            }
            
            with self._lock:
                self.alertas_criticas.append(alerta)
                # Mantener solo las últimas 20 alertas
                self.alertas_criticas = self.alertas_criticas[-20:]
                
        except Exception as e:
            self.logger.error(f"Error procesando evento crítico: {e}")
    
    async def _detectar_patrones(self):
        """Detectar patrones sospechosos"""
        try:
            umbral = self.configuracion_correlacion['umbral_eventos_similares']
            
            for tipo, count in self.patrones_detectados.items():
                if count > umbral:
                    await self._generar_alerta_patron(tipo, count)
                    
        except Exception as e:
            self.logger.error(f"Error detectando patrones: {e}")
    
    async def _generar_alerta_patron(self, tipo: str, count: int):
        """Generar alerta por patrón detectado"""
        self.logger.warning(f"Patrón sospechoso detectado: {tipo} ({count} ocurrencias)")
        
        # Registrar en SIEM
        if self.siem:
            self.siem.registrar_evento(
                TipoEvento.CORRELACION_AMENAZAS,
                f"Patrón sospechoso: {tipo}",
                {"tipo": tipo, "ocurrencias": count}
            )
    
    # Métodos de interfaz pública
    
    def registrar_evento(self, tipo: str, mensaje: str, datos: Optional[Dict[str, Any]] = None, 
                        nivel_criticidad: str = "MEDIO") -> str:
        """
        Registrar un evento en el SIEM con análisis de correlación.
        
        Args:
            tipo: Tipo de evento
            mensaje: Mensaje descriptivo del evento
            datos: Datos adicionales del evento
            nivel_criticidad: Nivel de criticidad del evento
            
        Returns:
            str: ID del evento registrado
        """
        try:
            # Registrar evento en SIEM
            evento_id = self.siem.registrar_evento(tipo, mensaje, datos or {}, nivel_criticidad)
            
            # Analizar correlaciones
            self._analizar_correlaciones(tipo, mensaje, datos or {}, nivel_criticidad)
            
            # Actualizar eventos recientes
            with self.lock:
                evento = {
                    'id': evento_id,
                    'tipo': tipo,
                    'mensaje': mensaje,
                    'datos': datos or {},
                    'nivel_criticidad': nivel_criticidad,
                    'timestamp': datetime.now()
                }
                
                self.eventos_recientes.append(evento)
                
                # Mantener solo los últimos 1000 eventos
                if len(self.eventos_recientes) > 1000:
                    self.eventos_recientes = self.eventos_recientes[-1000:]
                
                # Gestionar alertas críticas
                if nivel_criticidad in ['CRITICO', 'ALTO']:
                    self.alertas_criticas.append(evento)
                    
                    # Mantener solo las últimas 100 alertas críticas
                    if len(self.alertas_criticas) > 100:
                        self.alertas_criticas = self.alertas_criticas[-100:]
            
            return evento_id
        
        except Exception as e:
            self.logger.error(f"Error registrando evento: {e}")
            raise
    
    def _analizar_correlaciones(self, tipo: str, mensaje: str, datos: Dict[str, Any], 
                               nivel_criticidad: str):
        """
        Analizar correlaciones entre eventos.
        
        Args:
            tipo: Tipo de evento
            mensaje: Mensaje del evento
            datos: Datos del evento
            nivel_criticidad: Nivel de criticidad
        """
        try:
            ahora = datetime.now()
            ventana_inicio = ahora - timedelta(seconds=self.configuracion_correlacion['ventana_tiempo'])
            
            with self.lock:
                # Contar eventos similares en ventana de tiempo
                eventos_similares = 0
                for evento in self.eventos_recientes:
                    if (evento['timestamp'] >= ventana_inicio and 
                        evento['tipo'] == tipo and 
                        evento['timestamp'] <= ahora):
                        eventos_similares += 1
                
                # Detectar patrones sospechosos
                patron_key = f"{tipo}_{nivel_criticidad}"
                self.patrones_detectados[patron_key] += 1
                
                # Generar correlación si se supera el umbral
                if eventos_similares >= self.configuracion_correlacion['umbral_eventos_similares']:
                    self._generar_correlacion_eventos(tipo, eventos_similares, datos)
                
                # Análisis específico para eventos críticos
                if tipo in self.configuracion_correlacion['tipos_eventos_criticos']:
                    self._analizar_evento_critico(tipo, mensaje, datos)
        
        except Exception as e:
            self.logger.error(f"Error en análisis de correlaciones: {e}")
    
    def _generar_correlacion_eventos(self, tipo_evento: str, count: int, datos: Dict[str, Any]):
        """
        Generar correlación cuando se detecta un patrón.
        
        Args:
            tipo_evento: Tipo de evento correlacionado
            count: Número de eventos similares
            datos: Datos del evento
        """
        correlacion_id = f"corr_{int(time.time())}_{tipo_evento}"
        
        correlacion = {
            'id': correlacion_id,
            'tipo_evento': tipo_evento,
            'count_eventos': count,
            'timestamp': datetime.now(),
            'datos_asociados': datos,
            'nivel_riesgo': 'ALTO' if count >= 10 else 'MEDIO'
        }
        
        self.correlaciones_activas[correlacion_id] = correlacion
        
        # Registrar evento de correlación
        self.siem.registrar_evento(
            TipoEvento.PATRON_ATAQUE_DETECTADO,
            f"Patrón detectado: {count} eventos {tipo_evento} en ventana de tiempo",
            correlacion,
            correlacion['nivel_riesgo']
        )
        
        self.logger.warning(f"Correlación detectada: {correlacion_id} - {count} eventos {tipo_evento}")
    
    def _analizar_evento_critico(self, tipo: str, mensaje: str, datos: Dict[str, Any]):
        """
        Análisis especializado para eventos críticos.
        
        Args:
            tipo: Tipo de evento crítico
            mensaje: Mensaje del evento
            datos: Datos del evento
        """
        # Análisis específico por tipo de evento crítico
        if tipo == TipoEvento.AMENAZA_DETECTADA:
            self._analizar_amenaza(datos)
        elif tipo == TipoEvento.RANSOMWARE_DETECTADO:
            self._analizar_ransomware(datos)
        elif tipo == TipoEvento.ROOTKIT_DETECTADO:
            self._analizar_rootkit(datos)
    
    def _analizar_amenaza(self, datos: Dict[str, Any]):
        """Análisis específico para amenazas detectadas."""
        ruta_archivo = datos.get('ruta_archivo', '')
        if ruta_archivo:
            # Verificar si hay múltiples amenazas en el mismo directorio
            directorio = str(Path(ruta_archivo).parent) if ruta_archivo else ''
            amenazas_directorio = 0
            
            for evento in self.eventos_recientes[-50:]:  # Últimos 50 eventos
                if (evento['tipo'] == TipoEvento.AMENAZA_DETECTADA and 
                    evento['datos'].get('ruta_archivo', '').startswith(directorio)):
                    amenazas_directorio += 1
            
            if amenazas_directorio >= 3:
                self.siem.registrar_evento(
                    TipoEvento.CORRELACION_AMENAZAS,
                    f"Múltiples amenazas detectadas en directorio: {directorio}",
                    {'directorio': directorio, 'count_amenazas': amenazas_directorio},
                    "ALTO"
                )
    
    def _analizar_ransomware(self, datos: Dict[str, Any]):
        """Análisis específico para ransomware."""
        # Generar alerta de máxima prioridad para ransomware
        self.siem.registrar_evento(
            TipoEvento.ERROR_CRITICO,
            "ALERTA CRÍTICA: Ransomware detectado - Requiere respuesta inmediata",
            {'categoria': 'ransomware', 'prioridad': 'MAXIMA', **datos},
            "CRITICO"
        )
    
    def _analizar_rootkit(self, datos: Dict[str, Any]):
        """Análisis específico para rootkits."""
        # Los rootkits requieren análisis de sistema completo
        self.siem.registrar_evento(
            TipoEvento.ACTIVIDAD_ANOMALA,
            "Rootkit detectado - Se recomienda análisis forense completo",
            {'categoria': 'rootkit', 'accion_recomendada': 'analisis_forense', **datos},
            "ALTO"
        )
    
    def obtener_eventos_recientes(self, limite: int = 100, filtro_tipo: Optional[str] = None,
                                 filtro_criticidad: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Obtener eventos recientes con filtros opcionales.
        
        Args:
            limite: Número máximo de eventos a devolver
            filtro_tipo: Filtrar por tipo de evento específico
            filtro_criticidad: Filtrar por nivel de criticidad
            
        Returns:
            List[Dict[str, Any]]: Lista de eventos
        """
        with self.lock:
            eventos = self.eventos_recientes.copy()
        
        # Aplicar filtros
        if filtro_tipo:
            eventos = [e for e in eventos if e['tipo'] == filtro_tipo]
        
        if filtro_criticidad:
            eventos = [e for e in eventos if e['nivel_criticidad'] == filtro_criticidad]
        
        # Ordenar por timestamp descendente y limitar
        eventos.sort(key=lambda x: x['timestamp'], reverse=True)
        return eventos[:limite]
    
    def obtener_alertas_criticas(self, limite: int = 50) -> List[Dict[str, Any]]:
        """
        Obtener alertas críticas recientes.
        
        Args:
            limite: Número máximo de alertas a devolver
            
        Returns:
            List[Dict[str, Any]]: Lista de alertas críticas
        """
        with self.lock:
            alertas = self.alertas_criticas.copy()
        
        # Ordenar por timestamp descendente y limitar
        alertas.sort(key=lambda x: x['timestamp'], reverse=True)
        return alertas[:limite]
    
    def obtener_correlaciones_activas(self) -> Dict[str, Dict[str, Any]]:
        """
        Obtener correlaciones activas detectadas.
        
        Returns:
            Dict[str, Dict[str, Any]]: Diccionario de correlaciones activas
        """
        with self.lock:
            return self.correlaciones_activas.copy()
    
    def obtener_estadisticas_eventos(self, periodo_horas: int = 24) -> Dict[str, Any]:
        """
        Obtener estadísticas de eventos en un período específico.
        
        Args:
            periodo_horas: Período en horas para calcular estadísticas
            
        Returns:
            Dict[str, Any]: Estadísticas de eventos
        """
        limite_tiempo = datetime.now() - timedelta(hours=periodo_horas)
        
        with self.lock:
            eventos_periodo = [e for e in self.eventos_recientes if e['timestamp'] >= limite_tiempo]
        
        # Contar por tipo y criticidad
        conteo_tipos = defaultdict(int)
        conteo_criticidad = defaultdict(int)
        
        for evento in eventos_periodo:
            conteo_tipos[evento['tipo']] += 1
            conteo_criticidad[evento['nivel_criticidad']] += 1
        
        return {
            'periodo_horas': periodo_horas,
            'total_eventos': len(eventos_periodo),
            'eventos_por_tipo': dict(conteo_tipos),
            'eventos_por_criticidad': dict(conteo_criticidad),
            'correlaciones_activas': len(self.correlaciones_activas),
            'alertas_criticas': len([e for e in eventos_periodo if e['nivel_criticidad'] in ['CRITICO', 'ALTO']]),
            'timestamp': datetime.now().isoformat()
        }
    
    def limpiar_eventos_antiguos(self, dias_retencion: int = 30):
        """
        Limpiar eventos antiguos para liberar memoria.
        
        Args:
            dias_retencion: Días de retención de eventos
        """
        limite_tiempo = datetime.now() - timedelta(days=dias_retencion)
        
        with self.lock:
            eventos_nuevos = [e for e in self.eventos_recientes if e['timestamp'] >= limite_tiempo]
            eventos_removidos = len(self.eventos_recientes) - len(eventos_nuevos)
            self.eventos_recientes = eventos_nuevos
            
            # Limpiar alertas críticas antiguas
            alertas_nuevas = [a for a in self.alertas_criticas if a['timestamp'] >= limite_tiempo]
            alertas_removidas = len(self.alertas_criticas) - len(alertas_nuevas)
            self.alertas_criticas = alertas_nuevas
            
            # Limpiar correlaciones antiguas
            correlaciones_nuevas = {}
            for corr_id, correlacion in self.correlaciones_activas.items():
                if correlacion['timestamp'] >= limite_tiempo:
                    correlaciones_nuevas[corr_id] = correlacion
            correlaciones_removidas = len(self.correlaciones_activas) - len(correlaciones_nuevas)
            self.correlaciones_activas = correlaciones_nuevas
        
        self.logger.info(f"Limpieza completada: {eventos_removidos} eventos, {alertas_removidas} alertas, {correlaciones_removidas} correlaciones removidas")
    
    def configurar_correlacion(self, config: Dict[str, Any]):
        """
        Configurar parámetros de correlación.
        
        Args:
            config: Diccionario con configuración de correlación
        """
        with self.lock:
            self.configuracion_correlacion.update(config)
        
        self.logger.info(f"Configuración de correlación actualizada: {config}")
    
    def obtener_resumen_seguridad(self) -> Dict[str, Any]:
        """
        Obtener resumen general del estado de seguridad.
        
        Returns:
            Dict[str, Any]: Resumen del estado de seguridad
        """
        stats_24h = self.obtener_estadisticas_eventos(24)
        alertas_criticas = self.obtener_alertas_criticas(10)
        correlaciones = self.obtener_correlaciones_activas()
        
        # Calcular nivel de riesgo general
        alertas_criticas_count = stats_24h['alertas_criticas']
        if alertas_criticas_count >= 10:
            nivel_riesgo = "CRITICO"
        elif alertas_criticas_count >= 5:
            nivel_riesgo = "ALTO" 
        elif alertas_criticas_count >= 1:
            nivel_riesgo = "MEDIO"
        else:
            nivel_riesgo = "BAJO"
        
        return {
            'nivel_riesgo_general': nivel_riesgo,
            'total_eventos_24h': stats_24h['total_eventos'],
            'alertas_criticas_24h': alertas_criticas_count,
            'correlaciones_activas': len(correlaciones),
            'tipos_eventos_frecuentes': list(stats_24h['eventos_por_tipo'].keys())[:5],
            'ultimas_alertas': alertas_criticas[:5],
            'timestamp': datetime.now().isoformat()
        }
    
    def iniciar_siem(self) -> Dict[str, Any]:
        """
        Iniciar el sistema SIEM.
        
        Returns:
            Dict[str, Any]: Resultado de la operación
        """
        try:
            # Inicializar el SIEM si no está activo
            if not self.activo:
                asyncio.create_task(self.inicializar())
            
            # Limpiar estado anterior
            with self.lock:
                self.eventos_recientes.clear()
                self.alertas_criticas.clear()
                self.correlaciones_activas.clear()
                self.patrones_detectados.clear()
            
            self.logger.info("Sistema SIEM iniciado exitosamente")
            return {
                'success': True,
                'mensaje': 'SIEM iniciado correctamente',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error al iniciar SIEM: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def detener_siem(self) -> Dict[str, Any]:
        """
        Detener el sistema SIEM.
        
        Returns:
            Dict[str, Any]: Resultado de la operación
        """
        try:
            # Finalizar el controlador si está activo
            if self.activo:
                asyncio.create_task(self.finalizar())
            
            self.logger.info("Sistema SIEM detenido exitosamente")
            return {
                'success': True,
                'mensaje': 'SIEM detenido correctamente',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error al detener SIEM: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def obtener_metricas(self) -> Dict[str, int]:
        """
        Obtener métricas actuales del SIEM.
        
        Returns:
            Dict[str, int]: Métricas del sistema
        """
        with self.lock:
            return {
                'eventos_detectados': len(self.eventos_recientes),
                'alertas_criticas': len([e for e in self.eventos_recientes 
                                       if e.get('nivel_criticidad') == 'CRITICO']),
                'alertas_altas': len([e for e in self.eventos_recientes 
                                    if e.get('nivel_criticidad') == 'ALTO']),
                'alertas_medias': len([e for e in self.eventos_recientes 
                                     if e.get('nivel_criticidad') == 'MEDIO']),
                'correlaciones_activas': len(self.correlaciones_activas)
            }
    
    def exportar_eventos(self, ruta_archivo: str) -> bool:
        """
        Exportar eventos del SIEM a un archivo.
        
        Args:
            ruta_archivo: Ruta donde exportar los eventos
            
        Returns:
            bool: True si la exportación fue exitosa
        """
        try:
            import json
            from datetime import datetime
            
            with self.lock:
                eventos_export = []
                for evento in self.eventos_recientes:
                    evento_dict = {
                        'timestamp': evento.get('timestamp', datetime.now().isoformat()),
                        'tipo': evento.get('tipo', 'DESCONOCIDO'),
                        'severidad': evento.get('nivel_criticidad', 'MEDIO'),
                        'origen': evento.get('origen', 'Sistema'),
                        'descripcion': evento.get('descripcion', ''),
                        'detalles': evento.get('detalles', {})
                    }
                    eventos_export.append(evento_dict)
                
                datos_export = {
                    'fecha_exportacion': datetime.now().isoformat(),
                    'total_eventos': len(eventos_export),
                    'eventos': eventos_export,
                    'metricas': self.obtener_metricas()
                }
                
                with open(ruta_archivo, 'w', encoding='utf-8') as f:
                    json.dump(datos_export, f, indent=2, ensure_ascii=False, default=str)
                
                self.logger.info(f"Eventos exportados correctamente a {ruta_archivo}")
                return True
                
        except Exception as e:
            self.logger.error(f"Error exportando eventos: {e}")
            return False


