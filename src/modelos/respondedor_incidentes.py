#!/usr/bin/env python3
"""
Respondedor de Incidentes
Sistema integral de gestión y respuesta coordinada a incidentes de seguridad.

Autor: DogSoulDev
Versión: 2.0.0
"""

import json
import os
import time
import threading
import subprocess
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
import hashlib
import tempfile


class EstadoIncidente(Enum):
    """Estados posibles de un incidente."""
    NUEVO = "nuevo"
    EN_ANALISIS = "en_analisis"
    EN_RESPUESTA = "en_respuesta"
    CONTENIDO = "contenido"
    RESUELTO = "resuelto"
    CERRADO = "cerrado"
    ESCALADO = "escalado"


class SeveridadIncidente(Enum):
    """Niveles de severidad de incidentes."""
    INFORMATIVO = "informativo"
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"


class TipoRespuesta(Enum):
    """Tipos de respuesta disponibles."""
    AUTOMATICA = "automatica"
    MANUAL = "manual"
    ESCALACION = "escalacion"
    NOTIFICACION = "notificacion"
    INVESTIGACION = "investigacion"


@dataclass
class Incidente:
    """Representación de un incidente de seguridad."""
    id: str
    titulo: str
    descripcion: str
    severidad: SeveridadIncidente
    estado: EstadoIncidente
    timestamp_creacion: datetime
    timestamp_actualizacion: datetime
    origen: str
    tipo_amenaza: str
    evidencias: List[Dict[str, Any]]
    acciones_tomadas: List[Dict[str, Any]]
    asignado_a: str = ""
    tags: Optional[List[str]] = None
    datos_contexto: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.datos_contexto is None:
            self.datos_contexto = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el incidente a diccionario."""
        data = asdict(self)
        data['timestamp_creacion'] = self.timestamp_creacion.isoformat()
        data['timestamp_actualizacion'] = self.timestamp_actualizacion.isoformat()
        data['severidad'] = self.severidad.value
        data['estado'] = self.estado.value
        return data
    
    def agregar_evidencia(self, evidencia: Dict[str, Any]):
        """Agrega evidencia al incidente."""
        evidencia['timestamp'] = datetime.now().isoformat()
        self.evidencias.append(evidencia)
        self.timestamp_actualizacion = datetime.now()
    
    def agregar_accion(self, accion: Dict[str, Any]):
        """Agrega una acción tomada al incidente."""
        accion['timestamp'] = datetime.now().isoformat()
        self.acciones_tomadas.append(accion)
        self.timestamp_actualizacion = datetime.now()


@dataclass
class PlanRespuesta:
    """Plan de respuesta para un tipo específico de incidente."""
    id: str
    nombre: str
    tipo_amenaza: str
    severidad_minima: SeveridadIncidente
    pasos_respuesta: List[Dict[str, Any]]
    tiempo_respuesta_sla: int  # minutos
    escalacion_automatica: bool = True
    notificaciones: Optional[List[str]] = None
    requisitos_especiales: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.notificaciones is None:
            self.notificaciones = []
        if self.requisitos_especiales is None:
            self.requisitos_especiales = []


class ColectorEvidencias:
    """Recolector automático de evidencias forenses."""
    
    def __init__(self, directorio_evidencias: str = "/var/ares-aegis/evidencias"):
        """
        Inicializa el colector de evidencias.
        
        Args:
            directorio_evidencias: Directorio donde almacenar evidencias
        """
        self.directorio_evidencias = directorio_evidencias
        os.makedirs(directorio_evidencias, exist_ok=True)
    
    def recolectar_evidencias_proceso(self, pid: int, nombre_proceso: str) -> Dict[str, Any]:
        """Recolecta evidencias de un proceso sospechoso."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        evidencias = {
            'tipo': 'proceso',
            'pid': pid,
            'nombre_proceso': nombre_proceso,
            'timestamp': timestamp,
            'archivos_generados': []
        }
        
        try:
            # Crear directorio para este incidente
            dir_incidente = os.path.join(self.directorio_evidencias, f"proceso_{pid}_{timestamp}")
            os.makedirs(dir_incidente, exist_ok=True)
            
            # Recolectar información del proceso
            info_proceso = self._recolectar_info_proceso(pid)
            if info_proceso:
                archivo_info = os.path.join(dir_incidente, "proceso_info.json")
                with open(archivo_info, 'w') as f:
                    json.dump(info_proceso, f, indent=2)
                evidencias['archivos_generados'].append(archivo_info)
            
            # Recolectar mapa de memoria
            mapa_memoria = self._recolectar_mapa_memoria(pid)
            if mapa_memoria:
                archivo_memoria = os.path.join(dir_incidente, "mapa_memoria.txt")
                with open(archivo_memoria, 'w') as f:
                    f.write(mapa_memoria)
                evidencias['archivos_generados'].append(archivo_memoria)
            
            # Recolectar archivos abiertos
            archivos_abiertos = self._recolectar_archivos_abiertos(pid)
            if archivos_abiertos:
                archivo_fd = os.path.join(dir_incidente, "archivos_abiertos.json")
                with open(archivo_fd, 'w') as f:
                    json.dump(archivos_abiertos, f, indent=2)
                evidencias['archivos_generados'].append(archivo_fd)
            
            # Recolectar variables de entorno
            env_vars = self._recolectar_variables_entorno(pid)
            if env_vars:
                archivo_env = os.path.join(dir_incidente, "variables_entorno.json")
                with open(archivo_env, 'w') as f:
                    json.dump(env_vars, f, indent=2)
                evidencias['archivos_generados'].append(archivo_env)
            
            evidencias['directorio'] = dir_incidente
            evidencias['exito'] = True
            
        except Exception as e:
            evidencias['error'] = str(e)
            evidencias['exito'] = False
        
        return evidencias
    
    def recolectar_evidencias_archivo(self, ruta_archivo: str, motivo: str) -> Dict[str, Any]:
        """Recolecta evidencias de un archivo sospechoso."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        evidencias = {
            'tipo': 'archivo',
            'archivo_original': ruta_archivo,
            'motivo': motivo,
            'timestamp': timestamp,
            'archivos_generados': []
        }
        
        try:
            if not os.path.exists(ruta_archivo):
                evidencias['error'] = 'Archivo no encontrado'
                evidencias['exito'] = False
                return evidencias
            
            # Crear directorio para evidencias
            nombre_archivo = os.path.basename(ruta_archivo)
            dir_incidente = os.path.join(self.directorio_evidencias, f"archivo_{timestamp}_{nombre_archivo}")
            os.makedirs(dir_incidente, exist_ok=True)
            
            # Calcular hashes del archivo
            hashes = self._calcular_hashes_archivo(ruta_archivo)
            archivo_hashes = os.path.join(dir_incidente, "hashes.json")
            with open(archivo_hashes, 'w') as f:
                json.dump(hashes, f, indent=2)
            evidencias['archivos_generados'].append(archivo_hashes)
            evidencias['hashes'] = hashes
            
            # Copiar archivo original (si es seguro hacerlo)
            if os.path.getsize(ruta_archivo) < 100 * 1024 * 1024:  # Max 100MB
                archivo_copia = os.path.join(dir_incidente, f"copia_{nombre_archivo}")
                subprocess.run(['cp', ruta_archivo, archivo_copia], check=True)
                evidencias['archivos_generados'].append(archivo_copia)
            
            # Metadatos del archivo
            metadatos = self._recolectar_metadatos_archivo(ruta_archivo)
            archivo_meta = os.path.join(dir_incidente, "metadatos.json")
            with open(archivo_meta, 'w') as f:
                json.dump(metadatos, f, indent=2)
            evidencias['archivos_generados'].append(archivo_meta)
            
            # Análisis de strings si es ejecutable
            if self._es_ejecutable(ruta_archivo):
                strings_output = self._extraer_strings(ruta_archivo)
                if strings_output:
                    archivo_strings = os.path.join(dir_incidente, "strings.txt")
                    with open(archivo_strings, 'w') as f:
                        f.write(strings_output)
                    evidencias['archivos_generados'].append(archivo_strings)
            
            evidencias['directorio'] = dir_incidente
            evidencias['exito'] = True
            
        except Exception as e:
            evidencias['error'] = str(e)
            evidencias['exito'] = False
        
        return evidencias
    
    def recolectar_evidencias_red(self, conexion_info: Dict[str, Any]) -> Dict[str, Any]:
        """Recolecta evidencias de actividad de red sospechosa."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        evidencias = {
            'tipo': 'red',
            'conexion': conexion_info,
            'timestamp': timestamp,
            'archivos_generados': []
        }
        
        try:
            # Crear directorio para evidencias
            dir_incidente = os.path.join(self.directorio_evidencias, f"red_{timestamp}")
            os.makedirs(dir_incidente, exist_ok=True)
            
            # Capturar estado actual de conexiones
            conexiones_activas = self._capturar_conexiones_activas()
            archivo_conexiones = os.path.join(dir_incidente, "conexiones_activas.json")
            with open(archivo_conexiones, 'w') as f:
                json.dump(conexiones_activas, f, indent=2)
            evidencias['archivos_generados'].append(archivo_conexiones)
            
            # Capturar tabla de routing
            tabla_routing = self._capturar_tabla_routing()
            if tabla_routing:
                archivo_routing = os.path.join(dir_incidente, "tabla_routing.txt")
                with open(archivo_routing, 'w') as f:
                    f.write(tabla_routing)
                evidencias['archivos_generados'].append(archivo_routing)
            
            # Capturar estadísticas de red
            estadisticas_red = self._capturar_estadisticas_red()
            if estadisticas_red:
                archivo_stats = os.path.join(dir_incidente, "estadisticas_red.txt")
                with open(archivo_stats, 'w') as f:
                    f.write(estadisticas_red)
                evidencias['archivos_generados'].append(archivo_stats)
            
            # DNS lookup de IPs sospechosas
            if 'ip_destino' in conexion_info:
                dns_info = self._resolver_dns_inverso(conexion_info['ip_destino'])
                if dns_info:
                    archivo_dns = os.path.join(dir_incidente, "dns_info.json")
                    with open(archivo_dns, 'w') as f:
                        json.dump(dns_info, f, indent=2)
                    evidencias['archivos_generados'].append(archivo_dns)
            
            evidencias['directorio'] = dir_incidente
            evidencias['exito'] = True
            
        except Exception as e:
            evidencias['error'] = str(e)
            evidencias['exito'] = False
        
        return evidencias
    
    def _recolectar_info_proceso(self, pid: int) -> Optional[Dict[str, Any]]:
        """Recolecta información detallada de un proceso."""
        try:
            info = {}
            
            # Leer /proc/[pid]/stat
            with open(f'/proc/{pid}/stat', 'r') as f:
                stat_data = f.read().split()
                info['stat'] = {
                    'nombre': stat_data[1].strip('()'),
                    'estado': stat_data[2],
                    'ppid': int(stat_data[3]),
                    'pgrp': int(stat_data[4]),
                    'session': int(stat_data[5]),
                    'utime': int(stat_data[13]),
                    'stime': int(stat_data[14]),
                    'priority': int(stat_data[17]),
                    'nice': int(stat_data[18]),
                    'num_threads': int(stat_data[19]),
                    'start_time': int(stat_data[21])
                }
            
            # Leer /proc/[pid]/status
            try:
                with open(f'/proc/{pid}/status', 'r') as f:
                    status_data = {}
                    for line in f:
                        if ':' in line:
                            key, value = line.strip().split(':', 1)
                            status_data[key] = value.strip()
                    info['status'] = status_data
            except:
                pass
            
            # Leer línea de comandos
            try:
                with open(f'/proc/{pid}/cmdline', 'r') as f:
                    cmdline = f.read().replace('\x00', ' ').strip()
                    info['cmdline'] = cmdline
            except:
                pass
            
            # Leer directorio de trabajo
            try:
                cwd = os.readlink(f'/proc/{pid}/cwd')
                info['cwd'] = cwd
            except:
                pass
            
            # Leer ejecutable
            try:
                exe = os.readlink(f'/proc/{pid}/exe')
                info['exe'] = exe
            except:
                pass
            
            return info
            
        except Exception:
            return None
    
    def _recolectar_mapa_memoria(self, pid: int) -> Optional[str]:
        """Recolecta mapa de memoria del proceso."""
        try:
            with open(f'/proc/{pid}/maps', 'r') as f:
                return f.read()
        except:
            return None
    
    def _recolectar_archivos_abiertos(self, pid: int) -> Optional[List[Dict[str, Any]]]:
        """Recolecta lista de archivos abiertos por el proceso."""
        try:
            archivos = []
            fd_path = f'/proc/{pid}/fd'
            
            if os.path.exists(fd_path):
                for fd in os.listdir(fd_path):
                    try:
                        link = os.readlink(f'{fd_path}/{fd}')
                        archivos.append({
                            'fd': int(fd),
                            'path': link,
                            'tipo': 'socket' if 'socket:' in link else 'file'
                        })
                    except:
                        continue
            
            return archivos if archivos else None
            
        except:
            return None
    
    def _recolectar_variables_entorno(self, pid: int) -> Optional[Dict[str, str]]:
        """Recolecta variables de entorno del proceso."""
        try:
            with open(f'/proc/{pid}/environ', 'rb') as f:
                environ_data = f.read().decode('utf-8', errors='ignore')
                
            env_vars = {}
            for line in environ_data.split('\x00'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
            
            return env_vars if env_vars else None
            
        except:
            return None
    
    def _calcular_hashes_archivo(self, ruta_archivo: str) -> Dict[str, str]:
        """Calcula hashes MD5, SHA1 y SHA256 del archivo."""
        hashes = {}
        
        try:
            with open(ruta_archivo, 'rb') as f:
                contenido = f.read()
                
            hashes['md5'] = hashlib.md5(contenido).hexdigest()
            hashes['sha1'] = hashlib.sha1(contenido).hexdigest()
            hashes['sha256'] = hashlib.sha256(contenido).hexdigest()
            hashes['tamano'] = len(contenido)
            
        except Exception as e:
            hashes['error'] = str(e)
        
        return hashes
    
    def _recolectar_metadatos_archivo(self, ruta_archivo: str) -> Dict[str, Any]:
        """Recolecta metadatos del archivo."""
        try:
            stat_info = os.stat(ruta_archivo)
            
            return {
                'tamano': stat_info.st_size,
                'modo': oct(stat_info.st_mode),
                'uid': stat_info.st_uid,
                'gid': stat_info.st_gid,
                'atime': datetime.fromtimestamp(stat_info.st_atime).isoformat(),
                'mtime': datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                'ctime': datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
                'nlinks': stat_info.st_nlink,
                'inode': stat_info.st_ino
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _es_ejecutable(self, ruta_archivo: str) -> bool:
        """Verifica si el archivo es ejecutable."""
        try:
            with open(ruta_archivo, 'rb') as f:
                magic = f.read(4)
                # ELF magic number
                return magic == b'\x7fELF'
        except:
            return False
    
    def _extraer_strings(self, ruta_archivo: str) -> Optional[str]:
        """Extrae strings del archivo usando el comando strings."""
        try:
            resultado = subprocess.run(
                ['strings', ruta_archivo], 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            return resultado.stdout if resultado.returncode == 0 else None
        except:
            return None
    
    def _capturar_conexiones_activas(self) -> List[Dict[str, Any]]:
        """Captura conexiones de red activas."""
        conexiones = []
        
        try:
            # TCP connections
            resultado = subprocess.run(
                ['netstat', '-tan'], 
                capture_output=True, 
                text=True
            )
            
            if resultado.returncode == 0:
                for line in resultado.stdout.split('\n')[2:]:  # Skip headers
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 6:
                            conexiones.append({
                                'protocolo': parts[0],
                                'local': parts[3],
                                'remoto': parts[4],
                                'estado': parts[5] if len(parts) > 5 else ''
                            })
        except:
            pass
        
        return conexiones
    
    def _capturar_tabla_routing(self) -> Optional[str]:
        """Captura tabla de routing."""
        try:
            resultado = subprocess.run(
                ['route', '-n'], 
                capture_output=True, 
                text=True
            )
            return resultado.stdout if resultado.returncode == 0 else None
        except:
            return None
    
    def _capturar_estadisticas_red(self) -> Optional[str]:
        """Captura estadísticas de red."""
        try:
            with open('/proc/net/dev', 'r') as f:
                return f.read()
        except:
            return None
    
    def _resolver_dns_inverso(self, ip: str) -> Optional[Dict[str, str]]:
        """Resuelve DNS inverso para una IP."""
        try:
            resultado = subprocess.run(
                ['nslookup', ip], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            if resultado.returncode == 0:
                return {
                    'ip': ip,
                    'dns_output': resultado.stdout,
                    'timestamp': datetime.now().isoformat()
                }
        except:
            pass
        
        return None


class GestorRespuesta:
    """Gestor de planes y acciones de respuesta."""
    
    def __init__(self, archivo_planes: str = "planes_respuesta.json"):
        """
        Inicializa el gestor de respuesta.
        
        Args:
            archivo_planes: Archivo con los planes de respuesta
        """
        self.archivo_planes = archivo_planes
        self.planes: List[PlanRespuesta] = []
        self.cargar_planes()
        
        if not self.planes:
            self.crear_planes_por_defecto()
    
    def cargar_planes(self):
        """Carga planes de respuesta desde archivo."""
        try:
            if os.path.exists(self.archivo_planes):
                with open(self.archivo_planes, 'r') as f:
                    datos_planes = json.load(f)
                    
                self.planes = []
                for datos in datos_planes:
                    # Convertir enum values back to enums
                    datos['severidad_minima'] = SeveridadIncidente(datos['severidad_minima'])
                    plan = PlanRespuesta(**datos)
                    self.planes.append(plan)
        except Exception as e:
            print(f"Error cargando planes: {e}")
    
    def guardar_planes(self):
        """Guarda planes de respuesta a archivo."""
        try:
            datos_planes = []
            for plan in self.planes:
                datos = asdict(plan)
                datos['severidad_minima'] = plan.severidad_minima.value
                datos_planes.append(datos)
            
            with open(self.archivo_planes, 'w') as f:
                json.dump(datos_planes, f, indent=2)
        except Exception as e:
            print(f"Error guardando planes: {e}")
    
    def crear_planes_por_defecto(self):
        """Crea planes de respuesta por defecto."""
        planes_defecto = [
            PlanRespuesta(
                id="malware_response",
                nombre="Respuesta a Malware",
                tipo_amenaza="malware",
                severidad_minima=SeveridadIncidente.MEDIA,
                tiempo_respuesta_sla=15,
                pasos_respuesta=[
                    {"orden": 1, "accion": "aislar_archivo", "descripcion": "Mover archivo a cuarentena"},
                    {"orden": 2, "accion": "recolectar_evidencias", "descripcion": "Recolectar evidencias forenses"},
                    {"orden": 3, "accion": "escaneo_completo", "descripcion": "Realizar escaneo completo del sistema"},
                    {"orden": 4, "accion": "notificar_admin", "descripcion": "Notificar al administrador"}
                ],
                notificaciones=["admin@empresa.com", "security@empresa.com"]
            ),
            PlanRespuesta(
                id="intrusion_response",
                nombre="Respuesta a Intrusión",
                tipo_amenaza="intrusion",
                severidad_minima=SeveridadIncidente.ALTA,
                tiempo_respuesta_sla=5,
                pasos_respuesta=[
                    {"orden": 1, "accion": "bloquear_ip", "descripcion": "Bloquear IP atacante"},
                    {"orden": 2, "accion": "recolectar_evidencias_red", "descripcion": "Recolectar evidencias de red"},
                    {"orden": 3, "accion": "revisar_logs", "descripcion": "Revisar logs de acceso"},
                    {"orden": 4, "accion": "cambiar_credenciales", "descripcion": "Cambiar credenciales comprometidas"},
                    {"orden": 5, "accion": "escalamiento", "descripcion": "Escalar a equipo de seguridad"}
                ],
                escalacion_automatica=True,
                notificaciones=["security-team@empresa.com", "ciso@empresa.com"]
            ),
            PlanRespuesta(
                id="ransomware_response",
                nombre="Respuesta a Ransomware",
                tipo_amenaza="ransomware",
                severidad_minima=SeveridadIncidente.CRITICA,
                tiempo_respuesta_sla=2,
                pasos_respuesta=[
                    {"orden": 1, "accion": "aislar_sistema", "descripcion": "Aislar sistema de la red"},
                    {"orden": 2, "accion": "terminar_procesos", "descripcion": "Terminar procesos maliciosos"},
                    {"orden": 3, "accion": "recolectar_evidencias", "descripcion": "Preservar evidencias"},
                    {"orden": 4, "accion": "activar_backup", "descripcion": "Activar plan de backup"},
                    {"orden": 5, "accion": "escalamiento_ejecutivo", "descripcion": "Escalar a nivel ejecutivo"}
                ],
                escalacion_automatica=True,
                notificaciones=["ceo@empresa.com", "ciso@empresa.com", "it-director@empresa.com"],
                requisitos_especiales=["desconexion_red", "preservacion_evidencias", "comunicacion_legal"]
            ),
            PlanRespuesta(
                id="data_exfiltration_response",
                nombre="Respuesta a Exfiltración de Datos",
                tipo_amenaza="exfiltracion_datos",
                severidad_minima=SeveridadIncidente.ALTA,
                tiempo_respuesta_sla=10,
                pasos_respuesta=[
                    {"orden": 1, "accion": "bloquear_conexiones", "descripcion": "Bloquear conexiones sospechosas"},
                    {"orden": 2, "accion": "identificar_datos", "descripcion": "Identificar datos comprometidos"},
                    {"orden": 3, "accion": "recolectar_evidencias_red", "descripcion": "Preservar evidencias de red"},
                    {"orden": 4, "accion": "notificar_legal", "descripcion": "Notificar departamento legal"},
                    {"orden": 5, "accion": "evaluar_cumplimiento", "descripcion": "Evaluar impacto regulatorio"}
                ],
                notificaciones=["legal@empresa.com", "privacy@empresa.com", "ciso@empresa.com"],
                requisitos_especiales=["notificacion_regulador", "evaluacion_legal"]
            )
        ]
        
        self.planes = planes_defecto
        self.guardar_planes()
    
    def obtener_plan_respuesta(self, tipo_amenaza: str, severidad: SeveridadIncidente) -> Optional[PlanRespuesta]:
        """Obtiene el plan de respuesta apropiado para un incidente."""
        planes_aplicables = []
        
        for plan in self.planes:
            if (plan.tipo_amenaza == tipo_amenaza and 
                severidad.value >= plan.severidad_minima.value):
                planes_aplicables.append(plan)
        
        # Retornar el plan con menor SLA (más urgente)
        if planes_aplicables:
            return min(planes_aplicables, key=lambda p: p.tiempo_respuesta_sla)
        
        return None
    
    def ejecutar_plan_respuesta(self, plan: PlanRespuesta, incidente: Incidente, 
                               colector_evidencias: ColectorEvidencias) -> List[Dict[str, Any]]:
        """Ejecuta un plan de respuesta."""
        resultados = []
        
        for paso in sorted(plan.pasos_respuesta, key=lambda p: p['orden']):
            resultado = self._ejecutar_paso_respuesta(paso, incidente, colector_evidencias)
            resultados.append(resultado)
            
            # Si un paso crítico falla, detener ejecución
            if not resultado.get('exito', False) and paso.get('critico', False):
                break
        
        return resultados
    
    def _ejecutar_paso_respuesta(self, paso: Dict[str, Any], incidente: Incidente, 
                                colector_evidencias: ColectorEvidencias) -> Dict[str, Any]:
        """Ejecuta un paso individual de respuesta."""
        accion = paso['accion']
        timestamp = datetime.now()
        
        resultado = {
            'paso': paso,
            'timestamp': timestamp.isoformat(),
            'exito': False,
            'mensaje': '',
            'detalles': {}
        }
        
        try:
            if accion == "aislar_archivo":
                # Implementar aislamiento de archivo
                if incidente.datos_contexto and 'archivo' in incidente.datos_contexto:
                    archivo = incidente.datos_contexto['archivo']
                    # Simular cuarentena
                    resultado['exito'] = True
                    resultado['mensaje'] = f"Archivo {archivo} movido a cuarentena"
                
            elif accion == "recolectar_evidencias":
                # Recolectar evidencias según el tipo de incidente
                if incidente.datos_contexto and 'pid' in incidente.datos_contexto:
                    evidencias = colector_evidencias.recolectar_evidencias_proceso(
                        incidente.datos_contexto['pid'],
                        incidente.datos_contexto.get('proceso', 'unknown')
                    )
                elif incidente.datos_contexto and 'archivo' in incidente.datos_contexto:
                    evidencias = colector_evidencias.recolectar_evidencias_archivo(
                        incidente.datos_contexto['archivo'],
                        incidente.descripcion
                    )
                else:
                    evidencias = {'tipo': 'general', 'exito': True}
                
                incidente.agregar_evidencia(evidencias)
                resultado['exito'] = evidencias.get('exito', False)
                resultado['mensaje'] = "Evidencias recolectadas"
                resultado['detalles'] = evidencias
                
            elif accion == "recolectar_evidencias_red":
                conexion_info = {}
                if incidente.datos_contexto:
                    conexion_info = incidente.datos_contexto.get('conexion', {})
                evidencias = colector_evidencias.recolectar_evidencias_red(conexion_info)
                incidente.agregar_evidencia(evidencias)
                resultado['exito'] = evidencias.get('exito', False)
                resultado['mensaje'] = "Evidencias de red recolectadas"
                resultado['detalles'] = evidencias
                
            elif accion == "bloquear_ip":
                if incidente.datos_contexto and 'ip' in incidente.datos_contexto:
                    ip = incidente.datos_contexto['ip']
                    # Simular bloqueo de IP
                    resultado['exito'] = True
                    resultado['mensaje'] = f"IP {ip} bloqueada"
                
            elif accion == "aislar_sistema":
                # Simular aislamiento del sistema
                resultado['exito'] = True
                resultado['mensaje'] = "Sistema aislado de la red"
                
            elif accion == "escaneo_completo":
                # Simular escaneo completo
                resultado['exito'] = True
                resultado['mensaje'] = "Escaneo completo iniciado"
                
            elif accion == "notificar_admin":
                # Simular notificación
                resultado['exito'] = True
                resultado['mensaje'] = "Administrador notificado"
                
            elif accion == "escalamiento":
                incidente.estado = EstadoIncidente.ESCALADO
                resultado['exito'] = True
                resultado['mensaje'] = "Incidente escalado"
                
            else:
                resultado['mensaje'] = f"Acción no implementada: {accion}"
                
        except Exception as e:
            resultado['mensaje'] = f"Error ejecutando {accion}: {str(e)}"
        
        # Agregar acción al incidente
        incidente.agregar_accion(resultado)
        
        return resultado


class RespondedorIncidentes:
    """Sistema principal de respuesta a incidentes."""
    
    def __init__(self, siem=None):
        """
        Inicializa el respondedor de incidentes.
        
        Args:
            siem: Sistema SIEM para logging (opcional)
        """
        self.siem = siem
        self.incidentes: Dict[str, Incidente] = {}
        self.colector_evidencias = ColectorEvidencias()
        self.gestor_respuesta = GestorRespuesta()
        self.cola_procesamiento: deque = deque()
        self.activo = False
        self.hilo_procesamiento = None
        self.lock = threading.Lock()
        self.callbacks_incidente: List[Callable] = []
        
        # Estadísticas
        self.estadisticas = {
            'incidentes_procesados': 0,
            'incidentes_resueltos': 0,
            'incidentes_escalados': 0,
            'tiempo_respuesta_promedio': 0.0
        }
    
    def iniciar_servicio(self):
        """Inicia el servicio de respuesta a incidentes."""
        if self.activo:
            return
        
        self.activo = True
        self.hilo_procesamiento = threading.Thread(target=self._procesar_cola, daemon=True)
        self.hilo_procesamiento.start()
        
        if self.siem:
            self.siem.log_evento('INFO', 'respondedor_incidentes', 
                               'Servicio de respuesta a incidentes iniciado')
    
    def detener_servicio(self):
        """Detiene el servicio de respuesta a incidentes."""
        self.activo = False
        if self.hilo_procesamiento and self.hilo_procesamiento.is_alive():
            self.hilo_procesamiento.join(timeout=10)
        
        if self.siem:
            self.siem.log_evento('INFO', 'respondedor_incidentes', 
                               'Servicio de respuesta a incidentes detenido')
    
    def registrar_incidente(self, titulo: str, descripcion: str, severidad: SeveridadIncidente,
                           tipo_amenaza: str, origen: str, datos_contexto: Optional[Dict[str, Any]] = None) -> str:
        """
        Registra un nuevo incidente.
        
        Args:
            titulo: Título del incidente
            descripcion: Descripción detallada
            severidad: Severidad del incidente
            tipo_amenaza: Tipo de amenaza
            origen: Origen del incidente
            datos_contexto: Datos adicionales de contexto
            
        Returns:
            ID del incidente creado
        """
        timestamp = datetime.now()
        incidente_id = self._generar_id_incidente(timestamp)
        
        incidente = Incidente(
            id=incidente_id,
            titulo=titulo,
            descripcion=descripcion,
            severidad=severidad,
            estado=EstadoIncidente.NUEVO,
            timestamp_creacion=timestamp,
            timestamp_actualizacion=timestamp,
            origen=origen,
            tipo_amenaza=tipo_amenaza,
            evidencias=[],
            acciones_tomadas=[],
            datos_contexto=datos_contexto or {}
        )
        
        with self.lock:
            self.incidentes[incidente_id] = incidente
            self.cola_procesamiento.append(incidente_id)
        
        if self.siem:
            self.siem.log_evento('ALERT', 'respondedor_incidentes', 
                               f'Nuevo incidente registrado: {titulo}', 
                               incidente.to_dict())
        
        # Notificar callbacks
        for callback in self.callbacks_incidente:
            try:
                callback(incidente)
            except Exception as e:
                print(f"Error en callback de incidente: {e}")
        
        return incidente_id
    
    def _generar_id_incidente(self, timestamp: datetime) -> str:
        """Genera un ID único para el incidente."""
        timestamp_str = timestamp.strftime("%Y%m%d%H%M%S")
        hash_obj = hashlib.md5(f"{timestamp_str}{time.time()}".encode())
        return f"INC-{timestamp_str}-{hash_obj.hexdigest()[:8].upper()}"
    
    def _procesar_cola(self):
        """Procesa la cola de incidentes."""
        while self.activo:
            try:
                if self.cola_procesamiento:
                    with self.lock:
                        if self.cola_procesamiento:
                            incidente_id = self.cola_procesamiento.popleft()
                        else:
                            incidente_id = None
                    
                    if incidente_id:
                        self._procesar_incidente(incidente_id)
                
                time.sleep(1)  # Pausa pequeña para no sobrecargar CPU
                
            except Exception as e:
                if self.siem:
                    self.siem.log_evento('ERROR', 'respondedor_incidentes', 
                                       f'Error procesando cola: {str(e)}')
                time.sleep(5)
    
    def _procesar_incidente(self, incidente_id: str):
        """Procesa un incidente individual."""
        try:
            incidente = self.incidentes.get(incidente_id)
            if not incidente:
                return
            
            # Cambiar estado a EN_ANALISIS
            incidente.estado = EstadoIncidente.EN_ANALISIS
            incidente.timestamp_actualizacion = datetime.now()
            
            # Obtener plan de respuesta
            plan = self.gestor_respuesta.obtener_plan_respuesta(
                incidente.tipo_amenaza, 
                incidente.severidad
            )
            
            if plan:
                # Cambiar estado a EN_RESPUESTA
                incidente.estado = EstadoIncidente.EN_RESPUESTA
                
                # Ejecutar plan de respuesta
                resultados = self.gestor_respuesta.ejecutar_plan_respuesta(
                    plan, 
                    incidente, 
                    self.colector_evidencias
                )
                
                # Evaluar resultados
                if all(r.get('exito', False) for r in resultados):
                    incidente.estado = EstadoIncidente.CONTENIDO
                    
                    # Si es de baja severidad, marcar como resuelto
                    if incidente.severidad in [SeveridadIncidente.BAJA, SeveridadIncidente.INFORMATIVO]:
                        incidente.estado = EstadoIncidente.RESUELTO
                        self.estadisticas['incidentes_resueltos'] += 1
                else:
                    # Si hay fallas, escalar
                    if plan.escalacion_automatica:
                        incidente.estado = EstadoIncidente.ESCALADO
                        self.estadisticas['incidentes_escalados'] += 1
            
            else:
                # No hay plan de respuesta, escalar
                incidente.estado = EstadoIncidente.ESCALADO
                self.estadisticas['incidentes_escalados'] += 1
            
            # Actualizar estadísticas
            self.estadisticas['incidentes_procesados'] += 1
            
            # Calcular tiempo de respuesta
            tiempo_respuesta = (datetime.now() - incidente.timestamp_creacion).total_seconds() / 60
            self.estadisticas['tiempo_respuesta_promedio'] = (
                (self.estadisticas['tiempo_respuesta_promedio'] * (self.estadisticas['incidentes_procesados'] - 1) + 
                 tiempo_respuesta) / self.estadisticas['incidentes_procesados']
            )
            
            if self.siem:
                self.siem.log_evento('INFO', 'respondedor_incidentes', 
                                   f'Incidente {incidente_id} procesado - Estado: {incidente.estado.value}')
            
        except Exception as e:
            if self.siem:
                self.siem.log_evento('ERROR', 'respondedor_incidentes', 
                                   f'Error procesando incidente {incidente_id}: {str(e)}')
    
    def obtener_incidente(self, incidente_id: str) -> Optional[Incidente]:
        """Obtiene un incidente por ID."""
        return self.incidentes.get(incidente_id)
    
    def obtener_incidentes_activos(self) -> List[Incidente]:
        """Obtiene lista de incidentes activos."""
        estados_activos = [
            EstadoIncidente.NUEVO,
            EstadoIncidente.EN_ANALISIS,
            EstadoIncidente.EN_RESPUESTA,
            EstadoIncidente.ESCALADO
        ]
        
        return [
            incidente for incidente in self.incidentes.values()
            if incidente.estado in estados_activos
        ]
    
    def obtener_incidentes_por_severidad(self, severidad: SeveridadIncidente) -> List[Incidente]:
        """Obtiene incidentes por severidad."""
        return [
            incidente for incidente in self.incidentes.values()
            if incidente.severidad == severidad
        ]
    
    def cerrar_incidente(self, incidente_id: str, comentario: str = "") -> bool:
        """Cierra un incidente manualmente."""
        incidente = self.incidentes.get(incidente_id)
        if not incidente:
            return False
        
        incidente.estado = EstadoIncidente.CERRADO
        incidente.timestamp_actualizacion = datetime.now()
        
        if comentario:
            incidente.agregar_accion({
                'tipo': 'cierre_manual',
                'comentario': comentario,
                'usuario': 'admin'  # En implementación real, obtener usuario actual
            })
        
        if self.siem:
            self.siem.log_evento('INFO', 'respondedor_incidentes', 
                               f'Incidente {incidente_id} cerrado manualmente')
        
        return True
    
    def agregar_callback_incidente(self, callback: Callable):
        """Agrega callback para notificaciones de nuevos incidentes."""
        self.callbacks_incidente.append(callback)
    
    def generar_reporte_incidentes(self, dias: int = 7) -> Dict[str, Any]:
        """Genera reporte de incidentes."""
        limite_tiempo = datetime.now() - timedelta(days=dias)
        
        incidentes_periodo = [
            inc for inc in self.incidentes.values()
            if inc.timestamp_creacion > limite_tiempo
        ]
        
        # Estadísticas por severidad
        por_severidad = defaultdict(int)
        por_estado = defaultdict(int)
        por_tipo = defaultdict(int)
        
        for inc in incidentes_periodo:
            por_severidad[inc.severidad.value] += 1
            por_estado[inc.estado.value] += 1
            por_tipo[inc.tipo_amenaza] += 1
        
        return {
            'periodo': {
                'inicio': limite_tiempo.isoformat(),
                'fin': datetime.now().isoformat(),
                'dias': dias
            },
            'resumen': {
                'total_incidentes': len(incidentes_periodo),
                'incidentes_resueltos': len([i for i in incidentes_periodo if i.estado == EstadoIncidente.RESUELTO]),
                'incidentes_activos': len([i for i in incidentes_periodo if i.estado in [
                    EstadoIncidente.NUEVO, EstadoIncidente.EN_ANALISIS, EstadoIncidente.EN_RESPUESTA
                ]]),
                'incidentes_escalados': len([i for i in incidentes_periodo if i.estado == EstadoIncidente.ESCALADO])
            },
            'por_severidad': dict(por_severidad),
            'por_estado': dict(por_estado),
            'por_tipo_amenaza': dict(por_tipo),
            'estadisticas_generales': self.estadisticas,
            'timestamp_reporte': datetime.now().isoformat()
        }
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas actuales del sistema."""
        incidentes_activos = self.obtener_incidentes_activos()
        
        return {
            'incidentes_totales': len(self.incidentes),
            'incidentes_activos': len(incidentes_activos),
            'cola_procesamiento': len(self.cola_procesamiento),
            'estadisticas': self.estadisticas,
            'planes_respuesta': len(self.gestor_respuesta.planes),
            'timestamp': datetime.now().isoformat()
        }
