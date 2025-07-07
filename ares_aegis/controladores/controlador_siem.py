#!/usr/bin/env python3
"""
Ares Aegis - Controlador SIEM
Controlador especializado para gestionar eventos y correlaciones del SIEM

Copyright (c) 2025 DogSoulDev (https://github.com/DogSoulDev)
Todos los derechos reservados. Este código es propietario y confidencial.
La copia, distribución o modificación no autorizada está estrictamente prohibida.

Versión: 3.0.0
"""

import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Set
from collections import defaultdict
from pathlib import Path

from ..modelos.siem import SIEM, TipoEvento, EventoSIEM
from ..utilidades.ayuda_logging import configurar_logger_modulo


class ControladorSIEM:
    """Controlador especializado para operaciones del SIEM."""
    
    def __init__(self, siem: SIEM):
        """
        Inicializar el controlador SIEM.
        
        Args:
            siem: Instancia del SIEM
        """
        self.siem = siem
        self.logger = configurar_logger_modulo("controlador_siem")
        
        # Estado del controlador
        self.correlaciones_activas = {}
        self.alertas_criticas = []
        self.eventos_recientes = []
        self.patrones_detectados = defaultdict(int)
        self.lock = threading.Lock()
        
        # Configuración de correlación
        self.configuracion_correlacion = {
            'ventana_tiempo': 300,  # 5 minutos
            'umbral_eventos_similares': 5,
            'tipos_eventos_criticos': [
                TipoEvento.AMENAZA_DETECTADA,
                TipoEvento.MALWARE_DETECTADO,
                TipoEvento.VIRUS_ENCONTRADO,
                TipoEvento.RANSOMWARE_DETECTADO,
                TipoEvento.ROOTKIT_DETECTADO
            ]
        }
        
        self.logger.info("Controlador SIEM inicializado")
    
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
