#!/usr/bin/env python3
"""
Monitor de Red - Ares Aegis
Sistema de monitoreo de conexiones de red y tráfico sospechoso

Autor: DogSoulDev
Versión: 2.0.0
"""

import os
import re
import socket
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Tuple
from datetime import datetime


class ConexionRed:
    """Representa una conexión de red."""
    
    def __init__(self, protocolo: str, direccion_local: str, puerto_local: int,
                 direccion_remota: str, puerto_remoto: int, estado: str, 
                 proceso: str = "", pid: int = 0):
        self.protocolo = protocolo
        self.direccion_local = direccion_local
        self.puerto_local = puerto_local
        self.direccion_remota = direccion_remota
        self.puerto_remoto = puerto_remoto
        self.estado = estado
        self.pid = pid
        self.proceso = proceso if proceso else ""
        self.fecha_deteccion = datetime.now()
        self.es_sospechosa_flag = False
        self.razones_sospecha = []
        
        if not self.proceso:
            self._obtener_info_proceso()
    
    def _obtener_info_proceso(self):
        """Obtiene información del proceso asociado al PID."""
        if self.pid > 0:
            try:
                ruta_proceso = f"/proc/{self.pid}/comm"
                if os.path.exists(ruta_proceso):
                    with open(ruta_proceso, 'r') as archivo:
                        self.proceso = archivo.read().strip()
            except:
                self.proceso = "desconocido"
    
    def marcar_como_sospechosa(self, razon: str):
        """Marca la conexión como sospechosa con la razón especificada."""
        self.es_sospechosa_flag = True
        if razon not in self.razones_sospecha:
            self.razones_sospecha.append(razon)
    
    def es_sospechosa(self, puertos_conocidos: Set[int], ips_whitelist: Set[str]) -> bool:
        """Determina si la conexión es sospechosa."""
        # Puerto remoto no conocido y alto
        if self.puerto_remoto not in puertos_conocidos and self.puerto_remoto > 1024:
            return True
        
        # IP remota no en whitelist y no privada
        if self.direccion_remota not in ips_whitelist and not self._es_ip_privada(self.direccion_remota):
            return True
        
        # Procesos potencialmente sospechosos
        procesos_sospechosos = ['nc', 'netcat', 'wget', 'curl', 'python', 'perl', 'bash', 'sh']
        if any(proceso in self.proceso.lower() for proceso in procesos_sospechosos):
            return True
        
        return False
    
    def _es_ip_privada(self, ip: str) -> bool:
        """Verifica si una IP es privada."""
        try:
            partes = ip.split('.')
            if len(partes) != 4:
                return False
            
            partes = [int(parte) for parte in partes]
            
            # Rangos de IP privadas
            if partes[0] == 10:
                return True
            if partes[0] == 172 and 16 <= partes[1] <= 31:
                return True
            if partes[0] == 192 and partes[1] == 168:
                return True
            if partes[0] == 127:  # Loopback
                return True
            
            return False
        except:
            return False
    
    def a_dict(self) -> Dict[str, Any]:
        """Convierte la conexión a diccionario."""
        return {
            'protocolo': self.protocolo,
            'direccion_local': self.direccion_local,
            'puerto_local': self.puerto_local,
            'direccion_remota': self.direccion_remota,
            'puerto_remoto': self.puerto_remoto,
            'estado': self.estado,
            'pid': self.pid,
            'proceso': self.proceso,
            'fecha_deteccion': self.fecha_deteccion.isoformat(),
            'es_sospechosa': self.es_sospechosa_flag,
            'razones_sospecha': self.razones_sospecha
        }


