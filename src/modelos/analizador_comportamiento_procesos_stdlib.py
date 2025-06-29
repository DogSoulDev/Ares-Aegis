#!/usr/bin/env python3
"""
Monitor de Procesos Simplificado usando solo biblioteca estándar
Implementación alternativa para análisis de comportamiento de procesos
sin dependencias externas.

Autor: DogSoulDev
Versión: 2.0.0
"""

import os
import glob
import time
import threading
import json
import re
import subprocess
from typing import Dict, List, Optional, Any, Set, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from enum import Enum


class TipoComportamiento(Enum):
    """Tipos de comportamiento de procesos."""
    NORMAL = "normal"
    SOSPECHOSO = "sospechoso"
    MALICIOSO = "malicioso"
    DESCONOCIDO = "desconocido"


class CategoriaEvento(Enum):
    """Categorías de eventos de proceso."""
    CREACION = "creacion"
    TERMINACION = "terminacion"
    RED = "red"
    ARCHIVO = "archivo"
    MEMORIA = "memoria"
    CPU = "cpu"
    SYSCALL = "syscall"
    PRIVILEGIOS = "privilegios"


@dataclass
class EventoProceso:
    """Representa un evento de comportamiento de proceso."""
    timestamp: datetime
    pid: int
    nombre_proceso: str
    categoria: CategoriaEvento
    accion: str
    detalles: Dict[str, Any]
    riesgo: int = 0  # 0-100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el evento a diccionario."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['categoria'] = self.categoria.value
        return data


@dataclass
class ProcesoProcfs:
    """Información de proceso obtenida de /proc."""
    pid: int
    nombre: str
    comando: str
    ppid: int
    usuario: str
    estado: str
    cpu_time: float
    memoria_kb: int
    timestamp_lectura: datetime
    
    @classmethod
    def desde_procfs(cls, pid: int) -> Optional['ProcesoProcfs']:
        """Crea instancia leyendo de /proc/[pid]/."""
        try:
            # Leer información básica
            with open(f'/proc/{pid}/stat', 'r') as f:
                stat_data = f.read().split()
            
            nombre = stat_data[1].strip('()')
            ppid = int(stat_data[3])
            estado = stat_data[2]
            
            # Tiempo de CPU (user + system)
            utime = int(stat_data[13])
            stime = int(stat_data[14]) 
            cpu_time = (utime + stime) / 100.0  # Convertir de clock ticks a segundos
            
            # Memoria (RSS en páginas * tamaño de página)
            rss_pages = int(stat_data[23])
            memoria_kb = rss_pages * 4  # Asumiendo páginas de 4KB
            
            # Leer comando completo
            try:
                with open(f'/proc/{pid}/cmdline', 'r') as f:
                    cmdline = f.read().replace('\x00', ' ').strip()
                if not cmdline:
                    cmdline = f"[{nombre}]"
            except:
                cmdline = f"[{nombre}]"
            
            # Obtener usuario (aproximado via stat del directorio)
            try:
                stat_info = os.stat(f'/proc/{pid}')
                uid = stat_info.st_uid
                # Intentar resolver nombre de usuario
                try:
                    import pwd
                    usuario = pwd.getpwuid(uid).pw_name
                except:
                    usuario = str(uid)
            except:
                usuario = "unknown"
            
            return cls(
                pid=pid,
                nombre=nombre,
                comando=cmdline,
                ppid=ppid,
                usuario=usuario,
                estado=estado,
                cpu_time=cpu_time,
                memoria_kb=memoria_kb,
                timestamp_lectura=datetime.now()
            )
            
        except (FileNotFoundError, PermissionError, ValueError, IndexError):
            return None


