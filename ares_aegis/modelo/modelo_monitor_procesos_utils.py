#!/usr/bin/env python3
"""
Utilidades para Monitoreo de Procesos - Ares Aegis
Clases auxiliares, enums y dataclasses para el monitoreo de procesos

Creado por DogSoulDev
Versión: 4.0.0 - Arquitectura MVC Optimizada
"""

import os
import time
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set

try:
    import pwd  # type: ignore
    import grp  # type: ignore
    import resource  # type: ignore
except ImportError:
    pwd = grp = resource = None


class TipoProceso(Enum):
    SISTEMA = "sistema"
    USUARIO = "usuario" 
    SERVICIO = "servicio"
    DAEMON = "daemon"
    KERNEL = "kernel"
    TEMPORAL = "temporal"
    DESCONOCIDO = "desconocido"


class EstadoProceso(Enum):
    RUNNING = "running"
    SLEEPING = "sleeping"
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
    MALWARE = "malware"
    ROOTKIT = "rootkit"
    KEYLOGGER = "keylogger"
    BACKDOOR = "backdoor"
    MINER = "miner"
    RANSOMWARE = "ransomware"
    BOTNET = "botnet"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    NETWORK_SCANNER = "network_scanner"
    DATA_EXFILTRATION = "data_exfiltration"
    PERSISTENCE = "persistence"
    EVASION = "evasion"
    LATERAL_MOVEMENT = "lateral_movement"
    COMMAND_CONTROL = "command_control"
    DESCONOCIDA = "desconocida"


@dataclass
class ProcesoInfo:
    """Información detallada de un proceso."""
    pid: int
    ppid: int
    nombre: str
    cmd: str
    usuario: str
    estado: EstadoProceso
    cpu_percent: float
    memoria_rss: int  # KB
    memoria_vms: int  # KB
    tiempo_creacion: datetime
    archivos_abiertos: int = 0
    conexiones_red: int = 0
    hijos: List[int] = field(default_factory=list)
    tipo: TipoProceso = TipoProceso.DESCONOCIDO
    nivel_riesgo: NivelRiesgoProceso = NivelRiesgoProceso.LEGITIMO
    amenazas_detectadas: List[TipoAmenaza] = field(default_factory=list)
    hash_ejecutable: Optional[str] = None
    ruta_ejecutable: Optional[str] = None
    argumentos: List[str] = field(default_factory=list)

    def obtener_edad_proceso(self) -> float:
        """Obtener la edad del proceso en segundos."""
        return (datetime.now() - self.tiempo_creacion).total_seconds()

    def obtener_memoria_mb(self) -> float:
        """Obtener el uso de memoria en MB."""
        return self.memoria_rss / 1024.0

    def es_proceso_sospechoso(self) -> bool:
        """Determinar si el proceso es sospechoso."""
        return self.nivel_riesgo.value >= NivelRiesgoProceso.MEDIO.value

    def calcular_puntuacion_riesgo(self) -> int:
        """Calcular puntuación de riesgo basada en múltiples factores."""
        puntuacion = self.nivel_riesgo.value * 10
        
        # Factores de riesgo adicionales
        if self.cpu_percent > 80:
            puntuacion += 15
        if self.memoria_rss > 1024 * 1024:  # > 1GB
            puntuacion += 10
        if self.conexiones_red > 10:
            puntuacion += 5
        if self.archivos_abiertos > 50:
            puntuacion += 5
        if len(self.amenazas_detectadas) > 0:
            puntuacion += len(self.amenazas_detectadas) * 20
        
        # Procesos con nombres sospechosos
        nombres_sospechosos = ['tmp', 'temp', 'cache', 'random']
        if any(sospechoso in self.nombre.lower() for sospechoso in nombres_sospechosos):
            puntuacion += 10
            
        # Procesos corriendo desde ubicaciones no estándar
        if self.ruta_ejecutable:
            ubicaciones_sospechosas = ['/tmp/', '/var/tmp/', '/dev/shm/']
            if any(ubicacion in self.ruta_ejecutable for ubicacion in ubicaciones_sospechosas):
                puntuacion += 15
        
        return min(puntuacion, 100)  # Máximo 100


@dataclass
class AlertaProceso:
    """Alerta generada por el monitor de procesos."""
    timestamp: datetime
    proceso: ProcesoInfo
    tipo_alerta: str
    nivel_severidad: NivelRiesgoProceso
    descripcion: str
    evidencia: Dict[str, Any] = field(default_factory=dict)
    recomendaciones: List[str] = field(default_factory=list)
    procesada: bool = False
    
    def generar_mensaje_alerta(self) -> str:
        """Generar mensaje formateado para la alerta."""
        return (f"ALERTA {self.nivel_severidad.name}: {self.tipo_alerta}\n"
                f"Proceso: {self.proceso.nombre} (PID: {self.proceso.pid})\n"
                f"Usuario: {self.proceso.usuario}\n"
                f"Descripción: {self.descripcion}\n"
                f"Timestamp: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir la alerta a diccionario para serialización."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'proceso_pid': self.proceso.pid,
            'proceso_nombre': self.proceso.nombre,
            'usuario': self.proceso.usuario,
            'tipo_alerta': self.tipo_alerta,
            'nivel_severidad': self.nivel_severidad.name,
            'descripcion': self.descripcion,
            'evidencia': self.evidencia,
            'recomendaciones': self.recomendaciones,
            'procesada': self.procesada
        }