class MonitorRed:
    """Monitor de conexiones de red y detección de actividad sospechosa."""
    
    def __init__(self, siem=None):
        self.siem = siem
        self.conexiones_activas: List[ConexionRed] = []
        self.conexiones_historicas: List[ConexionRed] = []
        self.puertos_conocidos: Set[int] = set()
        self.ips_whitelist: Set[str] = set()
        self.puertos_sospechosos: Set[int] = set()
        
        self._inicializar_configuracion()
        
        if self.siem:
            self.siem.log_evento('INFO', 'monitor_red', 'Monitor de red inicializado')
    
    def _inicializar_configuracion(self):
        """Inicializa la configuración del monitor."""
        # Puertos estándar conocidos
        self.puertos_conocidos = {
            20, 21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 
            3389, 5432, 3306, 1433, 6379, 27017
        }
        
        # IPs de confianza
        self.ips_whitelist = {
            '127.0.0.1', '0.0.0.0', '::1', '192.168.1.1', 
            '192.168.0.1', '10.0.0.1'
        }
        
        # Puertos comúnmente usados por malware
        self.puertos_sospechosos = {
            1234, 1337, 4444, 5555, 6666, 7777, 8888, 9999,
            31337, 12345, 54321, 9876, 8080, 8443, 2222
        }
    
    def obtener_conexiones_activas(self) -> List[ConexionRed]:
        """Obtiene todas las conexiones activas del sistema."""
        conexiones = []
        conexiones.extend(self._obtener_conexiones_tcp())
        conexiones.extend(self._obtener_conexiones_udp())
        self.conexiones_activas = conexiones
        return conexiones
    
    def _obtener_conexiones_tcp(self) -> List[ConexionRed]:
        """Obtiene conexiones TCP activas."""
        conexiones = []
        
        try:
            with open('/proc/net/tcp', 'r') as archivo:
                lineas = archivo.readlines()[1:]  # Omitir cabecera
                
                for linea in lineas:
                    partes = linea.strip().split()
                    if len(partes) >= 10:
                        local_addr, local_port = self._parsear_direccion(partes[1])
                        remote_addr, remote_port = self._parsear_direccion(partes[2])
                        estado = self._obtener_estado_tcp(partes[3])
                        pid = self._obtener_pid_por_inode(partes[9])
                        
                        conexion = ConexionRed(
                            'TCP', local_addr, local_port,
                            remote_addr, remote_port, estado, "", pid
                        )
                        conexiones.append(conexion)
        
        except Exception as e:
            if self.siem:
                self.siem.log_evento('ERROR', 'monitor_red', f'Error obteniendo conexiones TCP: {e}')
        
        return conexiones
    
    def _obtener_conexiones_udp(self) -> List[ConexionRed]:
        """Obtiene conexiones UDP activas."""
        conexiones = []
        
        try:
            with open('/proc/net/udp', 'r') as archivo:
                lineas = archivo.readlines()[1:]  # Omitir cabecera
                
                for linea in lineas:
                    partes = linea.strip().split()
                    if len(partes) >= 10:
                        local_addr, local_port = self._parsear_direccion(partes[1])
                        remote_addr, remote_port = self._parsear_direccion(partes[2])
                        pid = self._obtener_pid_por_inode(partes[9])
                        
                        conexion = ConexionRed(
                            'UDP', local_addr, local_port,
                            remote_addr, remote_port, 'ACTIVA', "", pid
                        )
                        conexiones.append(conexion)
        
        except Exception as e:
            if self.siem:
                self.siem.log_evento('ERROR', 'monitor_red', f'Error obteniendo conexiones UDP: {e}')
        
        return conexiones
    
    def _parsear_direccion(self, direccion_hex: str) -> Tuple[str, int]:
        """Parsea dirección en formato hexadecimal."""
        try:
            ip_hex, puerto_hex = direccion_hex.split(':')
            
            # Convertir IP hexadecimal a decimal
            ip_int = int(ip_hex, 16)
            ip = f"{ip_int & 0xFF}.{(ip_int >> 8) & 0xFF}.{(ip_int >> 16) & 0xFF}.{(ip_int >> 24) & 0xFF}"
            puerto = int(puerto_hex, 16)
            
            return ip, puerto
        except:
            return "0.0.0.0", 0
    
    def _obtener_estado_tcp(self, estado_hex: str) -> str:
        """Convierte estado TCP hexadecimal a texto."""
        estados = {
            '01': 'ESTABLISHED', '02': 'SYN_SENT', '03': 'SYN_RECV',
            '04': 'FIN_WAIT1', '05': 'FIN_WAIT2', '06': 'TIME_WAIT',
            '07': 'CLOSE', '08': 'CLOSE_WAIT', '09': 'LAST_ACK',
            '0A': 'LISTEN', '0B': 'CLOSING'
        }
        return estados.get(estado_hex.upper(), 'UNKNOWN')
    
    def _obtener_pid_por_inode(self, inode: str) -> int:
        """Encuentra el PID asociado a un inode de socket."""
        try:
            for pid_dir in Path('/proc').glob('[0-9]*'):
                try:
                    fd_dir = pid_dir / 'fd'
                    if fd_dir.exists():
                        for fd_link in fd_dir.iterdir():
                            try:
                                link_target = fd_link.readlink()
                                if f'socket:[{inode}]' in str(link_target):
                                    return int(pid_dir.name)
                            except:
                                continue
                except:
                    continue
        except:
            pass
        
        return 0
    
    def detectar_conexiones_sospechosas(self) -> List[ConexionRed]:
        """Detecta conexiones potencialmente maliciosas."""
        conexiones_sospechosas = []
        
        for conexion in self.conexiones_activas:
            if conexion.es_sospechosa(self.puertos_conocidos, self.ips_whitelist):
                conexiones_sospechosas.append(conexion)
                
                if self.siem:
                    self.siem.log_evento('HIGH', 'monitor_red', 
                                             f'Conexión sospechosa detectada: {conexion.direccion_local}:{conexion.puerto_local} -> '
                                             f'{conexion.direccion_remota}:{conexion.puerto_remoto} ({conexion.proceso})')
        
        return conexiones_sospechosas
    
    def detectar_puertos_en_escucha_sospechosos(self) -> List[ConexionRed]:
        """Detecta puertos en escucha potencialmente peligrosos."""
        puertos_sospechosos_encontrados = []
        
        for conexion in self.conexiones_activas:
            if (conexion.estado == 'LISTEN' and 
                (conexion.puerto_local in self.puertos_sospechosos or conexion.puerto_local > 50000)):
                
                puertos_sospechosos_encontrados.append(conexion)
                
                if self.siem:
                    self.siem.log_evento('MEDIUM', 'monitor_red', 
                                             f'Puerto sospechoso en escucha: {conexion.puerto_local} ({conexion.proceso})')
        
        return puertos_sospechosos_encontrados
    
    def obtener_estadisticas_red(self) -> Dict[str, Any]:
        """Genera estadísticas de las conexiones de red."""
        total_conexiones = len(self.conexiones_activas)
        conexiones_tcp = len([c for c in self.conexiones_activas if c.protocolo == 'TCP'])
        conexiones_udp = len([c for c in self.conexiones_activas if c.protocolo == 'UDP'])
        conexiones_establecidas = len([c for c in self.conexiones_activas if c.estado == 'ESTABLISHED'])
        puertos_escucha = len([c for c in self.conexiones_activas if c.estado == 'LISTEN'])
        
        return {
            'total_conexiones': total_conexiones,
            'conexiones_tcp': conexiones_tcp,
            'conexiones_udp': conexiones_udp,
            'conexiones_establecidas': conexiones_establecidas,
            'puertos_en_escucha': puertos_escucha
        }
    
    def generar_reporte_markdown(self, conexiones_sospechosas: Optional[List[ConexionRed]] = None) -> str:
        """Genera reporte en formato Markdown."""
        estadisticas = self.obtener_estadisticas_red()
        
        reporte = "# Reporte de Monitoreo de Red - Ares Aegis\n\n"
        reporte += f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        reporte += "## Estadísticas Generales\n\n"
        reporte += f"- **Total de conexiones:** {estadisticas['total_conexiones']}\n"
        reporte += f"- **Conexiones TCP:** {estadisticas['conexiones_tcp']}\n"
        reporte += f"- **Conexiones UDP:** {estadisticas['conexiones_udp']}\n"
        reporte += f"- **Conexiones establecidas:** {estadisticas['conexiones_establecidas']}\n"
        reporte += f"- **Puertos en escucha:** {estadisticas['puertos_en_escucha']}\n\n"
        
        if conexiones_sospechosas:
            reporte += "## Conexiones Sospechosas Detectadas\n\n"
            for conexion in conexiones_sospechosas:
                reporte += f"### {conexion.protocolo}: {conexion.direccion_local}:{conexion.puerto_local} -> {conexion.direccion_remota}:{conexion.puerto_remoto}\n\n"
                reporte += f"- **Estado:** {conexion.estado}\n"
                reporte += f"- **Proceso:** {conexion.proceso} (PID: {conexion.pid})\n\n"
        
        return reporte


