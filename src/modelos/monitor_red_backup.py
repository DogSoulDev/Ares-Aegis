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
                 direccion_remota: str, puerto_remoto: int, estado: str, pid: int = 0):
        self.protocolo = protocolo
        self.direccion_local = direccion_local
        self.puerto_local = puerto_local
        self.direccion_remota = direccion_remota
        self.puerto_remoto = puerto_remoto
        self.estado = estado
        self.pid = pid
        self.proceso = ""
        self.fecha_deteccion = datetime.now()
        
        self._obtener_info_proceso()
    
    def _obtener_info_proceso(self):
        if self.pid > 0:
            try:
                ruta_proceso = f"/proc/{self.pid}/comm"
                if os.path.exists(ruta_proceso):
                    with open(ruta_proceso, 'r') as archivo:
                        self.proceso = archivo.read().strip()
            except:
                self.proceso = "desconocido"
    
    def es_sospechosa(self, puertos_conocidos: Set[int], ips_whitelist: Set[str]) -> bool:
        if self.puerto_remoto not in puertos_conocidos and self.puerto_remoto > 1024:
            return True
        
        if self.direccion_remota not in ips_whitelist and not self._es_ip_privada(self.direccion_remota):
            return True
        
        procesos_sospechosos = ['nc', 'netcat', 'wget', 'curl', 'python', 'perl', 'bash', 'sh']
        if any(proceso in self.proceso.lower() for proceso in procesos_sospechosos):
            return True
        
        return False
    
    def _es_ip_privada(self, ip: str) -> bool:
        try:
            partes = ip.split('.')
            if len(partes) != 4:
                return False
            
            partes = [int(parte) for parte in partes]
            
            if partes[0] == 10:
                return True
            if partes[0] == 172 and 16 <= partes[1] <= 31:
                return True
            if partes[0] == 192 and partes[1] == 168:
                return True
            if partes[0] == 127:
                return True
            
            return False
        except:
            return False
    
    def a_dict(self) -> Dict[str, Any]:
        return {
            'protocolo': self.protocolo,
            'direccion_local': self.direccion_local,
            'puerto_local': self.puerto_local,
            'direccion_remota': self.direccion_remota,
            'puerto_remoto': self.puerto_remoto,
            'estado': self.estado,
            'pid': self.pid,
            'proceso': self.proceso,
            'fecha_deteccion': self.fecha_deteccion.isoformat()
        }


