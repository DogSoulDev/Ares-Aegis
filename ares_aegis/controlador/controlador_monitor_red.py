#!/usr/bin/env python3
"""
Ares Aegis - Controlador de Monitor de Red
Controlador especializado para gestionar operaciones de monitoreo de red

Creado por DogSoulDev (https://github.com/DogSoulDev)
Todos los derechos reservados. Este código es propietario y confidencial.
La copia, distribución o modificación no autorizada está estrictamente prohibida.

Versión: 4.0.0
"""

import time
import threading
import subprocess
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Set
from collections import defaultdict

from ..modelo.modelo_monitor_red import MonitorRed
from ..modelo.modelo_siem import SIEM, TipoEvento
from ..utils.utils_ayuda_logging import configurar_logger_modulo


class ControladorMonitorRed:
    """Controlador especializado para operaciones de monitoreo de red."""
    
    def __init__(self, monitor_red: MonitorRed, siem: SIEM):
        """
        Inicializar el controlador de monitor de red.
        
        Args:
            monitor_red: Instancia del monitor de red
            siem: Instancia del SIEM para registro de eventos
        """
        self.monitor_red = monitor_red
        self.siem = siem
        self.logger = configurar_logger_modulo("controlador_monitor_red")
        
        # Estado del controlador
        self.alertas_red = []
        self.conexiones_sospechosas = []
        self.ips_bloqueadas = set()
        self.estadisticas_trafico = defaultdict(int)
        self.lock = threading.Lock()
        
        # Configuración de monitoreo
        self.configuracion = {
            'umbral_conexiones_sospechosas': 50,
            'ventana_analisis_minutos': 5,
            'puertos_criticos': [22, 23, 80, 443, 21, 25, 53, 110, 143, 993, 995],
            'ips_whitelist': set(),
            'ips_blacklist': set()
        }
        
        self.logger.info("Controlador de Monitor de Red inicializado")
    
    def iniciar_monitoreo(self) -> bool:
        """
        Iniciar el monitoreo de red.
        
        Returns:
            bool: True si se inició exitosamente
        """
        try:
            if not self.monitor_red.monitoreando:
                self.monitor_red.iniciar_monitoreo()
                
                # Registrar evento
                if self.siem:
                    self.siem.registrar_evento(
                        TipoEvento.SERVICIO_INICIADO,
                        "Monitoreo de red iniciado desde controlador",
                        {'componente': 'monitor_red'},
                        "MEDIO"
                    )
                
                self.logger.info("Monitoreo de red iniciado exitosamente")
                return True
            else:
                self.logger.warning("El monitoreo de red ya está activo")
                return True
        
        except Exception as e:
            self.logger.error(f"Error iniciando monitoreo de red: {e}")
            if self.siem:
                self.siem.registrar_evento(
                    TipoEvento.ERROR_SISTEMA,
                    f"Error iniciando monitoreo de red: {e}",
                    {'componente': 'monitor_red', 'error': str(e)},
                    "ALTO"
                )
            return False
    
    def detener_monitoreo(self) -> bool:
        """
        Detener el monitoreo de red.
        
        Returns:
            bool: True si se detuvo exitosamente
        """
        try:
            if self.monitor_red.monitoreando:
                self.monitor_red.detener_monitoreo()
                
                # Registrar evento
                if self.siem:
                    self.siem.registrar_evento(
                        TipoEvento.SERVICIO_DETENIDO,
                        "Monitoreo de red detenido desde controlador",
                        {'componente': 'monitor_red'},
                        "MEDIO"
                    )
                
                self.logger.info("Monitoreo de red detenido exitosamente")
                return True
            else:
                self.logger.warning("El monitoreo de red ya está inactivo")
                return True
        
        except Exception as e:
            self.logger.error(f"Error deteniendo monitoreo de red: {e}")
            if self.siem:
                self.siem.registrar_evento(
                    TipoEvento.ERROR_SISTEMA,
                    f"Error deteniendo monitoreo de red: {e}",
                    {'componente': 'monitor_red', 'error': str(e)},
                    "ALTO"
                )
            return False
    
    def obtener_estado_monitoreo(self) -> Dict[str, Any]:
        """
        Obtener el estado actual del monitoreo.
        
        Returns:
            Dict[str, Any]: Estado del monitoreo
        """
        try:
            stats_monitor = self.monitor_red.obtener_estadisticas()
            
            with self.lock:
                alertas_recientes = len([a for a in self.alertas_red 
                                       if a['timestamp'] > datetime.now() - timedelta(hours=1)])
            
            return {
                'activo': self.monitor_red.monitoreando,
                'conexiones_activas': stats_monitor.get('conexiones_activas', 0),
                'puertos_abiertos': stats_monitor.get('puertos_abiertos', 0),
                'alertas_ultima_hora': alertas_recientes,
                'ips_bloqueadas': len(self.ips_bloqueadas),
                'conexiones_sospechosas': len(self.conexiones_sospechosas),
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            self.logger.error(f"Error obteniendo estado de monitoreo: {e}")
            return {
                'activo': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def analizar_conexiones_red(self) -> Dict[str, Any]:
        """
        Analizar conexiones de red en busca de actividad sospechosa.
        
        Returns:
            Dict[str, Any]: Resultados del análisis
        """
        try:
            self.logger.info("Iniciando análisis de conexiones de red")
            
            conexiones = self.monitor_red.obtener_conexiones()
            conexiones_analizadas = len(conexiones)
            conexiones_sospechosas_nuevas = 0
            alertas_generadas = 0
            
            # Análisis de cada conexión
            for conexion in conexiones:
                if self._es_conexion_sospechosa(conexion):
                    self._procesar_conexion_sospechosa(conexion)
                    conexiones_sospechosas_nuevas += 1
                    alertas_generadas += 1
            
            resultado = {
                'conexiones_analizadas': conexiones_analizadas,
                'conexiones_sospechosas_nuevas': conexiones_sospechosas_nuevas,
                'alertas_generadas': alertas_generadas,
                'timestamp': datetime.now().isoformat()
            }
            
            # Registrar resultado en SIEM
            if self.siem:
                self.siem.registrar_evento(
                    TipoEvento.ANALISIS_COMPLETADO,
                    f"Análisis de red completado: {conexiones_sospechosas_nuevas} conexiones sospechosas de {conexiones_analizadas}",
                    resultado,
                    "ALTO" if conexiones_sospechosas_nuevas > 0 else "BAJO"
                )
            
            self.logger.info(f"Análisis completado: {conexiones_sospechosas_nuevas} conexiones sospechosas encontradas")
            return resultado
        
        except Exception as e:
            self.logger.error(f"Error en análisis de conexiones: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _es_conexion_sospechosa(self, conexion: Dict[str, Any]) -> bool:
        """
        Determinar si una conexión es sospechosa.
        
        Args:
            conexion: Datos de la conexión
            
        Returns:
            bool: True si la conexión es sospechosa
        """
        # Verificar IP en blacklist
        ip_remota = conexion.get('ip_remota', '')
        if ip_remota in self.configuracion['ips_blacklist']:
            return True
        
        # Verificar IP en whitelist
        if ip_remota in self.configuracion['ips_whitelist']:
            return False
        
        # Verificar puertos críticos
        puerto = conexion.get('puerto', 0)
        if puerto in self.configuracion['puertos_criticos']:
            return True
        
        # Verificar múltiples conexiones desde la misma IP
        with self.lock:
            conexiones_ip = sum(1 for c in self.conexiones_sospechosas 
                              if c.get('ip_remota') == ip_remota and 
                              c['timestamp'] > datetime.now() - timedelta(minutes=self.configuracion['ventana_analisis_minutos']))
            
            if conexiones_ip >= self.configuracion['umbral_conexiones_sospechosas']:
                return True
        
        return False
    
    def _procesar_conexion_sospechosa(self, conexion: Dict[str, Any]):
        """
        Procesar una conexión sospechosa detectada.
        
        Args:
            conexion: Datos de la conexión sospechosa
        """
        timestamp = datetime.now()
        ip_remota = conexion.get('ip_remota', 'desconocida')
        puerto = conexion.get('puerto', 0)
        
        # Agregar a lista de conexiones sospechosas
        with self.lock:
            conexion_sospechosa = {
                'ip_remota': ip_remota,
                'puerto': puerto,
                'timestamp': timestamp,
                'datos_conexion': conexion
            }
            self.conexiones_sospechosas.append(conexion_sospechosa)
            
            # Crear alerta
            alerta = {
                'tipo': 'conexion_sospechosa',
                'ip_remota': ip_remota,
                'puerto': puerto,
                'timestamp': timestamp,
                'descripcion': f"Conexión sospechosa desde {ip_remota}:{puerto}"
            }
            self.alertas_red.append(alerta)
        
        # Registrar en SIEM
        if self.siem:
            self.siem.registrar_evento(
                TipoEvento.CONEXION_SOSPECHOSA,
                f"Conexión sospechosa detectada desde {ip_remota}:{puerto}",
                conexion_sospechosa,
                "ALTO"
            )
        
        self.logger.warning(f"Conexión sospechosa detectada: {ip_remota}:{puerto}")
    
    def bloquear_ip(self, ip: str, razon: str = "Actividad sospechosa") -> bool:
        """
        Bloquear una dirección IP.
        
        Args:
            ip: Dirección IP a bloquear
            razon: Razón del bloqueo
            
        Returns:
            bool: True si se bloqueó exitosamente
        """
        try:
            with self.lock:
                self.ips_bloqueadas.add(ip)
                self.configuracion['ips_blacklist'].add(ip)
            
            # Registrar bloqueo
            if self.siem:
                self.siem.registrar_evento(
                    TipoEvento.IP_BLOQUEADA,
                    f"IP bloqueada: {ip} - {razon}",
                    {'ip': ip, 'razon': razon},
                    "ALTO"
                )
            
            self.logger.info(f"IP bloqueada exitosamente: {ip} - {razon}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error bloqueando IP {ip}: {e}")
            return False
    
    def desbloquear_ip(self, ip: str) -> bool:
        """
        Desbloquear una dirección IP.
        
        Args:
            ip: Dirección IP a desbloquear
            
        Returns:
            bool: True si se desbloqueó exitosamente
        """
        try:
            with self.lock:
                self.ips_bloqueadas.discard(ip)
                self.configuracion['ips_blacklist'].discard(ip)
            
            # Registrar desbloqueo
            if self.siem:
                self.siem.registrar_evento(
                    TipoEvento.CONFIGURACION_MODIFICADA,
                    f"IP desbloqueada: {ip}",
                    {'ip': ip, 'accion': 'desbloqueo'},
                    "MEDIO"
                )
            
            self.logger.info(f"IP desbloqueada exitosamente: {ip}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error desbloqueando IP {ip}: {e}")
            return False
    
    def obtener_ips_bloqueadas(self) -> List[str]:
        """
        Obtener lista de IPs bloqueadas.
        
        Returns:
            List[str]: Lista de IPs bloqueadas
        """
        with self.lock:
            return list(self.ips_bloqueadas)
    
    def obtener_conexiones_sospechosas(self, limite: int = 100) -> List[Dict[str, Any]]:
        """
        Obtener conexiones sospechosas recientes.
        
        Args:
            limite: Número máximo de conexiones a devolver
            
        Returns:
            List[Dict[str, Any]]: Lista de conexiones sospechosas
        """
        with self.lock:
            conexiones = self.conexiones_sospechosas.copy()
        
        # Ordenar por timestamp descendente y limitar
        conexiones.sort(key=lambda x: x['timestamp'], reverse=True)
        return conexiones[:limite]
    
    def obtener_alertas_red(self, limite: int = 50) -> List[Dict[str, Any]]:
        """
        Obtener alertas de red recientes.
        
        Args:
            limite: Número máximo de alertas a devolver
            
        Returns:
            List[Dict[str, Any]]: Lista de alertas de red
        """
        with self.lock:
            alertas = self.alertas_red.copy()
        
        # Ordenar por timestamp descendente y limitar
        alertas.sort(key=lambda x: x['timestamp'], reverse=True)
        return alertas[:limite]
    
    def obtener_estadisticas_trafico(self, periodo_horas: int = 24) -> Dict[str, Any]:
        """
        Obtener estadísticas de tráfico de red.
        
        Args:
            periodo_horas: Período en horas para las estadísticas
            
        Returns:
            Dict[str, Any]: Estadísticas de tráfico
        """
        limite_tiempo = datetime.now() - timedelta(hours=periodo_horas)
        
        with self.lock:
            conexiones_periodo = [c for c in self.conexiones_sospechosas 
                                if c['timestamp'] >= limite_tiempo]
            alertas_periodo = [a for a in self.alertas_red 
                             if a['timestamp'] >= limite_tiempo]
        
        # Contar por IP
        ips_frecuentes = defaultdict(int)
        puertos_frecuentes = defaultdict(int)
        
        for conexion in conexiones_periodo:
            ips_frecuentes[conexion.get('ip_remota', 'desconocida')] += 1
            puertos_frecuentes[conexion.get('puerto', 0)] += 1
        
        return {
            'periodo_horas': periodo_horas,
            'total_conexiones_sospechosas': len(conexiones_periodo),
            'total_alertas': len(alertas_periodo),
            'ips_mas_frecuentes': dict(sorted(ips_frecuentes.items(), 
                                            key=lambda x: x[1], reverse=True)[:10]),
            'puertos_mas_frecuentes': dict(sorted(puertos_frecuentes.items(), 
                                                key=lambda x: x[1], reverse=True)[:10]),
            'ips_bloqueadas_total': len(self.ips_bloqueadas),
            'timestamp': datetime.now().isoformat()
        }
    
    def configurar_monitoreo(self, config: Dict[str, Any]):
        """
        Configurar parámetros de monitoreo.
        
        Args:
            config: Diccionario con configuración
        """
        with self.lock:
            self.configuracion.update(config)
        
        self.logger.info(f"Configuración de monitoreo actualizada: {config}")
        
        if self.siem:
            self.siem.registrar_evento(
                TipoEvento.CONFIGURACION_MODIFICADA,
                "Configuración de monitoreo de red actualizada",
                config,
                "MEDIO"
            )
    
    def generar_reporte_red(self) -> str:
        """
        Generar reporte de actividad de red en formato Markdown.
        
        Returns:
            str: Reporte en formato Markdown
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        estado = self.obtener_estado_monitoreo()
        stats = self.obtener_estadisticas_trafico()
        alertas_recientes = self.obtener_alertas_red(10)
        
        md = f"# Reporte de Monitoreo de Red\n\n"
        md += f"**Fecha de generación:** {timestamp}\n\n"
        
        # Estado del monitoreo
        md += "## 🌐 Estado del Monitoreo\n\n"
        md += f"- **Estado:** {'🟢 Activo' if estado['activo'] else '🔴 Inactivo'}\n"
        md += f"- **Conexiones activas:** {estado.get('conexiones_activas', 0)}\n"
        md += f"- **Puertos abiertos:** {estado.get('puertos_abiertos', 0)}\n"
        md += f"- **IPs bloqueadas:** {estado.get('ips_bloqueadas', 0)}\n"
        md += f"- **Conexiones sospechosas:** {estado.get('conexiones_sospechosas', 0)}\n\n"
        
        # Estadísticas de tráfico
        md += "## 📊 Estadísticas de Tráfico (24h)\n\n"
        md += f"- **Total conexiones sospechosas:** {stats['total_conexiones_sospechosas']}\n"
        md += f"- **Total alertas:** {stats['total_alertas']}\n\n"
        
        # IPs más frecuentes
        if stats['ips_mas_frecuentes']:
            md += "### IPs más frecuentes:\n"
            for ip, count in list(stats['ips_mas_frecuentes'].items())[:5]:
                md += f"- **{ip}:** {count} conexiones\n"
            md += "\n"
        
        # Alertas recientes
        md += "## 🚨 Alertas Recientes\n\n"
        if alertas_recientes:
            for alerta in alertas_recientes[:5]:
                timestamp_alerta = alerta['timestamp'].strftime('%H:%M:%S')
                md += f"- **{timestamp_alerta}:** {alerta['descripcion']}\n"
        else:
            md += "No hay alertas recientes.\n"
        
        md += "\n---\n"
        md += "*Reporte generado automáticamente por Ares Aegis*\n"
        
        return md
    
    def limpiar_datos_antiguos(self, dias_retencion: int = 7):
        """
        Limpiar datos antiguos para liberar memoria.
        
        Args:
            dias_retencion: Días de retención de datos
        """
        limite_tiempo = datetime.now() - timedelta(days=dias_retencion)
        
        with self.lock:
            # Limpiar conexiones sospechosas antiguas
            conexiones_nuevas = [c for c in self.conexiones_sospechosas 
                               if c['timestamp'] >= limite_tiempo]
            conexiones_removidas = len(self.conexiones_sospechosas) - len(conexiones_nuevas)
            self.conexiones_sospechosas = conexiones_nuevas
            
            # Limpiar alertas antiguas
            alertas_nuevas = [a for a in self.alertas_red 
                            if a['timestamp'] >= limite_tiempo]
            alertas_removidas = len(self.alertas_red) - len(alertas_nuevas)
            self.alertas_red = alertas_nuevas
        
        self.logger.info(f"Limpieza completada: {conexiones_removidas} conexiones, {alertas_removidas} alertas removidas")
    
    def obtener_conexiones_red_activas(self) -> List[Dict[str, Any]]:
        """Obtener conexiones de red activas usando herramientas nativas de Kali Linux"""
        try:
            conexiones = []
            
            # Usar netstat para obtener conexiones activas
            resultado = subprocess.run(
                ['netstat', '-tuln'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if resultado.returncode != 0:
                self.logger.warning("No se pudo ejecutar netstat")
                return []
            
            # Procesar salida de netstat
            lineas = resultado.stdout.strip().split('\n')[2:]  # Omitir headers
            
            for linea in lineas:
                if not linea.strip():
                    continue
                    
                partes = linea.split()
                if len(partes) >= 6:
                    protocolo = partes[0]
                    direccion_local = partes[3]
                    direccion_remota = partes[4]
                    estado = partes[5] if len(partes) > 5 else "UNKNOWN"
                    
                    # Separar IP y puerto
                    try:
                        if ':' in direccion_local:
                            ip_local, puerto_local = direccion_local.rsplit(':', 1)
                        else:
                            ip_local, puerto_local = direccion_local, "0"
                            
                        if ':' in direccion_remota:
                            ip_remota, puerto_remoto = direccion_remota.rsplit(':', 1)
                        else:
                            ip_remota, puerto_remoto = direccion_remota, "0"
                        
                        conexion = {
                            "protocolo": protocolo.upper(),
                            "ip_local": ip_local,
                            "puerto_local": int(puerto_local) if puerto_local.isdigit() else 0,
                            "ip_remota": ip_remota,
                            "puerto_remoto": int(puerto_remoto) if puerto_remoto.isdigit() else 0,
                            "estado": estado,
                            "timestamp": datetime.now().isoformat()
                        }
                        conexiones.append(conexion)
                        
                    except (ValueError, IndexError) as e:
                        self.logger.debug(f"Error procesando línea de netstat: {linea} - {e}")
                        continue
            
            return conexiones
            
        except subprocess.TimeoutExpired:
            self.logger.error("Timeout ejecutando netstat")
            return []
        except Exception as e:
            self.logger.error(f"Error obteniendo conexiones de red: {e}")
            return []
    
    def obtener_conexiones_establecidas(self) -> List[Dict[str, Any]]:
        """Obtener solo las conexiones de red establecidas"""
        try:
            todas_conexiones = self.obtener_conexiones_red_activas()
            conexiones_establecidas = [
                c for c in todas_conexiones 
                if c.get('estado', '').upper() == 'ESTABLISHED'
            ]
            return conexiones_establecidas
            
        except Exception as e:
            self.logger.error(f"Error obteniendo conexiones establecidas: {e}")
            return []


