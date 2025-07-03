#!/usr/bin/env python3
"""
Analizador de Comportamiento de Procesos - Ares Aegis
Módulo para análisis heurístico y detección de patrones sospechosos en procesos

Este módulo analiza el comportamiento de los procesos en busca de anomalías
y patrones que puedan indicar actividad maliciosa o comprometida.

Autor: DogSoulDev
Versión: 2.0.0 - "El Oráculo de los Patrones"
"""

import os
import time
import re
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, NamedTuple
from collections import defaultdict, deque
from ..utilidades.ayuda_logging import configurar_logger_modulo


class PatronComportamiento(NamedTuple):
    """Patrón de comportamiento detectado."""
    tipo: str
    descripcion: str
    nivel_riesgo: str
    procesos_afectados: List[int]
    timestamp: datetime
    metadatos: Dict[str, Any]


class AnalisisComportamiento:
    """Resultado del análisis de comportamiento de un proceso."""
    
    def __init__(self, pid: int):
        """
        Inicializa el análisis de comportamiento.
        
        Args:
            pid: ID del proceso analizado
        """
        self.pid = pid
        self.timestamp_analisis = datetime.now()
        self.puntuacion_riesgo = 0
        self.nivel_riesgo = "BAJO"
        self.patrones_detectados: List[PatronComportamiento] = []
        self.comportamientos_sospechosos: List[str] = []
        self.indicadores_compromiso: List[str] = []
        self.recomendaciones: List[str] = []
        
        # Métricas del proceso
        self.tiempo_ejecucion = 0.0
        self.uso_cpu_promedio = 0.0
        self.uso_memoria_promedio = 0.0
        self.conexiones_red_total = 0
        self.archivos_accedidos = 0
        self.procesos_hijos = 0
        
        # Análisis de ubicación
        self.ruta_ejecutable = ""
        self.directorio_trabajo = ""
        self.ubicacion_sospechosa = False
        
        # Análisis de red
        self.dominios_contactados: Set[str] = set()
        self.ips_contactadas: Set[str] = set()
        self.puertos_utilizados: Set[int] = set()
        
        # Análisis de archivos
        self.archivos_creados: Set[str] = set()
        self.archivos_modificados: Set[str] = set()
        self.archivos_eliminados: Set[str] = set()
    
    def calcular_nivel_riesgo(self):
        """Calcula el nivel de riesgo basado en la puntuación."""
        if self.puntuacion_riesgo < 10:
            self.nivel_riesgo = "BAJO"
        elif self.puntuacion_riesgo < 25:
            self.nivel_riesgo = "MEDIO"
        elif self.puntuacion_riesgo < 50:
            self.nivel_riesgo = "ALTO"
        else:
            self.nivel_riesgo = "CRITICO"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el análisis a diccionario."""
        return {
            'pid': self.pid,
            'timestamp_analisis': self.timestamp_analisis.isoformat(),
            'puntuacion_riesgo': self.puntuacion_riesgo,
            'nivel_riesgo': self.nivel_riesgo,
            'patrones_detectados': len(self.patrones_detectados),
            'comportamientos_sospechosos': self.comportamientos_sospechosos,
            'indicadores_compromiso': self.indicadores_compromiso,
            'recomendaciones': self.recomendaciones,
            'metricas': {
                'tiempo_ejecucion': self.tiempo_ejecucion,
                'uso_cpu_promedio': self.uso_cpu_promedio,
                'uso_memoria_promedio': self.uso_memoria_promedio,
                'conexiones_red_total': self.conexiones_red_total,
                'archivos_accedidos': self.archivos_accedidos,
                'procesos_hijos': self.procesos_hijos
            },
            'ubicacion': {
                'ruta_ejecutable': self.ruta_ejecutable,
                'directorio_trabajo': self.directorio_trabajo,
                'ubicacion_sospechosa': self.ubicacion_sospechosa
            }
        }


class HistorialProceso:
    """Historial de comportamiento de un proceso específico."""
    
    def __init__(self, pid: int, max_entradas: int = 1000):
        """
        Inicializa el historial del proceso.
        
        Args:
            pid: ID del proceso
            max_entradas: Número máximo de entradas a mantener
        """
        self.pid = pid
        self.max_entradas = max_entradas
        self.timestamp_inicio = datetime.now()
        
        # Colas de datos históricos
        self.uso_cpu_historico = deque(maxlen=max_entradas)
        self.uso_memoria_historico = deque(maxlen=max_entradas)
        self.conexiones_historico = deque(maxlen=max_entradas)
        self.archivos_historico = deque(maxlen=max_entradas)
        
        # Eventos significativos
        self.eventos_red: List[Dict[str, Any]] = []
        self.eventos_archivos: List[Dict[str, Any]] = []
        self.eventos_procesos: List[Dict[str, Any]] = []
        
        # Patrones detectados
        self.patrones_comportamiento: List[PatronComportamiento] = []
    
    def agregar_muestra_recursos(self, cpu: float, memoria: int, timestamp: datetime):
        """Agrega una muestra de uso de recursos."""
        self.uso_cpu_historico.append((timestamp, cpu))
        self.uso_memoria_historico.append((timestamp, memoria))
    
    def agregar_evento_red(self, tipo: str, detalles: Dict[str, Any]):
        """Agrega un evento de red."""
        evento = {
            'timestamp': datetime.now(),
            'tipo': tipo,
            'detalles': detalles
        }
        self.eventos_red.append(evento)
        
        # Mantener solo eventos recientes
        if len(self.eventos_red) > 100:
            self.eventos_red = self.eventos_red[-50:]
    
    def agregar_evento_archivo(self, tipo: str, ruta: str):
        """Agrega un evento de archivo."""
        evento = {
            'timestamp': datetime.now(),
            'tipo': tipo,
            'ruta': ruta
        }
        self.eventos_archivos.append(evento)
        
        # Mantener solo eventos recientes
        if len(self.eventos_archivos) > 100:
            self.eventos_archivos = self.eventos_archivos[-50:]
    
    def detectar_picos_recursos(self) -> List[Dict[str, Any]]:
        """Detecta picos anómalos en el uso de recursos."""
        picos = []
        
        if len(self.uso_cpu_historico) < 10:
            return picos
        
        # Calcular promedio móvil y detectar picos de CPU
        cpu_valores = [cpu for _, cpu in self.uso_cpu_historico]
        promedio_cpu = sum(cpu_valores) / len(cpu_valores)
        
        for timestamp, cpu in self.uso_cpu_historico:
            if cpu > promedio_cpu * 3:  # Pico si es 3x el promedio
                picos.append({
                    'tipo': 'pico_cpu',
                    'timestamp': timestamp,
                    'valor': cpu,
                    'promedio': promedio_cpu
                })
        
        # Detectar picos de memoria
        memoria_valores = [mem for _, mem in self.uso_memoria_historico]
        if memoria_valores:
            promedio_memoria = sum(memoria_valores) / len(memoria_valores)
            
            for timestamp, memoria in self.uso_memoria_historico:
                if memoria > promedio_memoria * 2:  # Pico si es 2x el promedio
                    picos.append({
                        'tipo': 'pico_memoria',
                        'timestamp': timestamp,
                        'valor': memoria,
                        'promedio': promedio_memoria
                    })
        
        return picos


class AnalizadorComportamientoProcesos:
    """Analizador principal de comportamientos de procesos."""
    
    def __init__(self, monitor_procesos, monitor_red=None, siem=None):
        """
        Inicializa el analizador de comportamiento.
        
        Args:
            monitor_procesos: Instancia del monitor de procesos
            monitor_red: Instancia del monitor de red (opcional)
            siem: Instancia del SIEM para registro de eventos
        """
        self.logger = configurar_logger_modulo("analizador_comportamiento")
        self.monitor_procesos = monitor_procesos
        self.monitor_red = monitor_red
        self.siem = siem
        
        # Estado del analizador
        self.analizando = False
        self.hilo_analisis: Optional[threading.Thread] = None
        self.intervalo_analisis = 30  # segundos
        
        # Datos de análisis
        self.historiales_procesos: Dict[int, HistorialProceso] = {}
        self.analisis_completados: List[AnalisisComportamiento] = []
        self.patrones_globales: List[PatronComportamiento] = []
        
        # Configuración de detección
        self.config_deteccion = {
            'umbral_cpu_sostenido': 70.0,  # % CPU sostenido
            'tiempo_cpu_sostenido': 300,   # 5 minutos
            'umbral_memoria_crecimiento': 50 * 1024 * 1024,  # 50MB crecimiento
            'umbral_conexiones_rapidas': 10,  # conexiones por minuto
            'tiempo_ventana_conexiones': 60,   # segundos
            'umbral_archivos_creados': 20,     # archivos por minuto
            'tiempo_ventana_archivos': 60      # segundos
        }
        
        # Bases de conocimiento
        self.ubicaciones_sospechosas = {
            '/tmp/', '/var/tmp/', '/dev/shm/', '/tmp/.', '/var/tmp/.',
            '/home/.*/.cache/', '/tmp/.*/.', '/dev/shm/.*'
        }
        
        self.procesos_legítimos_conocidos = {
            'systemd', 'init', 'kernel', 'kthreadd', 'ksoftirqd',
            'migration', 'rcu_', 'watchdog', 'sshd', 'dbus',
            'NetworkManager', 'cron', 'rsyslog', 'systemd-',
            'gnome-', 'firefox', 'chrome', 'code', 'python3',
            'bash', 'zsh', 'vim', 'nano', 'apt', 'dpkg'
        }
        
        self.extensiones_ejecutables_sospechosas = {
            '.tmp', '.cache', '.download', '.part', '.bak',
            '.old', '.new', '.exe', '.bat', '.cmd', '.scr'
        }
        
        self.puertos_comunes_legitimos = {
            22, 53, 80, 443, 993, 995, 25, 587, 110, 143,
            21, 22, 23, 3389, 5900, 8080, 8443
        }
        
        self.logger.info("El Oráculo de los Patrones ha despertado para descifrar comportamientos")
    
    def iniciar_analisis(self):
        """Inicia el análisis continuo de comportamientos."""
        if self.analizando:
            self.logger.warning("El Oráculo ya contempla los patrones del reino")
            return
        
        self.analizando = True
        self.hilo_analisis = threading.Thread(target=self._loop_analisis, daemon=True)
        self.hilo_analisis.start()
        
        if self.siem:
            from .siem import TipoEvento
            self.siem.registrar_evento(
                TipoEvento.SISTEMA_INICIADO,
                "Oráculo de patrones activado para contemplar comportamientos",
                {"componente": "analizador_comportamiento"},
                "MEDIO"
            )
        
        self.logger.info("El Oráculo comienza a descifrar los misterios del comportamiento")
    
    def detener_analisis(self):
        """Detiene el análisis de comportamientos."""
        if not self.analizando:
            return
        
        self.analizando = False
        
        if self.hilo_analisis:
            self.hilo_analisis.join(timeout=15)
        
        if self.siem:
            from .siem import TipoEvento
            self.siem.registrar_evento(
                TipoEvento.SISTEMA_DETENIDO,
                "Oráculo de patrones cerrado",
                {
                    "procesos_analizados": len(self.historiales_procesos),
                    "patrones_detectados": len(self.patrones_globales)
                },
                "MEDIO"
            )
        
        self.logger.info("El Oráculo ha cerrado sus visiones para el descanso")
    
    def _loop_analisis(self):
        """Loop principal de análisis de comportamientos."""
        self.logger.info("Iniciando ciclo de contemplación de patrones")
        
        while self.analizando:
            try:
                self._actualizar_historiales()
                self._analizar_patrones_globales()
                self._detectar_anomalias_temporales()
                self._limpiar_datos_antiguos()
                time.sleep(self.intervalo_analisis)
                
            except Exception as e:
                self.logger.error(f"Error en ciclo de análisis de comportamiento: {e}")
                time.sleep(self.intervalo_analisis * 2)
    
    def _actualizar_historiales(self):
        """Actualiza los historiales de procesos con datos recientes."""
        if not self.monitor_procesos or not hasattr(self.monitor_procesos, 'procesos_actuales'):
            return
        
        timestamp_actual = datetime.now()
        
        for pid, proceso in self.monitor_procesos.procesos_actuales.items():
            # Crear historial si no existe
            if pid not in self.historiales_procesos:
                self.historiales_procesos[pid] = HistorialProceso(pid)
            
            historial = self.historiales_procesos[pid]
            
            # Actualizar métricas de recursos
            historial.agregar_muestra_recursos(
                proceso.uso_cpu, 
                proceso.uso_memoria, 
                timestamp_actual
            )
            
            # Actualizar eventos de red si hay conexiones nuevas
            if hasattr(proceso, 'conexiones_red') and proceso.conexiones_red:
                for conexion in proceso.conexiones_red:
                    historial.agregar_evento_red('conexion_establecida', conexion)
    
    def _analizar_patrones_globales(self):
        """Analiza patrones de comportamiento a nivel global."""
        # Detectar múltiples procesos desde ubicaciones sospechosas
        procesos_sospechosos = []
        
        if self.monitor_procesos and hasattr(self.monitor_procesos, 'procesos_actuales'):
            for proceso in self.monitor_procesos.procesos_actuales.values():
                if self._es_ubicacion_sospechosa(proceso.ruta_ejecutable):
                    procesos_sospechosos.append(proceso.pid)
        
        if len(procesos_sospechosos) >= 3:
            patron = PatronComportamiento(
                tipo="multiples_procesos_sospechosos",
                descripcion=f"Múltiples procesos ({len(procesos_sospechosos)}) ejecutándose desde ubicaciones sospechosas",
                nivel_riesgo="ALTO",
                procesos_afectados=procesos_sospechosos,
                timestamp=datetime.now(),
                metadatos={'count': len(procesos_sospechosos)}
            )
            
            self.patrones_globales.append(patron)
            self._notificar_patron_detectado(patron)
        
        # Detectar escalada de procesos hijos
        self._detectar_escalada_procesos()
        
        # Detectar comunicación entre procesos sospechosos
        self._detectar_comunicacion_procesos()
    
    def _detectar_escalada_procesos(self):
        """Detecta patrones de escalada de procesos (proceso padre creando muchos hijos)."""
        if not self.monitor_procesos or not hasattr(self.monitor_procesos, 'procesos_actuales'):
            return
        
        # Contar procesos hijos por padre
        hijos_por_padre = defaultdict(list)
        
        for proceso in self.monitor_procesos.procesos_actuales.values():
            if hasattr(proceso, 'pid_padre') and proceso.pid_padre > 0:
                hijos_por_padre[proceso.pid_padre].append(proceso.pid)
        
        # Detectar padres con muchos hijos
        for pid_padre, hijos in hijos_por_padre.items():
            if len(hijos) >= 5:  # Umbral configurable
                # Verificar si el padre es legítimo
                proceso_padre = self.monitor_procesos.procesos_actuales.get(pid_padre)
                
                if proceso_padre and not self._es_proceso_legitimo(proceso_padre.nombre):
                    patron = PatronComportamiento(
                        tipo="escalada_procesos",
                        descripcion=f"Proceso {proceso_padre.nombre} (PID: {pid_padre}) ha creado {len(hijos)} procesos hijos",
                        nivel_riesgo="MEDIO",
                        procesos_afectados=[pid_padre] + hijos,
                        timestamp=datetime.now(),
                        metadatos={
                            'pid_padre': pid_padre,
                            'nombre_padre': proceso_padre.nombre,
                            'num_hijos': len(hijos)
                        }
                    )
                    
                    self.patrones_globales.append(patron)
                    self._notificar_patron_detectado(patron)
    
    def _detectar_comunicacion_procesos(self):
        """Detecta comunicación sospechosa entre procesos."""
        # Por simplicidad, detectamos procesos que escuchan en puertos no estándar
        if not self.monitor_procesos or not hasattr(self.monitor_procesos, 'procesos_actuales'):
            return
        
        procesos_con_puertos_sospechosos = []
        
        for proceso in self.monitor_procesos.procesos_actuales.values():
            if hasattr(proceso, 'puertos_abiertos') and proceso.puertos_abiertos:
                for puerto in proceso.puertos_abiertos:
                    if puerto not in self.puertos_comunes_legitimos and puerto > 1024:
                        procesos_con_puertos_sospechosos.append(proceso.pid)
                        break
        
        if len(procesos_con_puertos_sospechosos) >= 2:
            patron = PatronComportamiento(
                tipo="comunicacion_procesos_sospechosa",
                descripcion=f"Múltiples procesos usando puertos no estándar para comunicación",
                nivel_riesgo="MEDIO",
                procesos_afectados=procesos_con_puertos_sospechosos,
                timestamp=datetime.now(),
                metadatos={'count': len(procesos_con_puertos_sospechosos)}
            )
            
            self.patrones_globales.append(patron)
            self._notificar_patron_detectado(patron)
    
    def _detectar_anomalias_temporales(self):
        """Detecta anomalías basadas en patrones temporales."""
        timestamp_actual = datetime.now()
        ventana_tiempo = timedelta(minutes=10)
        
        # Detectar picos de actividad recientes
        procesos_activos_recientes = 0
        conexiones_recientes = 0
        
        if self.monitor_procesos and hasattr(self.monitor_procesos, 'procesos_actuales'):
            for proceso in self.monitor_procesos.procesos_actuales.values():
                # Verificar si el proceso es muy reciente
                if hasattr(proceso, 'tiempo_inicio'):
                    tiempo_inicio_proceso = datetime.fromtimestamp(proceso.tiempo_inicio)
                    if timestamp_actual - tiempo_inicio_proceso < ventana_tiempo:
                        procesos_activos_recientes += 1
                
                # Contar conexiones recientes
                if hasattr(proceso, 'conexiones_red'):
                    conexiones_recientes += len(proceso.conexiones_red)
        
        # Alertar si hay demasiada actividad reciente
        if procesos_activos_recientes >= 10:
            patron = PatronComportamiento(
                tipo="pico_actividad_procesos",
                descripcion=f"Pico de actividad: {procesos_activos_recientes} procesos iniciados recientemente",
                nivel_riesgo="MEDIO",
                procesos_afectados=[],
                timestamp=timestamp_actual,
                metadatos={'procesos_recientes': procesos_activos_recientes}
            )
            
            self.patrones_globales.append(patron)
            self._notificar_patron_detectado(patron)
        
        if conexiones_recientes >= 20:
            patron = PatronComportamiento(
                tipo="pico_actividad_red",
                descripcion=f"Pico de actividad de red: {conexiones_recientes} conexiones activas",
                nivel_riesgo="MEDIO",
                procesos_afectados=[],
                timestamp=timestamp_actual,
                metadatos={'conexiones_activas': conexiones_recientes}
            )
            
            self.patrones_globales.append(patron)
            self._notificar_patron_detectado(patron)
    
    def _es_ubicacion_sospechosa(self, ruta: str) -> bool:
        """Determina si una ubicación es sospechosa."""
        if not ruta:
            return False
        
        ruta = ruta.lower()
        
        for ubicacion in self.ubicaciones_sospechosas:
            if ubicacion in ruta:
                return True
        
        # Verificar extensiones sospechosas
        extension = Path(ruta).suffix.lower()
        if extension in self.extensiones_ejecutables_sospechosas:
            return True
        
        return False
    
    def _es_proceso_legitimo(self, nombre_proceso: str) -> bool:
        """Determina si un proceso es conocido como legítimo."""
        if not nombre_proceso:
            return False
        
        nombre_lower = nombre_proceso.lower()
        
        for proceso_legitimo in self.procesos_legítimos_conocidos:
            if proceso_legitimo in nombre_lower:
                return True
        
        return False
    
    def _notificar_patron_detectado(self, patron: PatronComportamiento):
        """Notifica sobre un patrón de comportamiento detectado."""
        mensaje = f"Patrón sospechoso detectado: {patron.descripcion}"
        
        if self.siem:
            from .siem import TipoEvento
            self.siem.registrar_evento(
                TipoEvento.PROCESO_SOSPECHOSO,
                f"El Oráculo revela un patrón maligno: {mensaje}",
                {
                    'tipo_patron': patron.tipo,
                    'nivel_riesgo': patron.nivel_riesgo,
                    'procesos_afectados': patron.procesos_afectados,
                    'metadatos': patron.metadatos
                },
                "ALTO" if patron.nivel_riesgo in ["ALTO", "CRITICO"] else "MEDIO"
            )
        
        self.logger.warning(f"El Oráculo de los Patrones detecta: {mensaje}")
    
    def _limpiar_datos_antiguos(self):
        """Limpia datos antiguos para evitar uso excesivo de memoria."""
        timestamp_limite = datetime.now() - timedelta(hours=2)
        
        # Limpiar patrones antiguos
        self.patrones_globales = [
            patron for patron in self.patrones_globales 
            if patron.timestamp > timestamp_limite
        ]
        
        # Limpiar historiales de procesos que ya no existen
        if self.monitor_procesos and hasattr(self.monitor_procesos, 'procesos_actuales'):
            pids_actuales = set(self.monitor_procesos.procesos_actuales.keys())
            pids_historiales = set(self.historiales_procesos.keys())
            
            pids_a_limpiar = pids_historiales - pids_actuales
            for pid in pids_a_limpiar:
                del self.historiales_procesos[pid]
        
        # Limpiar análisis completados antiguos
        if len(self.analisis_completados) > 1000:
            self.analisis_completados = self.analisis_completados[-500:]
    
    def analizar_proceso_especifico(self, pid: int) -> AnalisisComportamiento:
        """
        Realiza un análisis detallado de un proceso específico.
        
        Args:
            pid: ID del proceso a analizar
            
        Returns:
            AnalisisComportamiento: Análisis completo del proceso
        """
        analisis = AnalisisComportamiento(pid)
        
        try:
            # Obtener información del proceso
            if not self.monitor_procesos or not hasattr(self.monitor_procesos, 'procesos_actuales'):
                analisis.comportamientos_sospechosos.append("Monitor de procesos no disponible")
                return analisis
            
            proceso = self.monitor_procesos.procesos_actuales.get(pid)
            if not proceso:
                analisis.comportamientos_sospechosos.append("Proceso no encontrado en monitoreo activo")
                return analisis
            
            # Análisis de ubicación
            analisis.ruta_ejecutable = proceso.ruta_ejecutable
            analisis.ubicacion_sospechosa = self._es_ubicacion_sospechosa(proceso.ruta_ejecutable)
            
            if analisis.ubicacion_sospechosa:
                analisis.puntuacion_riesgo += 15
                analisis.comportamientos_sospechosos.append(f"Ejecutándose desde ubicación sospechosa: {proceso.ruta_ejecutable}")
                analisis.recomendaciones.append("Investigar origen y legitimidad del ejecutable")
            
            # Análisis de recursos
            analisis.uso_cpu_promedio = proceso.uso_cpu
            analisis.uso_memoria_promedio = proceso.uso_memoria / (1024 * 1024)  # MB
            
            if proceso.uso_cpu > 80:
                analisis.puntuacion_riesgo += 10
                analisis.comportamientos_sospechosos.append(f"Uso elevado de CPU: {proceso.uso_cpu}%")
            
            if proceso.uso_memoria > 500 * 1024 * 1024:  # 500MB
                analisis.puntuacion_riesgo += 8
                analisis.comportamientos_sospechosos.append(f"Uso elevado de memoria: {analisis.uso_memoria_promedio:.1f}MB")
            
            # Análisis de red
            if hasattr(proceso, 'conexiones_red') and proceso.conexiones_red:
                analisis.conexiones_red_total = len(proceso.conexiones_red)
                
                if analisis.conexiones_red_total > 5:
                    analisis.puntuacion_riesgo += 12
                    analisis.comportamientos_sospechosos.append(f"Múltiples conexiones de red: {analisis.conexiones_red_total}")
                
                # Extraer IPs y dominios
                for conexion in proceso.conexiones_red:
                    remoto = conexion.get('remoto', '')
                    if ':' in remoto:
                        ip = remoto.split(':')[0]
                        analisis.ips_contactadas.add(ip)
            
            # Análisis de puertos
            if hasattr(proceso, 'puertos_abiertos') and proceso.puertos_abiertos:
                analisis.puertos_utilizados = set(proceso.puertos_abiertos)
                
                puertos_sospechosos = analisis.puertos_utilizados - self.puertos_comunes_legitimos
                if puertos_sospechosos:
                    analisis.puntuacion_riesgo += 8
                    analisis.comportamientos_sospechosos.append(f"Usando puertos no estándar: {list(puertos_sospechosos)}")
            
            # Análisis de legitimidad del proceso
            if not self._es_proceso_legitimo(proceso.nombre):
                if not analisis.ubicacion_sospechosa:  # Evitar doble penalización
                    analisis.puntuacion_riesgo += 5
                    analisis.comportamientos_sospechosos.append("Proceso no reconocido como legítimo")
            
            # Análisis de parentesco
            if hasattr(proceso, 'pid_padre'):
                if proceso.pid_padre == 1 and not self._es_proceso_legitimo(proceso.nombre):
                    analisis.puntuacion_riesgo += 8
                    analisis.comportamientos_sospechosos.append("Proceso huérfano con PPID 1 sospechoso")
            
            # Análisis de historial si está disponible
            if pid in self.historiales_procesos:
                historial = self.historiales_procesos[pid]
                picos = historial.detectar_picos_recursos()
                
                if picos:
                    analisis.puntuacion_riesgo += len(picos) * 2
                    analisis.comportamientos_sospechosos.append(f"Detectados {len(picos)} picos de recursos anómalos")
            
            # Generar recomendaciones
            self._generar_recomendaciones(analisis)
            
            # Calcular nivel de riesgo final
            analisis.calcular_nivel_riesgo()
            
            # Guardar análisis
            self.analisis_completados.append(analisis)
            
            self.logger.info(f"Análisis completado para PID {pid}: {analisis.nivel_riesgo} (puntuación: {analisis.puntuacion_riesgo})")
        
        except Exception as e:
            self.logger.error(f"Error analizando proceso {pid}: {e}")
            analisis.comportamientos_sospechosos.append(f"Error en análisis: {e}")
        
        return analisis
    
    def _generar_recomendaciones(self, analisis: AnalisisComportamiento):
        """Genera recomendaciones basadas en el análisis."""
        if analisis.nivel_riesgo in ["ALTO", "CRITICO"]:
            analisis.recomendaciones.append("Considerar terminar el proceso inmediatamente")
            analisis.recomendaciones.append("Analizar el ejecutable con herramientas de malware")
            analisis.recomendaciones.append("Verificar conexiones de red activas")
        
        if analisis.ubicacion_sospechosa:
            analisis.recomendaciones.append("Mover archivo a cuarentena para análisis")
            analisis.recomendaciones.append("Verificar integridad del sistema")
        
        if analisis.conexiones_red_total > 0:
            analisis.recomendaciones.append("Monitorear tráfico de red del proceso")
            analisis.recomendaciones.append("Verificar destinos de conexiones")
        
        if analisis.puntuacion_riesgo > 20:
            analisis.recomendaciones.append("Realizar análisis forense del sistema")
            analisis.recomendaciones.append("Revisar logs del sistema para actividad relacionada")
    
    def obtener_estadisticas_generales(self) -> Dict[str, Any]:
        """Obtiene estadísticas generales del analizador."""
        return {
            'analizando': self.analizando,
            'procesos_con_historial': len(self.historiales_procesos),
            'analisis_completados': len(self.analisis_completados),
            'patrones_detectados': len(self.patrones_globales),
            'timestamp_ultimo_analisis': datetime.now().isoformat()
        }
    
    def generar_reporte_markdown(self) -> str:
        """Genera un reporte detallado en formato Markdown."""
        stats = self.obtener_estadisticas_generales()
        
        md = "# 🔮 Informe del Oráculo de los Patrones\n\n"
        md += f"**Estado del Oráculo:** {'🟢 Contemplando' if self.analizando else '🔴 En reposo'}\n"
        md += f"**Procesos con Historial:** {stats['procesos_con_historial']}\n"
        md += f"**Análisis Completados:** {stats['analisis_completados']}\n"
        md += f"**Patrones Detectados:** {stats['patrones_detectados']}\n"
        md += f"**Última Contemplación:** {stats['timestamp_ultimo_analisis']}\n\n"
        
        # Patrones recientes
        patrones_recientes = sorted(
            self.patrones_globales,
            key=lambda p: p.timestamp,
            reverse=True
        )[:10]
        
        if patrones_recientes:
            md += "## 🌟 Patrones Revelados Recientemente\n\n"
            md += "| Tipo | Descripción | Nivel | Procesos | Timestamp |\n"
            md += "|------|-------------|-------|----------|----------|\n"
            
            for patron in patrones_recientes:
                timestamp_str = patron.timestamp.strftime("%H:%M:%S")
                md += f"| {patron.tipo} | {patron.descripcion} | {patron.nivel_riesgo} | {len(patron.procesos_afectados)} | {timestamp_str} |\n"
            md += "\n"
        
        # Análisis de alto riesgo
        analisis_alto_riesgo = [
            a for a in self.analisis_completados[-50:]  # Últimos 50
            if a.nivel_riesgo in ["ALTO", "CRITICO"]
        ]
        
        if analisis_alto_riesgo:
            md += "## 🚨 Análisis de Alto Riesgo\n\n"
            md += "| PID | Nivel | Puntuación | Comportamientos | Recomendaciones |\n"
            md += "|-----|-------|------------|----------------|------------------|\n"
            
            for analisis in analisis_alto_riesgo[-10:]:  # Últimos 10
                comportamientos_resumen = f"{len(analisis.comportamientos_sospechosos)} detectados"
                recomendaciones_resumen = f"{len(analisis.recomendaciones)} sugeridas"
                md += f"| {analisis.pid} | {analisis.nivel_riesgo} | {analisis.puntuacion_riesgo} | {comportamientos_resumen} | {recomendaciones_resumen} |\n"
            md += "\n"
        
        md += "---\n"
        md += "*Contemplación realizada por el Oráculo de los Patrones de Ares Aegis*\n"
        
        return md
