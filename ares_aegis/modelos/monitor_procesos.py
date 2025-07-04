#!/usr/bin/env python3
"""
Copyright (c) 2025 DogSoulDev (https://github.com/DogSoulDev)
Todos los derechos reservados. Este código es propietario y confidencial.

Monitor de Procesos
"""

import os
import time
import subprocess
import threading
import signal
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, NamedTuple
from ..utilidades.ayuda_logging import configurar_logger_modulo


class ProcesoInfo(NamedTuple):
    pid: int
    nombre: str
    comando: str
    usuario: str
    ruta_ejecutable: str
    pid_padre: int
    tiempo_inicio: float
    uso_cpu: float
    uso_memoria: int
    estado: str
    puertos_abiertos: List[int]
    conexiones_red: List[Dict[str, Any]]


class EstadisticaProceso:
    """Estadísticas históricas de un proceso."""
    
    def __init__(self, pid: int):
        """
        Inicializa las estadísticas del proceso.
        
        Args:
            pid: ID del proceso
        """
        self.pid = pid
        self.timestamp_inicio = time.time()
        self.muestras_cpu: List[float] = []
        self.muestras_memoria: List[int] = []
        self.picos_cpu = 0.0
        self.picos_memoria = 0
        self.tiempo_activo = 0.0
        self.conexiones_total = 0
        self.archivos_abiertos: Set[str] = set()
    
    def agregar_muestra(self, cpu: float, memoria: int):
        """Agrega una muestra de uso de recursos."""
        self.muestras_cpu.append(cpu)
        self.muestras_memoria.append(memoria)
        
        # Mantener solo las últimas 100 muestras
        if len(self.muestras_cpu) > 100:
            self.muestras_cpu = self.muestras_cpu[-100:]
        if len(self.muestras_memoria) > 100:
            self.muestras_memoria = self.muestras_memoria[-100:]
        
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


class MonitorProcesos:
    """Monitor principal de procesos del sistema."""
    
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
        self.estadisticas_procesos: Dict[int, EstadisticaProceso] = {}
        self.procesos_finalizados: List[ProcesoInfo] = []
        self.procesos_sospechosos: List[ProcesoInfo] = []
        
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
        
        self.logger.info("Los mil ojos de Argos han despertado para vigilar los procesos")
    
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
                "Monitor de procesos de Argos activado",
                {"componente": "monitor_procesos"},
                "MEDIO"
            )
        
        self.logger.info("Los ojos de Argos comienzan su vigilia eterna sobre los procesos")
    
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
                "Monitor de procesos de Argos desactivado",
                {
                    "procesos_monitoreados": len(self.procesos_actuales),
                    "procesos_sospechosos": len(self.procesos_sospechosos)
                },
                "MEDIO"
            )
        
        self.logger.info("Los ojos de Argos han cerrado para el descanso")
    
    def _loop_monitoreo(self):
        """Loop principal de monitoreo de procesos."""
        self.logger.info("Iniciando ciclo de vigilancia de los procesos")
        
        while self.monitoreando:
            try:
                self._escanear_procesos()
                self._analizar_procesos_sospechosos()
                self._limpiar_procesos_finalizados()
                time.sleep(self.intervalo_monitoreo)
                
            except Exception as e:
                self.logger.error(f"Error en ciclo de monitoreo de procesos: {e}")
                time.sleep(self.intervalo_monitoreo * 2)
    
    def _escanear_procesos(self):
        """Escanea todos los procesos activos del sistema."""
        try:
            pids_actuales = set()
            
            # Obtener lista de procesos usando subprocess (método alternativo)
            resultado = subprocess.run(['ps', 'aux'], capture_output=True, text=True, timeout=10)
            
            if resultado.returncode == 0:
                lineas = resultado.stdout.split('\n')[1:]  # Omitir header
                
                for linea in lineas:
                    if not linea.strip():
                        continue
                    
                    try:
                        proceso_info = self._parsear_linea_ps(linea)
                        if proceso_info:
                            pids_actuales.add(proceso_info.pid)
                            self._procesar_proceso(proceso_info)
                    
                    except Exception as e:
                        self.logger.debug(f"Error procesando línea de ps: {e}")
                        continue
            
            # Marcar procesos finalizados
            pids_finalizados = set(self.procesos_actuales.keys()) - pids_actuales
            for pid in pids_finalizados:
                proceso_finalizado = self.procesos_actuales.pop(pid, None)
                if proceso_finalizado:
                    self.procesos_finalizados.append(proceso_finalizado)
                    self.logger.debug(f"Proceso finalizado: PID {pid}")
        
        except Exception as e:
            self.logger.error(f"Error escaneando procesos: {e}")
    
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
                estado=estado,
                puertos_abiertos=puertos_abiertos,
                conexiones_red=conexiones_red
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
            self.estadisticas_procesos[proceso.pid] = EstadisticaProceso(proceso.pid)
        
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
                'proceso_info': proceso._asdict()
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