class MonitorRed:
    
    def __init__(self, siem=None):
        self.siem = siem
        self.conexiones_activas: List[ConexionRed] = []
        self.conexiones_historicas: List[ConexionRed] = []
        self.puertos_conocidos: Set[int] = set()
        self.ips_whitelist: Set[str] = set()
        self.puertos_sospechosos: Set[int] = set()
        
        self._inicializar_configuracion()
        
        if self.siem:
            self.siem.registrar_evento('INFO', 'monitor_red', 'Monitor de red inicializado')
    
    def _inicializar_configuracion(self):
        self.puertos_conocidos = {
            20, 21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 
            3389, 5432, 3306, 1433, 6379, 27017
        }
        
        self.ips_whitelist = {
            '127.0.0.1', '0.0.0.0', '::1', '192.168.1.1', 
            '192.168.0.1', '10.0.0.1'
        }
        
        self.puertos_sospechosos = {
            1234, 1337, 4444, 5555, 6666, 7777, 8888, 9999,
            31337, 12345, 54321, 9876, 8080, 8443, 2222
        }
    
    def obtener_conexiones_activas(self) -> List[ConexionRed]:
        conexiones = []
        conexiones.extend(self._obtener_conexiones_tcp())
        conexiones.extend(self._obtener_conexiones_udp())
        self.conexiones_activas = conexiones
        return conexiones
    
    def _obtener_conexiones_tcp(self) -> List[ConexionRed]:
        conexiones = []
        
        try:
            with open('/proc/net/tcp', 'r') as archivo:
                lineas = archivo.readlines()[1:]
                
                for linea in lineas:
                    partes = linea.strip().split()
                    if len(partes) >= 10:
                        local_addr, local_port = self._parsear_direccion(partes[1])
                        remote_addr, remote_port = self._parsear_direccion(partes[2])
                        estado = self._obtener_estado_tcp(partes[3])
                        pid = self._obtener_pid_por_inode(partes[9])
                        
                        conexion = ConexionRed(
                            'TCP', local_addr, local_port,
                            remote_addr, remote_port, estado, pid
                        )
                        conexiones.append(conexion)
        
        except Exception as e:
            if self.siem:
                self.siem.registrar_evento('ERROR', 'monitor_red', f'Error obteniendo conexiones TCP: {e}')
        
        return conexiones
    
    def _obtener_conexiones_udp(self) -> List[ConexionRed]:
        conexiones = []
        
        try:
            with open('/proc/net/udp', 'r') as archivo:
                lineas = archivo.readlines()[1:]
                
                for linea in lineas:
                    partes = linea.strip().split()
                    if len(partes) >= 10:
                        local_addr, local_port = self._parsear_direccion(partes[1])
                        remote_addr, remote_port = self._parsear_direccion(partes[2])
                        pid = self._obtener_pid_por_inode(partes[9])
                        
                        conexion = ConexionRed(
                            'UDP', local_addr, local_port,
                            remote_addr, remote_port, 'ACTIVA', pid
                        )
                        conexiones.append(conexion)
        
        except Exception as e:
            if self.siem:
                self.siem.registrar_evento('ERROR', 'monitor_red', f'Error obteniendo conexiones UDP: {e}')
        
        return conexiones
    
    def _parsear_direccion(self, direccion_hex: str) -> Tuple[str, int]:
        try:
            ip_hex, puerto_hex = direccion_hex.split(':')
            
            ip_int = int(ip_hex, 16)
            ip = f"{ip_int & 0xFF}.{(ip_int >> 8) & 0xFF}.{(ip_int >> 16) & 0xFF}.{(ip_int >> 24) & 0xFF}"
            puerto = int(puerto_hex, 16)
            
            return ip, puerto
        except:
            return "0.0.0.0", 0
    
    def _obtener_estado_tcp(self, estado_hex: str) -> str:
        estados = {
            '01': 'ESTABLISHED', '02': 'SYN_SENT', '03': 'SYN_RECV',
            '04': 'FIN_WAIT1', '05': 'FIN_WAIT2', '06': 'TIME_WAIT',
            '07': 'CLOSE', '08': 'CLOSE_WAIT', '09': 'LAST_ACK',
            '0A': 'LISTEN', '0B': 'CLOSING'
        }
        return estados.get(estado_hex.upper(), 'UNKNOWN')
    
    def _obtener_pid_por_inode(self, inode: str) -> int:
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
        conexiones_sospechosas = []
        
        for conexion in self.conexiones_activas:
            if conexion.es_sospechosa(self.puertos_conocidos, self.ips_whitelist):
                conexiones_sospechosas.append(conexion)
                
                if self.siem:
                    self.siem.registrar_evento('HIGH', 'monitor_red', 
                                             f'Conexión sospechosa detectada: {conexion.direccion_local}:{conexion.puerto_local} -> '
                                             f'{conexion.direccion_remota}:{conexion.puerto_remoto} ({conexion.proceso})')
        
        return conexiones_sospechosas
    
    def detectar_puertos_en_escucha_sospechosos(self) -> List[ConexionRed]:
        puertos_sospechosos_encontrados = []
        
        for conexion in self.conexiones_activas:
            if (conexion.estado == 'LISTEN' and 
                (conexion.puerto_local in self.puertos_sospechosos or conexion.puerto_local > 50000)):
                
                puertos_sospechosos_encontrados.append(conexion)
                
                if self.siem:
                    self.siem.registrar_evento('MEDIUM', 'monitor_red', 
                                             f'Puerto sospechoso en escucha: {conexion.puerto_local} ({conexion.proceso})')
        
        return puertos_sospechosos_encontrados
    
    def obtener_estadisticas_red(self) -> Dict[str, Any]:
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
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la conexión a diccionario."""
        return {
            'protocolo': self.protocolo,
            'direccion_local': self.direccion_local,
            'puerto_local': self.puerto_local,
            'direccion_remota': self.direccion_remota,
            'puerto_remoto': self.puerto_remoto,
            'estado': self.estado,
            'proceso': self.proceso,
            'timestamp': self.timestamp.isoformat(),
            'sospechosa': self.sospechosa,
            'razones_sospecha': self.razones_sospecha
        }


class PuertoAbierto:
    """Información sobre un puerto abierto en el sistema."""
    
    def __init__(self, puerto: int, protocolo: str, servicio: str = "Desconocido",
                 proceso: str = "Desconocido", direccion: str = "0.0.0.0"):
        self.puerto = puerto
        self.protocolo = protocolo
        self.servicio = servicio
        self.proceso = proceso
        self.direccion = direccion
        self.timestamp = datetime.now()
        self.sospechoso = False
        self.razones_sospecha: List[str] = []
    
    def marcar_como_sospechoso(self, razon: str) -> None:
        """Marca el puerto como sospechoso."""
        self.sospechoso = True
        if razon not in self.razones_sospecha:
            self.razones_sospecha.append(razon)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el puerto a diccionario."""
        return {
            'puerto': self.puerto,
            'protocolo': self.protocolo,
            'servicio': self.servicio,
            'proceso': self.proceso,
            'direccion': self.direccion,
            'timestamp': self.timestamp.isoformat(),
            'sospechoso': self.sospechoso,
            'razones_sospecha': self.razones_sospecha
        }


