#!/usr/bin/env python3
"""
Monitor de Procesos
Módulo para monitoreo y análisis de procesos del sistema usando solo módulos estándar

Autor: DogSoulDev
Versión: 2.0.0
"""

import os
import subprocess
import json
import re
from typing import List, Dict, Optional, Any
from datetime import datetime
from pathlib import Path


class InfoProceso:
    """Información detallada de un proceso del sistema."""
    
    def __init__(self, pid: int, nombre: str, cmdline: List[str], 
                 cpu_percent: float, memoria_mb: float, usuario: str,
                 estado: str, tiempo_inicio: datetime):
        self.pid = pid
        self.nombre = nombre
        self.cmdline = cmdline
        self.cpu_percent = cpu_percent
        self.memoria_mb = memoria_mb
        self.usuario = usuario
        self.estado = estado
        self.tiempo_inicio = tiempo_inicio
        self.sospechoso = False
        self.razones_sospecha: List[str] = []
    
    def marcar_como_sospechoso(self, razon: str) -> None:
        """Marca el proceso como sospechoso con una razón."""
        self.sospechoso = True
        if razon not in self.razones_sospecha:
            self.razones_sospecha.append(razon)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la información del proceso a diccionario."""
        return {
            'pid': self.pid,
            'nombre': self.nombre,
            'cmdline': ' '.join(self.cmdline) if self.cmdline else '',
            'cpu_percent': self.cpu_percent,
            'memoria_mb': self.memoria_mb,
            'usuario': self.usuario,
            'estado': self.estado,
            'tiempo_inicio': self.tiempo_inicio.isoformat(),
            'sospechoso': self.sospechoso,
            'razones_sospecha': self.razones_sospecha
        }


class MonitorProcesos:
    """Monitor de procesos del sistema."""
    
    def __init__(self, siem=None):
        """
        Inicializa el monitor de procesos.
        
        Args:
            siem: Sistema SIEM para logging (opcional)
        """
        self.siem = siem
        self.procesos_conocidos: Dict[int, InfoProceso] = {}
        self.patrones_sospechosos = self._cargar_patrones_sospechosos()
        self.umbrales = {
            'cpu_alto': 80.0,
            'memoria_alta': 1024.0  # MB
        }
    
    def _cargar_patrones_sospechosos(self) -> List[str]:
        """Carga patrones de nombres de procesos sospechosos."""
        return [
            'nc', 'netcat', 'ncat',
            'socat', 'telnet',
            'python -c', 'python3 -c',
            'perl -e', 'ruby -e',
            'php -r', 'node -e',
            'bash -i', 'sh -i',
            '/dev/tcp', 'reverse_shell',
            'backdoor', 'keylogger',
            'cryptominer', 'coinminer',
            'mimikatz', 'meterpreter'
        ]
    
    def obtener_procesos_actuales(self) -> List[InfoProceso]:
        """
        Obtiene lista de procesos actuales usando comandos del sistema.
        
        Returns:
            List[InfoProceso]: Lista de procesos del sistema
        """
        procesos = []
        
        try:
            # Usar comando ps para obtener información de procesos
            comando = [
                'ps', 'axo', 
                'pid,comm,user,pcpu,pmem,stat,lstart,cmd', 
                '--no-headers'
            ]
            
            resultado = subprocess.run(
                comando, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            if resultado.returncode != 0:
                if self.siem:
                    self.siem.log_evento('WARNING', 'monitor_procesos', 
                                       f"Error ejecutando ps: {resultado.stderr}")
                return procesos
            
            # Parsear salida de ps
            for linea in resultado.stdout.strip().split('\n'):
                if not linea.strip():
                    continue
                    
                try:
                    # Dividir la línea de manera más robusta
                    partes = linea.split(None, 7)
                    if len(partes) < 7:
                        continue
                    
                    pid = int(partes[0])
                    nombre = partes[1]
                    usuario = partes[2]
                    cpu_percent = float(partes[3])
                    memoria_percent = float(partes[4])
                    estado = partes[5]
                    cmdline_str = partes[7] if len(partes) > 7 else nombre
                    
                    # Convertir tiempo de inicio aproximado
                    tiempo_inicio = datetime.now()
                    
                    # Calcular memoria en MB
                    memoria_mb = self._calcular_memoria_mb(memoria_percent)
                    
                    # Parsear línea de comandos
                    cmdline = cmdline_str.split() if cmdline_str else [nombre]
                    
                    proceso = InfoProceso(
                        pid=pid,
                        nombre=nombre,
                        cmdline=cmdline,
                        cpu_percent=cpu_percent,
                        memoria_mb=memoria_mb,
                        usuario=usuario,
                        estado=estado,
                        tiempo_inicio=tiempo_inicio
                    )
                    
                    procesos.append(proceso)
                    
                except (ValueError, IndexError):
                    # Saltar líneas malformadas
                    continue
            
            if self.siem:
                self.siem.log_evento('INFO', 'monitor_procesos', 
                                   f'Obtenidos {len(procesos)} procesos del sistema')
            
        except subprocess.TimeoutExpired:
            if self.siem:
                self.siem.log_evento('WARNING', 'monitor_procesos', 
                                   'Timeout obteniendo procesos del sistema')
        except Exception as e:
            if self.siem:
                self.siem.log_evento('ERROR', 'monitor_procesos', 
                                   f'Error obteniendo procesos: {e}')
        
        return procesos
    
    def _calcular_memoria_mb(self, porcentaje_memoria: float) -> float:
        """
        Calcula memoria en MB basado en porcentaje.
        
        Args:
            porcentaje_memoria: Porcentaje de memoria usada
            
        Returns:
            float: Memoria aproximada en MB
        """
        try:
            # Obtener memoria total del sistema desde /proc/meminfo
            with open('/proc/meminfo', 'r') as f:
                for linea in f:
                    if linea.startswith('MemTotal:'):
                        # MemTotal está en kB
                        mem_total_kb = int(linea.split()[1])
                        mem_total_mb = mem_total_kb / 1024
                        return (porcentaje_memoria / 100.0) * mem_total_mb
        except Exception:
            # Si no se puede calcular, usar una estimación basada en 8GB
            return (porcentaje_memoria / 100.0) * 8192
        
        return 0.0
    
    def analizar_procesos_sospechosos(self, procesos: List[InfoProceso]) -> List[InfoProceso]:
        """
        Analiza procesos para detectar actividad sospechosa.
        
        Args:
            procesos: Lista de procesos a analizar
            
        Returns:
            List[InfoProceso]: Lista de procesos sospechosos
        """
        sospechosos = []
        
        for proceso in procesos:
            # Verificar uso alto de CPU
            if proceso.cpu_percent > self.umbrales['cpu_alto']:
                proceso.marcar_como_sospechoso(f"Uso alto de CPU: {proceso.cpu_percent:.1f}%")
            
            # Verificar uso alto de memoria
            if proceso.memoria_mb > self.umbrales['memoria_alta']:
                proceso.marcar_como_sospechoso(f"Uso alto de memoria: {proceso.memoria_mb:.1f} MB")
            
            # Verificar nombres sospechosos
            nombre_completo = proceso.nombre.lower()
            cmdline_completo = ' '.join(proceso.cmdline).lower()
            
            for patron in self.patrones_sospechosos:
                if patron.lower() in nombre_completo or patron.lower() in cmdline_completo:
                    proceso.marcar_como_sospechoso(f"Nombre sospechoso: {patron}")
                    break
            
            # Verificar ubicaciones sospechosas
            if proceso.cmdline:
                ruta_ejecutable = proceso.cmdline[0]
                if any(ubicacion in ruta_ejecutable for ubicacion in ['/tmp/', '/var/tmp/', '/dev/shm/']):
                    proceso.marcar_como_sospechoso("Ejecutándose desde ubicación temporal")
            
            # Verificar procesos ejecutándose como root que no deberían
            if proceso.usuario == 'root' and proceso.nombre in ['nc', 'netcat', 'telnet']:
                proceso.marcar_como_sospechoso("Proceso de red ejecutándose como root")
            
            if proceso.sospechoso:
                sospechosos.append(proceso)
        
        return sospechosos
    
    def detectar_procesos_nuevos(self, procesos_actuales: List[InfoProceso]) -> List[InfoProceso]:
        """
        Detecta procesos nuevos comparando con la lista conocida.
        
        Args:
            procesos_actuales: Lista de procesos actuales
            
        Returns:
            List[InfoProceso]: Lista de procesos nuevos
        """
        nuevos = []
        pids_actuales = {p.pid for p in procesos_actuales}
        
        for proceso in procesos_actuales:
            if proceso.pid not in self.procesos_conocidos:
                nuevos.append(proceso)
        
        # Actualizar procesos conocidos
        self.procesos_conocidos = {p.pid: p for p in procesos_actuales}
        
        return nuevos
    
    def obtener_conexiones_red_procesos(self) -> List[Dict[str, Any]]:
        """
        Obtiene conexiones de red asociadas a procesos usando comandos del sistema.
        
        Returns:
            List[Dict]: Lista de conexiones de red
        """
        conexiones = []
        
        try:
            # Usar netstat para obtener conexiones
            comando = ['netstat', '-tulpn']
            resultado = subprocess.run(comando, capture_output=True, text=True, timeout=30)
            
            if resultado.returncode == 0:
                for linea in resultado.stdout.split('\n'):
                    if 'LISTEN' in linea or 'ESTABLISHED' in linea:
                        partes = linea.split()
                        if len(partes) >= 7:
                            try:
                                protocolo = partes[0]
                                direccion_local = partes[3]
                                direccion_remota = partes[4]
                                estado = partes[5]
                                pid_programa = partes[6] if len(partes) > 6 else ''
                                
                                # Extraer PID si está disponible
                                pid = None
                                if '/' in pid_programa:
                                    try:
                                        pid = int(pid_programa.split('/')[0])
                                    except ValueError:
                                        pass
                                
                                conexion = {
                                    'protocolo': protocolo,
                                    'direccion_local': direccion_local,
                                    'direccion_remota': direccion_remota,
                                    'estado': estado,
                                    'pid': pid,
                                    'programa': pid_programa
                                }
                                
                                conexiones.append(conexion)
                                
                            except (ValueError, IndexError):
                                continue
            
            if self.siem:
                self.siem.log_evento('INFO', 'monitor_procesos', 
                                   f'Obtenidas {len(conexiones)} conexiones de red')
                
        except Exception as e:
            if self.siem:
                self.siem.log_evento('ERROR', 'monitor_procesos', 
                                   f'Error obteniendo conexiones de red: {e}')
        
        return conexiones
    
    def terminar_proceso(self, pid: int, forzar: bool = False) -> bool:
        """
        Termina un proceso por su PID usando comandos del sistema.
        
        Args:
            pid: PID del proceso a terminar
            forzar: Si usar SIGKILL en lugar de SIGTERM
            
        Returns:
            bool: True si el proceso fue terminado exitosamente
        """
        try:
            signal = 'KILL' if forzar else 'TERM'
            comando = ['kill', f'-{signal}', str(pid)]
            
            resultado = subprocess.run(comando, capture_output=True, text=True)
            
            if resultado.returncode == 0:
                if self.siem:
                    self.siem.log_evento('INFO', 'monitor_procesos', 
                                       f'Proceso {pid} terminado (señal {signal})')
                return True
            else:
                if self.siem:
                    self.siem.log_evento('WARNING', 'monitor_procesos', 
                                       f'No se pudo terminar proceso {pid}: {resultado.stderr}')
                return False
                
        except Exception as e:
            if self.siem:
                self.siem.log_evento('ERROR', 'monitor_procesos', 
                                   f'Error terminando proceso {pid}: {e}')
            return False
    
    def escanear_sistema(self) -> Dict[str, Any]:
        """
        Ejecuta un escaneo completo del sistema de procesos.
        
        Returns:
            Dict[str, Any]: Diccionario con resultados del escaneo
        """
        inicio_tiempo = datetime.now()
        
        # Obtener procesos actuales
        procesos_actuales = self.obtener_procesos_actuales()
        
        # Detectar procesos nuevos
        procesos_nuevos = self.detectar_procesos_nuevos(procesos_actuales)
        
        # Analizar procesos sospechosos
        procesos_sospechosos = self.analizar_procesos_sospechosos(procesos_actuales)
        
        # Obtener conexiones de red
        conexiones_red = self.obtener_conexiones_red_procesos()
        
        # Calcular estadísticas
        uso_cpu_total = sum(p.cpu_percent for p in procesos_actuales)
        uso_cpu_promedio = uso_cpu_total / len(procesos_actuales) if procesos_actuales else 0
        memoria_total = sum(p.memoria_mb for p in procesos_actuales)
        
        fin_tiempo = datetime.now()
        tiempo_escaneo = (fin_tiempo - inicio_tiempo).total_seconds()
        
        resultado = {
            'timestamp': inicio_tiempo.isoformat(),
            'estadisticas': {
                'total_procesos': len(procesos_actuales),
                'procesos_nuevos': len(procesos_nuevos),
                'procesos_sospechosos': len(procesos_sospechosos),
                'conexiones_red': len(conexiones_red),
                'uso_cpu_promedio': uso_cpu_promedio,
                'memoria_total_mb': memoria_total,
                'tiempo_escaneo': tiempo_escaneo
            },
            'procesos_sospechosos': [p.to_dict() for p in procesos_sospechosos],
            'procesos_nuevos': [p.to_dict() for p in procesos_nuevos],
            'conexiones_red': conexiones_red,
            'todos_los_procesos': [p.to_dict() for p in procesos_actuales]
        }
        
        if self.siem:
            self.siem.log_evento('INFO', 'monitor_procesos', 
                               f'Escaneo completado: {len(procesos_sospechosos)} sospechosos encontrados')
        
        return resultado
    
    def exportar_reporte_markdown(self, resultado: Dict[str, Any], 
                                 archivo_salida: Optional[str] = None) -> str:
        """
        Exporta los resultados del escaneo a un archivo Markdown.
        
        Args:
            resultado: Diccionario con resultados del escaneo
            archivo_salida: Ruta del archivo de salida (opcional)
            
        Returns:
            str: Ruta del archivo creado
        """
        if archivo_salida is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            archivo_salida = f"reporte_procesos_{timestamp}.md"
        
        try:
            with open(archivo_salida, 'w', encoding='utf-8') as f:
                f.write("# Reporte de Monitoreo de Procesos\n\n")
                f.write(f"**Fecha:** {resultado['timestamp']}\n")
                f.write(f"**Generado por:** Ares Aegis Monitor de Procesos\n\n")
                
                # Resumen ejecutivo
                stats = resultado['estadisticas']
                f.write("## Resumen Ejecutivo\n\n")
                f.write(f"- **Total de procesos:** {stats['total_procesos']}\n")
                f.write(f"- **Procesos sospechosos:** {stats['procesos_sospechosos']}\n")
                f.write(f"- **Procesos nuevos:** {stats['procesos_nuevos']}\n")
                f.write(f"- **Conexiones de red:** {stats['conexiones_red']}\n")
                f.write(f"- **Uso promedio de CPU:** {stats['uso_cpu_promedio']:.2f}%\n")
                f.write(f"- **Memoria total usada:** {stats['memoria_total_mb']:.2f} MB\n")
                f.write(f"- **Tiempo de escaneo:** {stats['tiempo_escaneo']:.2f} segundos\n\n")
                
                # Procesos sospechosos
                if resultado['procesos_sospechosos']:
                    f.write("## Procesos Sospechosos Detectados\n\n")
                    for proceso in resultado['procesos_sospechosos']:
                        f.write(f"### Proceso {proceso['nombre']} (PID: {proceso['pid']})\n\n")
                        f.write(f"- **Usuario:** {proceso['usuario']}\n")
                        f.write(f"- **Estado:** {proceso['estado']}\n")
                        f.write(f"- **Línea de comandos:** `{proceso['cmdline']}`\n")
                        f.write(f"- **CPU:** {proceso['cpu_percent']:.2f}%\n")
                        f.write(f"- **Memoria:** {proceso['memoria_mb']:.2f} MB\n")
                        f.write("- **Razones de sospecha:**\n")
                        for razon in proceso['razones_sospecha']:
                            f.write(f"  - {razon}\n")
                        f.write("\n")
                else:
                    f.write("## Procesos Sospechosos\n\n")
                    f.write("✅ No se detectaron procesos sospechosos.\n\n")
                
                # Procesos nuevos
                if resultado['procesos_nuevos']:
                    f.write("## Procesos Nuevos Detectados\n\n")
                    for proceso in resultado['procesos_nuevos']:
                        f.write(f"- **{proceso['nombre']}** (PID: {proceso['pid']}) - {proceso['usuario']}\n")
                    f.write("\n")
                
                # Conexiones de red
                if resultado['conexiones_red']:
                    f.write("## Conexiones de Red Activas\n\n")
                    f.write("| Protocolo | Dirección Local | Dirección Remota | Estado | PID |\n")
                    f.write("|-----------|----------------|------------------|--------|-----|\n")
                    for conn in resultado['conexiones_red']:
                        pid_str = str(conn['pid']) if conn['pid'] else 'N/A'
                        f.write(f"| {conn['protocolo']} | {conn['direccion_local']} | "
                               f"{conn['direccion_remota']} | {conn['estado']} | {pid_str} |\n")
                    f.write("\n")
                
                f.write("---\n")
                f.write("*Reporte generado por Ares Aegis*\n")
            
            if self.siem:
                self.siem.log_evento('INFO', 'monitor_procesos', 
                                   f'Reporte exportado a {archivo_salida}')
            
            return archivo_salida
            
        except Exception as e:
            if self.siem:
                self.siem.log_evento('ERROR', 'monitor_procesos', 
                                   f'Error exportando reporte: {e}')
            raise
