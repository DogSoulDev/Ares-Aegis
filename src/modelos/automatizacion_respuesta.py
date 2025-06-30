#!/usr/bin/env python3
"""
Automatización de Respuesta
Sistema de respuesta automática a incidentes de seguridad basado en reglas y políticas.

Autor: DogSoulDev
Versión: 2.0.0
"""

import json
import os
import subprocess
import time
import threading
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import re


class TipoAccion(Enum):
    """Tipos de acciones automáticas disponibles."""
    CUARENTENA = "cuarentena"
    BLOQUEAR_IP = "bloquear_ip"
    TERMINAR_PROCESO = "terminar_proceso"
    NOTIFICACION = "notificacion"
    BACKUP_ARCHIVO = "backup_archivo"
    ESCANEO_COMPLETO = "escaneo_completo"
    AISLAR_SISTEMA = "aislar_sistema"
    GENERAR_REPORTE = "generar_reporte"


class SeveridadIncidente(Enum):
    """Niveles de severidad de incidentes."""
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"


@dataclass
class Incidente:
    """Representa un incidente de seguridad."""
    id: str
    tipo: str
    severidad: SeveridadIncidente
    descripcion: str
    origen: str
    timestamp: datetime
    datos_adicionales: Dict[str, Any]
    estado: str = "pendiente"
    acciones_ejecutadas: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.acciones_ejecutadas is None:
            self.acciones_ejecutadas = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el incidente a diccionario."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['severidad'] = self.severidad.value
        return data


@dataclass
class ReglaRespuesta:
    """Define una regla de respuesta automática."""
    id: str
    nombre: str
    condiciones: Dict[str, Any]
    acciones: List[Dict[str, Any]]
    habilitada: bool = True
    prioridad: int = 5
    limite_tiempo: int = 60  # segundos
    descripcion: str = ""
    
    def coincide_con_incidente(self, incidente: Incidente) -> bool:
        """Verifica si el incidente coincide con las condiciones de la regla."""
        condiciones = self.condiciones
        
        # Verificar tipo de incidente
        if 'tipo' in condiciones:
            tipos_objetivo = condiciones['tipo']
            if isinstance(tipos_objetivo, str):
                tipos_objetivo = [tipos_objetivo]
            if incidente.tipo not in tipos_objetivo:
                return False
        
        # Verificar severidad
        if 'severidad' in condiciones:
            severidades_objetivo = condiciones['severidad']
            if isinstance(severidades_objetivo, str):
                severidades_objetivo = [severidades_objetivo]
            if incidente.severidad.value not in severidades_objetivo:
                return False
        
        # Verificar origen
        if 'origen' in condiciones:
            patrones_origen = condiciones['origen']
            if isinstance(patrones_origen, str):
                patrones_origen = [patrones_origen]
            
            coincide_origen = False
            for patron in patrones_origen:
                if re.search(patron, incidente.origen, re.IGNORECASE):
                    coincide_origen = True
                    break
            
            if not coincide_origen:
                return False
        
        # Verificar datos adicionales
        if 'datos' in condiciones:
            for clave, valor_esperado in condiciones['datos'].items():
                if clave not in incidente.datos_adicionales:
                    return False
                
                valor_actual = incidente.datos_adicionales[clave]
                if isinstance(valor_esperado, list):
                    if valor_actual not in valor_esperado:
                        return False
                elif valor_actual != valor_esperado:
                    return False
        
        return True