class PuertoAbierto:
    """Representa un puerto abierto en el sistema."""
    
    def __init__(self, puerto: int, protocolo: str, servicio: str = "", 
                 proceso: str = "", pid: int = 0, direccion: str = ""):
        self.puerto = puerto
        self.protocolo = protocolo.upper()
        self.servicio = servicio
        self.proceso = proceso
        self.pid = pid
        self.direccion = direccion
        self.fecha_deteccion = datetime.now()
        self.es_sospechoso = False
        self.razon_sospecha = ""
        self.razones_sospecha = []
        
        self._evaluar_sospecha()
    
    def _evaluar_sospecha(self):
        """Evalúa si el puerto abierto es sospechoso."""
        # Puertos comúnmente utilizados por malware
        puertos_sospechosos = {
            1337, 31337, 12345, 54321, 9999, 6666, 6667, 6668, 6669,
            7777, 27374, 30100, 53001, 27665, 20034, 9878, 10067,
            47262, 54283, 35555, 40412, 40421, 40422, 40423, 40426,
            58339, 5714, 28431, 31792, 33333, 65000
        }
        
        # Procesos sospechosos
        procesos_sospechosos = [
            'nc', 'netcat', 'ncat', 'socat', 'telnet', 'backdoor',
            'shell', 'cmd', 'powershell', 'meterpreter'
        ]
        
        # Verificar puerto sospechoso
        if self.puerto in puertos_sospechosos:
            self.es_sospechoso = True
            self.razon_sospecha = "Puerto comúnmente usado por malware"
        
        # Verificar proceso sospechoso
        elif any(proc in self.proceso.lower() for proc in procesos_sospechosos):
            self.es_sospechoso = True
            self.razon_sospecha = "Proceso potencialmente malicioso"
        
        # Puertos altos no estándar
        elif self.puerto > 49152 and not self.proceso:
            self.es_sospechoso = True
            self.razon_sospecha = "Puerto alto sin proceso identificado"
    
    def marcar_como_sospechoso(self, razon: str):
        """Marca el puerto como sospechoso con la razón especificada."""
        self.es_sospechoso = True
        if razon not in self.razones_sospecha:
            self.razones_sospecha.append(razon)
        if not self.razon_sospecha:
            self.razon_sospecha = razon
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la información del puerto a diccionario."""
        return {
            'puerto': self.puerto,
            'protocolo': self.protocolo,
            'servicio': self.servicio,
            'proceso': self.proceso,
            'pid': self.pid,
            'direccion': self.direccion,
            'fecha_deteccion': self.fecha_deteccion.isoformat(),
            'es_sospechoso': self.es_sospechoso,
            'razon_sospecha': self.razon_sospecha,
            'razones_sospecha': self.razones_sospecha
        }
