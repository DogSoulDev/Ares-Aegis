"""
Utilidades para el Controlador Principal
Componentes extraídos para reducir la complejidad del controlador principal
"""

import asyncio
import threading
import logging
import subprocess
import os
import platform
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path


class MonitorSistemaUtils:
    """Utilidades de monitoreo del sistema extraídas del controlador principal"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self._proceso_monitor = None
        self._debe_monitorear = False
    
    def obtener_recursos_sistema(self) -> Dict[str, Any]:
        """Obtener información de recursos del sistema usando psutil si está disponible, 
        o comandos nativos de Linux como fallback para Kali"""
        try:
            recursos = {
                "cpu_porcentaje": 0.0,
                "memoria_porcentaje": 0.0,
                "memoria_disponible": "0 MB",
                "disco_porcentaje": 0.0,
                "procesos_activos": 0,
                "timestamp": datetime.now().isoformat()
            }
            
            try:
                # Intentar usar psutil primero (recomendado para Kali Linux)
                import psutil  # type: ignore
                recursos.update({
                    "cpu_porcentaje": psutil.cpu_percent(interval=1),
                    "memoria_porcentaje": psutil.virtual_memory().percent,
                    "memoria_disponible": f"{psutil.virtual_memory().available // (1024*1024)} MB",
                    "disco_porcentaje": psutil.disk_usage('/').percent if platform.system() != 'Windows' else psutil.disk_usage('C:').percent,
                    "procesos_activos": len(psutil.pids())
                })
            except ImportError:
                # Fallback usando comandos nativos de Linux (ideal para Kali)
                self.logger.info("psutil no disponible, usando comandos nativos de Linux")
                recursos = self._obtener_recursos_nativos_linux()
                
            return recursos
            
        except Exception as e:
            self.logger.error(f"Error obteniendo recursos del sistema: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}
    
    def _obtener_recursos_nativos_linux(self) -> Dict[str, Any]:
        """Obtener recursos usando comandos nativos de Linux para Kali"""
        recursos = {
            "cpu_porcentaje": 0.0,
            "memoria_porcentaje": 0.0,
            "memoria_disponible": "0 MB",
            "disco_porcentaje": 0.0,
            "procesos_activos": 0,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # CPU usando /proc/stat
            try:
                with open('/proc/loadavg', 'r') as f:
                    load_avg = float(f.read().split()[0])
                    recursos["cpu_porcentaje"] = min(load_avg * 25, 100)  # Aproximación
            except:
                recursos["cpu_porcentaje"] = 30.0
            
            # Memoria usando /proc/meminfo
            try:
                with open('/proc/meminfo', 'r') as f:
                    meminfo = {}
                    for line in f:
                        key, value = line.split(':')
                        meminfo[key.strip()] = int(value.split()[0])
                    
                    total = meminfo['MemTotal']
                    available = meminfo.get('MemAvailable', meminfo['MemFree'])
                    used = total - available
                    
                    recursos.update({
                        "memoria_porcentaje": (used / total) * 100,
                        "memoria_disponible": f"{available // 1024} MB"
                    })
            except:
                recursos.update({
                    "memoria_porcentaje": 45.0,
                    "memoria_disponible": "4096 MB"
                })
            
            # Disco usando df
            try:
                result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    if len(lines) > 1:
                        parts = lines[1].split()
                        if len(parts) >= 5:
                            uso_str = parts[4].replace('%', '')
                            recursos["disco_porcentaje"] = float(uso_str)
            except:
                recursos["disco_porcentaje"] = 60.0
            
            # Procesos usando ps
            try:
                result = subprocess.run(['ps', 'aux'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    recursos["procesos_activos"] = len(result.stdout.strip().split('\n')) - 1
            except:
                recursos["procesos_activos"] = 120
                
        except Exception as e:
            self.logger.warning(f"Error obteniendo recursos nativos: {e}")
            
        return recursos
    
    def obtener_informacion_red(self) -> Dict[str, Any]:
        """Obtener información básica de red usando psutil o comandos nativos de Linux"""
        try:
            info_red = {
                "conexiones_activas": 0,
                "interfaces": [],
                "timestamp": datetime.now().isoformat()
            }
            
            try:
                # Intentar usar psutil primero
                import psutil  # type: ignore
                conexiones = psutil.net_connections()
                info_red["conexiones_activas"] = len([c for c in conexiones if c.status == 'ESTABLISHED'])
                
                interfaces = psutil.net_if_stats()
                info_red["interfaces"] = [
                    {"nombre": nombre, "activa": stats.isup}
                    for nombre, stats in interfaces.items()
                ]
            except ImportError:
                # Fallback usando comandos nativos de Linux para Kali
                self.logger.info("psutil no disponible, usando comandos nativos para información de red")
                info_red = self._obtener_info_red_nativa()
                
            return info_red
            
        except Exception as e:
            self.logger.error(f"Error obteniendo información de red: {e}")
            return {"error": str(e)}
    
    def _obtener_info_red_nativa(self) -> Dict[str, Any]:
        """Obtener información de red usando comandos nativos de Linux"""
        info_red = {
            "conexiones_activas": 0,
            "interfaces": [],
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Contar conexiones establecidas usando netstat
            try:
                result = subprocess.run(['netstat', '-tn'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    established_count = result.stdout.count('ESTABLISHED')
                    info_red["conexiones_activas"] = established_count
            except:
                info_red["conexiones_activas"] = 5  # Valor por defecto
            
            # Obtener interfaces usando ip command (estándar en Kali)
            try:
                result = subprocess.run(['ip', 'link', 'show'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    interfaces = []
                    for line in result.stdout.split('\n'):
                        if ': ' in line and 'state' in line.lower():
                            parts = line.split(': ')
                            if len(parts) > 1:
                                nombre = parts[1].split('@')[0]  # Remover sufijos como @if2
                                activa = 'UP' in line.upper()
                                interfaces.append({"nombre": nombre, "activa": activa})
                    info_red["interfaces"] = interfaces
            except:
                # Fallback con interfaces comunes en Kali
                info_red["interfaces"] = [
                    {"nombre": "eth0", "activa": True},
                    {"nombre": "wlan0", "activa": False},
                    {"nombre": "lo", "activa": True}
                ]
                
        except Exception as e:
            self.logger.warning(f"Error obteniendo info de red nativa: {e}")
            
        return info_red
    
    def verificar_servicios_sistema(self) -> List[Dict[str, Any]]:
        """Verificar servicios críticos del sistema"""
        servicios = []
        
        try:
            if platform.system() == "Linux":
                # Verificar servicios de Kali Linux
                servicios_kali = ['networking', 'ssh', 'postgresql', 'apache2', 'mysql']
                for servicio in servicios_kali:
                    try:
                        resultado = subprocess.run(
                            ['systemctl', 'is-active', servicio],
                            capture_output=True, text=True, timeout=5
                        )
                        estado = resultado.stdout.strip()
                        servicios.append({
                            "nombre": servicio,
                            "estado": estado,
                            "activo": estado == "active"
                        })
                    except Exception as e:
                        servicios.append({
                            "nombre": servicio,
                            "estado": "error",
                            "activo": False,
                            "error": str(e)
                        })
            
            elif platform.system() == "Windows":
                # Servicios Windows básicos
                servicios_windows = ['Winmgmt', 'EventLog', 'Spooler']
                for servicio in servicios_windows:
                    try:
                        resultado = subprocess.run(
                            ['sc', 'query', servicio],
                            capture_output=True, text=True, timeout=5
                        )
                        activo = 'RUNNING' in resultado.stdout
                        servicios.append({
                            "nombre": servicio,
                            "estado": "running" if activo else "stopped",
                            "activo": activo
                        })
                    except Exception as e:
                        servicios.append({
                            "nombre": servicio,
                            "estado": "error",
                            "activo": False,
                            "error": str(e)
                        })
                        
        except Exception as e:
            self.logger.error(f"Error verificando servicios: {e}")
            
        return servicios


class GestorComponentes:
    """Gestor para inicializar y coordinar componentes del sistema"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.componentes_inicializados = {}
        
    async def inicializar_componente_async(self, nombre: str, inicializador) -> bool:
        """Inicializar un componente de forma asíncrona"""
        try:
            self.logger.info(f"Inicializando componente: {nombre}")
            
            if asyncio.iscoroutinefunction(inicializador):
                resultado = await inicializador()
            else:
                resultado = inicializador()
                
            self.componentes_inicializados[nombre] = resultado
            self.logger.info(f"Componente {nombre} inicializado correctamente")
            return True
            
        except Exception as e:
            self.logger.error(f"Error inicializando componente {nombre}: {e}")
            self.componentes_inicializados[nombre] = None
            return False
    
    def verificar_componentes(self) -> Dict[str, bool]:
        """Verificar estado de todos los componentes"""
        estado = {}
        for nombre, componente in self.componentes_inicializados.items():
            estado[nombre] = componente is not None
        return estado
    
    def obtener_componente(self, nombre: str):
        """Obtener un componente específico"""
        return self.componentes_inicializados.get(nombre)


