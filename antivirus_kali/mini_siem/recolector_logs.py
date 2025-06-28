"""
Recolector de registros para el Mini-SIEM
Maneja la recopilación en tiempo real de logs desde múltiples fuentes en Kali Linux
"""

import asyncio
import subprocess
import json
import time
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, AsyncGenerator, Callable
import logging
import select
import threading

logger = logging.getLogger(__name__)

class RecolectorRegistros:
    """
    Recolector de registros en tiempo real para el Mini-SIEM
    Integra journalctl, archivos de log tradicionales y monitorización de eventos
    """
    
    def __init__(self):
        self.fuentes_activas = {}
        self.callbacks = []
        self.running = False
        
        # Fuentes de registros críticas para Kali Linux
        self.fuentes_criticas = {
            'auth': '/var/log/auth.log',
            'syslog': '/var/log/syslog', 
            'dpkg': '/var/log/dpkg.log',
            'kern': '/var/log/kern.log',
            'cron': '/var/log/cron.log'
        }
        
        # Configurar monitoring de archivos usando polling
        self.file_monitors = {}
        self.file_positions = {}
        
    def agregar_callback(self, callback: Callable):
        """Agregar callback para procesar eventos en tiempo real"""
        self.callbacks.append(callback)
        
    async def iniciar_recoleccion(self):
        """Iniciar recolección de registros en tiempo real"""
        self.running = True
        logger.info("Iniciando recolección de registros en tiempo real")
        
        # Ejecutar múltiples fuentes de forma concurrente
        tasks = [
            asyncio.create_task(self.monitorear_journalctl()),
            asyncio.create_task(self.monitorear_archivos_log())
        ]
        
        await asyncio.gather(*tasks)
        
    def detener_recoleccion(self):
        """Detener recolección de registros"""
        self.running = False
        logger.info("Deteniendo recolección de registros")
        
    async def monitorear_journalctl(self):
        """Monitorear journalctl en tiempo real usando subprocess"""
        try:
            # Comando para seguir journal en formato JSON
            cmd = ['journalctl', '-f', '-o', 'json', '--no-pager']
            
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            while self.running:
                if proc.stdout:
                    line = await proc.stdout.readline()
                    if line:
                        try:
                            # Decodificar línea JSON del journal
                            event_data = json.loads(line.decode('utf-8').strip())
                            await self.procesar_evento_journal(event_data)
                        except json.JSONDecodeError:
                            continue
                else:
                    await asyncio.sleep(0.1)
                        
        except Exception as e:
            logger.error(f"Error monitoreando journalctl: {e}")
            
    async def monitorear_archivos_log(self):
        """Monitorear archivos de log tradicionales"""
        monitores = {}
        
        for nombre, ruta in self.fuentes_criticas.items():
            if os.path.exists(ruta) and os.path.isfile(ruta):
                self.file_positions[ruta] = self.obtener_tamano_archivo(ruta)
                asyncio.create_task(self.monitorear_archivo_individual(ruta, nombre))
                
        while self.running:
            await asyncio.sleep(1)
            
    async def monitorear_archivo_individual(self, ruta: str, nombre: str):
        """Monitorear un archivo individual por cambios"""
        while self.running:
            try:
                tamano_actual = self.obtener_tamano_archivo(ruta)
                tamano_anterior = self.file_positions.get(ruta, 0)
                
                if tamano_actual > tamano_anterior:
                    # Archivo ha crecido, leer nuevas líneas
                    nuevas_lineas = await self.leer_nuevas_lineas(ruta, tamano_anterior)
                    for linea in nuevas_lineas:
                        evento = self.crear_evento_desde_linea(linea, ruta, nombre)
                        await self.procesar_evento_archivo(evento)
                    
                    self.file_positions[ruta] = tamano_actual
                    
                elif tamano_actual < tamano_anterior:
                    # Archivo rotado o truncado
                    logger.info(f"Rotación detectada en {ruta}")
                    self.file_positions[ruta] = tamano_actual
                    
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error monitoreando {ruta}: {e}")
                await asyncio.sleep(5)
                
    def obtener_tamano_archivo(self, ruta: str) -> int:
        """Obtener tamaño actual del archivo"""
        try:
            return os.path.getsize(ruta)
        except OSError:
            return 0
            
    async def leer_nuevas_lineas(self, ruta: str, posicion_inicial: int) -> List[str]:
        """Leer nuevas líneas desde posición específica"""
        lineas = []
        try:
            with open(ruta, 'r', encoding='utf-8', errors='ignore') as f:
                f.seek(posicion_inicial)
                lineas = f.readlines()
        except Exception as e:
            logger.error(f"Error leyendo archivo {ruta}: {e}")
            
        return [linea.strip() for linea in lineas if linea.strip()]
        
    def crear_evento_desde_linea(self, linea: str, ruta: str, fuente: str) -> Dict:
        """Crear evento estructurado desde línea de log"""
        return {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'raw_log': linea,
            'source_file': ruta,
            'source_type': fuente,
            'message': linea
        }
        
    async def procesar_evento_journal(self, evento: Dict):
        """Procesar evento del journal systemd"""
        # Normalizar evento del journal
        timestamp = evento.get('__REALTIME_TIMESTAMP')
        if timestamp:
            # Convertir timestamp de microsegundos a datetime
            timestamp_dt = datetime.utcfromtimestamp(int(timestamp) / 1000000)
            timestamp_str = timestamp_dt.isoformat() + 'Z'
        else:
            timestamp_str = datetime.utcnow().isoformat() + 'Z'
            
        evento_normalizado = {
            'timestamp': timestamp_str,
            'event.category': self.categorizar_evento_journal(evento),
            'host.name': evento.get('_HOSTNAME', 'unknown'),
            'process.name': evento.get('_COMM', 'unknown'),
            'process.pid': evento.get('_PID'),
            'user.name': evento.get('_UID'),
            'message': evento.get('MESSAGE', ''),
            'raw_log': json.dumps(evento),
            'source_type': 'journalctl'
        }
        
        # Enviar a callbacks
        await self.enviar_a_callbacks(evento_normalizado)
        
    async def procesar_evento_archivo(self, evento: Dict):
        """Procesar evento de archivo de log"""
        # Normalizar según el tipo de archivo
        evento_normalizado = await self.normalizar_evento_archivo(evento)
        
        # Enviar a callbacks  
        await self.enviar_a_callbacks(evento_normalizado)
        
    async def normalizar_evento_archivo(self, evento: Dict) -> Dict:
        """Normalizar evento de archivo según su tipo"""
        fuente = evento.get('source_type', '')
        linea = evento.get('raw_log', '')
        
        evento_base = {
            'timestamp': evento.get('timestamp'),
            'raw_log': linea,
            'source_file': evento.get('source_file'),
            'source_type': fuente,
            'message': linea
        }
        
        # Parsear según tipo de archivo
        if fuente == 'auth':
            return await self.parsear_auth_log(evento_base, linea)
        elif fuente == 'dpkg':
            return await self.parsear_dpkg_log(evento_base, linea)
        elif fuente == 'syslog':
            return await self.parsear_syslog(evento_base, linea)
        else:
            return evento_base
            
    async def parsear_auth_log(self, evento_base: Dict, linea: str) -> Dict:
        """Parsear línea de auth.log"""
        import re
        
        # Patrón para SSH failed password
        ssh_fail_pattern = r'Failed password for (?:invalid user )?(\w+) from (\d+\.\d+\.\d+\.\d+)'
        match = re.search(ssh_fail_pattern, linea)
        
        if match:
            evento_base.update({
                'event.category': 'authentication',
                'event.type': 'failed_password',
                'user.name': match.group(1),
                'source.ip': match.group(2),
                'action': 'failed',
                'severity': 'WARNING'
            })
            
        # Patrón para successful login
        login_success_pattern = r'Accepted password for (\w+) from (\d+\.\d+\.\d+\.\d+)'
        match = re.search(login_success_pattern, linea)
        
        if match:
            evento_base.update({
                'event.category': 'authentication',
                'event.type': 'login_success',
                'user.name': match.group(1),
                'source.ip': match.group(2),
                'action': 'accepted',
                'severity': 'INFO'
            })
            
        return evento_base
        
    async def parsear_dpkg_log(self, evento_base: Dict, linea: str) -> Dict:
        """Parsear línea de dpkg.log"""
        import re
        
        # Patrón para instalación de paquetes
        install_pattern = r'install (\S+) (\S+)'
        match = re.search(install_pattern, linea)
        
        if match:
            evento_base.update({
                'event.category': 'package',
                'event.type': 'package_install',
                'package.name': match.group(1),
                'package.version': match.group(2),
                'action': 'installed',
                'severity': 'INFO'
            })
            
        return evento_base
        
    async def parsear_syslog(self, evento_base: Dict, linea: str) -> Dict:
        """Parsear línea de syslog"""
        # Análisis básico de syslog
        evento_base.update({
            'event.category': 'system',
            'event.type': 'system_message',
            'severity': 'INFO'
        })
        
        return evento_base
        
    def categorizar_evento_journal(self, evento: Dict) -> str:
        """Categorizar evento del journal"""
        unit = evento.get('_SYSTEMD_UNIT', '')
        comm = evento.get('_COMM', '')
        
        if 'ssh' in unit or 'ssh' in comm:
            return 'authentication'
        elif 'kernel' in unit or evento.get('SYSLOG_IDENTIFIER') == 'kernel':
            return 'kernel'
        elif 'network' in unit:
            return 'network'
        else:
            return 'system'
            
    async def enviar_a_callbacks(self, evento: Dict):
        """Enviar evento a todos los callbacks registrados"""
        for callback in self.callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(evento)
                else:
                    callback(evento)
            except Exception as e:
                logger.error(f"Error en callback: {e}")
                
    async def obtener_eventos_historicos(self, 
                                       desde: Optional[datetime] = None,
                                       hasta: Optional[datetime] = None) -> List[Dict]:
        """Obtener eventos históricos del journal"""
        eventos = []
        
        # Construir comando journalctl para período específico
        cmd = ['journalctl', '-o', 'json', '--no-pager']
        
        if desde:
            cmd.extend(['--since', desde.strftime('%Y-%m-%d %H:%M:%S')])
        if hasta:
            cmd.extend(['--until', hasta.strftime('%Y-%m-%d %H:%M:%S')])
            
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await proc.communicate()
            
            if proc.returncode == 0:
                for line in stdout.decode('utf-8').strip().split('\n'):
                    if line:
                        try:
                            evento = json.loads(line)
                            eventos.append(evento)
                        except json.JSONDecodeError:
                            continue
                            
        except Exception as e:
            logger.error(f"Error obteniendo eventos históricos: {e}")
            
        return eventos