@dataclass
class PerfilProceso:
    """Perfil de comportamiento de un proceso."""
    pid: int
    nombre: str
    comando: str
    ppid: int
    usuario: str
    timestamp_inicio: datetime
    eventos: List[EventoProceso]
    puntuacion_riesgo: float = 0.0
    comportamiento: TipoComportamiento = TipoComportamiento.DESCONOCIDO
    conexiones_red: Optional[List[Dict[str, Any]]] = None
    archivos_accedidos: Optional[Set[str]] = None
    consumo_recursos: Optional[Dict[str, float]] = None
    syscalls_sospechosas: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.conexiones_red is None:
            self.conexiones_red = []
        if self.archivos_accedidos is None:
            self.archivos_accedidos = set()
        if self.consumo_recursos is None:
            self.consumo_recursos = {}
        if self.syscalls_sospechosas is None:
            self.syscalls_sospechosas = []
    
    def agregar_evento(self, evento: EventoProceso):
        """Agrega un evento al perfil del proceso."""
        self.eventos.append(evento)
        # Mantener solo los últimos 1000 eventos
        if len(self.eventos) > 1000:
            self.eventos = self.eventos[-1000:]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el perfil a diccionario."""
        return {
            'pid': self.pid,
            'nombre': self.nombre,
            'comando': self.comando,
            'ppid': self.ppid,
            'usuario': self.usuario,
            'timestamp_inicio': self.timestamp_inicio.isoformat(),
            'puntuacion_riesgo': self.puntuacion_riesgo,
            'comportamiento': self.comportamiento.value,
            'total_eventos': len(self.eventos),
            'conexiones_red': len(self.conexiones_red) if self.conexiones_red else 0,
            'archivos_accedidos': len(self.archivos_accedidos) if self.archivos_accedidos else 0,
            'consumo_recursos': self.consumo_recursos or {},
            'syscalls_sospechosas': len(self.syscalls_sospechosas) if self.syscalls_sospechosas else 0
        }


class DetectorPatrones:
    """Detector de patrones sospechosos en comportamiento de procesos."""
    
    def __init__(self):
        """Inicializa el detector de patrones."""
        self.patrones_sospechosos = self._cargar_patrones_sospechosos()
        self.umbrales = {
            'conexiones_por_minuto': 50,
            'archivos_por_minuto': 100,
            'cpu_porcentaje': 80,
            'memoria_mb': 1024,
            'procesos_hijos': 20,
            'syscalls_sospechosas': 10
        }
    
    def _cargar_patrones_sospechosos(self) -> Dict[str, Any]:
        """Carga patrones conocidos de comportamiento sospechoso."""
        return {
            'nombres_sospechosos': [
                r'.*\.tmp\.\w+$',
                r'^[a-f0-9]{8,}$',
                r'.*\.(scr|pif|bat|cmd|com|exe)$',
                r'svchost.*\.exe$',
                r'explorer.*\.exe$',
                r'chrome.*\.exe$',
                r'firefox.*\.exe$'
            ],
            'comandos_sospechosos': [
                r'powershell.*-enc.*',
                r'cmd.*\/c.*echo.*',
                r'wget.*http.*',
                r'curl.*http.*',
                r'nc\s+-l.*',
                r'ncat\s+-l.*',
                r'python.*-c.*',
                r'perl.*-e.*',
                r'sh\s+-c.*',
                r'bash\s+-c.*'
            ],
            'rutas_sospechosas': [
                '/tmp/',
                '/var/tmp/',
                '/dev/shm/',
                '/home/.*/.cache/',
                '/home/.*/Downloads/',
                r'/proc/\d+/fd/',
                r'/sys/.*'
            ],
            'conexiones_sospechosas': [
                'irc.',
                '.onion',
                'pastebin.',
                'raw.githubusercontent.',
                r'\d+\.\d+\.\d+\.\d+',
            ],
            'syscalls_peligrosas': [
                'ptrace', 'mprotect', 'mmap', 'execve', 'fork', 'clone',
                'setuid', 'setgid', 'chmod', 'chown', 'mount', 'umount',
                'delete_module', 'init_module'
            ]
        }
    
    def analizar_nombre_proceso(self, nombre: str, comando: str) -> int:
        """Analiza el nombre y comando del proceso."""
        riesgo = 0
        
        for patron in self.patrones_sospechosos['nombres_sospechosos']:
            if re.search(patron, nombre, re.IGNORECASE):
                riesgo += 30
        
        for patron in self.patrones_sospechosos['comandos_sospechosos']:
            if re.search(patron, comando, re.IGNORECASE):
                riesgo += 40
        
        for patron in self.patrones_sospechosos['rutas_sospechosas']:
            if re.search(patron, comando, re.IGNORECASE):
                riesgo += 25
        
        return min(riesgo, 100)
    
    def analizar_conexiones_red(self, conexiones: List[Dict[str, Any]]) -> int:
        """Analiza las conexiones de red del proceso."""
        riesgo = 0
        
        for conexion in conexiones:
            destino = conexion.get('destino', '')
            puerto = conexion.get('puerto', 0)
            
            for patron in self.patrones_sospechosos['conexiones_sospechosas']:
                if re.search(patron, destino, re.IGNORECASE):
                    riesgo += 20
            
            puertos_sospechosos = [1234, 4444, 5555, 6666, 31337, 12345]
            if puerto in puertos_sospechosos:
                riesgo += 30
            
            if puerto > 50000:
                riesgo += 10
        
        if len(conexiones) > 20:
            riesgo += 20
        
        return min(riesgo, 100)
    
    def analizar_acceso_archivos(self, archivos: Set[str]) -> int:
        """Analiza el acceso a archivos del proceso."""
        riesgo = 0
        
        for archivo in archivos:
            for patron in self.patrones_sospechosos['rutas_sospechosas']:
                if re.search(patron, archivo, re.IGNORECASE):
                    riesgo += 15
            
            archivos_criticos = [
                '/etc/passwd', '/etc/shadow', '/etc/sudoers',
                '/boot/', '/sys/kernel/', '/proc/sys/'
            ]
            
            for critico in archivos_criticos:
                if archivo.startswith(critico):
                    riesgo += 25
        
        if len(archivos) > 100:
            riesgo += 15
        
        return min(riesgo, 100)
    
    def analizar_consumo_recursos(self, recursos: Dict[str, float]) -> int:
        """Analiza el consumo de recursos del proceso."""
        riesgo = 0
        
        cpu = recursos.get('cpu_percent', 0)
        memoria = recursos.get('memory_mb', 0)
        procesos_hijos = recursos.get('num_children', 0)
        
        if cpu > self.umbrales['cpu_porcentaje']:
            riesgo += 20
        
        if memoria > self.umbrales['memoria_mb']:
            riesgo += 15
        
        if procesos_hijos > self.umbrales['procesos_hijos']:
            riesgo += 30
        
        return min(riesgo, 100)


class MonitorProcesos:
    """Monitor de procesos usando /proc filesystem."""
    
    def __init__(self, intervalo: float = 2.0):
        """
        Inicializa el monitor de procesos.
        
        Args:
            intervalo: Intervalo de monitoreo en segundos
        """
        self.intervalo = intervalo
        self.activo = False
        self.procesos_monitoreados: Dict[int, PerfilProceso] = {}
        self.detector = DetectorPatrones()
        self.callbacks_evento: List[Callable] = []
        self.lock = threading.Lock()
        self.hilo_monitor = None
        self.procesos_conocidos: Set[int] = set()
        self.stats_cpu_anterior: Dict[int, float] = {}
    
    def agregar_callback_evento(self, callback: Callable):
        """Agrega un callback para eventos de proceso."""
        self.callbacks_evento.append(callback)
    
    def iniciar_monitoreo(self):
        """Inicia el monitoreo de procesos."""
        if self.activo:
            return
        
        self.activo = True
        self.hilo_monitor = threading.Thread(target=self._monitorear_procesos, daemon=True)
        self.hilo_monitor.start()
    
    def detener_monitoreo(self):
        """Detiene el monitoreo de procesos."""
        self.activo = False
        if self.hilo_monitor and self.hilo_monitor.is_alive():
            self.hilo_monitor.join(timeout=5)
    
    def _obtener_pids_activos(self) -> Set[int]:
        """Obtiene lista de PIDs activos desde /proc."""
        pids = set()
        try:
            for entrada in os.listdir('/proc'):
                if entrada.isdigit():
                    pids.add(int(entrada))
        except:
            pass
        return pids
    
    def _monitorear_procesos(self):
        """Loop principal de monitoreo."""
        while self.activo:
            try:
                # Obtener procesos actuales
                procesos_actuales = self._obtener_pids_activos()
                
                # Procesar cada proceso activo
                for pid in procesos_actuales:
                    try:
                        proceso_info = ProcesoProcfs.desde_procfs(pid)
                        if proceso_info is None:
                            continue
                        
                        # Proceso nuevo
                        if pid not in self.procesos_conocidos:
                            self._procesar_proceso_nuevo(proceso_info)
                        
                        # Actualizar proceso existente
                        elif pid in self.procesos_monitoreados:
                            self._actualizar_proceso(proceso_info)
                    
                    except Exception as e:
                        continue
                
                # Detectar procesos terminados
                procesos_terminados = self.procesos_conocidos - procesos_actuales
                for pid in procesos_terminados:
                    self._procesar_proceso_terminado(pid)
                
                self.procesos_conocidos = procesos_actuales
                time.sleep(self.intervalo)
                
            except Exception as e:
                print(f"Error en monitoreo: {e}")
                time.sleep(self.intervalo)
    
    def _procesar_proceso_nuevo(self, proceso_info: ProcesoProcfs):
        """Procesa un proceso recién detectado."""
        try:
            pid = proceso_info.pid
            
            # Crear perfil del proceso
            perfil = PerfilProceso(
                pid=pid,
                nombre=proceso_info.nombre,
                comando=proceso_info.comando,
                ppid=proceso_info.ppid,
                usuario=proceso_info.usuario,
                timestamp_inicio=proceso_info.timestamp_lectura,
                eventos=[]
            )
            
            # Análisis inicial
            riesgo_nombre = self.detector.analizar_nombre_proceso(
                proceso_info.nombre, 
                proceso_info.comando
            )
            
            if riesgo_nombre > 0:
                perfil.puntuacion_riesgo += riesgo_nombre
            
            with self.lock:
                self.procesos_monitoreados[pid] = perfil
            
            # Crear evento de creación
            evento = EventoProceso(
                timestamp=datetime.now(),
                pid=pid,
                nombre_proceso=proceso_info.nombre,
                categoria=CategoriaEvento.CREACION,
                accion="proceso_iniciado",
                detalles={
                    'comando': proceso_info.comando,
                    'ppid': proceso_info.ppid,
                    'usuario': proceso_info.usuario,
                    'riesgo_inicial': riesgo_nombre
                },
                riesgo=riesgo_nombre
            )
            
            perfil.agregar_evento(evento)
            self._notificar_evento(evento)
            
        except Exception as e:
            print(f"Error procesando proceso nuevo {proceso_info.pid}: {e}")
    
    def _actualizar_proceso(self, proceso_info: ProcesoProcfs):
        """Actualiza información de un proceso existente."""
        try:
            pid = proceso_info.pid
            
            with self.lock:
                if pid not in self.procesos_monitoreados:
                    return
                
                perfil = self.procesos_monitoreados[pid]
            
            # Calcular uso de CPU (aproximado)
            cpu_percent = 0.0
            if pid in self.stats_cpu_anterior:
                diff_cpu = proceso_info.cpu_time - self.stats_cpu_anterior[pid]
                # Aproximación: diff_cpu / intervalo * 100
                cpu_percent = min((diff_cpu / self.intervalo) * 100, 100)
            
            self.stats_cpu_anterior[pid] = proceso_info.cpu_time
            
            # Actualizar consumo de recursos
            perfil.consumo_recursos = {
                'cpu_percent': cpu_percent,
                'memory_mb': proceso_info.memoria_kb / 1024,
                'num_children': self._contar_procesos_hijos(pid)
            }
            
            # Analizar consumo de recursos
            riesgo_recursos = self.detector.analizar_consumo_recursos(perfil.consumo_recursos)
            
            if riesgo_recursos > 20:
                evento = EventoProceso(
                    timestamp=datetime.now(),
                    pid=pid,
                    nombre_proceso=perfil.nombre,
                    categoria=CategoriaEvento.CPU if cpu_percent > 50 else CategoriaEvento.MEMORIA,
                    accion="alto_consumo_recursos",
                    detalles=perfil.consumo_recursos,
                    riesgo=riesgo_recursos
                )
                
                perfil.agregar_evento(evento)
                self._notificar_evento(evento)
            
            # Analizar conexiones de red (usando /proc/[pid]/net/tcp)
            conexiones = self._obtener_conexiones_red(pid)
            if conexiones:
                perfil.conexiones_red = conexiones
                riesgo_red = self.detector.analizar_conexiones_red(conexiones)
                
                if riesgo_red > 15:
                    evento = EventoProceso(
                        timestamp=datetime.now(),
                        pid=pid,
                        nombre_proceso=perfil.nombre,
                        categoria=CategoriaEvento.RED,
                        accion="conexiones_sospechosas",
                        detalles={'conexiones': conexiones},
                        riesgo=riesgo_red
                    )
                    
                    perfil.agregar_evento(evento)
                    self._notificar_evento(evento)
            
            # Analizar archivos abiertos
            archivos = self._obtener_archivos_abiertos(pid)
            if archivos:
                if perfil.archivos_accedidos is None:
                    perfil.archivos_accedidos = set()
                
                archivos_nuevos = archivos - perfil.archivos_accedidos
                perfil.archivos_accedidos.update(archivos)
                
                if archivos_nuevos:
                    riesgo_archivos = self.detector.analizar_acceso_archivos(archivos_nuevos)
                    
                    if riesgo_archivos > 10:
                        evento = EventoProceso(
                            timestamp=datetime.now(),
                            pid=pid,
                            nombre_proceso=perfil.nombre,
                            categoria=CategoriaEvento.ARCHIVO,
                            accion="acceso_archivos_sospechoso",
                            detalles={'archivos_nuevos': list(archivos_nuevos)},
                            riesgo=riesgo_archivos
                        )
                        
                        perfil.agregar_evento(evento)
                        self._notificar_evento(evento)
            
            # Actualizar puntuación de riesgo total
            self._actualizar_puntuacion_riesgo(perfil)
            
        except Exception as e:
            print(f"Error actualizando proceso {proceso_info.pid}: {e}")
    
    def _contar_procesos_hijos(self, ppid: int) -> int:
        """Cuenta procesos hijos de un proceso padre."""
        contador = 0
        try:
            for entrada in os.listdir('/proc'):
                if entrada.isdigit():
                    try:
                        with open(f'/proc/{entrada}/stat', 'r') as f:
                            stat_data = f.read().split()
                            if len(stat_data) > 3 and int(stat_data[3]) == ppid:
                                contador += 1
                    except:
                        continue
        except:
            pass
        return contador
    
    def _obtener_conexiones_red(self, pid: int) -> List[Dict[str, Any]]:
        """Obtiene conexiones de red del proceso."""
        conexiones = []
        try:
            # Leer archivos descriptores para encontrar sockets
            fd_path = f'/proc/{pid}/fd'
            if os.path.exists(fd_path):
                for fd in os.listdir(fd_path):
                    try:
                        link = os.readlink(f'{fd_path}/{fd}')
                        if 'socket:' in link:
                            # Extraer información del socket si es posible
                            # Esto es una simplificación
                            conexiones.append({
                                'destino': 'unknown',
                                'puerto': 0,
                                'estado': 'ESTABLISHED',
                                'tipo': 'TCP'
                            })
                    except:
                        continue
        except:
            pass
        
        return conexiones
    
    def _obtener_archivos_abiertos(self, pid: int) -> Set[str]:
        """Obtiene archivos abiertos por el proceso."""
        archivos = set()
        try:
            fd_path = f'/proc/{pid}/fd'
            if os.path.exists(fd_path):
                for fd in os.listdir(fd_path):
                    try:
                        link = os.readlink(f'{fd_path}/{fd}')
                        if link.startswith('/') and not link.startswith('/dev'):
                            archivos.add(link)
                    except:
                        continue
        except:
            pass
        
        return archivos
    
    def _procesar_proceso_terminado(self, pid: int):
        """Procesa un proceso que ha terminado."""
        with self.lock:
            if pid in self.procesos_monitoreados:
                perfil = self.procesos_monitoreados[pid]
                
                evento = EventoProceso(
                    timestamp=datetime.now(),
                    pid=pid,
                    nombre_proceso=perfil.nombre,
                    categoria=CategoriaEvento.TERMINACION,
                    accion="proceso_terminado",
                    detalles={
                        'duracion_segundos': (datetime.now() - perfil.timestamp_inicio).total_seconds(),
                        'total_eventos': len(perfil.eventos),
                        'puntuacion_riesgo_final': perfil.puntuacion_riesgo
                    },
                    riesgo=0
                )
                
                perfil.agregar_evento(evento)
                self._notificar_evento(evento)
                
                # Eliminar procesos de bajo riesgo para ahorrar memoria
                if perfil.puntuacion_riesgo < 30:
                    del self.procesos_monitoreados[pid]
            
            # Limpiar stats de CPU
            if pid in self.stats_cpu_anterior:
                del self.stats_cpu_anterior[pid]
    
    def _actualizar_puntuacion_riesgo(self, perfil: PerfilProceso):
        """Actualiza la puntuación de riesgo del proceso."""
        riesgo_total = 0
        
        # Analizar eventos recientes (últimos 5 minutos)
        hace_5_min = datetime.now() - timedelta(minutes=5)
        eventos_recientes = [e for e in perfil.eventos if e.timestamp > hace_5_min]
        
        if eventos_recientes:
            riesgo_total = sum(e.riesgo for e in eventos_recientes) / len(eventos_recientes)
        
        # Análisis adicional basado en patrones
        riesgo_nombre = self.detector.analizar_nombre_proceso(perfil.nombre, perfil.comando)
        riesgo_conexiones = self.detector.analizar_conexiones_red(perfil.conexiones_red or [])
        riesgo_archivos = self.detector.analizar_acceso_archivos(perfil.archivos_accedidos or set())
        riesgo_recursos = self.detector.analizar_consumo_recursos(perfil.consumo_recursos or {})
        
        # Calcular puntuación final
        perfil.puntuacion_riesgo = min(
            (riesgo_total + riesgo_nombre + riesgo_conexiones + riesgo_archivos + riesgo_recursos) / 5,
            100
        )
        
        # Determinar comportamiento
        if perfil.puntuacion_riesgo >= 70:
            perfil.comportamiento = TipoComportamiento.MALICIOSO
        elif perfil.puntuacion_riesgo >= 40:
            perfil.comportamiento = TipoComportamiento.SOSPECHOSO
        else:
            perfil.comportamiento = TipoComportamiento.NORMAL
    
    def _notificar_evento(self, evento: EventoProceso):
        """Notifica un evento a todos los callbacks registrados."""
        for callback in self.callbacks_evento:
            try:
                callback(evento)
            except Exception as e:
                print(f"Error en callback de evento: {e}")
    
    def obtener_procesos_sospechosos(self, umbral_riesgo: float = 40) -> List[PerfilProceso]:
        """Obtiene una lista de procesos sospechosos."""
        with self.lock:
            return [
                perfil for perfil in self.procesos_monitoreados.values()
                if perfil.puntuacion_riesgo >= umbral_riesgo
            ]
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas del monitoreo."""
        with self.lock:
            total_procesos = len(self.procesos_monitoreados)
            procesos_por_comportamiento = defaultdict(int)
            
            for perfil in self.procesos_monitoreados.values():
                procesos_por_comportamiento[perfil.comportamiento.value] += 1
            
            return {
                'total_procesos': total_procesos,
                'por_comportamiento': dict(procesos_por_comportamiento),
                'procesos_alto_riesgo': len([p for p in self.procesos_monitoreados.values() if p.puntuacion_riesgo >= 70]),
                'procesos_sospechosos': len([p for p in self.procesos_monitoreados.values() if p.puntuacion_riesgo >= 40]),
                'timestamp': datetime.now().isoformat()
            }


