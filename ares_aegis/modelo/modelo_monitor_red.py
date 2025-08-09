#!/usr/bin/env python3
"""
Creado por DogSoulDev (https://github.com/DogSoulDev)
Todos los derechos reservados. Este código es propietario y confidencial.

Monitor de Red - Ares Aegis
Sistema avanzado de monitoreo de conexiones de red para Kali Linux
"""

import os
import time
import logging
import subprocess
import re
import threading
import json
from typing import Dict, List, Optional, Tuple
from collections import defaultdict


class MonitorRed:
    """Monitor avanzado de red optimizado para Kali Linux."""
    
    def __init__(self, siem=None):
        """Inicializar el monitor de red."""
        self.logger = logging.getLogger(__name__)
        self.siem = siem
        self.monitoreando = False
        self.conexiones_activas = []
        self.estadisticas_red = {
            'bytes_enviados': 0,
            'bytes_recibidos': 0,
            'paquetes_enviados': 0,
            'paquetes_recibidos': 0,
            'conexiones_establecidas': 0,
            'puertos_abiertos': [],
            'interfaces_activas': []
        }
        self.conexiones_sospechosas = []
        self.puertos_monitoreados = [21, 22, 23, 25, 53, 80, 135, 139, 443, 445, 993, 995, 3389, 5432, 3306]
        self.info_sistema_red = {}
        
    def iniciar_monitoreo(self):
        """Iniciar el monitoreo de red."""
        self.monitoreando = True
        self.logger.info(" Monitor de red iniciado para Kali Linux")
        
    def detener_monitoreo(self):
        """Detener el monitoreo de red."""
        self.monitoreando = False
        self.logger.info(" Monitor de red detenido")
        
    def obtener_informacion_sistema_completa(self) -> Dict:
        """Obtener información completa del sistema de red en tiempo real."""
        info = {
            'interfaces': self.obtener_interfaces_red(),
            'conexiones_tcp': self.obtener_conexiones_tcp(),
            'conexiones_udp': self.obtener_conexiones_udp(),
            'puertos_escucha': self.obtener_puertos_escucha(),
            'estadisticas_trafico': self.obtener_estadisticas_trafico(),
            'routing_table': self.obtener_tabla_rutas(),
            'dns_info': self.obtener_informacion_dns(),
            'arp_table': self.obtener_tabla_arp(),
            'firewall_status': self.obtener_estado_firewall(),
            'conexiones_activas_detalladas': self.obtener_conexiones_detalladas(),
            'timestamp': time.time()
        }
        
        self.info_sistema_red = info
        return info
        
    def obtener_estadisticas(self):
        """Obtener estadísticas completas de red."""
        if self.monitoreando:
            self._actualizar_estadisticas_red()
        
        return {
            'conexiones_activas': len(self.conexiones_activas),
            'monitoreando': self.monitoreando,
            'timestamp': time.time(),
            'estadisticas': self.estadisticas_red.copy(),
            'conexiones_sospechosas': len(self.conexiones_sospechosas)
        }
        
    def obtener_conexiones(self):
        """Obtener lista de conexiones activas."""
        if self.monitoreando:
            self._actualizar_conexiones()
        return self.conexiones_activas
        
    def obtener_interfaces_red(self) -> List[Dict]:
        """Obtener información de interfaces de red usando herramientas nativas."""
        interfaces = []
        try:
            # Usar comando ip de Kali Linux
            result = subprocess.run(['ip', 'addr', 'show'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                interfaces = self._parsear_interfaces_ip(result.stdout)
            else:
                # Fallback a ifconfig si ip no funciona
                result = subprocess.run(['ifconfig'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    interfaces = self._parsear_interfaces_ifconfig(result.stdout)
                    
        except Exception as e:
            self.logger.warning(f"Error obteniendo interfaces: {e}")
            
        return interfaces
    
    def obtener_conexiones_netstat(self) -> List[Dict]:
        """Obtener conexiones usando netstat (herramienta nativa)."""
        conexiones = []
        try:
            # Usar netstat para obtener conexiones TCP
            result = subprocess.run(['netstat', '-tuln'], 
                                  capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                conexiones = self._parsear_netstat(result.stdout)
                
        except Exception as e:
            self.logger.warning(f"Error ejecutando netstat: {e}")
            
        return conexiones
    
    def obtener_trafico_interfaces(self) -> Dict:
        """Obtener estadísticas de tráfico de interfaces."""
        trafico = {}
        try:
            # Leer desde /proc/net/dev (disponible en Linux)
            with open('/proc/net/dev', 'r') as f:
                lines = f.readlines()
                
            for line in lines[2:]:  # Saltar headers
                if ':' in line:
                    parts = line.split(':')
                    interface = parts[0].strip()
                    stats = parts[1].split()
                    
                    if len(stats) >= 9:
                        trafico[interface] = {
                            'bytes_recibidos': int(stats[0]),
                            'paquetes_recibidos': int(stats[1]),
                            'bytes_enviados': int(stats[8]),
                            'paquetes_enviados': int(stats[9])
                        }
                        
        except Exception as e:
            self.logger.warning(f"Error leyendo tráfico de interfaces: {e}")
            
        return trafico
    
    def escanear_puertos_abiertos(self, host='127.0.0.1') -> List[int]:
        """Escanear puertos abiertos usando netstat."""
        puertos_abiertos = []
        try:
            # Usar netstat para puertos en escucha
            result = subprocess.run(['netstat', '-tln'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                puertos_abiertos = self._extraer_puertos_escucha(result.stdout)
                
        except Exception as e:
            self.logger.warning(f"Error escaneando puertos: {e}")
            
        return puertos_abiertos
    
    def detectar_conexiones_sospechosas(self) -> List[Dict]:
        """Detectar conexiones potencialmente sospechosas."""
        sospechosas = []
        try:
            # Obtener conexiones establecidas
            result = subprocess.run(['netstat', '-tupn'], 
                                  capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                sospechosas = self._analizar_conexiones_sospechosas(result.stdout)
                
        except Exception as e:
            self.logger.warning(f"Error detectando conexiones sospechosas: {e}")
            
        return sospechosas
    
    def _actualizar_estadisticas_red(self):
        """Actualizar estadísticas de red."""
        try:
            # Obtener tráfico de interfaces
            trafico = self.obtener_trafico_interfaces()
            
            # Sumar tráfico de todas las interfaces activas
            total_rx = sum(iface['bytes_recibidos'] for iface in trafico.values())
            total_tx = sum(iface['bytes_enviados'] for iface in trafico.values())
            total_rx_packets = sum(iface['paquetes_recibidos'] for iface in trafico.values())
            total_tx_packets = sum(iface['paquetes_enviados'] for iface in trafico.values())
            
            self.estadisticas_red.update({
                'bytes_recibidos': total_rx,
                'bytes_enviados': total_tx,
                'paquetes_recibidos': total_rx_packets,
                'paquetes_enviados': total_tx_packets,
                'interfaces_activas': list(trafico.keys()),
                'puertos_abiertos': self.escanear_puertos_abiertos()
            })
            
        except Exception as e:
            self.logger.warning(f"Error actualizando estadísticas de red: {e}")
    
    def _actualizar_conexiones(self):
        """Actualizar lista de conexiones activas."""
        try:
            self.conexiones_activas = self.obtener_conexiones_netstat()
            self.conexiones_sospechosas = self.detectar_conexiones_sospechosas()
            
        except Exception as e:
            self.logger.warning(f"Error actualizando conexiones: {e}")
    
    def _parsear_interfaces_ip(self, output: str) -> List[Dict]:
        """Parsear salida del comando 'ip addr show'."""
        interfaces = []
        current_interface = None
        
        for line in output.split('\n'):
            line = line.strip()
            
            # Nueva interfaz
            if line and line[0].isdigit():
                if current_interface:
                    interfaces.append(current_interface)
                
                parts = line.split()
                if len(parts) >= 2:
                    nombre = parts[1].rstrip(':')
                    current_interface = {
                        'nombre': nombre,
                        'estado': 'UP' if 'UP' in line else 'DOWN',
                        'ips': [],
                        'mac': ''
                    }
            
            # Dirección IP
            elif 'inet ' in line and current_interface:
                ip_match = re.search(r'inet (\S+)', line)
                if ip_match:
                    current_interface['ips'].append(ip_match.group(1))
            
            # Dirección MAC
            elif 'link/ether' in line and current_interface:
                mac_match = re.search(r'link/ether (\S+)', line)
                if mac_match:
                    current_interface['mac'] = mac_match.group(1)
        
        if current_interface:
            interfaces.append(current_interface)
            
        return interfaces
    
    def _parsear_interfaces_ifconfig(self, output: str) -> List[Dict]:
        """Parsear salida del comando ifconfig."""
        interfaces = []
        current_interface = None
        
        for line in output.split('\n'):
            line = line.strip()
            
            # Nueva interfaz (línea no empieza con espacio)
            if line and not line.startswith(' ') and ':' in line:
                if current_interface:
                    interfaces.append(current_interface)
                
                nombre = line.split(':')[0]
                current_interface = {
                    'nombre': nombre,
                    'estado': 'UP' if 'UP' in line else 'DOWN',
                    'ips': [],
                    'mac': ''
                }
            
            # Información de la interfaz actual
            elif current_interface:
                if 'inet ' in line:
                    ip_match = re.search(r'inet (\S+)', line)
                    if ip_match:
                        current_interface['ips'].append(ip_match.group(1))
                
                if 'ether ' in line:
                    mac_match = re.search(r'ether (\S+)', line)
                    if mac_match:
                        current_interface['mac'] = mac_match.group(1)
        
        if current_interface:
            interfaces.append(current_interface)
            
        return interfaces
    
    def _parsear_netstat(self, output: str) -> List[Dict]:
        """Parsear salida de netstat."""
        conexiones = []
        
        for line in output.split('\n'):
            if 'tcp' in line.lower() or 'udp' in line.lower():
                parts = line.split()
                if len(parts) >= 4:
                    conexion = {
                        'protocolo': parts[0],
                        'direccion_local': parts[3],
                        'direccion_remota': parts[4] if len(parts) > 4 else '',
                        'estado': parts[5] if len(parts) > 5 else '',
                        'proceso': parts[6] if len(parts) > 6 else ''
                    }
                    conexiones.append(conexion)
        
        return conexiones
    
    def _extraer_puertos_escucha(self, output: str) -> List[int]:
        """Extraer puertos en escucha de la salida de netstat."""
        puertos = []
        
        for line in output.split('\n'):
            if 'LISTEN' in line:
                parts = line.split()
                if len(parts) >= 4:
                    direccion_local = parts[3]
                    if ':' in direccion_local:
                        puerto_str = direccion_local.split(':')[-1]
                        try:
                            puerto = int(puerto_str)
                            if puerto not in puertos:
                                puertos.append(puerto)
                        except ValueError:
                            pass
        
        return sorted(puertos)
    
    def _analizar_conexiones_sospechosas(self, output: str) -> List[Dict]:
        """Analizar conexiones para detectar comportamiento sospechoso."""
        sospechosas = []
        conexiones_por_ip = defaultdict(int)
        
        for line in output.split('\n'):
            if 'ESTABLISHED' in line:
                parts = line.split()
                if len(parts) >= 5:
                    direccion_remota = parts[4]
                    if ':' in direccion_remota:
                        ip_remota = direccion_remota.split(':')[0]
                        
                        # Contar conexiones por IP
                        conexiones_por_ip[ip_remota] += 1
                        
                        # Verificar si es una IP sospechosa
                        if self._es_ip_sospechosa(ip_remota):
                            sospechosas.append({
                                'ip_remota': ip_remota,
                                'direccion_local': parts[3],
                                'tipo': 'IP_SOSPECHOSA',
                                'detalles': f"Conexión a IP potencialmente maliciosa: {ip_remota}"
                            })
        
        # Detectar demasiadas conexiones desde una IP
        for ip, count in conexiones_por_ip.items():
            if count > 10:  # Umbral configurable
                sospechosas.append({
                    'ip_remota': ip,
                    'tipo': 'MULTIPLES_CONEXIONES',
                    'detalles': f"Demasiadas conexiones desde {ip}: {count}"
                })
        
        return sospechosas
    
    def _es_ip_sospechosa(self, ip: str) -> bool:
        """Verificar si una IP es potencialmente sospechosa."""
        # IPs privadas generalmente no son sospechosas
        if ip.startswith(('192.168.', '10.', '172.16.', '172.17.', '172.18.', 
                         '172.19.', '172.20.', '172.21.', '172.22.', '172.23.',
                         '172.24.', '172.25.', '172.26.', '172.27.', '172.28.',
                         '172.29.', '172.30.', '172.31.', '127.')):
            return False
        
        # Aquí se podrían agregar verificaciones adicionales:
        # - Consulta a bases de datos de IPs maliciosas
        # - Verificación de geolocalización
        # - Patrones de tráfico anómalos
        
        return False
        
    def generar_reporte_avanzado(self):
        """Generar reporte avanzado de red."""
        interfaces = self.obtener_interfaces_red()
        conexiones = self.obtener_conexiones_netstat()
        puertos_abiertos = self.escanear_puertos_abiertos()
        trafico = self.obtener_trafico_interfaces()
        
        reporte = "#  REPORTE AVANZADO DE RED - ARES AEGIS\n\n"
        
        # Interfaces de red
        reporte += "##  INTERFACES DE RED\n"
        for interface in interfaces:
            estado_emoji = "" if interface['estado'] == 'UP' else ""
            reporte += f"{estado_emoji} **{interface['nombre']}** ({interface['estado']})\n"
            if interface['ips']:
                reporte += f"    IPs: {', '.join(interface['ips'])}\n"
            if interface['mac']:
                reporte += f"    MAC: {interface['mac']}\n"
            reporte += "\n"
        
        # Tráfico de red
        reporte += "## [STATS] TRÁFICO DE RED\n"
        for iface, stats in trafico.items():
            reporte += f" **{iface}**:\n"
            reporte += f"    Recibido: {self._formatear_bytes(stats['bytes_recibidos'])} ({stats['paquetes_recibidos']:,} paquetes)\n"
            reporte += f"    Enviado: {self._formatear_bytes(stats['bytes_enviados'])} ({stats['paquetes_enviados']:,} paquetes)\n\n"
        
        # Puertos abiertos
        reporte += "##  PUERTOS ABIERTOS\n"
        if puertos_abiertos:
            for puerto in puertos_abiertos:
                riesgo = "" if puerto in self.puertos_monitoreados else ""
                reporte += f"{riesgo} Puerto {puerto}\n"
        else:
            reporte += "[OK] No se detectaron puertos abiertos públicos\n"
        reporte += "\n"
        
        # Conexiones activas
        reporte += f"##  CONEXIONES ACTIVAS ({len(conexiones)})\n"
        for conn in conexiones[:10]:  # Mostrar solo las primeras 10
            reporte += f" {conn['protocolo']} {conn['direccion_local']} → {conn['direccion_remota']} ({conn['estado']})\n"
        
        if len(conexiones) > 10:
            reporte += f"... y {len(conexiones) - 10} conexiones más\n"
        
        # Conexiones sospechosas
        if self.conexiones_sospechosas:
            reporte += "\n##  CONEXIONES SOSPECHOSAS\n"
            for sospechosa in self.conexiones_sospechosas:
                reporte += f" {sospechosa['tipo']}: {sospechosa['detalles']}\n"
        
        reporte += f"\n---\n*Generado: {time.strftime('%Y-%m-%d %H:%M:%S')}*"
        
        return reporte
    
    def _formatear_bytes(self, bytes_count: int) -> str:
        """Formatear bytes en unidades legibles."""
        bytes_float = float(bytes_count)
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_float < 1024.0:
                return f"{bytes_float:.1f} {unit}"
            bytes_float /= 1024.0
        return f"{bytes_float:.1f} PB"
    
    def obtener_conexiones_tcp(self) -> List[Dict]:
        """Obtener conexiones TCP usando herramientas nativas."""
        conexiones = []
        try:
            result = subprocess.run(['netstat', '-tn'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines[2:]:  # Saltar headers
                    parts = line.split()
                    if len(parts) >= 6 and parts[0] == 'tcp':
                        conexiones.append({
                            'protocolo': 'TCP',
                            'local_addr': parts[3],
                            'remote_addr': parts[4],
                            'estado': parts[5],
                            'timestamp': time.time()
                        })
        except Exception as e:
            self.logger.warning(f"Error obteniendo conexiones TCP: {e}")
        return conexiones
    
    def obtener_conexiones_udp(self) -> List[Dict]:
        """Obtener conexiones UDP usando herramientas nativas."""
        conexiones = []
        try:
            result = subprocess.run(['netstat', '-un'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines[2:]:  # Saltar headers
                    parts = line.split()
                    if len(parts) >= 4 and parts[0] == 'udp':
                        conexiones.append({
                            'protocolo': 'UDP',
                            'local_addr': parts[3],
                            'remote_addr': parts[4] if len(parts) > 4 else 'N/A',
                            'estado': 'LISTENING',
                            'timestamp': time.time()
                        })
        except Exception as e:
            self.logger.warning(f"Error obteniendo conexiones UDP: {e}")
        return conexiones
    
    def obtener_puertos_escucha(self) -> List[Dict]:
        """Obtener puertos en escucha usando netstat."""
        puertos = []
        try:
            result = subprocess.run(['netstat', '-tln'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines[2:]:  # Saltar headers
                    parts = line.split()
                    if len(parts) >= 6 and 'LISTEN' in parts[5]:
                        local_addr = parts[3]
                        if ':' in local_addr:
                            ip, puerto = local_addr.rsplit(':', 1)
                            puertos.append({
                                'puerto': int(puerto),
                                'ip': ip,
                                'protocolo': parts[0].upper(),
                                'servicio': self._identificar_servicio(int(puerto)),
                                'timestamp': time.time()
                            })
        except Exception as e:
            self.logger.warning(f"Error obteniendo puertos en escucha: {e}")
        return puertos
    
    def obtener_estadisticas_trafico(self) -> Dict:
        """Obtener estadísticas detalladas de tráfico de red."""
        estadisticas = {}
        try:
            with open('/proc/net/dev', 'r') as f:
                lines = f.readlines()
            
            for line in lines[2:]:  # Saltar headers
                if ':' in line:
                    parts = line.split(':')
                    interface = parts[0].strip()
                    stats = parts[1].split()
                    
                    if len(stats) >= 16:
                        estadisticas[interface] = {
                            'bytes_rx': int(stats[0]),
                            'packets_rx': int(stats[1]),
                            'errors_rx': int(stats[2]),
                            'dropped_rx': int(stats[3]),
                            'bytes_tx': int(stats[8]),
                            'packets_tx': int(stats[9]),
                            'errors_tx': int(stats[10]),
                            'dropped_tx': int(stats[11]),
                            'timestamp': time.time()
                        }
        except Exception as e:
            self.logger.warning(f"Error obteniendo estadísticas de tráfico: {e}")
        return estadisticas
    
    def obtener_tabla_rutas(self) -> List[Dict]:
        """Obtener tabla de rutas usando herramientas nativas."""
        rutas = []
        try:
            result = subprocess.run(['route', '-n'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines[2:]:  # Saltar headers
                    parts = line.split()
                    if len(parts) >= 8:
                        rutas.append({
                            'destino': parts[0],
                            'gateway': parts[1],
                            'mascara': parts[2],
                            'flags': parts[3],
                            'interface': parts[7],
                            'timestamp': time.time()
                        })
        except Exception as e:
            self.logger.warning(f"Error obteniendo tabla de rutas: {e}")
        return rutas
    
    def obtener_informacion_dns(self) -> Dict:
        """Obtener información de DNS del sistema."""
        dns_info = {}
        try:
            # Leer resolv.conf
            with open('/etc/resolv.conf', 'r') as f:
                lines = f.readlines()
            
            dns_servers = []
            search_domains = []
            
            for line in lines:
                line = line.strip()
                if line.startswith('nameserver'):
                    dns_servers.append(line.split()[1])
                elif line.startswith('search'):
                    search_domains.extend(line.split()[1:])
            
            dns_info = {
                'dns_servers': dns_servers,
                'search_domains': search_domains,
                'timestamp': time.time()
            }
        except Exception as e:
            self.logger.warning(f"Error obteniendo información DNS: {e}")
        return dns_info
    
    def obtener_tabla_arp(self) -> List[Dict]:
        """Obtener tabla ARP usando herramientas nativas."""
        arp_entries = []
        try:
            result = subprocess.run(['arp', '-a'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    # Parsear líneas como: hostname (192.168.1.1) at 00:11:22:33:44:55 [ether] on eth0
                    match = re.search(r'(\S+)\s+\(([^)]+)\)\s+at\s+([0-9a-f:]{17})', line)
                    if match:
                        hostname, ip, mac = match.groups()
                        arp_entries.append({
                            'hostname': hostname,
                            'ip': ip,
                            'mac': mac,
                            'timestamp': time.time()
                        })
        except Exception as e:
            self.logger.warning(f"Error obteniendo tabla ARP: {e}")
        return arp_entries
    
    def obtener_estado_firewall(self) -> Dict:
        """Obtener estado del firewall usando iptables."""
        firewall_info = {}
        try:
            # Verificar iptables
            result = subprocess.run(['iptables', '-L', '-n'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                firewall_info['iptables'] = {
                    'activo': True,
                    'reglas': result.stdout.count('\n'),
                    'timestamp': time.time()
                }
            
            # Verificar ufw si está disponible
            result_ufw = subprocess.run(['ufw', 'status'], 
                                      capture_output=True, text=True, timeout=5)
            
            if result_ufw.returncode == 0:
                status = 'activo' if 'Status: active' in result_ufw.stdout else 'inactivo'
                firewall_info['ufw'] = {
                    'estado': status,
                    'timestamp': time.time()
                }
        except Exception as e:
            self.logger.warning(f"Error obteniendo estado del firewall: {e}")
        return firewall_info
    
    def obtener_conexiones_detalladas(self) -> List[Dict]:
        """Obtener conexiones activas con información detallada."""
        conexiones = []
        try:
            result = subprocess.run(['ss', '-tuln'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines[1:]:  # Saltar header
                    parts = line.split()
                    if len(parts) >= 5:
                        conexiones.append({
                            'protocolo': parts[0],
                            'estado': parts[1],
                            'recv_q': parts[2],
                            'send_q': parts[3],
                            'local_addr': parts[4],
                            'peer_addr': parts[5] if len(parts) > 5 else 'N/A',
                            'timestamp': time.time()
                        })
        except Exception as e:
            # Fallback a netstat si ss no está disponible
            try:
                result = subprocess.run(['netstat', '-tupln'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    conexiones = self._parsear_netstat_detallado(result.stdout)
            except Exception as e2:
                self.logger.warning(f"Error obteniendo conexiones detalladas: {e}, {e2}")
        return conexiones
    
    def _identificar_servicio(self, puerto: int) -> str:
        """Identificar servicio común por puerto."""
        servicios_comunes = {
            21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP', 
            53: 'DNS', 80: 'HTTP', 110: 'POP3', 143: 'IMAP',
            443: 'HTTPS', 993: 'IMAPS', 995: 'POP3S',
            3306: 'MySQL', 5432: 'PostgreSQL', 3389: 'RDP',
            135: 'RPC', 139: 'NetBIOS', 445: 'SMB'
        }
        return servicios_comunes.get(puerto, 'Desconocido')
    
    def _parsear_netstat_detallado(self, output: str) -> List[Dict]:
        """Parsear salida detallada de netstat."""
        conexiones = []
        lines = output.strip().split('\n')
        for line in lines[2:]:  # Saltar headers
            parts = line.split()
            if len(parts) >= 6:
                conexiones.append({
                    'protocolo': parts[0],
                    'estado': parts[5] if len(parts) > 5 else 'N/A',
                    'recv_q': '0',
                    'send_q': '0',
                    'local_addr': parts[3],
                    'peer_addr': parts[4],
                    'timestamp': time.time()
                })
        return conexiones

