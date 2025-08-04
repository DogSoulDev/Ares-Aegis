#!/usr/bin/env python3
"""
Ares Aegis - Controlador de Monitor de Procesos
Controlador especializado para monitorear procesos del sistema

Creado por DogSoulDev
Versión: 4.0.0 - Arquitectura MVC Optimizada
"""

import asyncio
import threading
import time
import subprocess
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

from ..modelo.modelo_monitor_procesos import MonitorProcesos
from ..modelo.modelo_siem import SIEM, TipoEvento
from ..utils.utils_ayuda_logging import configurar_logger_modulo
from .controlador_base import ControladorBase
from ..utils.utils_gestor_configuracion import gestor_configuracion


class ControladorMonitorProcesos(ControladorBase):
    """Controlador especializado para monitoreo de procesos del sistema."""
    
    def __init__(self, monitor_procesos: MonitorProcesos, siem: SIEM):
        """
        Inicializar el controlador de monitor de procesos.
        
        Args:
            monitor_procesos: Instancia del monitor de procesos
            siem: Instancia del SIEM para registro de eventos
        """
        super().__init__("monitor_procesos")
        
        self.monitor_procesos = monitor_procesos
        self.siem = siem
        self.configuracion = gestor_configuracion.obtener_config_controlador("monitor_procesos")
        
        # Estado del controlador
        self.monitoreo_activo = False
        self._hilo_monitoreo = None
        self._lock = threading.Lock()
        
        # Métricas
        self.procesos_monitoreados = 0
        self.alertas_generadas = 0
        self.ultimo_analisis = None
        
        self.logger.info("Controlador de Monitor de Procesos inicializado")
    
    async def _inicializar_impl(self) -> bool:
        """Implementación de inicialización del controlador."""
        try:
            # Inicializar sin depender de métodos específicos del modelo
            self.logger.info("Controlador de Monitor de Procesos inicializado correctamente")
            return True
            
        except Exception as e:
            self.logger.error(f"Error inicializando controlador de monitor de procesos: {e}")
            return False
    
    async def _finalizar_impl(self) -> bool:
        """Implementación de finalización del controlador."""
        try:
            await self.detener_monitoreo()
            
            self.logger.info("Controlador de Monitor de Procesos finalizado correctamente")
            return True
            
        except Exception as e:
            self.logger.error(f"Error finalizando controlador de monitor de procesos: {e}")
            return False
    
    async def iniciar_monitoreo(self) -> bool:
        """Iniciar el monitoreo de procesos."""
        try:
            with self._lock:
                if self.monitoreo_activo:
                    self.logger.warning("El monitoreo de procesos ya está activo")
                    return True
                
                self.monitoreo_activo = True
                
                # Iniciar hilo de monitoreo
                self._hilo_monitoreo = threading.Thread(
                    target=self._monitorear_procesos,
                    name="MonitorProcesos",
                    daemon=True
                )
                self._hilo_monitoreo.start()
                
                # Registrar evento en SIEM
                if self.siem:
                    self.siem.registrar_evento(
                        TipoEvento.SISTEMA_INICIADO,
                        "Monitoreo de procesos iniciado",
                        {"controlador": "monitor_procesos"}
                    )
                
                self.logger.info("Monitoreo de procesos iniciado correctamente")
                return True
                
        except Exception as e:
            self.logger.error(f"Error iniciando monitoreo de procesos: {e}")
            self.monitoreo_activo = False
            return False
    
    async def detener_monitoreo(self) -> bool:
        """Detener el monitoreo de procesos."""
        try:
            with self._lock:
                if not self.monitoreo_activo:
                    return True
                
                self.monitoreo_activo = False
                
                # Esperar a que termine el hilo
                if self._hilo_monitoreo and self._hilo_monitoreo.is_alive():
                    self._hilo_monitoreo.join(timeout=5.0)
                
                # Registrar evento en SIEM
                if self.siem:
                    self.siem.registrar_evento(
                        TipoEvento.SISTEMA_DETENIDO,
                        "Monitoreo de procesos detenido",
                        {"controlador": "monitor_procesos"}
                    )
                
                self.logger.info("Monitoreo de procesos detenido correctamente")
                return True
                
        except Exception as e:
            self.logger.error(f"Error deteniendo monitoreo de procesos: {e}")
            return False
    
    def _monitorear_procesos(self):
        """Hilo principal de monitoreo de procesos."""
        self.logger.info("Iniciando hilo de monitoreo de procesos")
        
        while self.monitoreo_activo:
            try:
                # Obtener procesos actuales básicos
                procesos_basicos = self.obtener_procesos_sistema()
                
                # Análisis básico
                self._analisis_basico_procesos(procesos_basicos)
                
                # Si tenemos monitor avanzado, también hacer análisis avanzado
                if self.monitor_procesos:
                    try:
                        procesos_avanzados = self.monitor_procesos.obtener_procesos_sistema()
                        # Análisis avanzado de amenazas
                        self._analisis_avanzado_procesos(procesos_avanzados)
                    except Exception as e:
                        self.logger.warning(f"Error en análisis avanzado: {e}")
                
                self.procesos_monitoreados = len(procesos_basicos)
                self.ultimo_analisis = datetime.now()
                
                # Pausa entre análisis
                time.sleep(self.configuracion.get("intervalo_monitoreo", 30))
                
            except Exception as e:
                self.logger.error(f"Error en monitoreo de procesos: {e}")
                time.sleep(5)  # Pausa de recuperación
        
        self.logger.info("Hilo de monitoreo de procesos finalizado")
    
    def _analisis_basico_procesos(self, procesos: List[Dict[str, Any]]):
        """Análisis básico de procesos sin modelo específico."""
        try:
            # Detectar procesos con uso elevado de CPU o memoria
            for proceso in procesos:
                cpu_percent = proceso.get('cpu_percent', 0)
                memory_percent = proceso.get('memory_percent', 0)
                
                # Alertar sobre uso elevado de recursos
                if cpu_percent > 80 or memory_percent > 80:
                    amenaza = {
                        'nombre': proceso.get('name', 'Desconocido'),
                        'pid': proceso.get('pid'),
                        'cpu_percent': cpu_percent,
                        'memory_percent': memory_percent,
                        'tipo': 'Uso elevado de recursos'
                    }
                    self._procesar_amenaza_proceso(amenaza)
                    
        except Exception as e:
            self.logger.error(f"Error en análisis básico de procesos: {e}")
    
    def obtener_procesos_sistema(self) -> List[Dict[str, Any]]:
        """Obtener lista de procesos del sistema usando comandos nativos de Linux."""
        try:
            procesos = []
            
            # Usar el comando ps para obtener información de procesos
            # ps -eo pid,ppid,cmd,pcpu,pmem,stat,etime,user --no-headers
            cmd = ["ps", "-eo", "pid,ppid,cmd,pcpu,pmem,stat,etime,user", "--no-headers"]
            
            resultado = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if resultado.returncode != 0:
                self.logger.error(f"Error ejecutando ps: {resultado.stderr}")
                return []
            
            # Procesar la salida línea por línea
            for linea in resultado.stdout.strip().split('\n'):
                if not linea.strip():
                    continue
                    
                partes = linea.strip().split(None, 7)  # Dividir en máximo 8 partes
                if len(partes) >= 8:
                    try:
                        pid = int(partes[0])
                        ppid = int(partes[1])
                        cpu_percent = float(partes[3])
                        memory_percent = float(partes[4])
                        status = partes[5]
                        etime = partes[6]
                        user = partes[7]
                        cmd_line = partes[2] if len(partes) > 2 else ""
                        
                        # Extraer nombre del proceso de la línea de comandos
                        name = os.path.basename(cmd_line.split()[0]) if cmd_line else "unknown"
                        
                        proceso = {
                            'pid': pid,
                            'ppid': ppid,
                            'name': name,
                            'cmd': cmd_line,
                            'cpu_percent': cpu_percent,
                            'memory_percent': memory_percent,
                            'status': status,
                            'etime': etime,
                            'user': user,
                            'timestamp': datetime.now().isoformat()
                        }
                        procesos.append(proceso)
                        
                    except (ValueError, IndexError) as e:
                        self.logger.debug(f"Error procesando línea de ps: {linea} - {e}")
                        continue
            
            return procesos
            
        except subprocess.TimeoutExpired:
            self.logger.error("Timeout ejecutando comando ps")
            return []
        except Exception as e:
            self.logger.error(f"Error obteniendo procesos del sistema: {e}")
            return []
    
    def terminar_proceso(self, pid: int) -> bool:
        """Terminar un proceso específico usando comandos nativos de Linux."""
        try:
            # Primero obtener información del proceso
            nombre_proceso = "desconocido"
            try:
                # Obtener nombre del proceso desde /proc/PID/comm
                with open(f'/proc/{pid}/comm', 'r') as f:
                    nombre_proceso = f.read().strip()
            except (FileNotFoundError, PermissionError):
                # Si no podemos leer /proc, usar ps
                try:
                    cmd = ["ps", "-p", str(pid), "-o", "comm="]
                    resultado = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                    if resultado.returncode == 0:
                        nombre_proceso = resultado.stdout.strip()
                except Exception:
                    pass
            
            # Intentar terminar el proceso con SIGTERM
            try:
                os.kill(pid, 15)  # SIGTERM
                time.sleep(2)
                
                # Verificar si el proceso aún existe
                try:
                    os.kill(pid, 0)  # Signal 0 solo verifica existencia
                    # Si llegamos aquí, el proceso aún existe, usar SIGKILL
                    os.kill(pid, 9)  # SIGKILL
                    time.sleep(1)
                except ProcessLookupError:
                    # El proceso ya no existe, terminación exitosa
                    pass
                    
            except ProcessLookupError:
                # El proceso ya no existe
                self.logger.warning(f"Proceso con PID {pid} no encontrado")
                return False
            except PermissionError:
                self.logger.error(f"Acceso denegado para terminar proceso PID {pid}")
                return False
            
            # Registrar en SIEM
            if self.siem:
                self.siem.registrar_evento(
                    TipoEvento.SISTEMA_DETENIDO,
                    f"Proceso terminado: {nombre_proceso} (PID: {pid})",
                    {"pid": pid, "proceso": nombre_proceso}
                )
            
            self.logger.info(f"Proceso terminado: {nombre_proceso} (PID: {pid})")
            return True
            
        except Exception as e:
            self.logger.error(f"Error terminando proceso {pid}: {e}")
            return False
    
    def _analisis_avanzado_procesos(self, procesos_avanzados):
        """Realizar análisis avanzado de procesos usando el modelo MonitorProcesos."""
        try:
            for proceso in procesos_avanzados:
                try:
                    # Usar el analizador del modelo para detectar amenazas
                    alertas = self.monitor_procesos.analizador.analizar_proceso(proceso)
                    
                    # Si hay alertas, procesar cada una
                    if alertas:
                        for alerta in alertas:
                            # Crear un diccionario de amenaza para procesamiento
                            amenaza = {
                                'nombre': proceso.nombre,
                                'pid': proceso.pid,
                                'tipo': alerta.tipo_alerta,
                                'descripcion': alerta.descripcion,
                                'prioridad': alerta.nivel_severidad.value if hasattr(alerta.nivel_severidad, 'value') else str(alerta.nivel_severidad),
                                'timestamp': alerta.timestamp,
                                'evidencia': alerta.evidencia,
                                'recomendaciones': alerta.recomendaciones
                            }
                            self._procesar_amenaza_proceso(amenaza)
                            
                except Exception as e:
                    self.logger.debug(f"Error analizando proceso {getattr(proceso, 'pid', 'N/A')}: {e}")
                
        except Exception as e:
            self.logger.error(f"Error en análisis avanzado de procesos: {e}")
    
    def _procesar_amenaza_proceso(self, proceso_amenaza):
        """Procesar una amenaza detectada en un proceso."""
        try:
            # Manejar tanto ProcesoInfo como diccionarios básicos
            if hasattr(proceso_amenaza, 'nombre'):
                # Es un objeto ProcesoInfo
                nombre = proceso_amenaza.nombre
                pid = proceso_amenaza.pid
                datos_evento = {
                    "pid": pid,
                    "nombre": nombre,
                    "amenazas": getattr(proceso_amenaza, 'amenazas_detectadas', []),
                    "nivel_riesgo": getattr(proceso_amenaza, 'nivel_riesgo', {}).get('value', 'MEDIO') if hasattr(getattr(proceso_amenaza, 'nivel_riesgo', {}), 'value') else 'MEDIO'
                }
                mensaje = f"⚠️ Proceso sospechoso: {nombre} (PID: {pid})"
            else:
                # Es un diccionario básico
                nombre = proceso_amenaza.get('nombre', 'Desconocido')
                pid = proceso_amenaza.get('pid', 'N/A')
                datos_evento = proceso_amenaza
                mensaje = f"⚠️ Amenaza en proceso: {nombre} (PID: {pid})"
            
            # Registrar la amenaza
            if self.siem:
                self.siem.registrar_evento(
                    "PROCESO_SOSPECHOSO",
                    f"Proceso sospechoso detectado: {nombre}",
                    datos_evento,
                    "ALTO"
                )
            
            self.alertas_generadas += 1
            self.logger.warning(mensaje)
            
        except Exception as e:
            self.logger.error(f"Error procesando amenaza de proceso: {e}")
    
    def obtener_metricas(self) -> Dict[str, Any]:
        """Obtener métricas del monitoreo de procesos."""
        return {
            "monitoreo_activo": self.monitoreo_activo,
            "procesos_monitoreados": self.procesos_monitoreados,
            "alertas_generadas": self.alertas_generadas,
            "ultimo_analisis": self.ultimo_analisis.isoformat() if self.ultimo_analisis else None
        }
    
    def obtener_estado(self) -> Dict[str, Any]:
        """Obtener estado completo del controlador."""
        return {
            "activo": self.activo,
            "monitoreo_activo": self.monitoreo_activo,
            "configuracion": self.configuracion,
            "metricas": self.obtener_metricas()
        }
