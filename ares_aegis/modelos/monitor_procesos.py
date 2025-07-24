#!/usr/bin/env python3
"""
Creado por DogSoulDev (https://github.com/DogSoulDev)
Todos los derechos reservados. Este código es propietario y confidencial.

Monitor de Procesos Avanzado - Los Mil Ojos de Argos
Sistema avanzado de monitoreo de procesos con análisis de comportamiento y detección de amenazas
"""

import os
import sys
import time
import subprocess
import threading
import signal
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set, NamedTuple
from collections import defaultdict, deque
from ..utils.ayuda_logging import configurar_logger_modulo


class TipoProceso(Enum):
    """Tipos de procesos del sistema."""
    SISTEMA = "sistema"
    USUARIO = "usuario"
    SERVICIO = "servicio"
    DAEMON = "daemon"
    KERNEL = "kernel"
    TEMPORAL = "temporal"
    DESCONOCIDO = "desconocido"


class EstadoProceso(Enum):
    """Estados de un proceso."""
    RUNNING = "running"         # R - En ejecución
    SLEEPING = "sleeping"       # S - Durmiendo (interruptible)
    DISK_SLEEP = "disk_sleep"   # D - Durmiendo en I/O (no interrumpible)
    STOPPED = "stopped"         # T - Detenido
    ZOMBIE = "zombie"           # Z - Proceso zombie
    DEAD = "dead"              # X - Proceso muerto
    DESCONOCIDO = "desconocido"


class NivelRiesgoProceso(Enum):
    """Niveles de riesgo para procesos."""
    LEGITIMO = 0    # Proceso completamente confiable
    BAJO = 1        # Proceso normal con pequeñas anomalías
    MEDIO = 2       # Proceso con comportamiento anómalo
    ALTO = 3        # Proceso potencialmente peligroso
    CRITICO = 4     # Proceso altamente sospechoso/malicioso
    
    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented
    
    def __le__(self, other):
        if self.__class__ is other.__class__:
            return self.value <= other.value
        return NotImplemented
    
    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return self.value > other.value
        return NotImplemented
    
    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return self.value >= other.value
        return NotImplemented


class TipoAmenaza(Enum):
    """Tipos de amenazas detectadas en procesos."""
    MALWARE = "malware"
    BACKDOOR = "backdoor"
    ROOTKIT = "rootkit"
    CRYPTOMINER = "cryptominer"
    BOTNET = "botnet"
    ESCALADA_PRIVILEGIOS = "escalada_privilegios"
    EXFILTRACION_DATOS = "exfiltracion_datos"
    PROCESO_HUERFANO = "proceso_huerfano"
    USO_RECURSOS_EXCESIVO = "uso_recursos_excesivo"
    CONEXIONES_SOSPECHOSAS = "conexiones_sospechosas"
    UBICACION_SOSPECHOSA = "ubicacion_sospechosa"
    COMPORTAMIENTO_ANOMALO = "comportamiento_anomalo"


@dataclass
class ProcesoInfo:
    """Información completa de un proceso del sistema."""
    pid: int
    nombre: str
    comando: str
    usuario: str
    ruta_ejecutable: str
    pid_padre: int
    tiempo_inicio: float
    uso_cpu: float
    uso_memoria: int
    estado: EstadoProceso
    tipo: TipoProceso
    nivel_riesgo: NivelRiesgoProceso
    hash_ejecutable: str
    puertos_abiertos: List[int] = field(default_factory=list)
    conexiones_red: List[Dict[str, Any]] = field(default_factory=list)
    archivos_abiertos: List[str] = field(default_factory=list)
    permisos: List[str] = field(default_factory=list)
    argumentos: List[str] = field(default_factory=list)
    variables_entorno: Dict[str, str] = field(default_factory=dict)
    amenazas_detectadas: List[TipoAmenaza] = field(default_factory=list)
    timestamp_deteccion: float = field(default_factory=time.time)
    es_proceso_critico: bool = False
    puede_escalada_privilegios: bool = False
    
    def obtener_edad_proceso(self) -> float:
        """Obtiene la edad del proceso en segundos."""
        return time.time() - self.tiempo_inicio
    
    def obtener_memoria_mb(self) -> float:
        """Obtiene el uso de memoria en MB."""
        return self.uso_memoria / (1024 * 1024)
    
    def es_proceso_sospechoso(self) -> bool:
        """Determina si el proceso es sospechoso."""
        return self.nivel_riesgo in [NivelRiesgoProceso.CRITICO, NivelRiesgoProceso.ALTO]
    
    def calcular_puntuacion_riesgo(self) -> int:
        """Calcula una puntuación numérica de riesgo (0-100)."""
        puntuacion = 0
        
        # Puntuación base por nivel de riesgo
        if self.nivel_riesgo == NivelRiesgoProceso.CRITICO:
            puntuacion += 80
        elif self.nivel_riesgo == NivelRiesgoProceso.ALTO:
            puntuacion += 60
        elif self.nivel_riesgo == NivelRiesgoProceso.MEDIO:
            puntuacion += 30
        elif self.nivel_riesgo == NivelRiesgoProceso.BAJO:
            puntuacion += 10
        
        # Bonificaciones por amenazas específicas
        puntuacion += len(self.amenazas_detectadas) * 5
        
        # Bonificaciones por conexiones de red
        if len(self.conexiones_red) > 10:
            puntuacion += 15
        elif len(self.conexiones_red) > 5:
            puntuacion += 10
        
        # Bonificaciones por uso de recursos
        if self.uso_cpu > 80:
            puntuacion += 10
        if self.obtener_memoria_mb() > 500:
            puntuacion += 10
        
        return min(puntuacion, 100)


@dataclass
class AlertaProceso:
    """Alerta generada por el monitor de procesos."""
    proceso: ProcesoInfo
    tipo_amenaza: TipoAmenaza
    nivel_severidad: NivelRiesgoProceso
    mensaje: str
    descripcion_tecnica: str
    recomendaciones: List[str]
    evidencia: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    requiere_accion_inmediata: bool = False
    id_alerta: str = field(default="")
    
    def __post_init__(self):
        """Inicialización posterior a la creación."""
        if not self.id_alerta:
            datos_hash = f"{self.proceso.pid}_{self.tipo_amenaza.value}_{self.timestamp.isoformat()}"
            self.id_alerta = hashlib.md5(datos_hash.encode()).hexdigest()[:12]
    
    def obtener_resumen_markdown(self) -> str:
        """Genera un resumen de la alerta en formato Markdown."""
        icono_severidad = {
            NivelRiesgoProceso.CRITICO: "🔴",
            NivelRiesgoProceso.ALTO: "🟠", 
            NivelRiesgoProceso.MEDIO: "🟡",
            NivelRiesgoProceso.BAJO: "⚪"
        }
        
        md = f"## {icono_severidad.get(self.nivel_severidad, '⚪')} Alerta de Proceso - {self.tipo_amenaza.value.upper()}\n\n"
        md += f"**Proceso:** {self.proceso.nombre} (PID: {self.proceso.pid})\n"
        md += f"**Usuario:** {self.proceso.usuario}\n"
        md += f"**Severidad:** {self.nivel_severidad.value}\n"
        md += f"**Mensaje:** {self.mensaje}\n\n"
        md += f"**Descripción Técnica:**\n{self.descripcion_tecnica}\n\n"
        
        if self.recomendaciones:
            md += "**Recomendaciones:**\n"
            for rec in self.recomendaciones:
                md += f"- {rec}\n"
        
        if self.requiere_accion_inmediata:
            md += "\n⚠️ **REQUIERE ACCIÓN INMEDIATA** ⚠️\n"
        
        return md


