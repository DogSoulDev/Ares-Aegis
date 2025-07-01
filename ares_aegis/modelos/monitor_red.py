#!/usr/bin/env python3
"""
Monitor de Red
Sistema de monitoreo de red para Ares Aegis

Autor: DogSoulDev
Versión: 2.0.0
"""

import socket
import threading
import time
import json
import subprocess
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass
from collections import defaultdict

from .siem import SIEM, TipoEvento
from ..utilidades.validaciones import validar_ip, validar_puerto
from ..utilidades.ayuda_logging import configurar_logger_modulo


@dataclass
class ConexionRed:
    """Representa una conexión de red."""
    direccion_local: str
    puerto_local: int
    direccion_remota: str
    puerto_remoto: int
    protocolo: str
    estado: str
    proceso_id: int
    proceso_nombre: str
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la conexión a diccionario."""
        return {
            'direccion_local': self.direccion_local,
            'puerto_local': self.puerto_local,
            'direccion_remota': self.direccion_remota,
            'puerto_remoto': self.puerto_remoto,
            'protocolo': self.protocolo,
            'estado': self.estado,
            'proceso_id': self.proceso_id,
            'proceso_nombre': self.proceso_nombre,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class PuertoAbierto:
    """Representa un puerto abierto en el sistema."""
    numero: int
    protocolo: str
    direccion: str
    proceso_id: int
    proceso_nombre: str
    estado: str
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el puerto a diccionario."""
        return {
            'numero': self.numero,
            'protocolo': self.protocolo,
            'direccion': self.direccion,
            'proceso_id': self.proceso_id,
            'proceso_nombre': self.proceso_nombre,
            'estado': self.estado,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class AlertaRed:
    """Representa una alerta de red."""
    tipo: str
    descripcion: str
    direccion_origen: str
    direccion_destino: str
    puerto: int
    protocolo: str
    severidad: str
    detalles: Dict[str, Any]
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la alerta a diccionario."""
        return {
            'tipo': self.tipo,
            'descripcion': self.descripcion,
            'direccion_origen': self.direccion_origen,
            'direccion_destino': self.direccion_destino,
            'puerto': self.puerto,
            'protocolo': self.protocolo,
            'severidad': self.severidad,
            'detalles': self.detalles,
            'timestamp': self.timestamp.isoformat()
        }
    
    def to_markdown(self) -> str:
        """Convierte la alerta a formato Markdown."""
        emoji_severidad = {
            'CRITICO': '🚨',
            'ALTO': '⚠️',
            'MEDIO': '⚡',
            'BAJO': 'ℹ️'
        }.get(self.severidad, '📋')
        
        md = f"### {emoji_severidad} {self.tipo} - {self.severidad}\n\n"
        md += f"**Descripción:** {self.descripcion}\n"
        md += f"**Origen:** {self.direccion_origen}\n"
        md += f"**Destino:** {self.direccion_destino}:{self.puerto}\n"
        md += f"**Protocolo:** {self.protocolo}\n"
        md += f"**Timestamp:** {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        if self.detalles:
            md += "\n**Detalles:**\n"
            for clave, valor in self.detalles.items():
                md += f"- **{clave}:** {valor}\n"
        
        md += "\n"
        return md


class AnalizadorTrafico:
    """Analizador de tráfico de red para detectar patrones sospechosos."""
    
    def __init__(self):
        """Inicializa el analizador de tráfico."""
        self.contador_conexiones = defaultdict(int)
        self.historial_conexiones = defaultdict(list)
        self.ips_bloqueadas: Set[str] = set()
        self.puertos_monitoreados = {22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 3389}
        
        # Umbrales para detección
        self.umbral_conexiones_por_minuto = 50
        self.umbral_conexiones_totales = 1000
        self.umbral_escaneo_puertos = 10
    
    def analizar_conexion(self, conexion: ConexionRed) -> List[AlertaRed]:
        """
        Analiza una conexión y detecta patrones sospechosos.
        
        Args:
            conexion: Conexión a analizar
            
        Returns:
            List[AlertaRed]: Lista de alertas generadas
        """
        alertas = []
        ip_remota = conexion.direccion_remota
        
        # Verificar IP bloqueada
        if ip_remota in self.ips_bloqueadas:
            alerta = AlertaRed(
                tipo="IP_BLOQUEADA",
                descripcion=f"Conexión desde IP bloqueada: {ip_remota}",
                direccion_origen=ip_remota,
                direccion_destino=conexion.direccion_local,
                puerto=conexion.puerto_local,
                protocolo=conexion.protocolo,
                severidad="ALTO",
                detalles={'proceso': conexion.proceso_nombre},
                timestamp=conexion.timestamp
            )
            alertas.append(alerta)
        
        # Contar conexiones por IP
        self.contador_conexiones[ip_remota] += 1
        self.historial_conexiones[ip_remota].append(conexion.timestamp)
        
        # Limpiar historial antiguo (últimos 5 minutos)
        limite_tiempo = datetime.now().timestamp() - 300
        self.historial_conexiones[ip_remota] = [
            ts for ts in self.historial_conexiones[ip_remota]
            if ts.timestamp() > limite_tiempo
        ]
        
        # Detectar demasiadas conexiones por minuto
        conexiones_recientes = len(self.historial_conexiones[ip_remota])
        if conexiones_recientes > self.umbral_conexiones_por_minuto:
            alerta = AlertaRed(
                tipo="EXCESO_CONEXIONES",
                descripcion=f"Demasiadas conexiones desde {ip_remota}: {conexiones_recientes} en 5 min",
                direccion_origen=ip_remota,
                direccion_destino=conexion.direccion_local,
                puerto=conexion.puerto_local,
                protocolo=conexion.protocolo,
                severidad="ALTO",
                detalles={'conexiones_recientes': conexiones_recientes},
                timestamp=conexion.timestamp
            )
            alertas.append(alerta)
        
        # Detectar total de conexiones sospechoso
        if self.contador_conexiones[ip_remota] > self.umbral_conexiones_totales:
            alerta = AlertaRed(
                tipo="CONEXIONES_MASIVAS",
                descripcion=f"Conexiones masivas desde {ip_remota}: {self.contador_conexiones[ip_remota]} total",
                direccion_origen=ip_remota,
                direccion_destino=conexion.direccion_local,
                puerto=conexion.puerto_local,
                protocolo=conexion.protocolo,
                severidad="CRITICO",
                detalles={'total_conexiones': self.contador_conexiones[ip_remota]},
                timestamp=conexion.timestamp
            )
            alertas.append(alerta)
        
        # Detectar conexiones a puertos sensibles
        if conexion.puerto_local in self.puertos_monitoreados:
            alerta = AlertaRed(
                tipo="PUERTO_SENSIBLE",
                descripcion=f"Conexión a puerto sensible {conexion.puerto_local} desde {ip_remota}",
                direccion_origen=ip_remota,
                direccion_destino=conexion.direccion_local,
                puerto=conexion.puerto_local,
                protocolo=conexion.protocolo,
                severidad="MEDIO",
                detalles={'puerto_sensible': True},
                timestamp=conexion.timestamp
            )
            alertas.append(alerta)
        
        return alertas
    
    def detectar_escaneo_puertos(self) -> List[AlertaRed]:
        """
        Detecta posibles escaneos de puertos.
        
        Returns:
            List[AlertaRed]: Lista de alertas de escaneo detectadas
        """
        alertas = []
        
        # Agrupar conexiones por IP en las últimas conexiones
        puertos_por_ip = defaultdict(set)
        
        for ip, timestamps in self.historial_conexiones.items():
            if len(timestamps) >= self.umbral_escaneo_puertos:
                # Esta IP ha hecho muchas conexiones, verificar si son a puertos diferentes
                # Nota: En una implementación real, necesitaríamos más información
                # sobre los puertos específicos de cada conexión
                if len(timestamps) > self.umbral_escaneo_puertos * 2:
                    alerta = AlertaRed(
                        tipo="POSIBLE_ESCANEO",
                        descripcion=f"Posible escaneo de puertos desde {ip}",
                        direccion_origen=ip,
                        direccion_destino="MULTIPLE",
                        puerto=0,
                        protocolo="MULTIPLE",
                        severidad="ALTO",
                        detalles={'conexiones_sospechosas': len(timestamps)},
                        timestamp=datetime.now()
                    )
                    alertas.append(alerta)
        
        return alertas
    
    def bloquear_ip(self, ip: str):
        """
        Bloquea una IP específica.
        
        Args:
            ip: Dirección IP a bloquear
        """
        if validar_ip(ip):
            self.ips_bloqueadas.add(ip)
    
    def desbloquear_ip(self, ip: str):
        """
        Desbloquea una IP específica.
        
        Args:
            ip: Dirección IP a desbloquear
        """
        self.ips_bloqueadas.discard(ip)


class MonitorRed:
    """Sistema de monitoreo de red."""
    
    def __init__(self, siem: SIEM):
        """
        Inicializa el monitor de red.
        
        Args:
            siem: Instancia del SIEM para registro de eventos
        """
        self.siem = siem
        self.logger = configurar_logger_modulo("monitor_red")
        
        # Componentes del monitor
        self.analizador_trafico = AnalizadorTrafico()
        
        # Estado del monitoreo
        self.monitoreando = False
        self.hilo_monitoreo: Optional[threading.Thread] = None
        
        # Datos de conexiones
        self.conexiones_activas: List[ConexionRed] = []
        self.puertos_abiertos: List[PuertoAbierto] = []
        self.alertas_generadas: List[AlertaRed] = []
        
        # Configuración
        self.intervalo_monitoreo = 10  # segundos
        self.mantener_historial_horas = 24
        
        self.logger.info("Monitor de red inicializado")
        self.siem.registrar_evento(
            TipoEvento.SISTEMA_INICIADO,
            "Monitor de red inicializado",
            nivel_criticidad="MEDIO"
        )
    
    def _obtener_conexiones_activas(self) -> List[ConexionRed]:
        """
        Obtiene las conexiones de red activas usando netstat.
        
        Returns:
            List[ConexionRed]: Lista de conexiones activas
        """
        conexiones = []
        
        try:
            # Ejecutar netstat para obtener conexiones
            resultado = subprocess.run(
                ['netstat', '-tuln'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if resultado.returncode == 0:
                lineas = resultado.stdout.split('\n')
                
                for linea in lineas:
                    if 'LISTEN' in linea or 'ESTABLISHED' in linea:
                        partes = linea.split()
                        if len(partes) >= 6:
                            protocolo = partes[0].lower()
                            direccion_local = partes[3]
                            direccion_remota = partes[4] if len(partes) > 4 else "0.0.0.0:0"
                            estado = partes[5] if len(partes) > 5 else "UNKNOWN"
                            
                            # Parsear direcciones y puertos
                            try:
                                if ':' in direccion_local:
                                    addr_local, puerto_local_str = direccion_local.rsplit(':', 1)
                                    puerto_local = int(puerto_local_str)
                                else:
                                    addr_local = direccion_local
                                    puerto_local = 0
                                
                                if ':' in direccion_remota:
                                    addr_remota, puerto_remoto_str = direccion_remota.rsplit(':', 1)
                                    puerto_remoto = int(puerto_remoto_str)
                                else:
                                    addr_remota = direccion_remota
                                    puerto_remoto = 0
                                
                                # Limpiar direcciones IPv6
                                if addr_local.startswith('::'):
                                    addr_local = '0.0.0.0'
                                if addr_remota.startswith('::'):
                                    addr_remota = '0.0.0.0'
                                
                                conexion = ConexionRed(
                                    direccion_local=addr_local,
                                    puerto_local=puerto_local,
                                    direccion_remota=addr_remota,
                                    puerto_remoto=puerto_remoto,
                                    protocolo=protocolo,
                                    estado=estado,
                                    proceso_id=0,  # netstat básico no proporciona PID
                                    proceso_nombre="unknown",
                                    timestamp=datetime.now()
                                )
                                
                                conexiones.append(conexion)
                            
                            except ValueError:
                                # Error parseando puertos, continuar con siguiente línea
                                continue
        
        except subprocess.TimeoutExpired:
            self.logger.warning("Timeout ejecutando netstat")
        except Exception as e:
            self.logger.error(f"Error obteniendo conexiones activas: {e}")
        
        return conexiones
    
    def _obtener_conexiones_con_procesos(self) -> List[ConexionRed]:
        """
        Obtiene conexiones con información de procesos usando ss.
        
        Returns:
            List[ConexionRed]: Lista de conexiones con información de procesos
        """
        conexiones = []
        
        try:
            # Usar ss que proporciona más información
            resultado = subprocess.run(
                ['ss', '-tulpn'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if resultado.returncode == 0:
                lineas = resultado.stdout.split('\n')
                
                for linea in lineas[1:]:  # Saltar encabezado
                    if not linea.strip():
                        continue
                    
                    partes = linea.split()
                    if len(partes) >= 5:
                        protocolo = partes[0].lower()
                        estado = partes[1]
                        direccion_local = partes[4]
                        direccion_remota = partes[5] if len(partes) > 5 else "0.0.0.0:0"
                        
                        # Extraer información del proceso
                        proceso_info = ""
                        proceso_id = 0
                        proceso_nombre = "unknown"
                        
                        if len(partes) > 6:
                            proceso_info = partes[6]
                            # Parsear algo como "users:(("sshd",pid=1234,fd=3))"
                            match = re.search(r'pid=(\d+)', proceso_info)
                            if match:
                                proceso_id = int(match.group(1))
                            
                            match = re.search(r'"([^"]+)"', proceso_info)
                            if match:
                                proceso_nombre = match.group(1)
                        
                        # Parsear direcciones y puertos
                        try:
                            if ':' in direccion_local:
                                addr_local, puerto_local_str = direccion_local.rsplit(':', 1)
                                puerto_local = int(puerto_local_str)
                            else:
                                addr_local = direccion_local
                                puerto_local = 0
                            
                            if ':' in direccion_remota and direccion_remota != "*:*":
                                addr_remota, puerto_remoto_str = direccion_remota.rsplit(':', 1)
                                try:
                                    puerto_remoto = int(puerto_remoto_str)
                                except ValueError:
                                    puerto_remoto = 0
                            else:
                                addr_remota = "0.0.0.0"
                                puerto_remoto = 0
                            
                            # Limpiar direcciones
                            if addr_local == '*':
                                addr_local = '0.0.0.0'
                            if addr_remota == '*':
                                addr_remota = '0.0.0.0'
                            
                            conexion = ConexionRed(
                                direccion_local=addr_local,
                                puerto_local=puerto_local,
                                direccion_remota=addr_remota,
                                puerto_remoto=puerto_remoto,
                                protocolo=protocolo,
                                estado=estado,
                                proceso_id=proceso_id,
                                proceso_nombre=proceso_nombre,
                                timestamp=datetime.now()
                            )
                            
                            conexiones.append(conexion)
                        
                        except ValueError:
                            # Error parseando, continuar
                            continue
        
        except subprocess.TimeoutExpired:
            self.logger.warning("Timeout ejecutando ss")
        except FileNotFoundError:
            # ss no disponible, usar método alternativo
            return self._obtener_conexiones_activas()
        except Exception as e:
            self.logger.error(f"Error obteniendo conexiones con procesos: {e}")
        
        return conexiones
    
    def _obtener_puertos_abiertos(self) -> List[PuertoAbierto]:
        """
        Obtiene los puertos abiertos en el sistema.
        
        Returns:
            List[PuertoAbierto]: Lista de puertos abiertos
        """
        puertos = []
        
        try:
            # Usar ss para puertos en escucha
            resultado = subprocess.run(
                ['ss', '-tlpn'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if resultado.returncode == 0:
                lineas = resultado.stdout.split('\n')
                
                for linea in lineas[1:]:  # Saltar encabezado
                    if not linea.strip() or 'LISTEN' not in linea:
                        continue
                    
                    partes = linea.split()
                    if len(partes) >= 4:
                        protocolo = partes[0].lower()
                        direccion_local = partes[3]
                        
                        # Extraer información del proceso
                        proceso_id = 0
                        proceso_nombre = "unknown"
                        
                        if len(partes) > 5:
                            proceso_info = partes[5]
                            match = re.search(r'pid=(\d+)', proceso_info)
                            if match:
                                proceso_id = int(match.group(1))
                            
                            match = re.search(r'"([^"]+)"', proceso_info)
                            if match:
                                proceso_nombre = match.group(1)
                        
                        # Parsear dirección y puerto
                        try:
                            if ':' in direccion_local:
                                addr, puerto_str = direccion_local.rsplit(':', 1)
                                puerto_num = int(puerto_str)
                            else:
                                addr = direccion_local
                                puerto_num = 0
                            
                            if addr == '*':
                                addr = '0.0.0.0'
                            
                            puerto = PuertoAbierto(
                                numero=puerto_num,
                                protocolo=protocolo,
                                direccion=addr,
                                proceso_id=proceso_id,
                                proceso_nombre=proceso_nombre,
                                estado="LISTEN",
                                timestamp=datetime.now()
                            )
                            
                            puertos.append(puerto)
                        
                        except ValueError:
                            # Error parseando puerto, continuar
                            continue
        
        except subprocess.TimeoutExpired:
            self.logger.warning("Timeout obteniendo puertos abiertos")
        except Exception as e:
            self.logger.error(f"Error obteniendo puertos abiertos: {e}")
        
        return puertos
    
    def _ciclo_monitoreo(self):
        """Ciclo principal de monitoreo de red."""
        self.logger.info("Iniciando ciclo de monitoreo de red")
        
        while self.monitoreando:
            try:
                # Obtener conexiones actuales
                conexiones_actuales = self._obtener_conexiones_con_procesos()
                self.conexiones_activas = conexiones_actuales
                
                # Obtener puertos abiertos
                puertos_actuales = self._obtener_puertos_abiertos()
                self.puertos_abiertos = puertos_actuales
                
                # Analizar tráfico y generar alertas
                for conexion in conexiones_actuales:
                    if conexion.direccion_remota != "0.0.0.0" and conexion.estado == "ESTABLISHED":
                        alertas = self.analizador_trafico.analizar_conexion(conexion)
                        
                        for alerta in alertas:
                            self.alertas_generadas.append(alerta)
                            
                            # Registrar en SIEM
                            self.siem.registrar_evento(
                                TipoEvento.CONEXION_SOSPECHOSA,
                                f"Alerta de red: {alerta.tipo}",
                                alerta.to_dict(),
                                alerta.severidad
                            )
                
                # Detectar escaneos de puertos
                alertas_escaneo = self.analizador_trafico.detectar_escaneo_puertos()
                for alerta in alertas_escaneo:
                    self.alertas_generadas.append(alerta)
                    
                    self.siem.registrar_evento(
                        TipoEvento.CONEXION_SOSPECHOSA,
                        f"Posible escaneo detectado: {alerta.descripcion}",
                        alerta.to_dict(),
                        alerta.severidad
                    )
                
                # Limpiar alertas antiguas
                self._limpiar_alertas_antiguas()
                
                # Log de estadísticas
                if len(conexiones_actuales) > 0 or len(puertos_actuales) > 0:
                    self.logger.debug(f"Monitor red: {len(conexiones_actuales)} conexiones, "
                                    f"{len(puertos_actuales)} puertos, "
                                    f"{len(self.alertas_generadas)} alertas")
                
                # Esperar antes del siguiente ciclo
                time.sleep(self.intervalo_monitoreo)
            
            except Exception as e:
                self.logger.error(f"Error en ciclo de monitoreo de red: {e}")
                time.sleep(self.intervalo_monitoreo)
        
        self.logger.info("Ciclo de monitoreo de red finalizado")
    
    def _limpiar_alertas_antiguas(self):
        """Limpia alertas más antiguas que el límite configurado."""
        limite_tiempo = datetime.now().timestamp() - (self.mantener_historial_horas * 3600)
        
        self.alertas_generadas = [
            alerta for alerta in self.alertas_generadas
            if alerta.timestamp.timestamp() > limite_tiempo
        ]
    
    def iniciar_monitoreo(self):
        """Inicia el monitoreo de red."""
        if not self.monitoreando:
            self.monitoreando = True
            self.hilo_monitoreo = threading.Thread(target=self._ciclo_monitoreo, daemon=True)
            self.hilo_monitoreo.start()
            
            self.logger.info("Monitoreo de red iniciado")
            self.siem.registrar_evento(
                TipoEvento.SISTEMA_INICIADO,
                "Monitoreo de red iniciado",
                {'intervalo_monitoreo': self.intervalo_monitoreo},
                "MEDIO"
            )
        else:
            self.logger.warning("El monitoreo de red ya está activo")
    
    def detener_monitoreo(self):
        """Detiene el monitoreo de red."""
        if self.monitoreando:
            self.monitoreando = False
            
            if self.hilo_monitoreo and self.hilo_monitoreo.is_alive():
                self.hilo_monitoreo.join(timeout=5)
            
            self.logger.info("Monitoreo de red detenido")
            self.siem.registrar_evento(
                TipoEvento.SISTEMA_DETENIDO,
                "Monitoreo de red detenido",
                nivel_criticidad="MEDIO"
            )
        else:
            self.logger.warning("El monitoreo de red no está activo")
    
    def obtener_conexiones_activas(self) -> List[ConexionRed]:
        """
        Obtiene las conexiones de red activas.
        
        Returns:
            List[ConexionRed]: Lista de conexiones activas
        """
        return self.conexiones_activas.copy()
    
    def obtener_puertos_abiertos(self) -> List[PuertoAbierto]:
        """
        Obtiene los puertos abiertos.
        
        Returns:
            List[PuertoAbierto]: Lista de puertos abiertos
        """
        return self.puertos_abiertos.copy()
    
    def obtener_alertas_recientes(self, limite: int = 100) -> List[AlertaRed]:
        """
        Obtiene las alertas más recientes.
        
        Args:
            limite: Número máximo de alertas a devolver
            
        Returns:
            List[AlertaRed]: Lista de alertas recientes
        """
        alertas_ordenadas = sorted(
            self.alertas_generadas,
            key=lambda x: x.timestamp,
            reverse=True
        )
        
        return alertas_ordenadas[:limite]
    
    def bloquear_ip(self, ip: str) -> bool:
        """
        Bloquea una dirección IP.
        
        Args:
            ip: Dirección IP a bloquear
            
        Returns:
            bool: True si se bloqueó exitosamente
        """
        if not validar_ip(ip):
            self.logger.warning(f"IP no válida para bloqueo: {ip}")
            return False
        
        self.analizador_trafico.bloquear_ip(ip)
        
        self.logger.info(f"IP bloqueada: {ip}")
        self.siem.registrar_evento(
            TipoEvento.IP_BLOQUEADA,
            f"IP bloqueada manualmente: {ip}",
            {'ip': ip},
            "MEDIO"
        )
        
        return True
    
    def desbloquear_ip(self, ip: str) -> bool:
        """
        Desbloquea una dirección IP.
        
        Args:
            ip: Dirección IP a desbloquear
            
        Returns:
            bool: True si se desbloqueó exitosamente
        """
        if not validar_ip(ip):
            self.logger.warning(f"IP no válida para desbloqueo: {ip}")
            return False
        
        self.analizador_trafico.desbloquear_ip(ip)
        
        self.logger.info(f"IP desbloqueada: {ip}")
        self.siem.registrar_evento(
            TipoEvento.SISTEMA_INICIADO,
            f"IP desbloqueada: {ip}",
            {'ip': ip},
            "BAJO"
        )
        
        return True
    
    def generar_reporte_markdown(self) -> str:
        """
        Genera un reporte de red en formato Markdown.
        
        Returns:
            str: Reporte en formato Markdown
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        md = f"# Reporte de Monitoreo de Red\n\n"
        md += f"**Fecha:** {timestamp}\n"
        md += f"**Estado:** {'🟢 Activo' if self.monitoreando else '🔴 Inactivo'}\n\n"
        
        # Estadísticas generales
        md += "## 📊 Estadísticas Generales\n\n"
        md += f"- **Conexiones activas:** {len(self.conexiones_activas)}\n"
        md += f"- **Puertos abiertos:** {len(self.puertos_abiertos)}\n"
        md += f"- **Alertas generadas:** {len(self.alertas_generadas)}\n"
        md += f"- **IPs bloqueadas:** {len(self.analizador_trafico.ips_bloqueadas)}\n\n"
        
        # Alertas recientes
        alertas_recientes = self.obtener_alertas_recientes(10)
        if alertas_recientes:
            md += "## 🚨 Alertas Recientes\n\n"
            for alerta in alertas_recientes:
                md += alerta.to_markdown()
                md += "---\n\n"
        else:
            md += "## ✅ Sin Alertas Recientes\n\n"
        
        # Puertos abiertos
        if self.puertos_abiertos:
            md += "## 🔓 Puertos Abiertos\n\n"
            md += "| Puerto | Protocolo | Dirección | Proceso |\n"
            md += "|--------|-----------|-----------|----------|\n"
            
            for puerto in sorted(self.puertos_abiertos, key=lambda x: x.numero):
                md += f"| {puerto.numero} | {puerto.protocolo.upper()} | {puerto.direccion} | {puerto.proceso_nombre} |\n"
            
            md += "\n"
        
        # IPs bloqueadas
        if self.analizador_trafico.ips_bloqueadas:
            md += "## 🚫 IPs Bloqueadas\n\n"
            for ip in sorted(self.analizador_trafico.ips_bloqueadas):
                md += f"- `{ip}`\n"
            md += "\n"
        
        return md
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del monitor de red.
        
        Returns:
            Dict[str, Any]: Estadísticas del monitor
        """
        return {
            'monitoreando': self.monitoreando,
            'conexiones_activas': len(self.conexiones_activas),
            'puertos_abiertos': len(self.puertos_abiertos),
            'alertas_generadas': len(self.alertas_generadas),
            'ips_bloqueadas': len(self.analizador_trafico.ips_bloqueadas),
            'intervalo_monitoreo': self.intervalo_monitoreo,
            'uptime': self.hilo_monitoreo.is_alive() if self.hilo_monitoreo else False
        }