class MonitorRed:
    """Monitor de actividad de red para detección de anomalías."""
    
    def __init__(self, siem_instance=None):
        self.siem = siem_instance
        self.conexiones_conocidas: Dict[str, ConexionRed] = {}
        self.puertos_conocidos: Dict[int, PuertoAbierto] = {}
        self.puertos_sospechosos = self._cargar_puertos_sospechosos()
        self.rangos_ip_privadas = self._cargar_rangos_privados()
        self.servicios_conocidos = self._cargar_servicios_conocidos()
        
    def _cargar_puertos_sospechosos(self) -> List[int]:
        """Carga lista de puertos comúnmente usados por malware."""
        return [
            # Puertos comunes de backdoors y malware
            1234, 1337, 2222, 3333, 4444, 5555, 6666, 7777, 8888, 9999,
            31337, 12345, 54321, 65535,
            # Puertos de herramientas de hacking
            4444, 4445, 5554, 9995, 9996, 9997, 9998, 9999,
            # Puertos de Metasploit comunes
            4444, 4445, 4446, 4447, 4448, 4449,
            # Otros puertos sospechosos
            1337, 31337, 54321, 12345, 65000, 65001, 65002
        ]
    
    def _cargar_rangos_privados(self) -> List[Tuple[str, str]]:
        """Carga rangos de direcciones IP privadas."""
        return [
            ('10.0.0.0', '10.255.255.255'),
            ('172.16.0.0', '172.31.255.255'),
            ('192.168.0.0', '192.168.255.255'),
            ('127.0.0.0', '127.255.255.255'),  # Loopback
            ('169.254.0.0', '169.254.255.255')  # Link-local
        ]
    
    def _cargar_servicios_conocidos(self) -> Dict[int, str]:
        """Carga servicios conocidos por puerto."""
        return {
            # Servicios web
            80: 'HTTP', 443: 'HTTPS', 8080: 'HTTP-Alt', 8443: 'HTTPS-Alt',
            # SSH y Telnet
            22: 'SSH', 23: 'Telnet', 2222: 'SSH-Alt',
            # FTP
            21: 'FTP', 20: 'FTP-Data',
            # Email
            25: 'SMTP', 110: 'POP3', 143: 'IMAP', 993: 'IMAPS', 995: 'POP3S',
            # DNS
            53: 'DNS',
            # Database
            3306: 'MySQL', 5432: 'PostgreSQL', 1521: 'Oracle', 1433: 'MSSQL',
            # Otros servicios comunes
            123: 'NTP', 161: 'SNMP', 389: 'LDAP', 636: 'LDAPS',
            # Servicios de red
            139: 'NetBIOS', 445: 'SMB', 135: 'RPC'
        }
    
    def _es_ip_privada(self, ip: str) -> bool:
        """Verifica si una IP está en rango privado."""
        try:
            ip_int = int(socket.inet_aton(ip).hex(), 16)
            for inicio_str, fin_str in self.rangos_ip_privadas:
                inicio_int = int(socket.inet_aton(inicio_str).hex(), 16)
                fin_int = int(socket.inet_aton(fin_str).hex(), 16)
                if inicio_int <= ip_int <= fin_int:
                    return True
            return False
        except socket.error:
            return False
    
    def obtener_conexiones_activas(self) -> List[ConexionRed]:
        """Obtiene las conexiones de red activas usando netstat."""
        conexiones = []
        
        try:
            # Usar netstat para obtener conexiones
            resultado = subprocess.run(
                ['netstat', '-tuln'], 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            if resultado.returncode == 0:
                conexiones.extend(self._parsear_netstat(resultado.stdout))
            else:
                if self.siem:
                    self.siem.registrar_evento(
                        'WARNING',
                        'monitor_red',
                        'netstat no disponible, intentando con ss'
                    )
                # Fallback a ss
                resultado_ss = subprocess.run(
                    ['ss', '-tuln'], 
                    capture_output=True, 
                    text=True, 
                    timeout=30
                )
                if resultado_ss.returncode == 0:
                    conexiones.extend(self._parsear_ss(resultado_ss.stdout))
                    
        except subprocess.TimeoutExpired:
            if self.siem:
                self.siem.registrar_evento(
                    'ERROR',
                    'monitor_red',
                    'Timeout al ejecutar comandos de red'
                )
        except Exception as e:
            if self.siem:
                self.siem.registrar_evento(
                    'ERROR',
                    'monitor_red',
                    f'Error al obtener conexiones: {e}'
                )
        
        return conexiones
    
    def _parsear_netstat(self, salida: str) -> List[ConexionRed]:
        """Parsea la salida de netstat."""
        conexiones = []
        
        for linea in salida.split('\n'):
            if 'tcp' in linea.lower() or 'udp' in linea.lower():
                partes = linea.split()
                if len(partes) >= 4:
                    protocolo = partes[0].upper()
                    direccion_local = partes[3] if len(partes) > 3 else ''
                    
                    # Extraer IP y puerto local
                    if ':' in direccion_local:
                        ip_local, puerto_local_str = direccion_local.rsplit(':', 1)
                        try:
                            puerto_local = int(puerto_local_str)
                        except ValueError:
                            continue
                    else:
                        continue
                    
                    # Para conexiones establecidas, obtener dirección remota
                    direccion_remota = ''
                    puerto_remoto = 0
                    estado = 'LISTEN'
                    
                    if len(partes) > 4 and partes[4] != '0.0.0.0:*':
                        direccion_remota_completa = partes[4]
                        if ':' in direccion_remota_completa:
                            ip_remota, puerto_remoto_str = direccion_remota_completa.rsplit(':', 1)
                            try:
                                puerto_remoto = int(puerto_remoto_str)
                                direccion_remota = ip_remota
                                estado = partes[5] if len(partes) > 5 else 'ESTABLISHED'
                            except ValueError:
                                pass
                    
                    conexion = ConexionRed(
                        protocolo=protocolo,
                        direccion_local=ip_local,
                        puerto_local=puerto_local,
                        direccion_remota=direccion_remota,
                        puerto_remoto=puerto_remoto,
                        estado=estado
                    )
                    
                    conexiones.append(conexion)
        
        return conexiones
    
    def _parsear_ss(self, salida: str) -> List[ConexionRed]:
        """Parsea la salida de ss (similar a netstat)."""
        conexiones = []
        
        for linea in salida.split('\n'):
            if any(proto in linea.lower() for proto in ['tcp', 'udp']):
                partes = linea.split()
                if len(partes) >= 4:
                    protocolo = partes[0].upper()
                    direccion_local = partes[3] if len(partes) > 3 else ''
                    
                    # Formato similar a netstat
                    if ':' in direccion_local:
                        if direccion_local.startswith('['):
                            # IPv6
                            continue
                        
                        ip_local, puerto_local_str = direccion_local.rsplit(':', 1)
                        try:
                            puerto_local = int(puerto_local_str)
                        except ValueError:
                            continue
                    else:
                        continue
                    
                    conexion = ConexionRed(
                        protocolo=protocolo,
                        direccion_local=ip_local,
                        puerto_local=puerto_local,
                        direccion_remota='',
                        puerto_remoto=0,
                        estado='LISTEN'
                    )
                    
                    conexiones.append(conexion)
        
        return conexiones
    
    def obtener_puertos_abiertos(self) -> List[PuertoAbierto]:
        """Obtiene los puertos abiertos en el sistema."""
        puertos = []
        
        # Escanear puertos TCP comunes
        puertos_comunes = list(range(1, 1024)) + [1337, 2222, 3389, 5432, 5900, 8080, 8443]
        
        for puerto in puertos_comunes:
            if self._verificar_puerto_tcp(puerto):
                servicio = self.servicios_conocidos.get(puerto, 'Desconocido')
                puerto_obj = PuertoAbierto(
                    puerto=puerto,
                    protocolo='TCP',
                    servicio=servicio
                )
                puertos.append(puerto_obj)
        
        return puertos
    
    def _verificar_puerto_tcp(self, puerto: int, host: str = 'localhost', timeout: float = 0.1) -> bool:
        """Verifica si un puerto TCP está abierto."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            resultado = sock.connect_ex((host, puerto))
            sock.close()
            return resultado == 0
        except Exception:
            return False
    
    def analizar_conexiones_sospechosas(self, conexiones: List[ConexionRed]) -> List[ConexionRed]:
        """Analiza conexiones para detectar actividad sospechosa."""
        conexiones_sospechosas = []
        
        for conexion in conexiones:
            # Verificar puertos sospechosos
            if conexion.puerto_local in self.puertos_sospechosos:
                conexion.marcar_como_sospechosa(f'Puerto sospechoso: {conexion.puerto_local}')
            
            if conexion.puerto_remoto in self.puertos_sospechosos:
                conexion.marcar_como_sospechosa(f'Puerto remoto sospechoso: {conexion.puerto_remoto}')
            
            # Verificar conexiones a IPs externas
            if conexion.direccion_remota and not self._es_ip_privada(conexion.direccion_remota):
                if conexion.direccion_remota != '0.0.0.0':
                    conexion.marcar_como_sospechosa('Conexión a IP externa')
            
            # Verificar servicios en puertos no estándar
            if conexion.puerto_local > 10000 and conexion.estado == 'LISTEN':
                conexion.marcar_como_sospechosa('Servicio en puerto alto no estándar')
            
            # Verificar conexiones de reverse shell comunes
            puertos_reverse_shell = [4444, 4445, 1337, 31337]
            if conexion.puerto_remoto in puertos_reverse_shell:
                conexion.marcar_como_sospechosa('Posible reverse shell')
            
            if conexion.sospechosa:
                conexiones_sospechosas.append(conexion)
        
        return conexiones_sospechosas
    
    def analizar_puertos_sospechosos(self, puertos: List[PuertoAbierto]) -> List[PuertoAbierto]:
        """Analiza puertos abiertos para detectar anomalías."""
        puertos_sospechosos = []
        
        for puerto in puertos:
            # Verificar puertos en lista de sospechosos
            if puerto.puerto in self.puertos_sospechosos:
                puerto.marcar_como_sospechoso('Puerto en lista de malware conocido')
            
            # Verificar puertos altos inusuales
            if puerto.puerto > 50000:
                puerto.marcar_como_sospechoso('Puerto muy alto (>50000)')
            
            # Verificar servicios no autorizados en puertos estándar
            if puerto.puerto in [80, 443, 8080, 8443] and puerto.proceso == 'Desconocido':
                puerto.marcar_como_sospechoso('Servicio web no identificado')
            
            if puerto.sospechoso:
                puertos_sospechosos.append(puerto)
        
        return puertos_sospechosos
    
    def escanear_red_local(self, rango_ip: str = "192.168.1.0/24") -> List[Dict[str, Any]]:
        """Escanea la red local para detectar dispositivos activos."""
        dispositivos = []
        
        try:
            # Usar nmap si está disponible
            resultado = subprocess.run(
                ['nmap', '-sn', rango_ip],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if resultado.returncode == 0:
                dispositivos = self._parsear_nmap_ping(resultado.stdout)
            else:
                # Fallback: ping a rango común
                dispositivos = self._escanear_ping_basico()
                
        except subprocess.TimeoutExpired:
            if self.siem:
                self.siem.registrar_evento(
                    'WARNING',
                    'monitor_red',
                    'Timeout en escaneo de red local'
                )
        except Exception as e:
            if self.siem:
                self.siem.registrar_evento(
                    'WARNING',
                    'monitor_red',
                    f'No se pudo escanear red local: {e}'
                )
            dispositivos = self._escanear_ping_basico()
        
        return dispositivos
    
    def _parsear_nmap_ping(self, salida: str) -> List[Dict[str, Any]]:
        """Parsea la salida de nmap ping scan."""
        dispositivos = []
        
        for linea in salida.split('\n'):
            if 'Nmap scan report for' in linea:
                # Extraer IP
                match = re.search(r'(\d+\.\d+\.\d+\.\d+)', linea)
                if match:
                    ip = match.group(1)
                    dispositivo = {
                        'ip': ip,
                        'estado': 'activo',
                        'metodo_deteccion': 'nmap',
                        'timestamp': datetime.now().isoformat()
                    }
                    dispositivos.append(dispositivo)
        
        return dispositivos
    
    def _escanear_ping_basico(self) -> List[Dict[str, Any]]:
        """Escaneo básico con ping para detectar dispositivos."""
        dispositivos = []
        
        # Obtener la IP local
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.connect(("8.8.8.8", 80))
            ip_local = sock.getsockname()[0]
            sock.close()
            
            # Extraer subnet
            partes_ip = ip_local.split('.')
            subnet = f"{partes_ip[0]}.{partes_ip[1]}.{partes_ip[2]}"
            
            # Ping a IPs comunes en la subnet
            for i in [1, 254, 100, 101, 102]:  # IPs comunes de gateway/dispositivos
                ip_target = f"{subnet}.{i}"
                try:
                    resultado = subprocess.run(
                        ['ping', '-c', '1', '-W', '1', ip_target],
                        capture_output=True,
                        timeout=2
                    )
                    if resultado.returncode == 0:
                        dispositivo = {
                            'ip': ip_target,
                            'estado': 'activo',
                            'metodo_deteccion': 'ping',
                            'timestamp': datetime.now().isoformat()
                        }
                        dispositivos.append(dispositivo)
                except (subprocess.TimeoutExpired, Exception):
                    continue
                    
        except Exception as e:
            if self.siem:
                self.siem.registrar_evento(
                    'WARNING',
                    'monitor_red',
                    f'Error en escaneo básico: {e}'
                )
        
        return dispositivos
    
    def escanear_sistema_red(self) -> Dict[str, Any]:
        """Realiza un escaneo completo del sistema de red."""
        inicio = datetime.now()
        
        # Obtener conexiones activas
        conexiones = self.obtener_conexiones_activas()
        
        # Obtener puertos abiertos
        puertos = self.obtener_puertos_abiertos()
        
        # Analizar conexiones sospechosas
        conexiones_sospechosas = self.analizar_conexiones_sospechosas(conexiones)
        
        # Analizar puertos sospechosos
        puertos_sospechosos = self.analizar_puertos_sospechosos(puertos)
        
        # Escanear red local
        dispositivos_red = self.escanear_red_local()
        
        # Estadísticas
        estadisticas = {
            'total_conexiones': len(conexiones),
            'conexiones_sospechosas': len(conexiones_sospechosas),
            'total_puertos_abiertos': len(puertos),
            'puertos_sospechosos': len(puertos_sospechosos),
            'dispositivos_en_red': len(dispositivos_red),
            'tiempo_escaneo': (datetime.now() - inicio).total_seconds()
        }
        
        resultado = {
            'timestamp': inicio.isoformat(),
            'estadisticas': estadisticas,
            'conexiones_activas': [c.to_dict() for c in conexiones],
            'conexiones_sospechosas': [c.to_dict() for c in conexiones_sospechosas],
            'puertos_abiertos': [p.to_dict() for p in puertos],
            'puertos_sospechosos': [p.to_dict() for p in puertos_sospechosos],
            'dispositivos_red': dispositivos_red
        }
        
        # Registrar eventos en SIEM
        if self.siem:
            if conexiones_sospechosas:
                self.siem.registrar_evento(
                    'WARNING',
                    'monitor_red',
                    f'Detectadas {len(conexiones_sospechosas)} conexiones sospechosas'
                )
            
            if puertos_sospechosos:
                self.siem.registrar_evento(
                    'WARNING',
                    'monitor_red',
                    f'Detectados {len(puertos_sospechosos)} puertos sospechosos'
                )
            
            self.siem.registrar_evento(
                'INFO',
                'monitor_red',
                f'Escaneo de red completado: {len(conexiones)} conexiones, {len(puertos)} puertos'
            )
        
        return resultado
    
    def exportar_reporte_markdown(self, resultado_escaneo: Dict[str, Any],
                                 ruta_archivo: Optional[str] = None) -> str:
        """Exporta el resultado del escaneo a formato Markdown."""
        if not ruta_archivo:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            ruta_archivo = f"reporte_red_{timestamp}.md"
        
        estadisticas = resultado_escaneo['estadisticas']
        conexiones_sospechosas = resultado_escaneo['conexiones_sospechosas']
        puertos_sospechosos = resultado_escaneo['puertos_sospechosos']
        dispositivos_red = resultado_escaneo['dispositivos_red']
        
        contenido = f"""# Reporte de Monitoreo de Red - Ares Aegis

## Resumen Ejecutivo

**Fecha del Escaneo:** {resultado_escaneo['timestamp']}  
**Duración del Escaneo:** {estadisticas['tiempo_escaneo']:.2f} segundos

### Estadísticas Generales

- **Total de Conexiones:** {estadisticas['total_conexiones']}
- **Conexiones Sospechosas:** {estadisticas['conexiones_sospechosas']}
- **Puertos Abiertos:** {estadisticas['total_puertos_abiertos']}
- **Puertos Sospechosos:** {estadisticas['puertos_sospechosos']}
- **Dispositivos en Red:** {estadisticas['dispositivos_en_red']}

## Conexiones Sospechosas Detectadas

"""
        
        if conexiones_sospechosas:
            contenido += "| Protocolo | Local | Remoto | Estado | Razones de Sospecha |\n"
            contenido += "|-----------|-------|--------|--------|--------------------||\n"
            
            for conexion in conexiones_sospechosas:
                local = f"{conexion['direccion_local']}:{conexion['puerto_local']}"
                remoto = f"{conexion['direccion_remota']}:{conexion['puerto_remoto']}" if conexion['direccion_remota'] else 'N/A'
                razones = ', '.join(conexion['razones_sospecha'])
                contenido += f"| {conexion['protocolo']} | {local} | {remoto} | {conexion['estado']} | {razones} |\n"
        else:
            contenido += "✅ No se detectaron conexiones sospechosas.\n"
        
        contenido += """

## Puertos Sospechosos Detectados

"""
        
        if puertos_sospechosos:
            contenido += "| Puerto | Protocolo | Servicio | Razones de Sospecha |\n"
            contenido += "|--------|-----------|----------|--------------------||\n"
            
            for puerto in puertos_sospechosos:
                razones = ', '.join(puerto['razones_sospecha'])
                contenido += f"| {puerto['puerto']} | {puerto['protocolo']} | {puerto['servicio']} | {razones} |\n"
        else:
            contenido += "✅ No se detectaron puertos sospechosos.\n"
        
        contenido += f"""

## Dispositivos Activos en Red

Total de dispositivos detectados: {len(dispositivos_red)}

"""
        
        if dispositivos_red:
            contenido += "| IP | Estado | Método de Detección |\n"
            contenido += "|----|--------|--------------------||\n"
            
            for dispositivo in dispositivos_red:
                contenido += f"| {dispositivo['ip']} | {dispositivo['estado']} | {dispositivo['metodo_deteccion']} |\n"
        else:
            contenido += "⚠️ No se pudieron detectar dispositivos en la red local.\n"
        
        contenido += """

## Recomendaciones de Seguridad

"""
        
        if conexiones_sospechosas or puertos_sospechosos:
            contenido += """### 🚨 Acción Inmediata Requerida
1. **Investigar conexiones sospechosas** identificadas
2. **Cerrar puertos innecesarios** o no autorizados
3. **Verificar procesos** asociados a puertos sospechosos
4. **Implementar firewall** para bloquear tráfico malicioso

"""
        
        contenido += """### ✅ Mejores Prácticas
- Monitorear conexiones de red regularmente
- Implementar reglas de firewall restrictivas
- Usar herramientas de detección de intrusiones
- Mantener inventario de servicios autorizados
- Revisar logs de conexiones periódicamente

### 🔧 Herramientas Recomendadas
- `netstat -tuln` - Ver conexiones activas
- `ss -tuln` - Alternativa moderna a netstat
- `nmap` - Escaneo de puertos y servicios
- `iptables` - Configuración de firewall
- `tcpdump` - Captura de paquetes de red

---

*Reporte generado por Ares Aegis - Antivirus Avanzado para Kali Linux*  
*Para más información sobre seguridad de red, consulte la documentación.*
"""
        
        # Guardar archivo
        try:
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                f.write(contenido)
        except Exception as e:
            if self.siem:
                self.siem.registrar_evento(
                    'ERROR',
                    'monitor_red',
                    f'Error al exportar reporte: {e}'
                )
            raise
        
        return ruta_archivo


# Función principal para uso desde línea de comandos
def main():
    """Función principal para ejecutar el monitor desde línea de comandos."""
    monitor = MonitorRed()
    resultado = monitor.escanear_sistema_red()
    
    print("=== Monitoreo de Red - Ares Aegis ===")
    print(f"Total de conexiones: {resultado['estadisticas']['total_conexiones']}")
    print(f"Conexiones sospechosas: {resultado['estadisticas']['conexiones_sospechosas']}")
    print(f"Puertos abiertos: {resultado['estadisticas']['total_puertos_abiertos']}")
    print(f"Puertos sospechosos: {resultado['estadisticas']['puertos_sospechosos']}")
    print(f"Dispositivos en red: {resultado['estadisticas']['dispositivos_en_red']}")
    
    if resultado['conexiones_sospechosas']:
        print("\n🚨 CONEXIONES SOSPECHOSAS:")
        for conexion in resultado['conexiones_sospechosas']:
            print(f"  - {conexion['protocolo']} {conexion['direccion_local']}:{conexion['puerto_local']} -> {conexion['direccion_remota']}:{conexion['puerto_remoto']}")
    
    if resultado['puertos_sospechosos']:
        print("\n🚨 PUERTOS SOSPECHOSOS:")
        for puerto in resultado['puertos_sospechosos']:
            print(f"  - Puerto {puerto['puerto']}/{puerto['protocolo']} ({puerto['servicio']})")
    
    # Exportar reporte
    archivo_reporte = monitor.exportar_reporte_markdown(resultado)
    print(f"\n📄 Reporte exportado a: {archivo_reporte}")


if __name__ == "__main__":
    main()