class AnalizadorComportamientoProcesos:
    """Analizador avanzado de comportamiento de procesos."""
    
    def __init__(self):
        """Inicializa el analizador de comportamiento."""
        self.patrones_malware = {
            'cryptominer': ['miner', 'xmrig', 'cpuminer', 'minerd', 'ccminer'],
            'backdoor': ['nc', 'netcat', 'ncat', 'socat', 'reverse_tcp'],
            'rootkit': ['rootkit', 'stealth', 'hide', 'invisible'],
            'botnet': ['bot', 'drone', 'slave', 'c2', 'command']
        }
        
        self.ubicaciones_sospechosas = {
            '/tmp/', '/var/tmp/', '/dev/shm/', '/home/.*/.cache/',
            '/home/.*/Downloads/', '/tmp/.', '/var/tmp/.', '\\tmp\\'
        }
        
        self.procesos_sistema_legitimos = {
            'systemd', 'kthreadd', 'init', 'kernel', 'kworker', 'migration',
            'rcu_', 'watchdog', 'sshd', 'dbus', 'NetworkManager', 'systemd-',
            'cron', 'rsyslog', 'apache2', 'nginx', 'mysql', 'postgres'
        }
        
        self.extensiones_ejecutables_sospechosas = {
            '.tmp', '.cache', '.download', '.part', '.bin', '.run'
        }
    
    def analizar_proceso(self, proceso: ProcesoInfo) -> ProcesoInfo:
        """Analiza un proceso y determina su nivel de riesgo."""
        amenazas = []
        nivel_riesgo = NivelRiesgoProceso.LEGITIMO
        
        # Análisis de ubicación
        if self._es_ubicacion_sospechosa(proceso.ruta_ejecutable):
            amenazas.append(TipoAmenaza.UBICACION_SOSPECHOSA)
            nivel_riesgo = max(nivel_riesgo, NivelRiesgoProceso.MEDIO)
        
        # Análisis de patrones de malware
        tipo_malware = self._detectar_patron_malware(proceso.nombre, proceso.comando)
        if tipo_malware:
            if tipo_malware == 'cryptominer':
                amenazas.append(TipoAmenaza.CRYPTOMINER)
                nivel_riesgo = max(nivel_riesgo, NivelRiesgoProceso.ALTO)
            elif tipo_malware == 'backdoor':
                amenazas.append(TipoAmenaza.BACKDOOR)
                nivel_riesgo = max(nivel_riesgo, NivelRiesgoProceso.CRITICO)
            elif tipo_malware == 'rootkit':
                amenazas.append(TipoAmenaza.ROOTKIT)
                nivel_riesgo = max(nivel_riesgo, NivelRiesgoProceso.CRITICO)
            elif tipo_malware == 'botnet':
                amenazas.append(TipoAmenaza.BOTNET)
                nivel_riesgo = max(nivel_riesgo, NivelRiesgoProceso.ALTO)
        
        # Análisis de procesos huérfanos
        if self._es_proceso_huerfano_sospechoso(proceso):
            amenazas.append(TipoAmenaza.PROCESO_HUERFANO)
            nivel_riesgo = max(nivel_riesgo, NivelRiesgoProceso.MEDIO)
        
        # Análisis de uso de recursos
        if self._uso_recursos_excesivo(proceso):
            amenazas.append(TipoAmenaza.USO_RECURSOS_EXCESIVO)
            nivel_riesgo = max(nivel_riesgo, NivelRiesgoProceso.BAJO)
        
        # Análisis de conexiones de red
        if self._conexiones_sospechosas(proceso):
            amenazas.append(TipoAmenaza.CONEXIONES_SOSPECHOSAS)
            nivel_riesgo = max(nivel_riesgo, NivelRiesgoProceso.MEDIO)
        
        # Análisis de escalada de privilegios
        if self._puede_escalada_privilegios(proceso):
            amenazas.append(TipoAmenaza.ESCALADA_PRIVILEGIOS)
            proceso.puede_escalada_privilegios = True
            nivel_riesgo = max(nivel_riesgo, NivelRiesgoProceso.ALTO)
        
        # Actualizar proceso con resultados del análisis
        proceso.amenazas_detectadas = amenazas
        proceso.nivel_riesgo = nivel_riesgo
        
        return proceso
    
    def _es_ubicacion_sospechosa(self, ruta: str) -> bool:
        """Verifica si la ubicación del ejecutable es sospechosa."""
        if not ruta:
            return True
        
        ruta_lower = ruta.lower()
        return any(ubicacion in ruta_lower for ubicacion in self.ubicaciones_sospechosas)
    
    def _detectar_patron_malware(self, nombre: str, comando: str) -> Optional[str]:
        """Detecta patrones conocidos de malware."""
        texto_busqueda = f"{nombre} {comando}".lower()
        
        for tipo_malware, patrones in self.patrones_malware.items():
            if any(patron in texto_busqueda for patron in patrones):
                return tipo_malware
        
        return None
    
    def _es_proceso_huerfano_sospechoso(self, proceso: ProcesoInfo) -> bool:
        """Verifica si un proceso huérfano es sospechoso."""
        if proceso.pid_padre != 1:
            return False
        
        # Los procesos del sistema con PPID=1 son normales
        return not any(proc_sistema in proceso.nombre.lower() 
                      for proc_sistema in self.procesos_sistema_legitimos)
    
    def _uso_recursos_excesivo(self, proceso: ProcesoInfo) -> bool:
        """Verifica si el proceso usa recursos excesivamente."""
        return (proceso.uso_cpu > 80.0 or 
                proceso.obtener_memoria_mb() > 500 or
                len(proceso.conexiones_red) > 20)
    
    def _conexiones_sospechosas(self, proceso: ProcesoInfo) -> bool:
        """Analiza si las conexiones de red son sospechosas."""
        if len(proceso.conexiones_red) > 10:
            return True
        
        # Verificar conexiones a IPs sospechosas (ejemplo simple)
        for conexion in proceso.conexiones_red:
            ip_remota = conexion.get('remoto', '').split(':')[0]
            if self._es_ip_sospechosa(ip_remota):
                return True
        
        return False
    
    def _es_ip_sospechosa(self, ip: str) -> bool:
        """Verifica si una IP es conocida como sospechosa."""
        # Implementación básica - en producción usaría listas de IPs maliciosas
        ips_sospechosas = ['10.0.0.1', '192.168.1.1']  # Placeholder
        return ip in ips_sospechosas
    
    def _puede_escalada_privilegios(self, proceso: ProcesoInfo) -> bool:
        """Verifica si el proceso puede realizar escalada de privilegios."""
        # Verificar permisos especiales
        permisos_sospechosos = ['setuid', 'setgid', 'sudo', 'su']
        return any(permiso in ' '.join(proceso.permisos) for permiso in permisos_sospechosos)


