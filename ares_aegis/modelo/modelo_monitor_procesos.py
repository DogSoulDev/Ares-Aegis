#!/usr/bin/env python3
"""
Ares Aegis - Monitor de Procesos Principal
Monitor avanzado de procesos del sistema - Los Mil Ojos de Argos

Creado por DogSoulDev
Versión: 4.0.0 - Arquitectura MVC Optimizada
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
from typing import Dict, List, Any, Optional, Set
from collections import defaultdict, deque
from ..utils.utils_ayuda_logging import configurar_logger_modulo
from .modelo_monitor_procesos_utils import (
    TipoProceso, EstadoProceso, NivelRiesgoProceso, TipoAmenaza,
    ProcesoInfo, AlertaProceso, EstadisticasProceso,
    PATRONES_PROCESOS_SISTEMA, PATRONES_PROCESOS_SOSPECHOSOS,
    UBICACIONES_EJECUTABLES_SEGURAS, UBICACIONES_EJECUTABLES_SOSPECHOSAS
)

try:
    import pwd
    import grp
    import resource
except ImportError:
    pwd = grp = resource = None


class AnalizadorComportamientoProcesos:
    """Analizador de comportamiento de procesos usando técnicas de ML básicas."""
    
    def __init__(self):
        self.logger = configurar_logger_modulo(__name__)
        self.estadisticas_procesos = {}
        self.patrones_normales = {}
        self.alertas_generadas = deque(maxlen=1000)
        
    def analizar_proceso(self, proceso: ProcesoInfo) -> List[AlertaProceso]:
        """Analizar un proceso y generar alertas si es necesario."""
        alertas = []
        
        # Actualizar estadísticas
        if proceso.pid not in self.estadisticas_procesos:
            self.estadisticas_procesos[proceso.pid] = EstadisticasProceso(
                pid=proceso.pid, nombre=proceso.nombre
            )
        
        stats = self.estadisticas_procesos[proceso.pid]
        stats.actualizar(proceso)
        
        # Análisis de comportamiento
        alertas.extend(self._analizar_uso_recursos(proceso, stats))
        alertas.extend(self._analizar_patrones_sospechosos(proceso))
        alertas.extend(self._analizar_ubicacion_ejecutable(proceso))
        
        return alertas
    
    def _analizar_uso_recursos(self, proceso: ProcesoInfo, stats: EstadisticasProceso) -> List[AlertaProceso]:
        """Analizar el uso de recursos del proceso."""
        alertas = []
        
        # CPU alto por tiempo prolongado
        if proceso.cpu_percent > 90 and stats.total_muestras > 5:
            if stats.cpu_promedio > 80:
                alertas.append(AlertaProceso(
                    timestamp=datetime.now(),
                    proceso=proceso,
                    tipo_alerta="CPU_USAGE_HIGH",
                    nivel_severidad=NivelRiesgoProceso.MEDIO,
                    descripcion=f"Uso de CPU persistentemente alto: {proceso.cpu_percent:.1f}%",
                    evidencia={'cpu_promedio': stats.cpu_promedio, 'muestras': stats.total_muestras}
                ))
        
        # Memoria excesiva
        memoria_mb = proceso.obtener_memoria_mb()
        if memoria_mb > 1024:  # > 1GB
            alertas.append(AlertaProceso(
                timestamp=datetime.now(),
                proceso=proceso,
                tipo_alerta="MEMORY_USAGE_HIGH",
                nivel_severidad=NivelRiesgoProceso.BAJO,
                descripcion=f"Uso de memoria alto: {memoria_mb:.1f} MB",
                evidencia={'memoria_mb': memoria_mb}
            ))
        
        return alertas
    
    def _analizar_patrones_sospechosos(self, proceso: ProcesoInfo) -> List[AlertaProceso]:
        """Analizar patrones sospechosos en el proceso."""
        alertas = []
        
        # Nombres sospechosos
        nombre_lower = proceso.nombre.lower()
        for patron in PATRONES_PROCESOS_SOSPECHOSOS:
            if patron in nombre_lower:
                alertas.append(AlertaProceso(
                    timestamp=datetime.now(),
                    proceso=proceso,
                    tipo_alerta="SUSPICIOUS_PROCESS_NAME",
                    nivel_severidad=NivelRiesgoProceso.ALTO,
                    descripcion=f"Nombre de proceso sospechoso detectado: {proceso.nombre}",
                    evidencia={'patron_detectado': patron}
                ))
        
        return alertas
    
    def _analizar_ubicacion_ejecutable(self, proceso: ProcesoInfo) -> List[AlertaProceso]:
        """Analizar la ubicación del ejecutable."""
        alertas = []
        
        if not proceso.ruta_ejecutable:
            return alertas
        
        # Verificar ubicaciones sospechosas
        for ubicacion in UBICACIONES_EJECUTABLES_SOSPECHOSAS:
            if ubicacion in proceso.ruta_ejecutable:
                alertas.append(AlertaProceso(
                    timestamp=datetime.now(),
                    proceso=proceso,
                    tipo_alerta="SUSPICIOUS_EXECUTABLE_LOCATION",
                    nivel_severidad=NivelRiesgoProceso.MEDIO,
                    descripcion=f"Ejecutable en ubicación sospechosa: {proceso.ruta_ejecutable}",
                    evidencia={'ubicacion': ubicacion}
                ))
                break
        
        return alertas


class MonitorProcesos:
    """Monitor avanzado de procesos del sistema - Los Mil Ojos de Argos."""
    
    def __init__(self, siem=None):
        """Inicializa el monitor de procesos."""
        self.logger = configurar_logger_modulo(__name__)
        self.siem = siem
        
        # Estado del monitor
        self.monitoreando = False
        self.hilo_monitor = None
        self.intervalo_monitoreo = 5.0
        self.lock = threading.Lock()
        
        # Componentes
        self.analizador = AnalizadorComportamientoProcesos()
        
        # Cache y estado
        self.procesos_activos = {}
        self.procesos_terminados = deque(maxlen=100)
        self.baseline_establecida = False
        
        # Métricas
        self.total_procesos_analizados = 0
        self.alertas_generadas = 0
        self.ultima_actualizacion = None
        
        self.logger.info(" Monitor de Procesos inicializado")
    
    def iniciar_monitoreo(self) -> bool:
        """Iniciar el monitoreo de procesos."""
        with self.lock:
            if self.monitoreando:
                self.logger.warning("El monitoreo ya está activo")
                return False
            
            self.monitoreando = True
            self.hilo_monitor = threading.Thread(
                target=self._bucle_monitoreo,
                daemon=True,
                name="MonitorProcesos"
            )
            self.hilo_monitor.start()
            
            self.logger.info(" Monitoreo de procesos iniciado")
            return True
    
    def detener_monitoreo(self) -> bool:
        """Detener el monitoreo de procesos."""
        with self.lock:
            if not self.monitoreando:
                return False
            
            self.monitoreando = False
            if self.hilo_monitor:
                self.hilo_monitor.join(timeout=2.0)
            
            self.logger.info(" Monitoreo de procesos detenido")
            return True
    
    def _bucle_monitoreo(self):
        """Bucle principal de monitoreo."""
        while self.monitoreando:
            try:
                inicio = time.time()
                
                # Obtener procesos actuales
                procesos_actuales = self.obtener_procesos_sistema()
                
                # Analizar cada proceso
                for proceso in procesos_actuales:
                    alertas = self.analizador.analizar_proceso(proceso)
                    
                    # Procesar alertas
                    for alerta in alertas:
                        self._procesar_alerta(alerta)
                
                # Actualizar estado
                self.procesos_activos = {p.pid: p for p in procesos_actuales}
                self.total_procesos_analizados += len(procesos_actuales)
                self.ultima_actualizacion = datetime.now()
                
                # Pausa calculada
                tiempo_transcurrido = time.time() - inicio
                tiempo_espera = max(0, self.intervalo_monitoreo - tiempo_transcurrido)
                time.sleep(tiempo_espera)
                
            except Exception as e:
                self.logger.error(f"Error en bucle de monitoreo: {e}")
                time.sleep(2)
    
    def obtener_procesos_sistema(self) -> List[ProcesoInfo]:
        """Obtener lista de procesos del sistema usando ps."""
        procesos = []
        
        try:
            # Usar ps para obtener información de procesos
            cmd = ['ps', 'axo', 'pid,ppid,comm,cmd,user,stat,%cpu,%mem,lstart']
            resultado = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if resultado.returncode != 0:
                self.logger.error("Error ejecutando ps")
                return procesos
            
            lineas = resultado.stdout.strip().split('\n')[1:]  # Skip header
            
            for linea in lineas:
                try:
                    proceso = self._parsear_linea_ps(linea)
                    if proceso:
                        procesos.append(proceso)
                except Exception as e:
                    self.logger.debug(f"Error parseando línea ps: {e}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error obteniendo procesos: {e}")
        
        return procesos
    
    def _parsear_linea_ps(self, linea: str) -> Optional[ProcesoInfo]:
        """Parsear una línea de salida de ps."""
        try:
            partes = linea.split(None, 8)
            if len(partes) < 8:
                return None
            
            pid = int(partes[0])
            ppid = int(partes[1])
            nombre = partes[2]
            usuario = partes[4]
            estado_str = partes[5]
            cpu = float(partes[6])
            mem = float(partes[7])
            
            # Parsear comando completo si está disponible
            cmd = partes[8] if len(partes) > 8 else nombre
            
            # Convertir estado
            estado = self._convertir_estado_proceso(estado_str)
            
            # Crear proceso
            proceso = ProcesoInfo(
                pid=pid,
                ppid=ppid,
                nombre=nombre,
                cmd=cmd,
                usuario=usuario,
                estado=estado,
                cpu_percent=cpu,
                memoria_rss=int(mem * 1024),  # Aproximación
                memoria_vms=0,
                tiempo_creacion=datetime.now(),  # Aproximación
                tipo=self._clasificar_proceso(nombre, cmd),
                ruta_ejecutable=self._obtener_ruta_ejecutable(pid)
            )
            
            return proceso
            
        except (ValueError, IndexError) as e:
            self.logger.debug(f"Error parseando proceso: {e}")
            return None
    
    def _convertir_estado_proceso(self, estado_str: str) -> EstadoProceso:
        """Convertir estado de proceso de ps a enum."""
        if not estado_str:
            return EstadoProceso.DESCONOCIDO
        
        primer_char = estado_str[0].upper()
        mapeo = {
            'R': EstadoProceso.RUNNING,
            'S': EstadoProceso.SLEEPING,
            'D': EstadoProceso.DISK_SLEEP,
            'T': EstadoProceso.STOPPED,
            'Z': EstadoProceso.ZOMBIE,
            'X': EstadoProceso.DEAD
        }
        
        return mapeo.get(primer_char, EstadoProceso.DESCONOCIDO)
    
    def _clasificar_proceso(self, nombre: str, cmd: str) -> TipoProceso:
        """Clasificar el tipo de proceso."""
        nombre_lower = nombre.lower()
        cmd_lower = cmd.lower()
        
        # Procesos del kernel
        if nombre.startswith('[') and nombre.endswith(']'):
            return TipoProceso.KERNEL
        
        # Buscar en patrones conocidos
        for tipo, patrones in PATRONES_PROCESOS_SISTEMA.items():
            for patron in patrones:
                if patron in nombre_lower or patron in cmd_lower:
                    if tipo == 'kernel':
                        return TipoProceso.KERNEL
                    elif tipo == 'sistema':
                        return TipoProceso.SISTEMA
                    elif tipo == 'servicios':
                        return TipoProceso.SERVICIO
                    elif tipo == 'daemons':
                        return TipoProceso.DAEMON
        
        return TipoProceso.USUARIO
    
    def _obtener_ruta_ejecutable(self, pid: int) -> Optional[str]:
        """Obtener la ruta del ejecutable de un proceso."""
        try:
            ruta_exe = f"/proc/{pid}/exe"
            if os.path.exists(ruta_exe):
                return os.readlink(ruta_exe)
        except (OSError, PermissionError):
            pass
        return None
    
    def _procesar_alerta(self, alerta: AlertaProceso):
        """Procesar una alerta generada."""
        self.alertas_generadas += 1
        
        # Registrar en SIEM si está disponible
        if self.siem:
            self.siem.registrar_evento({
                'tipo': 'alerta_proceso',
                'subtipo': alerta.tipo_alerta,
                'nivel': alerta.nivel_severidad.name,
                'proceso_pid': alerta.proceso.pid,
                'proceso_nombre': alerta.proceso.nombre,
                'usuario': alerta.proceso.usuario,
                'descripcion': alerta.descripcion,
                'evidencia': alerta.evidencia,
                'timestamp': alerta.timestamp.isoformat()
            })
        
        # Log según severidad
        if alerta.nivel_severidad.value >= NivelRiesgoProceso.ALTO.value:
            self.logger.warning(f" ALERTA CRÍTICA: {alerta.generar_mensaje_alerta()}")
        else:
            self.logger.info(f" Alerta: {alerta.tipo_alerta} - PID {alerta.proceso.pid}")
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtener estadísticas del monitor."""
        return {
            'monitoreando': self.monitoreando,
            'procesos_activos': len(self.procesos_activos),
            'total_analizados': self.total_procesos_analizados,
            'alertas_generadas': self.alertas_generadas,
            'ultima_actualizacion': self.ultima_actualizacion.isoformat() if self.ultima_actualizacion else None,
            'intervalo_monitoreo': self.intervalo_monitoreo
        }
    
    def obtener_procesos_sospechosos(self) -> List[ProcesoInfo]:
        """Obtener lista de procesos considerados sospechosos."""
        return [p for p in self.procesos_activos.values() if p.es_proceso_sospechoso()]
    
    def terminar_proceso(self, pid: int, forzar: bool = False) -> bool:
        """Terminar un proceso específico."""
        try:
            if forzar:
                # En sistemas Unix usar SIGKILL, en Windows usar taskkill /F
                try:
                    os.kill(pid, 9)  # SIGKILL es 9
                    self.logger.warning(f" Proceso {pid} terminado forzosamente")
                except (OSError, AttributeError):
                    subprocess.run(['taskkill', '/PID', str(pid), '/F'], check=True)
                    self.logger.warning(f" Proceso {pid} terminado forzosamente")
            else:
                # En sistemas Unix usar SIGTERM, en Windows usar taskkill normal
                try:
                    os.kill(pid, 15)  # SIGTERM es 15
                    self.logger.info(f" Proceso {pid} terminado")
                except (OSError, AttributeError):
                    subprocess.run(['taskkill', '/PID', str(pid)], check=True)
                    self.logger.info(f" Proceso {pid} terminado")
            return True
        except (OSError, PermissionError, subprocess.CalledProcessError) as e:
            self.logger.error(f"Error terminando proceso {pid}: {e}")
            return False
    
    def suspender_proceso(self, pid: int) -> bool:
        """Suspender un proceso específico."""
        try:
            try:
                os.kill(pid, 19)  # SIGSTOP es 19
                self.logger.info(f"⏸ Proceso {pid} suspendido")
                return True
            except (OSError, AttributeError):
                # En Windows usar pssuspend si está disponible
                try:
                    subprocess.run(['pssuspend', str(pid)], check=True)
                    self.logger.info(f"⏸ Proceso {pid} suspendido")
                    return True
                except (subprocess.CalledProcessError, FileNotFoundError):
                    self.logger.warning("Suspensión de procesos no soportada en esta plataforma")
                    return False
        except (OSError, PermissionError) as e:
            self.logger.error(f"Error suspendiendo proceso {pid}: {e}")
            return False
    
    def reanudar_proceso(self, pid: int) -> bool:
        """Reanudar un proceso suspendido."""
        try:
            try:
                os.kill(pid, 18)  # SIGCONT es 18
                self.logger.info(f" Proceso {pid} reanudado")
                return True
            except (OSError, AttributeError):
                # En Windows usar pssuspend si está disponible
                try:
                    subprocess.run(['pssuspend', '-r', str(pid)], check=True)
                    self.logger.info(f" Proceso {pid} reanudado")
                    return True
                except (subprocess.CalledProcessError, FileNotFoundError):
                    self.logger.warning("Reanudación de procesos no soportada en esta plataforma")
                    return False
        except (OSError, PermissionError) as e:
            self.logger.error(f"Error reanudando proceso {pid}: {e}")
            return False