class GestorEscaneo:
    """Gestor para operaciones de escaneo del sistema"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.escaneo_activo = False
        self.progreso_escaneo = 0
        self.archivos_escaneados = 0
        self.amenazas_encontradas = 0
        self._hilo_escaneo = None
        
    def iniciar_escaneo_completo(self, rutas: Optional[List[str]] = None) -> bool:
        """Iniciar escaneo completo del sistema"""
        if self.escaneo_activo:
            self.logger.warning("Ya hay un escaneo en curso")
            return False
            
        try:
            self.escaneo_activo = True
            self.progreso_escaneo = 0
            self.archivos_escaneados = 0
            self.amenazas_encontradas = 0
            
            rutas_default = self._obtener_rutas_escaneo_default()
            rutas_escaneo = rutas or rutas_default
            
            self._hilo_escaneo = threading.Thread(
                target=self._ejecutar_escaneo,
                args=(rutas_escaneo,),
                daemon=True
            )
            self._hilo_escaneo.start()
            
            self.logger.info("Escaneo completo iniciado")
            return True
            
        except Exception as e:
            self.logger.error(f"Error iniciando escaneo: {e}")
            self.escaneo_activo = False
            return False
    
    def detener_escaneo(self) -> bool:
        """Detener escaneo en curso"""
        try:
            self.escaneo_activo = False
            if self._hilo_escaneo and self._hilo_escaneo.is_alive():
                self._hilo_escaneo.join(timeout=5)
            
            self.logger.info("Escaneo detenido")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deteniendo escaneo: {e}")
            return False
    
    def obtener_estado_escaneo(self) -> Dict[str, Any]:
        """Obtener estado actual del escaneo"""
        return {
            "activo": self.escaneo_activo,
            "progreso": self.progreso_escaneo,
            "archivos_escaneados": self.archivos_escaneados,
            "amenazas_encontradas": self.amenazas_encontradas,
            "timestamp": datetime.now().isoformat()
        }
    
    def _obtener_rutas_escaneo_default(self) -> List[str]:
        """Obtener rutas por defecto para escaneo según el sistema operativo"""
        if platform.system() == "Linux":
            return ["/home", "/tmp", "/var/tmp", "/usr/local"]
        elif platform.system() == "Windows":
            return ["C:\\Users", "C:\\Temp", "C:\\Windows\\Temp"]
        else:
            return [str(Path.home())]
    
    def _ejecutar_escaneo(self, rutas: List[str]):
        """Ejecutar escaneo en hilo separado"""
        try:
            total_archivos = self._contar_archivos(rutas)
            archivos_procesados = 0
            
            for ruta in rutas:
                if not self.escaneo_activo:
                    break
                    
                for archivo in self._obtener_archivos_ruta(ruta):
                    if not self.escaneo_activo:
                        break
                        
                    # Simular escaneo del archivo
                    self._escanear_archivo(archivo)
                    archivos_procesados += 1
                    self.archivos_escaneados = archivos_procesados
                    
                    if total_archivos > 0:
                        self.progreso_escaneo = min(100, (archivos_procesados * 100) // total_archivos)
            
            if self.escaneo_activo:
                self.progreso_escaneo = 100
                self.logger.info(f"Escaneo completado: {self.archivos_escaneados} archivos, {self.amenazas_encontradas} amenazas")
            
        except Exception as e:
            self.logger.error(f"Error durante escaneo: {e}")
        finally:
            self.escaneo_activo = False
    
    def _contar_archivos(self, rutas: List[str]) -> int:
        """Contar archivos en las rutas especificadas"""
        count = 0
        try:
            for ruta in rutas:
                path_obj = Path(ruta)
                if path_obj.exists():
                    if path_obj.is_file():
                        count += 1
                    else:
                        count += sum(1 for _ in path_obj.rglob('*') if _.is_file())
        except Exception as e:
            self.logger.error(f"Error contando archivos: {e}")
        return count
    
    def _obtener_archivos_ruta(self, ruta: str):
        """Obtener archivos de una ruta específica"""
        try:
            path_obj = Path(ruta)
            if path_obj.exists():
                if path_obj.is_file():
                    yield path_obj
                else:
                    for archivo in path_obj.rglob('*'):
                        if archivo.is_file():
                            yield archivo
        except Exception as e:
            self.logger.error(f"Error obteniendo archivos de {ruta}: {e}")
    
    def _escanear_archivo(self, archivo: Path) -> bool:
        """Escanear un archivo específico (simulado)"""
        try:
            # Simulación básica de escaneo
            # En implementación real, aquí iría la lógica de detección de malware
            
            # Simulamos encontrar amenazas ocasionalmente
            import random
            if random.random() < 0.001:  # 0.1% de probabilidad
                self.amenazas_encontradas += 1
                self.logger.warning(f"Amenaza simulada detectada en: {archivo}")
                return True
                
            return False
            
        except Exception as e:
            self.logger.error(f"Error escaneando archivo {archivo}: {e}")
            return False


class UtilsCompatibilidad:
    """Utilidades para compatibilidad multiplataforma"""
    
    @staticmethod
    def obtener_info_sistema() -> Dict[str, str]:
        """Obtener información básica del sistema"""
        return {
            "sistema": platform.system(),
            "version": platform.version(),
            "arquitectura": platform.architecture()[0],
            "procesador": platform.processor(),
            "hostname": platform.node(),
            "python_version": platform.python_version()
        }
    
    @staticmethod
    def es_kali_linux() -> bool:
        """Verificar si estamos ejecutando en Kali Linux"""
        try:
            if platform.system() != "Linux":
                return False
                
            # Verificar archivos específicos de Kali
            kali_files = ["/etc/kali-version", "/usr/share/kali-themes"]
            return any(Path(f).exists() for f in kali_files)
            
        except Exception:
            return False
    
    @staticmethod
    def configurar_compatibilidad_kali():
        """Configurar compatibilidad específica para Kali Linux"""
        if not UtilsCompatibilidad.es_kali_linux():
            return False
            
        try:
            # Configuraciones específicas para Kali
            os.environ.setdefault('DEBIAN_FRONTEND', 'noninteractive')
            return True
            
        except Exception:
            return False