class EstadisticasProceso:
    """Estadísticas históricas de un proceso."""
    
    def __init__(self, pid: int):
        """Inicializa las estadísticas del proceso."""
        self.pid = pid
        self.timestamp_inicio = time.time()
        self.muestras_cpu: deque = deque(maxlen=100)
        self.muestras_memoria: deque = deque(maxlen=100)
        self.picos_cpu = 0.0
        self.picos_memoria = 0
        self.tiempo_activo = 0.0
        self.conexiones_total = 0
        self.archivos_abiertos: Set[str] = set()
        self.historial_conexiones: List[Dict[str, Any]] = []
        self.cambios_permisos: List[Dict[str, Any]] = []
        self.alertas_generadas: List[str] = []
    
    def agregar_muestra(self, cpu: float, memoria: int):
        """Agrega una muestra de uso de recursos."""
        self.muestras_cpu.append(cpu)
        self.muestras_memoria.append(memoria)
        
        # Actualizar picos
        self.picos_cpu = max(self.picos_cpu, cpu)
        self.picos_memoria = max(self.picos_memoria, memoria)
        
        # Actualizar tiempo activo
        self.tiempo_activo = time.time() - self.timestamp_inicio
    
    def obtener_promedio_cpu(self) -> float:
        """Obtiene el promedio de uso de CPU."""
        return sum(self.muestras_cpu) / len(self.muestras_cpu) if self.muestras_cpu else 0.0
    
    def obtener_promedio_memoria(self) -> float:
        """Obtiene el promedio de uso de memoria."""
        return sum(self.muestras_memoria) / len(self.muestras_memoria) if self.muestras_memoria else 0.0
    
    def detectar_anomalias(self) -> List[str]:
        """Detecta anomalías en el comportamiento del proceso."""
        anomalias = []
        
        if len(self.muestras_cpu) >= 10:
            promedio_cpu = self.obtener_promedio_cpu()
            if self.picos_cpu > promedio_cpu * 3:
                anomalias.append(f"Pico de CPU anómalo: {self.picos_cpu:.1f}% (promedio: {promedio_cpu:.1f}%)")
        
        if len(self.muestras_memoria) >= 10:
            promedio_memoria = self.obtener_promedio_memoria()
            if self.picos_memoria > promedio_memoria * 2:
                memoria_mb = self.picos_memoria / (1024 * 1024)
                promedio_mb = promedio_memoria / (1024 * 1024)
                anomalias.append(f"Pico de memoria anómalo: {memoria_mb:.1f}MB (promedio: {promedio_mb:.1f}MB)")
        
        return anomalias