class EjecutorAcciones:
    """Ejecutor de acciones automáticas."""
    
    def __init__(self, directorio_cuarentena: str = "/var/ares-aegis/cuarentena"):
        """
        Inicializa el ejecutor de acciones.
        
        Args:
            directorio_cuarentena: Directorio para archivos en cuarentena
        """
        self.directorio_cuarentena = directorio_cuarentena
        self.acciones_registradas: Dict[str, Callable] = {}
        self._registrar_acciones_basicas()
        
        # Crear directorio de cuarentena si no existe
        os.makedirs(directorio_cuarentena, exist_ok=True)
    
    def _registrar_acciones_basicas(self):
        """Registra las acciones básicas disponibles."""
        self.acciones_registradas = {
            TipoAccion.CUARENTENA.value: self._accion_cuarentena,
            TipoAccion.BLOQUEAR_IP.value: self._accion_bloquear_ip,
            TipoAccion.TERMINAR_PROCESO.value: self._accion_terminar_proceso,
            TipoAccion.NOTIFICACION.value: self._accion_notificacion,
            TipoAccion.BACKUP_ARCHIVO.value: self._accion_backup_archivo,
            TipoAccion.ESCANEO_COMPLETO.value: self._accion_escaneo_completo,
            TipoAccion.AISLAR_SISTEMA.value: self._accion_aislar_sistema,
            TipoAccion.GENERAR_REPORTE.value: self._accion_generar_reporte
        }
    
    def ejecutar_accion(self, tipo_accion: str, parametros: Dict[str, Any], 
                       incidente: Incidente) -> Dict[str, Any]:
        """
        Ejecuta una acción específica.
        
        Args:
            tipo_accion: Tipo de acción a ejecutar
            parametros: Parámetros de la acción
            incidente: Incidente que desencadenó la acción
            
        Returns:
            Dict con resultado de la ejecución
        """
        if tipo_accion not in self.acciones_registradas:
            return {
                'exito': False,
                'error': f'Tipo de acción no registrada: {tipo_accion}',
                'timestamp': datetime.now().isoformat()
            }
        
        try:
            resultado = self.acciones_registradas[tipo_accion](parametros, incidente)
            resultado['timestamp'] = datetime.now().isoformat()
            return resultado
            
        except Exception as e:
            return {
                'exito': False,
                'error': f'Error ejecutando acción {tipo_accion}: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def _accion_cuarentena(self, parametros: Dict[str, Any], incidente: Incidente) -> Dict[str, Any]:
        """Ejecuta acción de cuarentena de archivo."""
        archivo = parametros.get('archivo')
        if not archivo:
            return {'exito': False, 'error': 'Parámetro archivo requerido'}
        
        if not os.path.exists(archivo):
            return {'exito': False, 'error': f'Archivo no encontrado: {archivo}'}
        
        try:
            # Generar nombre único para cuarentena
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = os.path.basename(archivo)
            archivo_cuarentena = os.path.join(
                self.directorio_cuarentena, 
                f"{timestamp}_{nombre_archivo}"
            )
            
            # Mover archivo a cuarentena
            os.rename(archivo, archivo_cuarentena)
            
            # Crear archivo de metadatos
            metadatos = {
                'archivo_original': archivo,
                'archivo_cuarentena': archivo_cuarentena,
                'incidente_id': incidente.id,
                'timestamp': datetime.now().isoformat(),
                'razon': incidente.descripcion
            }
            
            archivo_metadatos = archivo_cuarentena + '.meta'
            with open(archivo_metadatos, 'w') as f:
                json.dump(metadatos, f, indent=2)
            
            return {
                'exito': True,
                'mensaje': f'Archivo movido a cuarentena: {archivo_cuarentena}',
                'archivo_cuarentena': archivo_cuarentena
            }
            
        except Exception as e:
            return {'exito': False, 'error': f'Error en cuarentena: {str(e)}'}
    
    def _accion_bloquear_ip(self, parametros: Dict[str, Any], incidente: Incidente) -> Dict[str, Any]:
        """Ejecuta acción de bloqueo de IP usando iptables."""
        ip = parametros.get('ip')
        if not ip:
            return {'exito': False, 'error': 'Parámetro IP requerido'}
        
        try:
            # Verificar si ya está bloqueada
            resultado_check = subprocess.run(
                ['iptables', '-L', 'INPUT', '-n'], 
                capture_output=True, 
                text=True
            )
            
            if ip in resultado_check.stdout:
                return {
                    'exito': True,
                    'mensaje': f'IP {ip} ya estaba bloqueada',
                    'ip_bloqueada': ip
                }
            
            # Bloquear IP
            comando = ['iptables', '-I', 'INPUT', '-s', ip, '-j', 'DROP']
            resultado = subprocess.run(comando, capture_output=True, text=True)
            
            if resultado.returncode == 0:
                return {
                    'exito': True,
                    'mensaje': f'IP bloqueada exitosamente: {ip}',
                    'ip_bloqueada': ip
                }
            else:
                return {
                    'exito': False,
                    'error': f'Error bloqueando IP: {resultado.stderr}'
                }
                
        except Exception as e:
            return {'exito': False, 'error': f'Error en bloqueo de IP: {str(e)}'}
    
    def _accion_terminar_proceso(self, parametros: Dict[str, Any], incidente: Incidente) -> Dict[str, Any]:
        """Ejecuta acción de terminación de proceso."""
        pid = parametros.get('pid')
        nombre_proceso = parametros.get('nombre_proceso')
        
        if not pid and not nombre_proceso:
            return {'exito': False, 'error': 'Se requiere PID o nombre_proceso'}
        
        try:
            procesos_terminados = []
            
            if pid:
                # Terminar por PID
                try:
                    os.kill(int(pid), 15)  # SIGTERM
                    time.sleep(2)
                    
                    # Verificar si sigue vivo
                    try:
                        os.kill(int(pid), 0)  # Verificar existencia
                        os.kill(int(pid), 9)  # SIGKILL
                    except ProcessLookupError:
                        pass  # Ya terminó
                    
                    procesos_terminados.append(f"PID {pid}")
                    
                except ProcessLookupError:
                    return {'exito': False, 'error': f'Proceso con PID {pid} no encontrado'}
            
            if nombre_proceso:
                # Terminar por nombre usando pkill
                resultado = subprocess.run(
                    ['pkill', '-f', nombre_proceso], 
                    capture_output=True
                )
                
                if resultado.returncode == 0:
                    procesos_terminados.append(f"Procesos con nombre {nombre_proceso}")
                else:
                    return {
                        'exito': False,
                        'error': f'No se encontraron procesos con nombre {nombre_proceso}'
                    }
            
            return {
                'exito': True,
                'mensaje': f'Procesos terminados: {", ".join(procesos_terminados)}',
                'procesos_terminados': procesos_terminados
            }
            
        except Exception as e:
            return {'exito': False, 'error': f'Error terminando proceso: {str(e)}'}
    
    def _accion_notificacion(self, parametros: Dict[str, Any], incidente: Incidente) -> Dict[str, Any]:
        """Ejecuta acción de notificación."""
        mensaje = parametros.get('mensaje', incidente.descripcion)
        metodo = parametros.get('metodo', 'log')
        
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            notificacion = f"[{timestamp}] INCIDENTE {incidente.severidad.value.upper()}: {mensaje}"
            
            if metodo == 'log':
                # Escribir a log del sistema
                with open('/var/log/ares-aegis-alertas.log', 'a') as f:
                    f.write(notificacion + '\n')
            
            elif metodo == 'wall':
                # Enviar mensaje a todos los usuarios conectados
                subprocess.run(['wall', notificacion], input=notificacion.encode())
            
            elif metodo == 'syslog':
                # Enviar a syslog
                subprocess.run(['logger', '-t', 'ares-aegis', notificacion])
            
            return {
                'exito': True,
                'mensaje': f'Notificación enviada por {metodo}',
                'contenido': notificacion
            }
            
        except Exception as e:
            return {'exito': False, 'error': f'Error enviando notificación: {str(e)}'}
    
    def _accion_backup_archivo(self, parametros: Dict[str, Any], incidente: Incidente) -> Dict[str, Any]:
        """Ejecuta acción de backup de archivo."""
        archivo = parametros.get('archivo')
        if not archivo or not os.path.exists(archivo):
            return {'exito': False, 'error': 'Archivo no encontrado o no especificado'}
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_backup = f"{archivo}.backup_{timestamp}"
            
            # Crear copia del archivo
            subprocess.run(['cp', archivo, nombre_backup], check=True)
            
            return {
                'exito': True,
                'mensaje': f'Backup creado: {nombre_backup}',
                'archivo_backup': nombre_backup
            }
            
        except Exception as e:
            return {'exito': False, 'error': f'Error creando backup: {str(e)}'}
    
    def _accion_escaneo_completo(self, parametros: Dict[str, Any], incidente: Incidente) -> Dict[str, Any]:
        """Ejecuta acción de escaneo completo del sistema."""
        directorio = parametros.get('directorio', '/home')
        
        try:
            # Simular inicio de escaneo completo
            # En implementación real, esto iniciaría el escaneador principal
            timestamp = datetime.now().isoformat()
            
            return {
                'exito': True,
                'mensaje': f'Escaneo completo iniciado en {directorio}',
                'directorio_escaneado': directorio,
                'timestamp_inicio': timestamp
            }
            
        except Exception as e:
            return {'exito': False, 'error': f'Error iniciando escaneo: {str(e)}'}
    
    def _accion_aislar_sistema(self, parametros: Dict[str, Any], incidente: Incidente) -> Dict[str, Any]:
        """Ejecuta acción de aislamiento del sistema."""
        try:
            acciones_realizadas = []
            
            # Bloquear tráfico de red saliente
            resultado_out = subprocess.run(
                ['iptables', '-P', 'OUTPUT', 'DROP'], 
                capture_output=True
            )
            if resultado_out.returncode == 0:
                acciones_realizadas.append("Tráfico saliente bloqueado")
            
            # Bloquear tráfico de red entrante (excepto loopback)
            resultado_in = subprocess.run(
                ['iptables', '-P', 'INPUT', 'DROP'], 
                capture_output=True
            )
            if resultado_in.returncode == 0:
                acciones_realizadas.append("Tráfico entrante bloqueado")
            
            return {
                'exito': True,
                'mensaje': 'Sistema aislado de la red',
                'acciones_realizadas': acciones_realizadas,
                'advertencia': 'Para restaurar conectividad, ejecutar: iptables -P INPUT ACCEPT && iptables -P OUTPUT ACCEPT'
            }
            
        except Exception as e:
            return {'exito': False, 'error': f'Error aislando sistema: {str(e)}'}
    
    def _accion_generar_reporte(self, parametros: Dict[str, Any], incidente: Incidente) -> Dict[str, Any]:
        """Ejecuta acción de generación de reporte."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archivo_reporte = f"/var/log/ares-aegis-reporte-{timestamp}.json"
            
            reporte = {
                'incidente': incidente.to_dict(),
                'timestamp_reporte': datetime.now().isoformat(),
                'sistema': {
                    'hostname': subprocess.run(['hostname'], capture_output=True, text=True).stdout.strip(),
                    'usuario': os.getenv('USER', 'unknown'),
                    'uptime': subprocess.run(['uptime'], capture_output=True, text=True).stdout.strip()
                }
            }
            
            with open(archivo_reporte, 'w') as f:
                json.dump(reporte, f, indent=2)
            
            return {
                'exito': True,
                'mensaje': f'Reporte generado: {archivo_reporte}',
                'archivo_reporte': archivo_reporte
            }
            
        except Exception as e:
            return {'exito': False, 'error': f'Error generando reporte: {str(e)}'}


class AutomatizacionRespuesta:
    """Sistema principal de automatización de respuesta."""
    
    def __init__(self, archivo_reglas: str = "reglas_respuesta.json", siem=None):
        """
        Inicializa el sistema de automatización.
        
        Args:
            archivo_reglas: Archivo con las reglas de respuesta
            siem: Sistema SIEM para logging (opcional)
        """
        self.archivo_reglas = archivo_reglas
        self.siem = siem
        self.reglas: List[ReglaRespuesta] = []
        self.ejecutor = EjecutorAcciones()
        self.incidentes_procesados: Dict[str, Incidente] = {}
        self.cola_incidentes: List[Incidente] = []
        self.procesando = False
        
        # Cargar reglas
        self.cargar_reglas()
        
        # Inicializar reglas por defecto si no existen
        if not self.reglas:
            self.crear_reglas_por_defecto()
    
    def cargar_reglas(self):
        """Carga las reglas desde archivo."""
        try:
            if os.path.exists(self.archivo_reglas):
                with open(self.archivo_reglas, 'r') as f:
                    datos_reglas = json.load(f)
                    
                self.reglas = []
                for datos in datos_reglas:
                    regla = ReglaRespuesta(**datos)
                    self.reglas.append(regla)
                
                if self.siem:
                    self.siem.log_evento('INFO', 'automatizacion_respuesta', 
                                       f'Cargadas {len(self.reglas)} reglas desde {self.archivo_reglas}')
        except Exception as e:
            if self.siem:
                self.siem.log_evento('ERROR', 'automatizacion_respuesta', 
                                   f'Error cargando reglas: {str(e)}')
    
    def guardar_reglas(self):
        """Guarda las reglas a archivo."""
        try:
            datos_reglas = [asdict(regla) for regla in self.reglas]
            
            with open(self.archivo_reglas, 'w') as f:
                json.dump(datos_reglas, f, indent=2)
                
            if self.siem:
                self.siem.log_evento('INFO', 'automatizacion_respuesta', 
                                   f'Reglas guardadas en {self.archivo_reglas}')
        except Exception as e:
            if self.siem:
                self.siem.log_evento('ERROR', 'automatizacion_respuesta', 
                                   f'Error guardando reglas: {str(e)}')
    
    def crear_reglas_por_defecto(self):
        """Crea reglas de respuesta por defecto."""
        reglas_defecto = [
            ReglaRespuesta(
                id="malware_critico",
                nombre="Respuesta a Malware Crítico",
                condiciones={
                    "tipo": ["malware_detectado", "virus_encontrado"],
                    "severidad": ["critica", "alta"]
                },
                acciones=[
                    {"tipo": "cuarentena", "parametros": {"archivo": "${datos.archivo}"}},
                    {"tipo": "notificacion", "parametros": {"metodo": "wall", "mensaje": "ALERTA: Malware detectado y puesto en cuarentena"}},
                    {"tipo": "generar_reporte", "parametros": {}}
                ],
                prioridad=1,
                descripcion="Respuesta automática para malware crítico"
            ),
            ReglaRespuesta(
                id="conexion_sospechosa",
                nombre="Bloqueo de Conexiones Sospechosas",
                condiciones={
                    "tipo": ["conexion_sospechosa", "intrusion_detectada"],
                    "severidad": ["alta", "critica"]
                },
                acciones=[
                    {"tipo": "bloquear_ip", "parametros": {"ip": "${datos.ip_origen}"}},
                    {"tipo": "notificacion", "parametros": {"metodo": "syslog"}},
                    {"tipo": "generar_reporte", "parametros": {}}
                ],
                prioridad=2,
                descripcion="Bloqueo automático de IPs sospechosas"
            ),
            ReglaRespuesta(
                id="proceso_malicioso",
                nombre="Terminación de Procesos Maliciosos",
                condiciones={
                    "tipo": ["proceso_sospechoso", "comportamiento_anomalo"],
                    "severidad": ["alta", "critica"]
                },
                acciones=[
                    {"tipo": "terminar_proceso", "parametros": {"pid": "${datos.pid}"}},
                    {"tipo": "backup_archivo", "parametros": {"archivo": "${datos.ejecutable}"}},
                    {"tipo": "cuarentena", "parametros": {"archivo": "${datos.ejecutable}"}},
                    {"tipo": "notificacion", "parametros": {"metodo": "wall"}}
                ],
                prioridad=1,
                descripcion="Terminación y cuarentena de procesos maliciosos"
            ),
            ReglaRespuesta(
                id="incidente_critico",
                nombre="Aislamiento por Incidente Crítico",
                condiciones={
                    "severidad": ["critica"],
                    "tipo": ["ransomware", "rootkit_detectado", "exfiltracion_datos"]
                },
                acciones=[
                    {"tipo": "aislar_sistema", "parametros": {}},
                    {"tipo": "notificacion", "parametros": {"metodo": "wall", "mensaje": "SISTEMA AISLADO - Incidente crítico detectado"}},
                    {"tipo": "generar_reporte", "parametros": {}},
                    {"tipo": "escaneo_completo", "parametros": {"directorio": "/"}}
                ],
                prioridad=0,
                descripcion="Aislamiento completo del sistema por incidentes críticos"
            )
        ]
        
        self.reglas = reglas_defecto
        self.guardar_reglas()
        
        if self.siem:
            self.siem.log_evento('INFO', 'automatizacion_respuesta', 
                               'Reglas por defecto creadas y guardadas')
    
    def procesar_incidente(self, incidente: Incidente) -> Dict[str, Any]:
        """
        Procesa un incidente y ejecuta las acciones correspondientes.
        
        Args:
            incidente: Incidente a procesar
            
        Returns:
            Dict con resultado del procesamiento
        """
        if self.siem:
            self.siem.log_evento('INFO', 'automatizacion_respuesta', 
                               f'Procesando incidente {incidente.id}: {incidente.tipo}')
        
        # Buscar reglas aplicables
        reglas_aplicables = []
        for regla in self.reglas:
            if regla.habilitada and regla.coincide_con_incidente(incidente):
                reglas_aplicables.append(regla)
        
        # Ordenar por prioridad
        reglas_aplicables.sort(key=lambda r: r.prioridad)
        
        if not reglas_aplicables:
            return {
                'incidente_id': incidente.id,
                'reglas_aplicadas': 0,
                'acciones_ejecutadas': [],
                'mensaje': 'No se encontraron reglas aplicables'
            }
        
        # Ejecutar acciones de las reglas aplicables
        acciones_ejecutadas = []
        for regla in reglas_aplicables:
            for accion_def in regla.acciones:
                tipo_accion = accion_def['tipo']
                parametros = accion_def.get('parametros', {})
                
                # Resolver variables en parámetros
                parametros_resueltos = self._resolver_variables(parametros, incidente)
                
                # Ejecutar acción
                resultado = self.ejecutor.ejecutar_accion(tipo_accion, parametros_resueltos, incidente)
                
                accion_ejecutada = {
                    'regla_id': regla.id,
                    'tipo': tipo_accion,
                    'parametros': parametros_resueltos,
                    'resultado': resultado
                }
                
                acciones_ejecutadas.append(accion_ejecutada)
                if incidente.acciones_ejecutadas is not None:
                    incidente.acciones_ejecutadas.append(f"{regla.id}:{tipo_accion}")
                
                if self.siem:
                    estado = 'EXITOSA' if resultado.get('exito') else 'FALLIDA'
                    self.siem.log_evento('INFO', 'automatizacion_respuesta', 
                                       f'Acción {tipo_accion} {estado} para incidente {incidente.id}')
        
        # Actualizar estado del incidente
        incidente.estado = "procesado"
        self.incidentes_procesados[incidente.id] = incidente
        
        return {
            'incidente_id': incidente.id,
            'reglas_aplicadas': len(reglas_aplicables),
            'acciones_ejecutadas': acciones_ejecutadas,
            'timestamp': datetime.now().isoformat()
        }
    
    def _resolver_variables(self, parametros: Dict[str, Any], incidente: Incidente) -> Dict[str, Any]:
        """Resuelve variables en los parámetros usando datos del incidente."""
        parametros_resueltos = {}
        
        for clave, valor in parametros.items():
            if isinstance(valor, str) and valor.startswith('${'):
                # Extraer nombre de variable
                variable = valor[2:-1]  # Remover ${ y }
                
                if variable.startswith('datos.'):
                    # Variable de datos adicionales
                    campo_datos = variable[6:]  # Remover 'datos.'
                    valor_resuelto = incidente.datos_adicionales.get(campo_datos, valor)
                    parametros_resueltos[clave] = valor_resuelto
                else:
                    # Variable de incidente
                    if hasattr(incidente, variable):
                        parametros_resueltos[clave] = getattr(incidente, variable)
                    else:
                        parametros_resueltos[clave] = valor
            else:
                parametros_resueltos[clave] = valor
        
        return parametros_resueltos
    
    def agregar_regla(self, regla: ReglaRespuesta):
        """Agrega una nueva regla de respuesta."""
        self.reglas.append(regla)
        self.guardar_reglas()
        
        if self.siem:
            self.siem.log_evento('INFO', 'automatizacion_respuesta', 
                               f'Nueva regla agregada: {regla.id}')
    
    def eliminar_regla(self, regla_id: str) -> bool:
        """Elimina una regla de respuesta."""
        reglas_iniciales = len(self.reglas)
        self.reglas = [r for r in self.reglas if r.id != regla_id]
        
        if len(self.reglas) < reglas_iniciales:
            self.guardar_reglas()
            if self.siem:
                self.siem.log_evento('INFO', 'automatizacion_respuesta', 
                                   f'Regla eliminada: {regla_id}')
            return True
        
        return False
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas del sistema de automatización."""
        total_reglas = len(self.reglas)
        reglas_habilitadas = len([r for r in self.reglas if r.habilitada])
        total_incidentes = len(self.incidentes_procesados)
        
        # Estadísticas por severidad
        severidades = {}
        for incidente in self.incidentes_procesados.values():
            sev = incidente.severidad.value
            severidades[sev] = severidades.get(sev, 0) + 1
        
        return {
            'reglas': {
                'total': total_reglas,
                'habilitadas': reglas_habilitadas,
                'deshabilitadas': total_reglas - reglas_habilitadas
            },
            'incidentes': {
                'total_procesados': total_incidentes,
                'por_severidad': severidades
            },
            'timestamp': datetime.now().isoformat()
        }