@dataclass
class EstadisticasProceso:
    """Estadísticas de un proceso a lo largo del tiempo."""
    pid: int
    nombre: str
    
    # Contadores
    total_muestras: int = 0
    tiempo_monitoreado: float = 0.0
    
    # CPU
    cpu_promedio: float = 0.0
    cpu_maximo: float = 0.0
    cpu_minimo: float = 100.0
    
    # Memoria
    memoria_promedio: float = 0.0
    memoria_maxima: float = 0.0
    memoria_minima: float = float('inf')
    
    # Actividad de red
    conexiones_promedio: float = 0.0
    conexiones_maximas: int = 0
    
    # Archivos
    archivos_promedio: float = 0.0
    archivos_maximos: int = 0
    
    # Historial de valores (últimos N valores)
    historial_cpu: List[float] = field(default_factory=lambda: [])
    historial_memoria: List[float] = field(default_factory=lambda: [])
    historial_conexiones: List[int] = field(default_factory=lambda: [])
    
    def actualizar(self, proceso: ProcesoInfo):
        """Actualizar estadísticas con nueva información del proceso."""
        self.total_muestras += 1
        
        # Actualizar CPU
        self.cpu_promedio = ((self.cpu_promedio * (self.total_muestras - 1)) + proceso.cpu_percent) / self.total_muestras
        self.cpu_maximo = max(self.cpu_maximo, proceso.cpu_percent)
        self.cpu_minimo = min(self.cpu_minimo, proceso.cpu_percent)
        
        # Actualizar memoria
        memoria_mb = proceso.obtener_memoria_mb()
        self.memoria_promedio = ((self.memoria_promedio * (self.total_muestras - 1)) + memoria_mb) / self.total_muestras
        self.memoria_maxima = max(self.memoria_maxima, memoria_mb)
        self.memoria_minima = min(self.memoria_minima, memoria_mb)
        
        # Actualizar red
        self.conexiones_promedio = ((self.conexiones_promedio * (self.total_muestras - 1)) + proceso.conexiones_red) / self.total_muestras
        self.conexiones_maximas = max(self.conexiones_maximas, proceso.conexiones_red)
        
        # Actualizar archivos
        self.archivos_promedio = ((self.archivos_promedio * (self.total_muestras - 1)) + proceso.archivos_abiertos) / self.total_muestras
        self.archivos_maximos = max(self.archivos_maximos, proceso.archivos_abiertos)
        
        # Mantener historial limitado (últimos 50 valores)
        self.historial_cpu.append(proceso.cpu_percent)
        self.historial_memoria.append(memoria_mb)
        self.historial_conexiones.append(proceso.conexiones_red)
        
        if len(self.historial_cpu) > 50:
            self.historial_cpu.pop(0)
            self.historial_memoria.pop(0)
            self.historial_conexiones.pop(0)
    
    def detectar_anomalias(self) -> List[str]:
        """Detectar anomalías en el comportamiento del proceso."""
        anomalias = []
        
        if len(self.historial_cpu) > 10:
            # Detectar picos de CPU
            cpu_reciente = sum(self.historial_cpu[-5:]) / 5
            if cpu_reciente > self.cpu_promedio * 2:
                anomalias.append("Pico anómalo de uso de CPU")
            
            # Detectar uso de memoria creciente
            if len(self.historial_memoria) > 10:
                memoria_reciente = sum(self.historial_memoria[-5:]) / 5
                memoria_anterior = sum(self.historial_memoria[-10:-5]) / 5
                if memoria_reciente > memoria_anterior * 1.5:
                    anomalias.append("Crecimiento anómalo de memoria")
        
        return anomalias
    
    def generar_resumen(self) -> Dict[str, Any]:
        """Generar resumen de estadísticas."""
        return {
            'pid': self.pid,
            'nombre': self.nombre,
            'total_muestras': self.total_muestras,
            'tiempo_monitoreado': self.tiempo_monitoreado,
            'cpu': {
                'promedio': round(self.cpu_promedio, 2),
                'maximo': round(self.cpu_maximo, 2),
                'minimo': round(self.cpu_minimo, 2)
            },
            'memoria': {
                'promedio_mb': round(self.memoria_promedio, 2),
                'maxima_mb': round(self.memoria_maxima, 2),
                'minima_mb': round(self.memoria_minima, 2)
            },
            'red': {
                'conexiones_promedio': round(self.conexiones_promedio, 2),
                'conexiones_maximas': self.conexiones_maximas
            },
            'archivos': {
                'promedio': round(self.archivos_promedio, 2),
                'maximo': self.archivos_maximos
            },
            'anomalias': self.detectar_anomalias()
        }


# Patrones comunes para clasificación de procesos
PATRONES_PROCESOS_SISTEMA = {
    'kernel': ['kthreadd', 'ksoftirqd', 'migration', 'rcu_', 'watchdog'],
    'sistema': ['systemd', 'init', 'kmod', 'udev', 'dbus'],
    'servicios': ['ssh', 'apache', 'nginx', 'mysql', 'postgres', 'redis'],
    'daemons': ['cron', 'rsyslog', 'networkd', 'resolved']
}

PATRONES_PROCESOS_SOSPECHOSOS = [
    'miner', 'bitcoin', 'monero', 'cryptonight',
    'xmrig', 'ccminer', 'ethminer',
    'keylogger', 'backdoor', 'rootkit',
    'malware', 'trojan', 'virus',
    'reverse_shell', 'bind_shell',
    'netcat', 'socat', 'ncat'
]

UBICACIONES_EJECUTABLES_SEGURAS = [
    '/bin/', '/sbin/', '/usr/bin/', '/usr/sbin/',
    '/usr/local/bin/', '/usr/local/sbin/',
    '/opt/', '/snap/'
]

UBICACIONES_EJECUTABLES_SOSPECHOSAS = [
    '/tmp/', '/var/tmp/', '/dev/shm/',
    '/home/', '/root/', '/var/www/',
    '/var/log/', '/etc/'
]