class MonitorProcesos:
    """Monitor avanzado de procesos del sistema - Los Mil Ojos de Argos."""
    
    def __init__(self, siem=None):
        """
        Inicializa el monitor de procesos.
        
        Args:
            siem: Instancia del SIEM para registro de eventos
        """
        self.logger = configurar_logger_modulo("monitor_procesos")
        self.siem = siem
        
        # Estado del monitor
        self.monitoreando = False
        self.hilo_monitor: Optional[threading.Thread] = None
        self.intervalo_monitoreo = 5  # segundos
        
        # Datos de procesos
        self.procesos_actuales: Dict[int, ProcesoInfo] = {}
        self.estadisticas_procesos: Dict[int, EstadisticasProceso] = {}
        self.procesos_finalizados: List[ProcesoInfo] = []
        self.procesos_sospechosos: List[ProcesoInfo] = []
        self.alertas_activas: List[AlertaProceso] = []
        
        # Analizador de comportamiento
        self.analizador = AnalizadorComportamientoProcesos()
        
        # Configuración de alertas
        self.umbral_cpu_alto = 80.0  # %
        self.umbral_memoria_alto = 500 * 1024 * 1024  # 500MB en bytes
        self.umbrales_conexiones_red = 10  # número máximo de conexiones
        
        # Listas de procesos conocidos
        self.procesos_sistema = {
            'systemd', 'kthreadd', 'init', 'kernel', 'kworker',
            'migration', 'rcu_', 'watchdog', 'sshd', 'dbus',
            'NetworkManager', 'systemd-', 'cron', 'rsyslog'
        }
        
        self.directorios_sospechosos = {
            '/tmp/', '/var/tmp/', '/dev/shm/', '/home/.*/.cache/',
            '/home/.*/Downloads/', '/tmp/.', '/var/tmp/.'
        }
        
        self.logger.info("🔱 Los mil ojos de Argos han despertado para vigilar los procesos del reino")
    
    def iniciar_monitoreo(self):
        """Inicia el monitoreo continuo de procesos."""
        if self.monitoreando:
            self.logger.warning("El vigía de Argos ya observa los procesos del reino")
            return
        
        self.monitoreando = True
        self.hilo_monitor = threading.Thread(target=self._loop_monitoreo, daemon=True)
        self.hilo_monitor.start()
        
        if self.siem:
            from .siem import TipoEvento
            self.siem.registrar_evento(
                TipoEvento.SISTEMA_INICIADO,
                "🔱 Monitor de procesos de Argos activado - Los mil ojos comienzan su vigilia",
                {"componente": "monitor_procesos_avanzado"},
                "MEDIO"
            )
        
        self.logger.info("⚔️ Los ojos de Argos comienzan su vigilia eterna sobre los procesos")
    
    def detener_monitoreo(self):
        """Detiene el monitoreo de procesos."""
        if not self.monitoreando:
            return
        
        self.monitoreando = False
        
        if self.hilo_monitor:
            self.hilo_monitor.join(timeout=10)
        
        if self.siem:
            from .siem import TipoEvento
            self.siem.registrar_evento(
                TipoEvento.SISTEMA_DETENIDO,
                "🔱 Monitor de procesos de Argos desactivado - Los ojos se cierran",
                {
                    "procesos_monitoreados": len(self.procesos_actuales),
                    "procesos_sospechosos": len(self.procesos_sospechosos),
                    "alertas_generadas": len(self.alertas_activas)
                },
                "MEDIO"
            )
        
        self.logger.info("💤 Los ojos de Argos han cerrado para el descanso")
    
    def _loop_monitoreo(self):
        """Loop principal de monitoreo de procesos."""
        self.logger.info("🔄 Iniciando ciclo eterno de vigilancia de los procesos")
        
        while self.monitoreando:
            try:
                self._escanear_procesos()
                self._identificar_procesos_sospechosos()
                self._generar_alertas()
                self._limpiar_datos_antiguos()
                time.sleep(self.intervalo_monitoreo)
                
            except Exception as e:
                self.logger.error(f"💥 Error en ciclo de monitoreo de procesos: {e}")
                time.sleep(self.intervalo_monitoreo * 2)
    
    def _escanear_procesos(self):
        """Escanea todos los procesos activos del sistema."""
        try:
            pids_actuales = set()
            
            # Obtener lista de procesos usando subprocess
            resultado = subprocess.run(['ps', 'aux'], capture_output=True, text=True, timeout=10)
            
            if resultado.returncode == 0:
                lineas = resultado.stdout.split('\n')[1:]  # Omitir header
                
                for linea in lineas:
                    if not linea.strip():
                        continue
                    
                    try:
                        proceso_info = self._parsear_linea_ps(linea)
                        if proceso_info:
                            # Analizar el proceso con nuestro analizador avanzado
                            proceso_analizado = self.analizador.analizar_proceso(proceso_info)
                            pids_actuales.add(proceso_analizado.pid)
                            self._procesar_proceso(proceso_analizado)
                    
                    except Exception as e:
                        self.logger.debug(f"Error procesando línea de ps: {e}")
                        continue
            
            # Marcar procesos finalizados
            pids_finalizados = set(self.procesos_actuales.keys()) - pids_actuales
            for pid in pids_finalizados:
                proceso_finalizado = self.procesos_actuales.pop(pid, None)
                if proceso_finalizado:
                    self.procesos_finalizados.append(proceso_finalizado)
                    self.logger.debug(f"⚱️ Proceso finalizado: PID {pid} ({proceso_finalizado.nombre})")
        
        except Exception as e:
            self.logger.error(f"💥 Error escaneando procesos: {e}")
    
    def _identificar_procesos_sospechosos(self):
        """Identifica procesos marcados como sospechosos por el analizador avanzado."""
        for proceso in self.procesos_actuales.values():
            # Si el analizador ya marcó el proceso como sospechoso
            if proceso.es_proceso_sospechoso():
                if proceso not in self.procesos_sospechosos:
                    self.procesos_sospechosos.append(proceso)
                    self.logger.warning(f"🚨 Proceso sospechoso detectado: {proceso.nombre} (PID: {proceso.pid}) - Nivel: {proceso.nivel_riesgo.name}")
    
    def _generar_alertas(self):
        """Genera alertas para procesos que requieren atención."""
        for proceso in self.procesos_actuales.values():
            if proceso.es_proceso_sospechoso():
                # Generar alertas específicas por cada amenaza detectada
                for amenaza in proceso.amenazas_detectadas:
                    if not self._alerta_ya_existe(proceso.pid, amenaza):
                        alerta = self._crear_alerta_proceso(proceso, amenaza)
                        self.alertas_activas.append(alerta)
                        self._notificar_alerta(alerta)
    
    def _alerta_ya_existe(self, pid: int, amenaza: TipoAmenaza) -> bool:
        """Verifica si ya existe una alerta para este proceso y amenaza."""
        for alerta in self.alertas_activas:
            if alerta.proceso.pid == pid and alerta.tipo_amenaza == amenaza:
                return True
        return False
    
    def _crear_alerta_proceso(self, proceso: ProcesoInfo, amenaza: TipoAmenaza) -> AlertaProceso:
        """Crea una alerta detallada para un proceso."""
        mensaje = f"Amenaza {amenaza.value} detectada en proceso {proceso.nombre}"
        
        # Descripción técnica específica por tipo de amenaza
        descripcion_tecnica = self._obtener_descripcion_amenaza(proceso, amenaza)
        
        # Recomendaciones específicas
        recomendaciones = self._obtener_recomendaciones_amenaza(amenaza)
        
        # Evidencia técnica
        evidencia = {
            'pid': proceso.pid,
            'ruta_ejecutable': proceso.ruta_ejecutable,
            'hash_ejecutable': proceso.hash_ejecutable,
            'uso_cpu': proceso.uso_cpu,
            'uso_memoria_mb': proceso.obtener_memoria_mb(),
            'conexiones_red': len(proceso.conexiones_red),
            'puertos_abiertos': proceso.puertos_abiertos,
            'usuario': proceso.usuario,
            'argumentos': proceso.argumentos,
            'edad_proceso': proceso.obtener_edad_proceso()
        }
        
        return AlertaProceso(
            proceso=proceso,
            tipo_amenaza=amenaza,
            nivel_severidad=proceso.nivel_riesgo,
            mensaje=mensaje,
            descripcion_tecnica=descripcion_tecnica,
            recomendaciones=recomendaciones,
            evidencia=evidencia,
            requiere_accion_inmediata=(proceso.nivel_riesgo in [NivelRiesgoProceso.CRITICO, NivelRiesgoProceso.ALTO])
        )
    
    def _obtener_descripcion_amenaza(self, proceso: ProcesoInfo, amenaza: TipoAmenaza) -> str:
        """Obtiene descripción técnica específica para cada tipo de amenaza."""
        descripciones = {
            TipoAmenaza.MALWARE: f"Proceso {proceso.nombre} muestra patrones característicos de malware",
            TipoAmenaza.BACKDOOR: f"Proceso {proceso.nombre} presenta comportamiento típico de backdoor",
            TipoAmenaza.CRYPTOMINER: f"Proceso {proceso.nombre} detectado como posible cryptominer - Alto uso de CPU: {proceso.uso_cpu}%",
            TipoAmenaza.UBICACION_SOSPECHOSA: f"Proceso ejecutándose desde ubicación no confiable: {proceso.ruta_ejecutable}",
            TipoAmenaza.CONEXIONES_SOSPECHOSAS: f"Proceso estableciendo múltiples conexiones de red: {len(proceso.conexiones_red)} conexiones activas",
            TipoAmenaza.PROCESO_HUERFANO: f"Proceso huérfano con PPID=1 sin ser servicio del sistema legítimo",
            TipoAmenaza.USO_RECURSOS_EXCESIVO: f"Consumo excesivo de recursos - CPU: {proceso.uso_cpu}%, Memoria: {proceso.obtener_memoria_mb():.1f}MB",
            TipoAmenaza.ESCALADA_PRIVILEGIOS: f"Proceso con capacidad de escalada de privilegios detectada"
        }
        
        return descripciones.get(amenaza, f"Amenaza {amenaza.value} detectada en proceso {proceso.nombre}")
    
    def _obtener_recomendaciones_amenaza(self, amenaza: TipoAmenaza) -> List[str]:
        """Obtiene recomendaciones específicas para cada tipo de amenaza."""
        recomendaciones = {
            TipoAmenaza.MALWARE: [
                "Aislar inmediatamente el proceso",
                "Ejecutar análisis antimalware completo",
                "Verificar integridad del sistema",
                "Revisar logs de actividad reciente"
            ],
            TipoAmenaza.BACKDOOR: [
                "Terminar proceso inmediatamente",
                "Bloquear conexiones de red asociadas",
                "Cambiar todas las credenciales del sistema",
                "Investigar punto de entrada inicial"
            ],
            TipoAmenaza.CRYPTOMINER: [
                "Terminar proceso de minería",
                "Verificar otros procesos relacionados",
                "Revisar tareas programadas",
                "Actualizar protecciones del sistema"
            ],
            TipoAmenaza.UBICACION_SOSPECHOSA: [
                "Verificar origen del ejecutable",
                "Mover archivo a cuarentena",
                "Escanear directorio de origen",
                "Revisar logs de acceso"
            ],
            TipoAmenaza.CONEXIONES_SOSPECHOSAS: [
                "Monitorear tráfico de red",
                "Verificar destinos de conexiones",
                "Aplicar reglas de firewall",
                "Analizar patrones de comunicación"
            ]
        }
        
        return recomendaciones.get(amenaza, ["Investigar actividad del proceso", "Considerar terminación si es malicioso"])
    
    def _notificar_alerta(self, alerta: AlertaProceso):
        """Notifica sobre una alerta de proceso."""
        if self.siem:
            from .siem import TipoEvento
            nivel_evento = "CRITICO" if alerta.nivel_severidad == NivelRiesgoProceso.CRITICO else "ALTO"
            
            self.siem.registrar_evento(
                TipoEvento.AMENAZA_DETECTADA,
                f"⚡ Argos detecta amenaza {alerta.tipo_amenaza.value}: {alerta.mensaje}",
                alerta.evidencia,
                nivel_evento
            )
        
        # Log según severidad
        if alerta.nivel_severidad == NivelRiesgoProceso.CRITICO:
            self.logger.critical(f"🔴 AMENAZA CRÍTICA: {alerta.mensaje}")
        elif alerta.nivel_severidad == NivelRiesgoProceso.ALTO:
            self.logger.error(f"🟠 AMENAZA ALTA: {alerta.mensaje}")
        else:
            self.logger.warning(f"🟡 AMENAZA DETECTADA: {alerta.mensaje}")
    
    def _limpiar_datos_antiguos(self):
        """Limpia datos antiguos para mantener el rendimiento."""
        # Limpiar procesos finalizados (mantener últimos 1000)
        if len(self.procesos_finalizados) > 1000:
            self.procesos_finalizados = self.procesos_finalizados[-500:]
        
        # Limpiar alertas antiguas (más de 1 hora)
        tiempo_limite = datetime.now() - timedelta(hours=1)
        self.alertas_activas = [
            alerta for alerta in self.alertas_activas
            if alerta.timestamp > tiempo_limite
        ]
        
        # Limpiar estadísticas de procesos muy antiguos
        tiempo_actual = time.time()
        pids_a_limpiar = []
        
        for pid, estadistica in self.estadisticas_procesos.items():
            if tiempo_actual - estadistica.timestamp_inicio > 3600:  # 1 hora
                if pid not in self.procesos_actuales:
                    pids_a_limpiar.append(pid)
        
        for pid in pids_a_limpiar:
            del self.estadisticas_procesos[pid]
    
    def _parsear_linea_ps(self, linea: str) -> Optional[ProcesoInfo]:
        """
        Parsea una línea de salida del comando ps aux.
        
        Args:
            linea: Línea de salida de ps aux
            
        Returns:
            ProcesoInfo o None si hay error
        """
        try:
            partes = linea.split(None, 10)
            if len(partes) < 11:
                return None
            
            usuario = partes[0]
            pid = int(partes[1])
            uso_cpu = float(partes[2])
            uso_memoria_kb = int(partes[5])
            estado = partes[7]
            comando_completo = partes[10]
            
            # Extraer nombre del proceso y ruta ejecutable
            comando_partes = comando_completo.split()
            if comando_partes:
                ruta_ejecutable = comando_partes[0]
                nombre = os.path.basename(ruta_ejecutable)
            else:
                nombre = "desconocido"
                ruta_ejecutable = ""
            
            # Obtener información adicional del proceso
            pid_padre = self._obtener_pid_padre(pid)
            tiempo_inicio = self._obtener_tiempo_inicio_proceso(pid)
            puertos_abiertos = self._obtener_puertos_proceso(pid)
            conexiones_red = self._obtener_conexiones_proceso(pid)
            
            # Calcular hash del ejecutable
            hash_ejecutable = self._calcular_hash_ejecutable(ruta_ejecutable)
            
            # Determinar tipo de proceso
            tipo_proceso = self._determinar_tipo_proceso(nombre, ruta_ejecutable, pid_padre)
            
            # Determinar estado del proceso
            estado_proceso = self._convertir_estado_proceso(estado)
            
            # Obtener información adicional de seguridad
            permisos = self._obtener_permisos_proceso(pid)
            argumentos = comando_partes[1:] if len(comando_partes) > 1 else []
            variables_entorno = self._obtener_variables_entorno(pid)
            
            return ProcesoInfo(
                pid=pid,
                nombre=nombre,
                comando=comando_completo,
                usuario=usuario,
                ruta_ejecutable=ruta_ejecutable,
                pid_padre=pid_padre,
                tiempo_inicio=tiempo_inicio,
                uso_cpu=uso_cpu,
                uso_memoria=uso_memoria_kb * 1024,  # Convertir a bytes
                estado=estado_proceso,
                tipo=tipo_proceso,
                nivel_riesgo=NivelRiesgoProceso.LEGITIMO,  # Se evaluará después
                hash_ejecutable=hash_ejecutable,
                puertos_abiertos=puertos_abiertos,
                conexiones_red=conexiones_red,
                permisos=permisos,
                argumentos=argumentos,
                variables_entorno=variables_entorno
            )
        
        except (ValueError, IndexError) as e:
            self.logger.debug(f"Error parseando línea ps: {e}")
            return None
    
    def _obtener_pid_padre(self, pid: int) -> int:
        """Obtiene el PID padre de un proceso."""
        try:
            with open(f'/proc/{pid}/stat', 'r') as f:
                stat_data = f.read().split()
                return int(stat_data[3])  # PPID está en la posición 3
        except (IOError, ValueError, IndexError):
            return -1
    
    def _obtener_tiempo_inicio_proceso(self, pid: int) -> float:
        """Obtiene el tiempo de inicio de un proceso."""
        try:
            with open(f'/proc/{pid}/stat', 'r') as f:
                stat_data = f.read().split()
                starttime = int(stat_data[21])  # starttime en jiffies
                
                # Convertir jiffies a tiempo real (aproximado)
                boot_time = self._obtener_boot_time()
                clock_ticks = os.sysconf(os.sysconf_names['SC_CLK_TCK'])
                return boot_time + (starttime / clock_ticks)
        
        except (IOError, ValueError, IndexError):
            return time.time()
    
    def _calcular_hash_ejecutable(self, ruta_ejecutable: str) -> str:
        """Calcula el hash SHA256 del ejecutable."""
        try:
            if not ruta_ejecutable or not os.path.exists(ruta_ejecutable):
                return "no_disponible"
            
            with open(ruta_ejecutable, 'rb') as f:
                # Leer solo los primeros 8KB para eficiencia
                contenido = f.read(8192)
                return hashlib.sha256(contenido).hexdigest()[:16]
        except (IOError, PermissionError):
            return "acceso_denegado"
    
    def _determinar_tipo_proceso(self, nombre: str, ruta: str, pid_padre: int) -> TipoProceso:
        """Determina el tipo de proceso basado en características."""
        nombre_lower = nombre.lower()
        
        # Procesos del kernel
        if 'kernel' in nombre_lower or ruta.startswith('[') or pid_padre == 0:
            return TipoProceso.KERNEL
        
        # Procesos del sistema
        if any(proc in nombre_lower for proc in ['systemd', 'init', 'kthread']):
            return TipoProceso.SISTEMA
        
        # Daemons
        if nombre_lower.endswith('d') or 'daemon' in nombre_lower:
            return TipoProceso.DAEMON
        
        # Servicios
        if any(servicio in ruta for servicio in ['/usr/sbin/', '/sbin/', 'service']):
            return TipoProceso.SERVICIO
        
        # Procesos temporales
        if any(temp in ruta for temp in ['/tmp/', '/var/tmp/', '.tmp']):
            return TipoProceso.TEMPORAL
        
        # Procesos de usuario
        if '/home/' in ruta or '/usr/bin/' in ruta:
            return TipoProceso.USUARIO
        
        return TipoProceso.DESCONOCIDO
    
    def _convertir_estado_proceso(self, estado: str) -> EstadoProceso:
        """Convierte el estado del proceso a nuestro enum."""
        estado_map = {
            'R': EstadoProceso.RUNNING,
            'S': EstadoProceso.SLEEPING,
            'D': EstadoProceso.DISK_SLEEP,
            'T': EstadoProceso.STOPPED,
            'Z': EstadoProceso.ZOMBIE,
            'X': EstadoProceso.DEAD
        }
        
        return estado_map.get(estado, EstadoProceso.DESCONOCIDO)
    
    def _obtener_permisos_proceso(self, pid: int) -> List[str]:
        """Obtiene los permisos especiales del proceso."""
        permisos = []
        try:
            # Verificar si tiene capacidades especiales
            with open(f'/proc/{pid}/status', 'r') as f:
                for linea in f:
                    if linea.startswith('CapEff:'):
                        cap_eff = linea.split(':')[1].strip()
                        if cap_eff != '0000000000000000':
                            permisos.append('capabilities')
                        break
        except (IOError, PermissionError):
            pass
        
        return permisos
    
    def _obtener_variables_entorno(self, pid: int) -> Dict[str, str]:
        """Obtiene variables de entorno relevantes del proceso."""
        variables = {}
        try:
            with open(f'/proc/{pid}/environ', 'rb') as f:
                environ_data = f.read().decode('utf-8', errors='ignore')
                for var in environ_data.split('\0'):
                    if '=' in var:
                        key, value = var.split('=', 1)
                        # Solo guardamos variables relevantes para seguridad
                        if key in ['PATH', 'LD_LIBRARY_PATH', 'HOME', 'USER']:
                            variables[key] = value
        except (IOError, PermissionError):
            pass
        
        return variables

    def _obtener_boot_time(self) -> float:
        """Obtiene el tiempo de arranque del sistema."""
        try:
            with open('/proc/stat', 'r') as f:
                for linea in f:
                    if linea.startswith('btime'):
                        return float(linea.split()[1])
        except IOError:
            pass
        return time.time()
    
    def _obtener_puertos_proceso(self, pid: int) -> List[int]:
        """Obtiene los puertos abiertos por un proceso."""
        puertos = []
        try:
            # Buscar en conexiones TCP
            resultado = subprocess.run(['netstat', '-tlnp'], capture_output=True, text=True, timeout=5)
            if resultado.returncode == 0:
                for linea in resultado.stdout.split('\n'):
                    if f'{pid}/' in linea:
                        partes = linea.split()
                        if len(partes) >= 4:
                            direccion_local = partes[3]
                            if ':' in direccion_local:
                                puerto_str = direccion_local.split(':')[-1]
                                try:
                                    puerto = int(puerto_str)
                                    puertos.append(puerto)
                                except ValueError:
                                    continue
        
        except Exception as e:
            self.logger.debug(f"Error obteniendo puertos del proceso {pid}: {e}")
        
        return puertos
    
    def _obtener_conexiones_proceso(self, pid: int) -> List[Dict[str, Any]]:
        """Obtiene las conexiones de red activas de un proceso."""
        conexiones = []
        try:
            resultado = subprocess.run(['netstat', '-tnp'], capture_output=True, text=True, timeout=5)
            if resultado.returncode == 0:
                for linea in resultado.stdout.split('\n'):
                    if f'{pid}/' in linea and 'ESTABLISHED' in linea:
                        partes = linea.split()
                        if len(partes) >= 5:
                            local = partes[3]
                            remoto = partes[4]
                            estado = partes[5]
                            
                            conexion = {
                                'local': local,
                                'remoto': remoto,
                                'estado': estado,
                                'timestamp': datetime.now().isoformat()
                            }
                            conexiones.append(conexion)
        
        except Exception as e:
            self.logger.debug(f"Error obteniendo conexiones del proceso {pid}: {e}")
        
        return conexiones
    
    def _procesar_proceso(self, proceso: ProcesoInfo):
        """Procesa un proceso individual y actualiza estadísticas."""
        # Actualizar proceso actual
        self.procesos_actuales[proceso.pid] = proceso
        
        # Actualizar estadísticas
        if proceso.pid not in self.estadisticas_procesos:
            self.estadisticas_procesos[proceso.pid] = EstadisticasProceso(proceso.pid)
        
        estadistica = self.estadisticas_procesos[proceso.pid]
        estadistica.agregar_muestra(proceso.uso_cpu, proceso.uso_memoria)
        estadistica.conexiones_total += len(proceso.conexiones_red)
        
        # Detectar uso excesivo de recursos
        if proceso.uso_cpu > self.umbral_cpu_alto:
            self._alertar_uso_alto_cpu(proceso)
        
        if proceso.uso_memoria > self.umbral_memoria_alto:
            self._alertar_uso_alto_memoria(proceso)
        
        if len(proceso.conexiones_red) > self.umbrales_conexiones_red:
            self._alertar_muchas_conexiones(proceso)
    
    def _analizar_procesos_sospechosos(self):
        """Analiza procesos para detectar comportamientos sospechosos."""
        for proceso in self.procesos_actuales.values():
            es_sospechoso = False
            razones_sospecha = []
            
            # Verificar ubicación sospechosa
            if any(directorio in proceso.ruta_ejecutable for directorio in self.directorios_sospechosos):
                es_sospechoso = True
                razones_sospecha.append(f"Ejecutándose desde ubicación sospechosa: {proceso.ruta_ejecutable}")
            
            # Verificar proceso sin padre legítimo
            if proceso.pid_padre == 1 and proceso.nombre not in self.procesos_sistema:
                es_sospechoso = True
                razones_sospecha.append("Proceso huérfano o con PPID sospechoso")
            
            # Verificar nombre de proceso sospechoso
            nombres_sospechosos = ['nc', 'netcat', 'ncat', 'socat', 'cryptominer', 'miner']
            if any(nombre in proceso.nombre.lower() for nombre in nombres_sospechosos):
                es_sospechoso = True
                razones_sospecha.append(f"Nombre de proceso sospechoso: {proceso.nombre}")
            
            # Verificar comportamiento de red sospechoso
            if len(proceso.conexiones_red) > 5:
                es_sospechoso = True
                razones_sospecha.append(f"Múltiples conexiones de red: {len(proceso.conexiones_red)}")
            
            # Registrar proceso sospechoso
            if es_sospechoso and proceso not in self.procesos_sospechosos:
                self.procesos_sospechosos.append(proceso)
                self._alertar_proceso_sospechoso(proceso, razones_sospecha)
    
    def _alertar_uso_alto_cpu(self, proceso: ProcesoInfo):
        """Alerta sobre uso alto de CPU."""
        mensaje = f"Proceso {proceso.nombre} (PID: {proceso.pid}) usando {proceso.uso_cpu}% CPU"
        
        if self.siem:
            from .siem import TipoEvento
            self.siem.registrar_evento(
                TipoEvento.PROCESO_SOSPECHOSO,
                f"Ares detecta gula de poder computacional: {mensaje}",
                {
                    'pid': proceso.pid,
                    'nombre': proceso.nombre,
                    'uso_cpu': proceso.uso_cpu,
                    'umbral': self.umbral_cpu_alto
                },
                "MEDIO"
            )
        
        self.logger.warning(f"Una entidad codiciosa consume la fuerza vital del CPU: {mensaje}")
    
    def _alertar_uso_alto_memoria(self, proceso: ProcesoInfo):
        """Alerta sobre uso alto de memoria."""
        memoria_mb = proceso.uso_memoria / (1024 * 1024)
        mensaje = f"Proceso {proceso.nombre} (PID: {proceso.pid}) usando {memoria_mb:.1f}MB de memoria"
        
        if self.siem:
            from .siem import TipoEvento
            self.siem.registrar_evento(
                TipoEvento.PROCESO_SOSPECHOSO,
                f"Las fuentes de Mnemósine se agotan: {mensaje}",
                {
                    'pid': proceso.pid,
                    'nombre': proceso.nombre,
                    'uso_memoria_bytes': proceso.uso_memoria,
                    'uso_memoria_mb': memoria_mb
                },
                "MEDIO"
            )
        
        self.logger.warning(f"Una bestia devora la memoria del reino: {mensaje}")
    
    def _alertar_muchas_conexiones(self, proceso: ProcesoInfo):
        """Alerta sobre múltiples conexiones de red."""
        mensaje = f"Proceso {proceso.nombre} (PID: {proceso.pid}) con {len(proceso.conexiones_red)} conexiones"
        
        if self.siem:
            from .siem import TipoEvento
            self.siem.registrar_evento(
                TipoEvento.CONEXION_SOSPECHOSA,
                f"Hermes susurra sobre múltiples caminos: {mensaje}",
                {
                    'pid': proceso.pid,
                    'nombre': proceso.nombre,
                    'conexiones': len(proceso.conexiones_red),
                    'detalles_conexiones': proceso.conexiones_red
                },
                "ALTO"
            )
        
        self.logger.warning(f"Un proceso teje demasiados hilos en la red: {mensaje}")
    
    def _alertar_proceso_sospechoso(self, proceso: ProcesoInfo, razones: List[str]):
        """Alerta sobre proceso sospechoso detectado."""
        mensaje = f"Proceso sospechoso: {proceso.nombre} (PID: {proceso.pid})"
        
        if self.siem:
            from .siem import TipoEvento
            self.siem.registrar_evento(
                TipoEvento.AMENAZA_DETECTADA,
                f"Una sombra se agita en los reinos inferiores: {mensaje}",
                {
                    'pid': proceso.pid,
                    'nombre': proceso.nombre,
                    'ruta_ejecutable': proceso.ruta_ejecutable,
                    'usuario': proceso.usuario,
                    'razones_sospecha': razones,
                    'conexiones_red': len(proceso.conexiones_red)
                },
                "ALTO"
            )
        
        self.logger.warning(f"Los ojos de Argos detectan una presencia maligna: {mensaje}")
        for razon in razones:
            self.logger.warning(f"  Razón: {razon}")
    
    def _limpiar_procesos_finalizados(self):
        """Limpia la lista de procesos finalizados manteniéndola a un tamaño manejable."""
        if len(self.procesos_finalizados) > 1000:
            self.procesos_finalizados = self.procesos_finalizados[-500:]
        
        # Limpiar estadísticas de procesos muy antiguos
        tiempo_actual = time.time()
        pids_a_limpiar = []
        
        for pid, estadistica in self.estadisticas_procesos.items():
            if tiempo_actual - estadistica.timestamp_inicio > 3600:  # 1 hora
                if pid not in self.procesos_actuales:
                    pids_a_limpiar.append(pid)
        
        for pid in pids_a_limpiar:
            del self.estadisticas_procesos[pid]
    
    def obtener_procesos(self) -> List[ProcesoInfo]:
        """
        Obtiene la lista actual de procesos monitoreados.
        
        Returns:
            Lista de procesos activos
        """
        return list(self.procesos_actuales.values())
    
    def obtener_proceso_por_pid(self, pid: int) -> Optional[ProcesoInfo]:
        """
        Obtiene información detallada de un proceso por su PID.
        
        Args:
            pid: ID del proceso
            
        Returns:
            ProcesoInfo o None si no se encuentra
        """
        return self.procesos_actuales.get(pid)
    
    def buscar_procesos_por_nombre(self, nombre: str) -> List[ProcesoInfo]:
        """
        Busca procesos por nombre.
        
        Args:
            nombre: Nombre del proceso a buscar
            
        Returns:
            Lista de procesos encontrados
        """
        resultado = []
        nombre_lower = nombre.lower()
        
        for proceso in self.procesos_actuales.values():
            if nombre_lower in proceso.nombre.lower() or nombre_lower in proceso.comando.lower():
                resultado.append(proceso)
        
        return resultado
    
    def obtener_procesos_por_usuario(self, usuario: str) -> List[ProcesoInfo]:
        """
        Obtiene todos los procesos de un usuario específico.
        
        Args:
            usuario: Nombre del usuario
            
        Returns:
            Lista de procesos del usuario
        """
        return [proceso for proceso in self.procesos_actuales.values() 
                if proceso.usuario == usuario]
    
    def obtener_estadisticas_generales(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas generales del monitor de procesos.
        
        Returns:
            Dict con estadísticas generales
        """
        total_procesos = len(self.procesos_actuales)
        procesos_con_red = len([p for p in self.procesos_actuales.values() if p.conexiones_red])
        
        # Calcular uso total de recursos
        uso_total_cpu = sum(p.uso_cpu for p in self.procesos_actuales.values())
        uso_total_memoria = sum(p.uso_memoria for p in self.procesos_actuales.values())
        
        return {
            'total_procesos': total_procesos,
            'procesos_sospechosos': len(self.procesos_sospechosos),
            'procesos_con_conexiones_red': procesos_con_red,
            'procesos_finalizados_total': len(self.procesos_finalizados),
            'uso_total_cpu_porcentaje': uso_total_cpu,
            'uso_total_memoria_mb': uso_total_memoria / (1024 * 1024),
            'monitoreando': self.monitoreando,
            'timestamp_ultimo_escaneo': datetime.now().isoformat()
        }
    
    def generar_reporte_markdown(self) -> str:
        """
        Genera un reporte detallado en formato Markdown.
        
        Returns:
            str: Reporte en formato Markdown
        """
        stats = self.obtener_estadisticas_generales()
        
        md = "# 👁️ Informe de los Mil Ojos de Argos\n\n"
        md += f"**Estado del Vigía:** {'🟢 Vigilando' if self.monitoreando else '🔴 Dormido'}\n"
        md += f"**Procesos Vigilados:** {stats['total_procesos']}\n"
        md += f"**Entidades Sospechosas:** {stats['procesos_sospechosos']}\n"
        md += f"**Conectados a la Red:** {stats['procesos_con_conexiones_red']}\n"
        md += f"**Última Vigilancia:** {stats['timestamp_ultimo_escaneo']}\n\n"
        
        # Top procesos por uso de CPU
        procesos_ordenados_cpu = sorted(
            self.procesos_actuales.values(),
            key=lambda p: p.uso_cpu,
            reverse=True
        )[:10]
        
        if procesos_ordenados_cpu:
            md += "## ⚡ Top Consumidores de Poder CPU\n\n"
            md += "| Proceso | PID | CPU% | Usuario | Comando |\n"
            md += "|---------|-----|------|---------|----------|\n"
            
            for proceso in procesos_ordenados_cpu:
                comando_corto = proceso.comando[:50] + "..." if len(proceso.comando) > 50 else proceso.comando
                md += f"| {proceso.nombre} | {proceso.pid} | {proceso.uso_cpu:.1f}% | {proceso.usuario} | `{comando_corto}` |\n"
            md += "\n"
        
        # Top procesos por uso de memoria
        procesos_ordenados_mem = sorted(
            self.procesos_actuales.values(),
            key=lambda p: p.uso_memoria,
            reverse=True
        )[:10]
        
        if procesos_ordenados_mem:
            md += "## 🧠 Top Devoradores de Memoria\n\n"
            md += "| Proceso | PID | Memoria | Usuario | Comando |\n"
            md += "|---------|-----|---------|---------|----------|\n"
            
            for proceso in procesos_ordenados_mem:
                memoria_mb = proceso.uso_memoria / (1024 * 1024)
                comando_corto = proceso.comando[:50] + "..." if len(proceso.comando) > 50 else proceso.comando
                md += f"| {proceso.nombre} | {proceso.pid} | {memoria_mb:.1f}MB | {proceso.usuario} | `{comando_corto}` |\n"
            md += "\n"
        
        # Procesos sospechosos
        if self.procesos_sospechosos:
            md += "## 🚨 Entidades Sospechosas Detectadas\n\n"
            md += "| Proceso | PID | Usuario | Ubicación | Conexiones |\n"
            md += "|---------|-----|---------|-----------|------------|\n"
            
            for proceso in self.procesos_sospechosos[-20:]:  # Últimos 20
                ubicacion_corta = proceso.ruta_ejecutable[:40] + "..." if len(proceso.ruta_ejecutable) > 40 else proceso.ruta_ejecutable
                md += f"| {proceso.nombre} | {proceso.pid} | {proceso.usuario} | `{ubicacion_corta}` | {len(proceso.conexiones_red)} |\n"
            md += "\n"
        
        # Procesos con conexiones de red
        procesos_con_red = [p for p in self.procesos_actuales.values() if p.conexiones_red]
        if procesos_con_red:
            md += "## 🌐 Procesos con Conexiones de Red\n\n"
            md += "| Proceso | PID | Conexiones | Puertos | Usuario |\n"
            md += "|---------|-----|------------|---------|----------|\n"
            
            for proceso in procesos_con_red[:15]:  # Limitar a 15
                puertos_str = ", ".join(map(str, proceso.puertos_abiertos[:5]))
                if len(proceso.puertos_abiertos) > 5:
                    puertos_str += "..."
                md += f"| {proceso.nombre} | {proceso.pid} | {len(proceso.conexiones_red)} | {puertos_str} | {proceso.usuario} |\n"
            md += "\n"
        
        md += "---\n"
        md += "*Vigilancia realizada por los Mil Ojos de Argos*\n"
        
        return md
    
    def terminar_proceso(self, pid: int, forzar: bool = False) -> Dict[str, Any]:
        """
        Termina un proceso específico.
        
        Args:
            pid: ID del proceso a terminar
            forzar: Si usar SIGKILL en lugar de SIGTERM
            
        Returns:
            Dict con resultado de la operación
        """
        try:
            proceso = self.procesos_actuales.get(pid)
            if not proceso:
                return {
                    'exitoso': False,
                    'mensaje': f"El proceso PID {pid} no existe en los registros de Argos"
                }
            
            # Intentar terminación
            signal_usado = signal.SIGKILL if forzar else signal.SIGTERM
            os.kill(pid, signal_usado)
            
            # Esperar un momento y verificar
            time.sleep(1)
            try:
                os.kill(pid, 0)  # Verificar si aún existe
                estado = "proceso aún activo"
            except ProcessLookupError:
                estado = "proceso terminado exitosamente"
            
            mensaje = f"Proceso {proceso.nombre} (PID: {pid}) juzgado por Ares - {estado}"
            
            if self.siem:
                from .siem import TipoEvento
                self.siem.registrar_evento(
                    TipoEvento.PROCESO_SOSPECHOSO,
                    f"Juicio divino ejecutado: {mensaje}",
                    {
                        'pid': pid,
                        'nombre_proceso': proceso.nombre,
                        'signal_usado': 'SIGKILL' if forzar else 'SIGTERM',
                        'resultado': estado
                    },
                    "ALTO"
                )
            
            self.logger.info(mensaje)
            
            return {
                'exitoso': True,
                'mensaje': mensaje,
                'proceso_info': {
                    'pid': proceso.pid,
                    'nombre': proceso.nombre,
                    'usuario': proceso.usuario,
                    'ruta_ejecutable': proceso.ruta_ejecutable,
                    'nivel_riesgo': proceso.nivel_riesgo.name
                }
            }
        
        except ProcessLookupError:
            mensaje = f"El proceso PID {pid} ya había partido al reino de las sombras"
            self.logger.info(mensaje)
            return {
                'exitoso': True,
                'mensaje': mensaje
            }
        
        except PermissionError:
            mensaje = f"Los dioses no conceden poder suficiente para juzgar al proceso PID {pid}"
            self.logger.error(mensaje)
            return {
                'exitoso': False,
                'mensaje': mensaje
            }
        
        except Exception as e:
            mensaje = f"Error ejecutando juicio divino sobre PID {pid}: {e}"
            self.logger.error(mensaje)
            return {
                'exitoso': False,
                'mensaje': mensaje
            }

