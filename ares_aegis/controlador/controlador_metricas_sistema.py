#!/usr/bin/env python3
"""
Ares Aegis - Controlador de Métricas del Sistema
Controlador especializado para obtener y gestionar métricas del sistema

Creado por DogSoulDev
Versión: 4.0.0 - Arquitectura MVC Optimizada
"""

import asyncio
import os
import subprocess
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

from ..utils.utils_ayuda_logging import configurar_logger_modulo
from .controlador_base import ControladorBase
from ..utils.utils_gestor_configuracion import gestor_configuracion


class ControladorMetricasSistema(ControladorBase):
    """Controlador especializado para métricas del sistema."""
    
    def __init__(self):
        """Inicializar el controlador de métricas del sistema."""
        super().__init__("metricas_sistema")
        
        self.configuracion = gestor_configuracion.obtener_config_controlador("metricas_sistema")
        
        # Cache de métricas
        self._cache_metricas = {}
        self._ultima_actualizacion = None
        self._intervalo_cache = 30  # segundos
        
        self.logger.info("Controlador de Métricas del Sistema inicializado")
    
    async def _inicializar_impl(self) -> bool:
        """Implementación de inicialización del controlador."""
        try:
            # Verificar herramientas del sistema
            self._verificar_herramientas_sistema()
            
            self.logger.info("Controlador de Métricas del Sistema inicializado correctamente")
            return True
            
        except Exception as e:
            self.logger.error(f"Error inicializando controlador de métricas del sistema: {e}")
            return False
    
    async def _finalizar_impl(self) -> bool:
        """Implementación de finalización del controlador."""
        try:
            # Limpiar cache
            self._cache_metricas.clear()
            
            self.logger.info("Controlador de Métricas del Sistema finalizado correctamente")
            return True
            
        except Exception as e:
            self.logger.error(f"Error finalizando controlador de métricas del sistema: {e}")
            return False
    
    def _verificar_herramientas_sistema(self):
        """Verificar que las herramientas del sistema estén disponibles."""
        herramientas = ['ps', 'df', 'free', 'uptime', 'uname']
        for herramienta in herramientas:
            try:
                subprocess.run(['which', herramienta], 
                             capture_output=True, check=True, timeout=5)
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                self.logger.warning(f"Herramienta {herramienta} no disponible")
    
    def obtener_metricas_sistema(self, forzar_actualizacion: bool = False) -> Dict[str, Any]:
        """
        Obtener métricas completas del sistema.
        
        Args:
            forzar_actualizacion: Si True, ignora el cache y actualiza
            
        Returns:
            Dict con métricas del sistema
        """
        try:
            # Verificar cache
            if not forzar_actualizacion and self._cache_valido():
                return self._cache_metricas.copy()
            
            # Recolectar métricas
            metricas = {
                'timestamp': datetime.now().isoformat(),
                'cpu': self._obtener_metricas_cpu(),
                'memoria': self._obtener_metricas_memoria(),
                'disco': self._obtener_metricas_disco(),
                'red': self._obtener_metricas_red(),
                'procesos': self._obtener_metricas_procesos(),
                'sistema': self._obtener_info_sistema(),
                'uptime': self._obtener_uptime_sistema()
            }
            
            # Actualizar cache
            self._cache_metricas = metricas
            self._ultima_actualizacion = time.time()
            
            return metricas.copy()
            
        except Exception as e:
            self.logger.error(f"Error obteniendo métricas del sistema: {e}")
            return {}
    
    def _cache_valido(self) -> bool:
        """Verificar si el cache de métricas es válido."""
        if not self._cache_metricas or not self._ultima_actualizacion:
            return False
        
        return (time.time() - self._ultima_actualizacion) < self._intervalo_cache
    
    def _obtener_metricas_cpu(self) -> Dict[str, Any]:
        """Obtener métricas de CPU usando herramientas nativas."""
        try:
            metricas_cpu = {
                'cores': self._obtener_numero_cores(),
                'uso_actual': self._obtener_uso_cpu(),
                'load_average': self._obtener_load_average(),
                'arquitectura': self._obtener_arquitectura_cpu()
            }
            return metricas_cpu
            
        except Exception as e:
            self.logger.error(f"Error obteniendo métricas de CPU: {e}")
            return {}
    
    def _obtener_numero_cores(self) -> int:
        """Obtener número de cores de CPU."""
        try:
            # Leer /proc/cpuinfo
            with open('/proc/cpuinfo', 'r') as f:
                content = f.read()
            
            # Contar procesadores
            cores = content.count('processor')
            return cores if cores > 0 else 1
            
        except Exception:
            return 1
    
    def _obtener_uso_cpu(self) -> float:
        """Obtener uso actual de CPU."""
        try:
            # Usar top para obtener uso de CPU
            cmd = ['top', '-bn1', '|', 'grep', '"Cpu(s)"']
            resultado = subprocess.run(
                ' '.join(cmd), 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            
            if resultado.returncode == 0 and resultado.stdout:
                # Parsear salida de top
                linea = resultado.stdout.strip()
                # Buscar el porcentaje de uso
                partes = linea.split()
                for i, parte in enumerate(partes):
                    if 'us' in parte and i > 0:
                        try:
                            return float(partes[i-1].replace('%', ''))
                        except ValueError:
                            pass
            
            return 0.0
            
        except Exception:
            return 0.0
    
    def _obtener_load_average(self) -> Dict[str, float]:
        """Obtener load average del sistema."""
        try:
            with open('/proc/loadavg', 'r') as f:
                content = f.read().strip()
            
            valores = content.split()[:3]
            return {
                '1min': float(valores[0]),
                '5min': float(valores[1]),
                '15min': float(valores[2])
            }
            
        except Exception:
            return {'1min': 0.0, '5min': 0.0, '15min': 0.0}
    
    def _obtener_arquitectura_cpu(self) -> str:
        """Obtener arquitectura del CPU."""
        try:
            resultado = subprocess.run(
                ['uname', '-m'], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            
            if resultado.returncode == 0:
                return resultado.stdout.strip()
            
            return "unknown"
            
        except Exception:
            return "unknown"
    
    def _obtener_metricas_memoria(self) -> Dict[str, Any]:
        """Obtener métricas de memoria usando /proc/meminfo."""
        try:
            with open('/proc/meminfo', 'r') as f:
                content = f.read()
            
            metricas = {}
            for linea in content.split('\n'):
                if ':' in linea:
                    nombre, valor = linea.split(':', 1)
                    nombre = nombre.strip()
                    valor = valor.strip().replace(' kB', '')
                    
                    try:
                        metricas[nombre.lower()] = int(valor) * 1024  # Convertir a bytes
                    except ValueError:
                        continue
            
            # Calcular métricas derivadas
            total = metricas.get('memtotal', 0)
            available = metricas.get('memavailable', 0)
            usado = total - available if total and available else 0
            
            return {
                'total': total,
                'disponible': available,
                'usado': usado,
                'porcentaje_uso': (usado / total * 100) if total > 0 else 0,
                'swap_total': metricas.get('swaptotal', 0),
                'swap_libre': metricas.get('swapfree', 0),
                'buffers': metricas.get('buffers', 0),
                'cached': metricas.get('cached', 0)
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo métricas de memoria: {e}")
            return {}
    
    def _obtener_metricas_disco(self) -> Dict[str, Any]:
        """Obtener métricas de disco usando df."""
        try:
            resultado = subprocess.run(
                ['df', '-h'], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            if resultado.returncode != 0:
                return {}
            
            lineas = resultado.stdout.strip().split('\n')[1:]  # Omitir header
            discos = []
            
            for linea in lineas:
                partes = linea.split()
                if len(partes) >= 6:
                    disco = {
                        'filesystem': partes[0],
                        'tamaño': partes[1],
                        'usado': partes[2],
                        'disponible': partes[3],
                        'porcentaje_uso': partes[4].replace('%', ''),
                        'montaje': partes[5]
                    }
                    discos.append(disco)
            
            return {'discos': discos}
            
        except Exception as e:
            self.logger.error(f"Error obteniendo métricas de disco: {e}")
            return {}
    
    def _obtener_metricas_red(self) -> Dict[str, Any]:
        """Obtener métricas de red usando /proc/net/dev."""
        try:
            with open('/proc/net/dev', 'r') as f:
                content = f.read()
            
            lineas = content.strip().split('\n')[2:]  # Omitir headers
            interfaces = []
            
            for linea in lineas:
                if ':' in linea:
                    nombre_iface, datos = linea.split(':', 1)
                    nombre_iface = nombre_iface.strip()
                    
                    valores = datos.split()
                    if len(valores) >= 16:
                        interface = {
                            'nombre': nombre_iface,
                            'rx_bytes': int(valores[0]),
                            'rx_packets': int(valores[1]),
                            'rx_errors': int(valores[2]),
                            'tx_bytes': int(valores[8]),
                            'tx_packets': int(valores[9]),
                            'tx_errors': int(valores[10])
                        }
                        interfaces.append(interface)
            
            return {'interfaces': interfaces}
            
        except Exception as e:
            self.logger.error(f"Error obteniendo métricas de red: {e}")
            return {}
    
    def _obtener_metricas_procesos(self) -> Dict[str, Any]:
        """Obtener métricas de procesos usando ps."""
        try:
            resultado = subprocess.run(
                ['ps', 'aux'], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            if resultado.returncode != 0:
                return {}
            
            lineas = resultado.stdout.strip().split('\n')[1:]  # Omitir header
            
            total_procesos = len(lineas)
            procesos_root = 0
            uso_cpu_total = 0.0
            uso_memoria_total = 0.0
            
            for linea in lineas:
                partes = linea.split(None, 10)
                if len(partes) >= 11:
                    usuario = partes[0]
                    cpu = float(partes[2]) if partes[2].replace('.', '').isdigit() else 0.0
                    memoria = float(partes[3]) if partes[3].replace('.', '').isdigit() else 0.0
                    
                    if usuario == 'root':
                        procesos_root += 1
                    
                    uso_cpu_total += cpu
                    uso_memoria_total += memoria
            
            return {
                'total': total_procesos,
                'root': procesos_root,
                'usuario': total_procesos - procesos_root,
                'uso_cpu_total': uso_cpu_total,
                'uso_memoria_total': uso_memoria_total
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo métricas de procesos: {e}")
            return {}
    
    def _obtener_info_sistema(self) -> Dict[str, Any]:
        """Obtener información general del sistema."""
        try:
            info = {}
            
            # Información del kernel
            resultado = subprocess.run(
                ['uname', '-a'], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            if resultado.returncode == 0:
                info['kernel'] = resultado.stdout.strip()
            
            # Distribución
            try:
                with open('/etc/os-release', 'r') as f:
                    content = f.read()
                
                for linea in content.split('\n'):
                    if linea.startswith('PRETTY_NAME='):
                        info['distribucion'] = linea.split('=', 1)[1].strip('"')
                        break
            except Exception:
                info['distribucion'] = "Desconocida"
            
            # Hostname
            try:
                resultado = subprocess.run(
                    ['hostname'], 
                    capture_output=True, 
                    text=True, 
                    timeout=5
                )
                if resultado.returncode == 0:
                    info['hostname'] = resultado.stdout.strip()
                else:
                    info['hostname'] = "desconocido"
            except Exception:
                info['hostname'] = "desconocido"
            
            return info
            
        except Exception as e:
            self.logger.error(f"Error obteniendo información del sistema: {e}")
            return {}
    
    def _obtener_uptime_sistema(self) -> Dict[str, Any]:
        """Obtener uptime del sistema."""
        try:
            with open('/proc/uptime', 'r') as f:
                content = f.read().strip()
            
            uptime_seconds = float(content.split()[0])
            
            # Convertir a formato legible
            dias = int(uptime_seconds // 86400)
            horas = int((uptime_seconds % 86400) // 3600)
            minutos = int((uptime_seconds % 3600) // 60)
            
            return {
                'seconds': uptime_seconds,
                'dias': dias,
                'horas': horas,
                'minutos': minutos,
                'formato_legible': f"{dias}d {horas}h {minutos}m"
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo uptime: {e}")
            return {}
    
    def obtener_estadisticas_sistema(self) -> Dict[str, Any]:
        """Obtener estadísticas resumidas del sistema."""
        try:
            metricas = self.obtener_metricas_sistema()
            
            estadisticas = {
                'timestamp': metricas.get('timestamp'),
                'cpu_cores': metricas.get('cpu', {}).get('cores', 0),
                'cpu_uso': metricas.get('cpu', {}).get('uso_actual', 0),
                'memoria_total': metricas.get('memoria', {}).get('total', 0),
                'memoria_uso_porcentaje': metricas.get('memoria', {}).get('porcentaje_uso', 0),
                'procesos_total': metricas.get('procesos', {}).get('total', 0),
                'uptime': metricas.get('uptime', {}).get('formato_legible', ''),
                'hostname': metricas.get('sistema', {}).get('hostname', ''),
                'distribucion': metricas.get('sistema', {}).get('distribucion', '')
            }
            
            return estadisticas
            
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas del sistema: {e}")
            return {}
    
    def obtener_estado_recursos(self) -> Dict[str, Any]:
        """Obtener estado actual de recursos del sistema."""
        try:
            metricas = self.obtener_metricas_sistema()
            
            # Determinar estado basado en umbrales
            cpu_uso = metricas.get('cpu', {}).get('uso_actual', 0)
            memoria_uso = metricas.get('memoria', {}).get('porcentaje_uso', 0)
            
            estado_cpu = self._determinar_estado_recurso(cpu_uso, 70, 90)
            estado_memoria = self._determinar_estado_recurso(memoria_uso, 80, 95)
            
            return {
                'cpu': {
                    'uso': cpu_uso,
                    'estado': estado_cpu
                },
                'memoria': {
                    'uso': memoria_uso,
                    'estado': estado_memoria
                },
                'estado_general': self._determinar_estado_general(estado_cpu, estado_memoria)
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo estado de recursos: {e}")
            return {}
    
    def _determinar_estado_recurso(self, uso: float, umbral_medio: float, umbral_alto: float) -> str:
        """Determinar estado de un recurso basado en su uso."""
        if uso >= umbral_alto:
            return "CRITICO"
        elif uso >= umbral_medio:
            return "ADVERTENCIA"
        else:
            return "NORMAL"
    
    def _determinar_estado_general(self, estado_cpu: str, estado_memoria: str) -> str:
        """Determinar estado general del sistema."""
        estados = [estado_cpu, estado_memoria]
        
        if "CRITICO" in estados:
            return "CRITICO"
        elif "ADVERTENCIA" in estados:
            return "ADVERTENCIA"
        else:
            return "NORMAL"
    
    def obtener_metricas(self) -> Dict[str, Any]:
        """Obtener métricas del controlador."""
        return {
            "activo": self.activo,
            "cache_valido": self._cache_valido(),
            "ultima_actualizacion": self._ultima_actualizacion,
            "configuracion": self.configuracion
        }
    
    def obtener_estado(self) -> Dict[str, Any]:
        """Obtener estado completo del controlador."""
        return {
            "activo": self.activo,
            "configuracion": self.configuracion,
            "metricas": self.obtener_metricas(),
            "estado_recursos": self.obtener_estado_recursos()
        }
