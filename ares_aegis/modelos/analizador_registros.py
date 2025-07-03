#!/usr/bin/env python3
"""
Analizador de Registros - Ares Aegis
Módulo para análisis de archivos de log del sistema en busca de patrones de ataque

Este módulo lee y analiza logs del sistema para detectar actividad sospechosa,
patrones de ataque y eventos de seguridad relevantes.

Autor: DogSoulDev
Versión: 2.0.0 - "Los Escribas de Temis"
"""

import os
import re
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Pattern, NamedTuple
from collections import defaultdict, deque
from ..utilidades.ayuda_logging import configurar_logger_modulo


class EventoLog(NamedTuple):
    """Evento extraído de un log."""
    timestamp: datetime
    fuente: str
    nivel: str
    mensaje: str
    ip_origen: Optional[str]
    usuario: Optional[str]
    metadatos: Dict[str, Any]


class PatronAtaque(NamedTuple):
    """Patrón de ataque detectado."""
    tipo: str
    descripcion: str
    eventos_relacionados: List[EventoLog]
    nivel_gravedad: str
    timestamp_deteccion: datetime
    metadatos: Dict[str, Any]


class EstadisticasLog:
    """Estadísticas de análisis de logs."""
    
    def __init__(self, fuente: str):
        """
        Inicializa las estadísticas para una fuente de log.
        
        Args:
            fuente: Nombre de la fuente del log
        """
        self.fuente = fuente
        self.timestamp_inicio = datetime.now()
        self.lineas_procesadas = 0
        self.eventos_extraidos = 0
        self.patrones_detectados = 0
        self.errores_parseo = 0
        
        # Contadores por tipo
        self.eventos_por_tipo: Dict[str, int] = defaultdict(int)
        self.ips_unicas: Set[str] = set()
        self.usuarios_unicos: Set[str] = set()
        
        # Eventos recientes (últimos 100)
        self.eventos_recientes: deque = deque(maxlen=100)
    
    def agregar_evento(self, evento: EventoLog):
        """Agrega un evento a las estadísticas."""
        self.eventos_extraidos += 1
        self.eventos_por_tipo[evento.nivel] += 1
        self.eventos_recientes.append(evento)
        
        if evento.ip_origen:
            self.ips_unicas.add(evento.ip_origen)
        
        if evento.usuario:
            self.usuarios_unicos.add(evento.usuario)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte las estadísticas a diccionario."""
        return {
            'fuente': self.fuente,
            'timestamp_inicio': self.timestamp_inicio.isoformat(),
            'lineas_procesadas': self.lineas_procesadas,
            'eventos_extraidos': self.eventos_extraidos,
            'patrones_detectados': self.patrones_detectados,
            'errores_parseo': self.errores_parseo,
            'eventos_por_tipo': dict(self.eventos_por_tipo),
            'ips_unicas_count': len(self.ips_unicas),
            'usuarios_unicos_count': len(self.usuarios_unicos),
            'eventos_recientes_count': len(self.eventos_recientes)
        }


class AnalizadorRegistros:
    """Analizador principal de archivos de log del sistema."""
    
    def __init__(self, siem=None):
        """
        Inicializa el analizador de registros.
        
        Args:
            siem: Instancia del SIEM para registro de eventos
        """
        self.logger = configurar_logger_modulo("analizador_registros")
        self.siem = siem
        
        # Estado del analizador
        self.analizando = False
        self.hilo_analisis: Optional[threading.Thread] = None
        self.intervalo_analisis = 60  # segundos
        
        # Configuración de logs a monitorear
        self.archivos_log = {
            'auth': '/var/log/auth.log',
            'syslog': '/var/log/syslog',
            'kern': '/var/log/kern.log',
            'daemon': '/var/log/daemon.log',
            'messages': '/var/log/messages',
            'secure': '/var/log/secure',  # RHEL/CentOS
            'access': '/var/log/apache2/access.log',  # Apache si existe
            'error': '/var/log/apache2/error.log',   # Apache si existe
            'nginx_access': '/var/log/nginx/access.log',  # Nginx si existe
            'nginx_error': '/var/log/nginx/error.log'     # Nginx si existe
        }
        
        # Estado de archivos monitoreados
        self.posiciones_archivo: Dict[str, int] = {}
        self.estadisticas_archivos: Dict[str, EstadisticasLog] = {}
        
        # Patrones detectados
        self.patrones_detectados: List[PatronAtaque] = []
        
        # Configuración de detección
        self.config_deteccion = {
            'ventana_tiempo_fuerza_bruta': 300,  # 5 minutos
            'umbral_intentos_ssh': 5,
            'umbral_intentos_sudo': 10,
            'ventana_tiempo_escaneo_puertos': 60,  # 1 minuto
            'umbral_conexiones_diferentes': 10,
            'patrones_malware_conocidos': [
                'backdoor', 'rootkit', 'trojan', 'malware',
                'ransomware', 'cryptolock', 'wannacry'
            ]
        }
        
        # Compilar patrones de regex para eficiencia
        self._compilar_patrones_regex()
        
        # Contadores de eventos para detección de patrones
        self.contadores_ssh: Dict[str, List[datetime]] = defaultdict(list)
        self.contadores_sudo: Dict[str, List[datetime]] = defaultdict(list)
        self.contadores_conexiones: Dict[str, List[datetime]] = defaultdict(list)
        
        self.logger.info("Los Escribas de Temis han despertado para descifrar los pergaminos del sistema")
    
    def _compilar_patrones_regex(self):
        """Compila patrones de expresiones regulares para análisis eficiente."""
        self.patrones_regex = {
            # Patrones SSH
            'ssh_failed_password': re.compile(
                r'Failed password for (?:invalid user )?(\w+) from ([\d.]+) port (\d+)'
            ),
            'ssh_invalid_user': re.compile(
                r'Invalid user (\w+) from ([\d.]+) port (\d+)'
            ),
            'ssh_connection_closed': re.compile(
                r'Connection closed by ([\d.]+) port (\d+)'
            ),
            'ssh_accepted': re.compile(
                r'Accepted (?:password|publickey) for (\w+) from ([\d.]+) port (\d+)'
            ),
            
            # Patrones sudo
            'sudo_command': re.compile(
                r'(\w+) : TTY=(\S+) ; PWD=(\S+) ; USER=(\w+) ; COMMAND=(.+)'
            ),
            'sudo_failed': re.compile(
                r'(\w+) : (?:command not allowed|authentication failure)'
            ),
            
            # Patrones de red
            'iptables_drop': re.compile(
                r'IN=(\w*) OUT=(\w*) SRC=([\d.]+) DST=([\d.]+).*PROTO=(\w+).*DPT=(\d+)'
            ),
            'iptables_accept': re.compile(
                r'ACCEPT.*SRC=([\d.]+) DST=([\d.]+).*DPT=(\d+)'
            ),
            
            # Patrones generales de IP
            'ip_address': re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'),
            
            # Patrones de timestamp
            'timestamp_syslog': re.compile(
                r'(\w{3} \d{1,2} \d{2}:\d{2}:\d{2})'
            ),
            'timestamp_iso': re.compile(
                r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})'
            ),
            
            # Patrones de procesos sospechosos
            'proceso_killed': re.compile(
                r'Killed process (\d+) \(([^)]+)\)'
            ),
            'out_of_memory': re.compile(
                r'Out of memory: Kill process (\d+) \(([^)]+)\)'
            ),
            
            # Patrones de servicios
            'service_start': re.compile(
                r'(?:Started|Starting) (.+)'
            ),
            'service_stop': re.compile(
                r'(?:Stopped|Stopping) (.+)'
            ),
            'service_failed': re.compile(
                r'(?:Failed|failed) (.+)'
            )
        }
    
    def iniciar_analisis(self):
        """Inicia el análisis continuo de logs."""
        if self.analizando:
            self.logger.warning("Los Escribas ya descifran los pergaminos del reino")
            return
        
        # Verificar archivos de log existentes
        archivos_existentes = {}
        for nombre, ruta in self.archivos_log.items():
            if os.path.exists(ruta) and os.access(ruta, os.R_OK):
                archivos_existentes[nombre] = ruta
                self.estadisticas_archivos[nombre] = EstadisticasLog(nombre)
                # Obtener posición al final del archivo para monitoreo continuo
                with open(ruta, 'r', encoding='utf-8', errors='ignore') as f:
                    f.seek(0, 2)  # Ir al final
                    self.posiciones_archivo[nombre] = f.tell()
        
        if not archivos_existentes:
            self.logger.warning("No se encontraron archivos de log legibles para analizar")
            return
        
        self.archivos_log = archivos_existentes
        self.analizando = True
        
        self.hilo_analisis = threading.Thread(target=self._loop_analisis, daemon=True)
        self.hilo_analisis.start()
        
        if self.siem:
            from .siem import TipoEvento
            self.siem.registrar_evento(
                TipoEvento.SISTEMA_INICIADO,
                "Escribas de Temis activados para descifrar pergaminos",
                {
                    "archivos_monitoreados": list(archivos_existentes.keys()),
                    "componente": "analizador_registros"
                },
                "MEDIO"
            )
        
        self.logger.info(f"Los Escribas comienzan a descifrar {len(archivos_existentes)} pergaminos sagrados")
    
    def detener_analisis(self):
        """Detiene el análisis de logs."""
        if not self.analizando:
            return
        
        self.analizando = False
        
        if self.hilo_analisis:
            self.hilo_analisis.join(timeout=15)
        
        if self.siem:
            from .siem import TipoEvento
            self.siem.registrar_evento(
                TipoEvento.SISTEMA_DETENIDO,
                "Escribas de Temis han cerrado los pergaminos",
                {
                    "patrones_detectados": len(self.patrones_detectados),
                    "archivos_analizados": len(self.estadisticas_archivos)
                },
                "MEDIO"
            )
        
        self.logger.info("Los Escribas de Temis han cerrado los pergaminos para el descanso")
    
    def _loop_analisis(self):
        """Loop principal de análisis de logs."""
        self.logger.info("Iniciando ciclo de descifrado de pergaminos")
        
        while self.analizando:
            try:
                self._analizar_nuevas_entradas()
                self._detectar_patrones_globales()
                self._limpiar_contadores_antiguos()
                time.sleep(self.intervalo_analisis)
                
            except Exception as e:
                self.logger.error(f"Error en ciclo de análisis de logs: {e}")
                time.sleep(self.intervalo_analisis * 2)
    
    def _analizar_nuevas_entradas(self):
        """Analiza nuevas entradas en todos los archivos de log monitoreados."""
        for nombre_archivo, ruta_archivo in self.archivos_log.items():
            try:
                self._procesar_archivo_log(nombre_archivo, ruta_archivo)
            except Exception as e:
                self.logger.error(f"Error procesando log {nombre_archivo}: {e}")
    
    def _procesar_archivo_log(self, nombre_archivo: str, ruta_archivo: str):
        """Procesa un archivo de log específico desde la última posición."""
        if not os.path.exists(ruta_archivo):
            return
        
        estadisticas = self.estadisticas_archivos[nombre_archivo]
        posicion_actual = self.posiciones_archivo.get(nombre_archivo, 0)
        
        try:
            with open(ruta_archivo, 'r', encoding='utf-8', errors='ignore') as f:
                # Verificar si el archivo se ha truncado (rotación de logs)
                tamaño_archivo = os.path.getsize(ruta_archivo)
                if posicion_actual > tamaño_archivo:
                    posicion_actual = 0
                
                f.seek(posicion_actual)
                nuevas_lineas = f.readlines()
                
                # Actualizar posición
                self.posiciones_archivo[nombre_archivo] = f.tell()
                
                # Procesar nuevas líneas
                for linea in nuevas_lineas:
                    linea = linea.strip()
                    if linea:
                        self._procesar_linea_log(linea, nombre_archivo, estadisticas)
                
                estadisticas.lineas_procesadas += len(nuevas_lineas)
        
        except Exception as e:
            self.logger.error(f"Error leyendo archivo {ruta_archivo}: {e}")
            estadisticas.errores_parseo += 1
    
    def _procesar_linea_log(self, linea: str, fuente: str, estadisticas: EstadisticasLog):
        """Procesa una línea individual de log."""
        try:
            # Extraer timestamp
            timestamp = self._extraer_timestamp(linea)
            
            # Extraer información básica
            ip_origen = self._extraer_ip(linea)
            usuario = self._extraer_usuario(linea, fuente)
            nivel = self._determinar_nivel_evento(linea)
            
            # Crear evento
            evento = EventoLog(
                timestamp=timestamp,
                fuente=fuente,
                nivel=nivel,
                mensaje=linea,
                ip_origen=ip_origen,
                usuario=usuario,
                metadatos={}
            )
            
            # Agregar a estadísticas
            estadisticas.agregar_evento(evento)
            
            # Análisis específico por tipo de log
            if fuente == 'auth':
                self._analizar_evento_auth(evento)
            elif fuente == 'syslog':
                self._analizar_evento_syslog(evento)
            elif fuente == 'kern':
                self._analizar_evento_kernel(evento)
            
            # Análisis general de patrones
            self._analizar_patrones_linea(evento)
        
        except Exception as e:
            self.logger.debug(f"Error procesando línea de log: {e}")
            estadisticas.errores_parseo += 1
    
    def _extraer_timestamp(self, linea: str) -> datetime:
        """Extrae timestamp de una línea de log."""
        # Intentar formato ISO
        match = self.patrones_regex['timestamp_iso'].search(linea)
        if match:
            try:
                return datetime.fromisoformat(match.group(1))
            except:
                pass
        
        # Intentar formato syslog
        match = self.patrones_regex['timestamp_syslog'].search(linea)
        if match:
            try:
                timestamp_str = match.group(1)
                # Agregar año actual ya que syslog no lo incluye
                año_actual = datetime.now().year
                timestamp_completo = f"{año_actual} {timestamp_str}"
                return datetime.strptime(timestamp_completo, "%Y %b %d %H:%M:%S")
            except:
                pass
        
        # Si no se puede extraer, usar tiempo actual
        return datetime.now()
    
    def _extraer_ip(self, linea: str) -> Optional[str]:
        """Extrae dirección IP de una línea de log."""
        match = self.patrones_regex['ip_address'].search(linea)
        return match.group(0) if match else None
    
    def _extraer_usuario(self, linea: str, fuente: str) -> Optional[str]:
        """Extrae nombre de usuario de una línea de log."""
        if fuente == 'auth':
            # Intentar patrones SSH
            for patron_name in ['ssh_failed_password', 'ssh_accepted']:
                match = self.patrones_regex[patron_name].search(linea)
                if match:
                    return match.group(1)
            
            # Intentar patrón sudo
            match = self.patrones_regex['sudo_command'].search(linea)
            if match:
                return match.group(1)
        
        return None
    
    def _determinar_nivel_evento(self, linea: str) -> str:
        """Determina el nivel de gravedad de un evento."""
        linea_lower = linea.lower()
        
        if any(keyword in linea_lower for keyword in ['error', 'failed', 'failure', 'denied']):
            return 'ERROR'
        elif any(keyword in linea_lower for keyword in ['warning', 'warn']):
            return 'WARNING'
        elif any(keyword in linea_lower for keyword in ['info', 'notice']):
            return 'INFO'
        elif any(keyword in linea_lower for keyword in ['debug']):
            return 'DEBUG'
        else:
            return 'INFO'
    
    def _analizar_evento_auth(self, evento: EventoLog):
        """Analiza eventos del log de autenticación."""
        linea = evento.mensaje
        
        # Detectar intentos fallidos SSH
        match = self.patrones_regex['ssh_failed_password'].search(linea)
        if match:
            usuario = match.group(1)
            ip = match.group(2)
            
            # Agregar a contador de intentos SSH
            self.contadores_ssh[ip].append(evento.timestamp)
            
            # Verificar si excede el umbral
            self._verificar_fuerza_bruta_ssh(ip, evento)
        
        # Detectar usuarios inválidos SSH
        match = self.patrones_regex['ssh_invalid_user'].search(linea)
        if match:
            usuario = match.group(1)
            ip = match.group(2)
            
            self._detectar_escaneo_usuarios(ip, usuario, evento)
        
        # Detectar intentos sudo fallidos
        if 'sudo' in linea and ('authentication failure' in linea or 'command not allowed' in linea):
            match = self.patrones_regex['sudo_failed'].search(linea)
            if match:
                usuario = match.group(1)
                self.contadores_sudo[usuario].append(evento.timestamp)
                self._verificar_escalada_privilegios(usuario, evento)
    
    def _analizar_evento_syslog(self, evento: EventoLog):
        """Analiza eventos del syslog general."""
        linea = evento.mensaje
        
        # Detectar procesos eliminados por OOM
        match = self.patrones_regex['out_of_memory'].search(linea)
        if match:
            pid = match.group(1)
            proceso = match.group(2)
            self._detectar_agotamiento_memoria(pid, proceso, evento)
        
        # Detectar servicios que fallan repetidamente
        match = self.patrones_regex['service_failed'].search(linea)
        if match:
            servicio = match.group(1)
            self._detectar_falla_servicio(servicio, evento)
    
    def _analizar_evento_kernel(self, evento: EventoLog):
        """Analiza eventos del kernel."""
        linea = evento.mensaje
        
        # Detectar bloqueos de iptables
        match = self.patrones_regex['iptables_drop'].search(linea)
        if match:
            src_ip = match.group(3)
            dst_ip = match.group(4)
            puerto = match.group(6)
            
            self._detectar_escaneo_puertos(src_ip, dst_ip, puerto, evento)
    
    def _analizar_patrones_linea(self, evento: EventoLog):
        """Analiza patrones generales en cualquier línea de log."""
        linea_lower = evento.mensaje.lower()
        
        # Buscar patrones de malware conocidos
        for patron_malware in self.config_deteccion['patrones_malware_conocidos']:
            if patron_malware in linea_lower:
                self._detectar_referencia_malware(patron_malware, evento)
                break
    
    def _verificar_fuerza_bruta_ssh(self, ip: str, evento: EventoLog):
        """Verifica si una IP está realizando un ataque de fuerza bruta SSH."""
        ahora = evento.timestamp
        ventana = timedelta(seconds=self.config_deteccion['ventana_tiempo_fuerza_bruta'])
        
        # Filtrar intentos en la ventana de tiempo
        intentos_recientes = [
            t for t in self.contadores_ssh[ip]
            if ahora - t <= ventana
        ]
        
        if len(intentos_recientes) >= self.config_deteccion['umbral_intentos_ssh']:
            self._crear_patron_ataque(
                tipo="fuerza_bruta_ssh",
                descripcion=f"Ataque de fuerza bruta SSH desde {ip}: {len(intentos_recientes)} intentos en {self.config_deteccion['ventana_tiempo_fuerza_bruta']}s",
                eventos_relacionados=[evento],
                nivel_gravedad="ALTO",
                metadatos={
                    'ip_atacante': ip,
                    'intentos_total': len(intentos_recientes),
                    'ventana_tiempo': self.config_deteccion['ventana_tiempo_fuerza_bruta']
                }
            )
    
    def _detectar_escaneo_usuarios(self, ip: str, usuario: str, evento: EventoLog):
        """Detecta escaneo de usuarios válidos."""
        if usuario in ['admin', 'administrator', 'root', 'test', 'guest', 'oracle', 'postgres']:
            self._crear_patron_ataque(
                tipo="escaneo_usuarios",
                descripcion=f"Intento de acceso con usuario común '{usuario}' desde {ip}",
                eventos_relacionados=[evento],
                nivel_gravedad="MEDIO",
                metadatos={
                    'ip_origen': ip,
                    'usuario_intentado': usuario
                }
            )
    
    def _verificar_escalada_privilegios(self, usuario: str, evento: EventoLog):
        """Verifica intentos de escalada de privilegios."""
        ahora = evento.timestamp
        ventana = timedelta(seconds=self.config_deteccion['ventana_tiempo_fuerza_bruta'])
        
        intentos_recientes = [
            t for t in self.contadores_sudo[usuario]
            if ahora - t <= ventana
        ]
        
        if len(intentos_recientes) >= self.config_deteccion['umbral_intentos_sudo']:
            self._crear_patron_ataque(
                tipo="escalada_privilegios",
                descripcion=f"Múltiples intentos fallidos de sudo por usuario {usuario}: {len(intentos_recientes)} intentos",
                eventos_relacionados=[evento],
                nivel_gravedad="ALTO",
                metadatos={
                    'usuario': usuario,
                    'intentos_total': len(intentos_recientes)
                }
            )
    
    def _detectar_agotamiento_memoria(self, pid: str, proceso: str, evento: EventoLog):
        """Detecta agotamiento de memoria por procesos."""
        self._crear_patron_ataque(
            tipo="agotamiento_memoria",
            descripcion=f"Proceso {proceso} (PID: {pid}) eliminado por agotamiento de memoria",
            eventos_relacionados=[evento],
            nivel_gravedad="MEDIO",
            metadatos={
                'pid': pid,
                'proceso': proceso
            }
        )
    
    def _detectar_falla_servicio(self, servicio: str, evento: EventoLog):
        """Detecta fallos repetidos de servicios."""
        # Por simplicidad, cada falla se considera un patrón menor
        self._crear_patron_ataque(
            tipo="falla_servicio",
            descripcion=f"Falla del servicio: {servicio}",
            eventos_relacionados=[evento],
            nivel_gravedad="BAJO",
            metadatos={
                'servicio': servicio
            }
        )
    
    def _detectar_escaneo_puertos(self, src_ip: str, dst_ip: str, puerto: str, evento: EventoLog):
        """Detecta posibles escaneos de puertos."""
        # Agregar conexión al contador
        self.contadores_conexiones[src_ip].append(evento.timestamp)
        
        ahora = evento.timestamp
        ventana = timedelta(seconds=self.config_deteccion['ventana_tiempo_escaneo_puertos'])
        
        conexiones_recientes = [
            t for t in self.contadores_conexiones[src_ip]
            if ahora - t <= ventana
        ]
        
        if len(conexiones_recientes) >= self.config_deteccion['umbral_conexiones_diferentes']:
            self._crear_patron_ataque(
                tipo="escaneo_puertos",
                descripcion=f"Posible escaneo de puertos desde {src_ip}: {len(conexiones_recientes)} conexiones en {self.config_deteccion['ventana_tiempo_escaneo_puertos']}s",
                eventos_relacionados=[evento],
                nivel_gravedad="MEDIO",
                metadatos={
                    'ip_origen': src_ip,
                    'ip_destino': dst_ip,
                    'puerto': puerto,
                    'conexiones_total': len(conexiones_recientes)
                }
            )
    
    def _detectar_referencia_malware(self, patron_malware: str, evento: EventoLog):
        """Detecta referencias a malware conocido."""
        self._crear_patron_ataque(
            tipo="referencia_malware",
            descripcion=f"Referencia a malware conocido detectada: {patron_malware}",
            eventos_relacionados=[evento],
            nivel_gravedad="ALTO",
            metadatos={
                'patron_malware': patron_malware,
                'fuente_log': evento.fuente
            }
        )
    
    def _crear_patron_ataque(self, tipo: str, descripcion: str, eventos_relacionados: List[EventoLog],
                           nivel_gravedad: str, metadatos: Dict[str, Any]):
        """Crea un nuevo patrón de ataque detectado."""
        patron = PatronAtaque(
            tipo=tipo,
            descripcion=descripcion,
            eventos_relacionados=eventos_relacionados,
            nivel_gravedad=nivel_gravedad,
            timestamp_deteccion=datetime.now(),
            metadatos=metadatos
        )
        
        self.patrones_detectados.append(patron)
        
        # Notificar al SIEM
        if self.siem:
            from .siem import TipoEvento
            
            # Mapear nivel de gravedad a tipo de evento SIEM
            tipo_evento = TipoEvento.AMENAZA_DETECTADA if nivel_gravedad == "ALTO" else TipoEvento.PROCESO_SOSPECHOSO
            
            self.siem.registrar_evento(
                tipo_evento,
                f"Los Escribas revelan un patrón maligno: {descripcion}",
                {
                    'tipo_patron': tipo,
                    'nivel_gravedad': nivel_gravedad,
                    'eventos_relacionados': len(eventos_relacionados),
                    'metadatos': metadatos
                },
                nivel_gravedad
            )
        
        self.logger.warning(f"Patrón de ataque detectado: {descripcion}")
        
        # Actualizar estadísticas
        for evento in eventos_relacionados:
            if evento.fuente in self.estadisticas_archivos:
                self.estadisticas_archivos[evento.fuente].patrones_detectados += 1
    
    def _detectar_patrones_globales(self):
        """Detecta patrones que requieren análisis global de múltiples fuentes."""
        # Detectar correlaciones entre diferentes fuentes de log
        timestamp_actual = datetime.now()
        ventana_correlacion = timedelta(minutes=10)
        
        # Buscar patrones recientes
        patrones_recientes = [
            p for p in self.patrones_detectados
            if timestamp_actual - p.timestamp_deteccion <= ventana_correlacion
        ]
        
        # Agrupar por IP origen
        ips_atacantes = defaultdict(list)
        for patron in patrones_recientes:
            ip = patron.metadatos.get('ip_atacante') or patron.metadatos.get('ip_origen')
            if ip:
                ips_atacantes[ip].append(patron)
        
        # Detectar IPs con múltiples tipos de ataque
        for ip, patrones_ip in ips_atacantes.items():
            tipos_ataque = set(p.tipo for p in patrones_ip)
            if len(tipos_ataque) >= 2:
                self._crear_patron_ataque(
                    tipo="ataque_coordinado",
                    descripcion=f"Ataque coordinado desde {ip}: {len(tipos_ataque)} tipos diferentes de ataque",
                    eventos_relacionados=[],
                    nivel_gravedad="CRITICO",
                    metadatos={
                        'ip_atacante': ip,
                        'tipos_ataque': list(tipos_ataque),
                        'patrones_relacionados': len(patrones_ip)
                    }
                )
    
    def _limpiar_contadores_antiguos(self):
        """Limpia contadores antiguos para evitar uso excesivo de memoria."""
        timestamp_limite = datetime.now() - timedelta(hours=1)
        
        # Limpiar contadores SSH
        for ip in list(self.contadores_ssh.keys()):
            self.contadores_ssh[ip] = [
                t for t in self.contadores_ssh[ip]
                if t > timestamp_limite
            ]
            if not self.contadores_ssh[ip]:
                del self.contadores_ssh[ip]
        
        # Limpiar contadores sudo
        for usuario in list(self.contadores_sudo.keys()):
            self.contadores_sudo[usuario] = [
                t for t in self.contadores_sudo[usuario]
                if t > timestamp_limite
            ]
            if not self.contadores_sudo[usuario]:
                del self.contadores_sudo[usuario]
        
        # Limpiar contadores de conexiones
        for ip in list(self.contadores_conexiones.keys()):
            self.contadores_conexiones[ip] = [
                t for t in self.contadores_conexiones[ip]
                if t > timestamp_limite
            ]
            if not self.contadores_conexiones[ip]:
                del self.contadores_conexiones[ip]
        
        # Limpiar patrones antiguos
        if len(self.patrones_detectados) > 1000:
            self.patrones_detectados = self.patrones_detectados[-500:]
    
    def buscar_eventos_por_ip(self, ip: str, horas: int = 24) -> List[EventoLog]:
        """
        Busca todos los eventos relacionados con una IP específica.
        
        Args:
            ip: Dirección IP a buscar
            horas: Número de horas hacia atrás para buscar
            
        Returns:
            Lista de eventos relacionados con la IP
        """
        timestamp_limite = datetime.now() - timedelta(hours=horas)
        eventos_encontrados = []
        
        for estadisticas in self.estadisticas_archivos.values():
            for evento in estadisticas.eventos_recientes:
                if (evento.ip_origen == ip and 
                    evento.timestamp > timestamp_limite):
                    eventos_encontrados.append(evento)
        
        return sorted(eventos_encontrados, key=lambda e: e.timestamp, reverse=True)
    
    def buscar_eventos_por_usuario(self, usuario: str, horas: int = 24) -> List[EventoLog]:
        """
        Busca todos los eventos relacionados con un usuario específico.
        
        Args:
            usuario: Nombre de usuario a buscar
            horas: Número de horas hacia atrás para buscar
            
        Returns:
            Lista de eventos relacionados con el usuario
        """
        timestamp_limite = datetime.now() - timedelta(hours=horas)
        eventos_encontrados = []
        
        for estadisticas in self.estadisticas_archivos.values():
            for evento in estadisticas.eventos_recientes:
                if (evento.usuario == usuario and 
                    evento.timestamp > timestamp_limite):
                    eventos_encontrados.append(evento)
        
        return sorted(eventos_encontrados, key=lambda e: e.timestamp, reverse=True)
    
    def obtener_estadisticas_generales(self) -> Dict[str, Any]:
        """Obtiene estadísticas generales del analizador."""
        total_lineas = sum(stats.lineas_procesadas for stats in self.estadisticas_archivos.values())
        total_eventos = sum(stats.eventos_extraidos for stats in self.estadisticas_archivos.values())
        total_errores = sum(stats.errores_parseo for stats in self.estadisticas_archivos.values())
        
        return {
            'analizando': self.analizando,
            'archivos_monitoreados': len(self.archivos_log),
            'total_lineas_procesadas': total_lineas,
            'total_eventos_extraidos': total_eventos,
            'total_errores_parseo': total_errores,
            'patrones_detectados': len(self.patrones_detectados),
            'ips_atacantes_activas': len(self.contadores_ssh) + len(self.contadores_conexiones),
            'timestamp_ultimo_analisis': datetime.now().isoformat(),
            'estadisticas_por_archivo': {
                nombre: stats.to_dict() 
                for nombre, stats in self.estadisticas_archivos.items()
            }
        }
    
    def generar_reporte_markdown(self) -> str:
        """Genera un reporte detallado en formato Markdown."""
        stats = self.obtener_estadisticas_generales()
        
        md = "# 📜 Informe de los Escribas de Temis\n\n"
        md += f"**Estado de los Escribas:** {'🟢 Descifrando' if self.analizando else '🔴 En reposo'}\n"
        md += f"**Pergaminos Monitoreados:** {stats['archivos_monitoreados']}\n"
        md += f"**Líneas Procesadas:** {stats['total_lineas_procesadas']:,}\n"
        md += f"**Eventos Extraídos:** {stats['total_eventos_extraidos']:,}\n"
        md += f"**Patrones Malignos:** {stats['patrones_detectados']}\n"
        md += f"**Última Lectura:** {stats['timestamp_ultimo_analisis']}\n\n"
        
        # Patrones detectados recientes
        patrones_recientes = sorted(
            self.patrones_detectados,
            key=lambda p: p.timestamp_deteccion,
            reverse=True
        )[:15]
        
        if patrones_recientes:
            md += "## 🚨 Patrones de Ataque Recientes\n\n"
            md += "| Tipo | Descripción | Gravedad | Timestamp |\n"
            md += "|------|-------------|----------|----------|\n"
            
            for patron in patrones_recientes:
                timestamp_str = patron.timestamp_deteccion.strftime("%H:%M:%S")
                descripcion_corta = patron.descripcion[:60] + "..." if len(patron.descripcion) > 60 else patron.descripcion
                emoji_gravedad = {"BAJO": "🟢", "MEDIO": "🟡", "ALTO": "🟠", "CRITICO": "🔴"}.get(patron.nivel_gravedad, "⚪")
                md += f"| {patron.tipo} | {descripcion_corta} | {emoji_gravedad} {patron.nivel_gravedad} | {timestamp_str} |\n"
            md += "\n"
        
        # Estadísticas por archivo
        md += "## 📁 Estadísticas por Pergamino\n\n"
        md += "| Archivo | Líneas | Eventos | Patrones | Errores |\n"
        md += "|---------|--------|---------|----------|----------|\n"
        
        for nombre, stats_archivo in stats['estadisticas_por_archivo'].items():
            md += f"| {nombre} | {stats_archivo['lineas_procesadas']:,} | {stats_archivo['eventos_extraidos']:,} | {stats_archivo['patrones_detectados']} | {stats_archivo['errores_parseo']} |\n"
        md += "\n"
        
        # Top IPs atacantes
        ips_atacantes = {}
        for patron in patrones_recientes:
            ip = patron.metadatos.get('ip_atacante') or patron.metadatos.get('ip_origen')
            if ip:
                ips_atacantes[ip] = ips_atacantes.get(ip, 0) + 1
        
        if ips_atacantes:
            md += "## 🌐 Top IPs Atacantes\n\n"
            md += "| IP | Patrones Detectados |\n"
            md += "|----|--------------------|\n"
            
            for ip, count in sorted(ips_atacantes.items(), key=lambda x: x[1], reverse=True)[:10]:
                md += f"| {ip} | {count} |\n"
            md += "\n"
        
        md += "---\n"
        md += "*Análisis realizado por los Escribas de Temis de Ares Aegis*\n"
        
        return md
    
    def exportar_patrones_json(self) -> List[Dict[str, Any]]:
        """Exporta los patrones detectados en formato JSON."""
        return [
            {
                'tipo': patron.tipo,
                'descripcion': patron.descripcion,
                'nivel_gravedad': patron.nivel_gravedad,
                'timestamp_deteccion': patron.timestamp_deteccion.isoformat(),
                'eventos_relacionados': len(patron.eventos_relacionados),
                'metadatos': patron.metadatos
            }
            for patron in self.patrones_detectados
        ]