class AnalizadorComportamientoProcesos:
    """Sistema principal de análisis de comportamiento de procesos."""
    
    def __init__(self, siem=None):
        """
        Inicializa el analizador de comportamiento.
        
        Args:
            siem: Sistema SIEM para logging (opcional)
        """
        self.siem = siem
        self.monitor = MonitorProcesos()
        self.historial_eventos: deque = deque(maxlen=10000)
        self.alertas_activas: List[Dict[str, Any]] = []
        
        # Registrar callback para eventos
        self.monitor.agregar_callback_evento(self._procesar_evento)
    
    def iniciar_analisis(self):
        """Inicia el análisis de comportamiento."""
        self.monitor.iniciar_monitoreo()
        
        if self.siem:
            self.siem.log_evento('INFO', 'analizador_comportamiento', 
                               'Análisis de comportamiento de procesos iniciado')
    
    def detener_analisis(self):
        """Detiene el análisis de comportamiento."""
        self.monitor.detener_monitoreo()
        
        if self.siem:
            self.siem.log_evento('INFO', 'analizador_comportamiento', 
                               'Análisis de comportamiento de procesos detenido')
    
    def _procesar_evento(self, evento: EventoProceso):
        """Procesa un evento de proceso."""
        # Agregar al historial
        self.historial_eventos.append(evento)
        
        # Generar alerta si es de alto riesgo
        if evento.riesgo >= 50:
            alerta = {
                'id': f"comportamiento_{evento.pid}_{int(evento.timestamp.timestamp())}",
                'timestamp': evento.timestamp.isoformat(),
                'tipo': 'comportamiento_sospechoso',
                'severidad': 'alta' if evento.riesgo >= 70 else 'media',
                'proceso': {
                    'pid': evento.pid,
                    'nombre': evento.nombre_proceso,
                    'categoria': evento.categoria.value,
                    'accion': evento.accion
                },
                'detalles': evento.detalles,
                'riesgo': evento.riesgo
            }
            
            self.alertas_activas.append(alerta)
            
            if self.siem:
                self.siem.log_evento('ALERT', 'analizador_comportamiento', 
                                   f'Comportamiento sospechoso detectado: {evento.nombre_proceso} (PID {evento.pid})', 
                                   alerta)
    
    def obtener_procesos_sospechosos(self, umbral_riesgo: float = 40) -> List[Dict[str, Any]]:
        """Obtiene procesos con comportamiento sospechoso."""
        procesos = self.monitor.obtener_procesos_sospechosos(umbral_riesgo)
        return [proceso.to_dict() for proceso in procesos]
    
    def obtener_alertas_recientes(self, horas: int = 24) -> List[Dict[str, Any]]:
        """Obtiene alertas recientes."""
        limite_tiempo = datetime.now() - timedelta(hours=horas)
        
        alertas_recientes = []
        for alerta in self.alertas_activas:
            timestamp_alerta = datetime.fromisoformat(alerta['timestamp'])
            if timestamp_alerta > limite_tiempo:
                alertas_recientes.append(alerta)
        
        return alertas_recientes
    
    def generar_reporte_comportamiento(self, horas: int = 24) -> Dict[str, Any]:
        """Genera un reporte de comportamiento de procesos."""
        limite_tiempo = datetime.now() - timedelta(hours=horas)
        
        # Filtrar eventos recientes
        eventos_recientes = [
            evento for evento in self.historial_eventos
            if evento.timestamp > limite_tiempo
        ]
        
        # Estadísticas por categoría
        eventos_por_categoria = defaultdict(int)
        eventos_por_riesgo = defaultdict(int)
        
        for evento in eventos_recientes:
            eventos_por_categoria[evento.categoria.value] += 1
            
            if evento.riesgo >= 70:
                eventos_por_riesgo['alto'] += 1
            elif evento.riesgo >= 40:
                eventos_por_riesgo['medio'] += 1
            else:
                eventos_por_riesgo['bajo'] += 1
        
        # Procesos más activos
        procesos_activos = defaultdict(int)
        for evento in eventos_recientes:
            procesos_activos[f"{evento.nombre_proceso} (PID {evento.pid})"] += 1
        
        procesos_top = sorted(procesos_activos.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'periodo_analisis': {
                'inicio': limite_tiempo.isoformat(),
                'fin': datetime.now().isoformat(),
                'horas': horas
            },
            'resumen': {
                'total_eventos': len(eventos_recientes),
                'procesos_monitoreados': self.monitor.obtener_estadisticas()['total_procesos'],
                'alertas_generadas': len(self.obtener_alertas_recientes(horas))
            },
            'eventos_por_categoria': dict(eventos_por_categoria),
            'eventos_por_riesgo': dict(eventos_por_riesgo),
            'procesos_mas_activos': procesos_top,
            'procesos_sospechosos': self.obtener_procesos_sospechosos(),
            'alertas_recientes': self.obtener_alertas_recientes(horas),
            'timestamp_reporte': datetime.now().isoformat()
        }
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas generales del análisis."""
        stats_monitor = self.monitor.obtener_estadisticas()
        
        return {
            'monitor': stats_monitor,
            'historial': {
                'total_eventos': len(self.historial_eventos),
                'alertas_activas': len(self.alertas_activas)
            },
            'timestamp': datetime.now().isoformat()
        }
