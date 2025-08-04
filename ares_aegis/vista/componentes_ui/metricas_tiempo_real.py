#!/usr/bin/env python3
"""
Métricas en Tiempo Real para Ares Aegis
Sistema de monitoreo de métricas optimizado
"""

import threading
import time
import os
import logging
from datetime import datetime


class MetricasTiempoReal:
    """Sistema de métricas en tiempo real optimizado para bajo consumo de recursos"""
    
    def __init__(self, controlador, callback_actualizacion):
        self.controlador = controlador
        self.callback_actualizacion = callback_actualizacion
        self.activo = False
        self.thread_actualizacion = None
        self.intervalo_actualizacion = 3.0  # 3 segundos (bajo consumo)
        self.logger = logging.getLogger(__name__)
        
        # Cache de métricas para evitar cálculos repetitivos
        self._cache_metricas = {}
        self._ultimo_cache = 0
        self._duracion_cache = 2.0  # Cache por 2 segundos
        
    def iniciar(self):
        """Iniciar monitoreo de métricas en tiempo real"""
        if not self.activo:
            self.activo = True
            self.thread_actualizacion = threading.Thread(
                target=self._ciclo_actualizacion,
                daemon=True,
                name="MetricasTiempoReal"
            )
            self.thread_actualizacion.start()
            self.logger.info("📊 Sistema de métricas en tiempo real iniciado")
    
    def detener(self):
        """Detener monitoreo de métricas"""
        self.activo = False
        if self.thread_actualizacion:
            self.thread_actualizacion.join(timeout=1.0)
        self.logger.info("📊 Sistema de métricas en tiempo real detenido")
    
    def _ciclo_actualizacion(self):
        """Ciclo principal de actualización de métricas"""
        while self.activo:
            try:
                metricas = self._obtener_metricas_optimizadas()
                
                # Actualizar UI en thread principal
                if self.callback_actualizacion:
                    # Usar after para ejecutar en UI thread de forma segura
                    self.callback_actualizacion(metricas)
                
                time.sleep(self.intervalo_actualizacion)
                
            except Exception as e:
                self.logger.error(f"Error en ciclo de métricas: {e}")
                time.sleep(self.intervalo_actualizacion * 2)  # Espera más en caso de error
    
    def _obtener_metricas_optimizadas(self) -> dict:
        """Obtener métricas del sistema Kali Linux de forma optimizada con cache"""
        ahora = time.time()
        
        # Usar cache si está disponible y no ha expirado
        if (ahora - self._ultimo_cache) < self._duracion_cache and self._cache_metricas:
            return self._cache_metricas.copy()
        
        try:
            # CPU usando load average nativo de Linux
            load_avg = getattr(os, 'getloadavg')()[0]  # Usar getattr para evitar warnings de análisis estático
            cpu_count = os.cpu_count() or 1
            cpu_percent = min(100, (load_avg / cpu_count) * 100)
            
            # Memoria desde /proc/meminfo (nativo Linux)
            with open('/proc/meminfo', 'r') as f:
                meminfo = f.read()
            
            mem_total = mem_available = 0
            for line in meminfo.split('\n'):
                if line.startswith('MemTotal:'):
                    mem_total = int(line.split()[1]) * 1024  # KB a bytes
                elif line.startswith('MemAvailable:'):
                    mem_available = int(line.split()[1]) * 1024  # KB a bytes
            
            memoria_total_gb = mem_total / (1024**3)
            memoria_usada_gb = (mem_total - mem_available) / (1024**3)
            memoria_percent = (memoria_usada_gb / memoria_total_gb) * 100
            
            # Disco desde statvfs (nativo Linux)
            statvfs_func = getattr(os, 'statvfs')  # Usar getattr para evitar warnings de análisis estático
            stat = statvfs_func('/')
            disco_total_gb = (stat.f_blocks * stat.f_frsize) / (1024**3)
            disco_libre_gb = (stat.f_available * stat.f_frsize) / (1024**3)
            disco_usado_gb = disco_total_gb - disco_libre_gb
            disco_percent = (disco_usado_gb / disco_total_gb) * 100
            
            metricas_controlador = {}
            estado_componentes = {}
            
            if self.controlador:
                try:
                    estado_sistema = self.controlador.obtener_estado_sistema()
                    metricas_controlador = estado_sistema.get("metricas", {})
                    estado_componentes = estado_sistema.get("componentes", {})
                except Exception as e:
                    self.logger.debug(f"No se pudieron obtener métricas del controlador: {e}")
            
            metricas = {
                "cpu_percent": round(cpu_percent, 1),
                "memoria_percent": round(memoria_percent, 1),
                "memoria_usada_gb": round(memoria_usada_gb, 1),
                "memoria_total_gb": round(memoria_total_gb, 1),
                "disco_percent": round(disco_percent, 1),
                "disco_usado_gb": round(disco_usado_gb, 1),
                "disco_total_gb": round(disco_total_gb, 1),
                
                # Métricas de aplicación
                "amenazas_detectadas": metricas_controlador.get("amenazas_detectadas", 0),
                "archivos_escaneados": metricas_controlador.get("archivos_escaneados", 0),
                "archivos_cuarentena": metricas_controlador.get("archivos_cuarentena", 0),
                "alertas_activas": metricas_controlador.get("alertas_activas", 0),
                "procesos_activos": metricas_controlador.get("procesos_activos", 0),
                "procesos_sospechosos": metricas_controlador.get("procesos_sospechosos", 0),
                "conexiones_activas": metricas_controlador.get("conexiones_activas", 0),
                
                # Estado de componentes
                "siem_activo": estado_componentes.get("siem", False),
                "escaneador_activo": estado_componentes.get("escaneador", False),
                "fim_activo": estado_componentes.get("fim", False),
                "monitor_red_activo": estado_componentes.get("monitor_red", False),
                "cuarentena_activa": estado_componentes.get("cuarentena", False),
                
                # Información temporal
                "timestamp": datetime.now(),
                "uptime": self._calcular_uptime()
            }
            
            # Actualizar cache
            self._cache_metricas = metricas
            self._ultimo_cache = ahora
            
            return metricas
            
        except Exception as e:
            self.logger.error(f"Error obteniendo métricas del sistema: {e}")
            return self._obtener_metricas_fallback()
    
    def _obtener_metricas_fallback(self) -> dict:
        """Métricas básicas en caso de error - optimizado para Kali Linux"""
        return {
            "cpu_percent": 0.0,
            "memoria_percent": 0.0,
            "memoria_usada_gb": 0.0,
            "memoria_total_gb": 0.0,
            "disco_percent": 0.0,
            "disco_usado_gb": 0.0,
            "disco_total_gb": 0.0,
            "amenazas_detectadas": 0,
            "archivos_escaneados": 0,
            "archivos_cuarentena": 0,
            "alertas_activas": 0,
            "procesos_activos": 0,
            "procesos_sospechosos": 0,
            "conexiones_activas": 0,
            "siem_activo": False,
            "escaneador_activo": False,
            "fim_activo": False,
            "monitor_red_activo": False,
            "cuarentena_activa": False,
            "timestamp": datetime.now(),
            "uptime": "Error"
        }
    
    def _calcular_uptime(self) -> str:
        """Calcular tiempo de actividad del sistema Kali Linux usando /proc/uptime"""
        try:
            # Leer uptime nativo de Linux
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.read().split()[0])
            
            # Convertir a formato legible
            days = int(uptime_seconds // 86400)
            hours = int((uptime_seconds % 86400) // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            
            if days > 0:
                return f"{days}d {hours}h {minutes}m"
            else:
                return f"{hours}h {minutes}m"
                
        except Exception as e:
            self.logger.error(f"Error calculando uptime desde /proc/uptime: {e}")
            return "N/A"
