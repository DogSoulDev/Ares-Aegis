#!/usr/bin/env python3
"""
Analizador Dinámico
Mini-sandbox para análisis dinámico de archivos ejecutables y comportamiento en tiempo real.

Autor: DogSoulDev
Versión: 2.0.0
"""

import os
import subprocess
import threading
import time
import tempfile
import shutil
import signal
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict


class EntornoSandbox:
    """Entorno de sandbox para ejecución controlada de archivos."""
    
    def __init__(self, directorio_trabajo: Optional[str] = None):
        """
        Inicializa el entorno de sandbox.
        
        Args:
            directorio_trabajo: Directorio base para el sandbox (opcional)
        """
        self.directorio_trabajo = directorio_trabajo or tempfile.mkdtemp(prefix="ares_sandbox_")
        self.directorio_entrada = os.path.join(self.directorio_trabajo, "entrada")
        self.directorio_salida = os.path.join(self.directorio_trabajo, "salida")
        self.directorio_logs = os.path.join(self.directorio_trabajo, "logs")
        
        # Crear estructura de directorios
        os.makedirs(self.directorio_entrada, exist_ok=True)
        os.makedirs(self.directorio_salida, exist_ok=True)
        os.makedirs(self.directorio_logs, exist_ok=True)
        
        # Estado del sandbox
        self.proceso_activo: Optional[subprocess.Popen] = None
        self.esta_ejecutando = False
        self.tiempo_inicio: Optional[datetime] = None
        self.limite_tiempo = 30  # 30 segundos por defecto
        
        # Monitoreo
        self.actividad_archivos = []
        self.actividad_red = []
        self.actividad_procesos = []
        self.cambios_sistema = []
    
    def preparar_archivo(self, ruta_archivo: str) -> str:
        """
        Prepara un archivo para ejecución en el sandbox.
        
        Args:
            ruta_archivo: Ruta al archivo a analizar
            
        Returns:
            Ruta del archivo en el sandbox
        """
        if not os.path.exists(ruta_archivo):
            raise FileNotFoundError(f"Archivo no encontrado: {ruta_archivo}")
        
        nombre_archivo = os.path.basename(ruta_archivo)
        ruta_sandbox = os.path.join(self.directorio_entrada, nombre_archivo)
        
        # Copiar archivo al sandbox
        shutil.copy2(ruta_archivo, ruta_sandbox)
        
        # Hacer ejecutable si es necesario
        if os.access(ruta_archivo, os.X_OK):
            os.chmod(ruta_sandbox, 0o755)
        
        return ruta_sandbox
    
    def crear_entorno_restringido(self) -> Dict[str, str]:
        """Crea un entorno de variables restringido para el proceso."""
        entorno = {
            'PATH': '/usr/bin:/bin',
            'HOME': self.directorio_trabajo,
            'TMPDIR': self.directorio_trabajo,
            'USER': 'sandbox',
            'SHELL': '/bin/bash'
        }
        return entorno
    
    def limpiar(self):
        """Limpia el entorno de sandbox."""
        if self.proceso_activo and self.proceso_activo.poll() is None:
            try:
                self.proceso_activo.terminate()
                time.sleep(2)
                if self.proceso_activo.poll() is None:
                    self.proceso_activo.kill()
            except:
                pass
        
        # Limpiar directorio de trabajo
        try:
            shutil.rmtree(self.directorio_trabajo, ignore_errors=True)
        except:
            pass


class MonitorActividad:
    """Monitor de actividad del sistema durante la ejecución en sandbox."""
    
    def __init__(self, entorno_sandbox: EntornoSandbox):
        """
        Inicializa el monitor de actividad.
        
        Args:
            entorno_sandbox: Entorno de sandbox a monitorear
        """
        self.sandbox = entorno_sandbox
        self.monitoreando = False
        self.thread_monitor = None
        
        # Estado inicial del sistema
        self.archivos_iniciales = set()
        self.procesos_iniciales = set()
        self.conexiones_iniciales = set()
        
        # Actividad detectada
        self.archivos_creados = []
        self.archivos_modificados = []
        self.archivos_eliminados = []
        self.procesos_nuevos = []
        self.conexiones_red = []
        self.comandos_ejecutados = []
    
    def capturar_estado_inicial(self):
        """Captura el estado inicial del sistema."""
        # Capturar archivos en directorio de trabajo
        try:
            for root, dirs, files in os.walk(self.sandbox.directorio_trabajo):
                for file in files:
                    ruta_completa = os.path.join(root, file)
                    self.archivos_iniciales.add(ruta_completa)
        except:
            pass
        
        # Capturar procesos actuales
        try:
            resultado = subprocess.run(['ps', 'aux'], capture_output=True, text=True, timeout=5)
            if resultado.returncode == 0:
                for linea in resultado.stdout.split('\n')[1:]:  # Saltar header
                    if linea.strip():
                        partes = linea.split(None, 10)
                        if len(partes) >= 11:
                            pid = partes[1]
                            comando = partes[10]
                            self.procesos_iniciales.add((pid, comando))
        except:
            pass
    
    def iniciar_monitoreo(self):
        """Inicia el monitoreo de actividad."""
        if self.monitoreando:
            return
        
        self.capturar_estado_inicial()
        self.monitoreando = True
        self.thread_monitor = threading.Thread(target=self._loop_monitoreo)
        self.thread_monitor.daemon = True
        self.thread_monitor.start()
    
    def detener_monitoreo(self):
        """Detiene el monitoreo de actividad."""
        self.monitoreando = False
        if self.thread_monitor:
            self.thread_monitor.join(timeout=2)
    
    def _loop_monitoreo(self):
        """Loop principal de monitoreo."""
        while self.monitoreando:
            try:
                self._monitorear_archivos()
                self._monitorear_procesos()
                self._monitorear_red()
                time.sleep(1)  # Verificar cada segundo
            except Exception:
                continue
    
    def _monitorear_archivos(self):
        """Monitorea cambios en el sistema de archivos."""
        try:
            archivos_actuales = set()
            for root, dirs, files in os.walk(self.sandbox.directorio_trabajo):
                for file in files:
                    ruta_completa = os.path.join(root, file)
                    archivos_actuales.add(ruta_completa)
                    
                    # Verificar si es un archivo nuevo
                    if ruta_completa not in self.archivos_iniciales:
                        if ruta_completa not in [a['ruta'] for a in self.archivos_creados]:
                            self.archivos_creados.append({
                                'ruta': ruta_completa,
                                'timestamp': datetime.now().isoformat(),
                                'tamaño': os.path.getsize(ruta_completa) if os.path.exists(ruta_completa) else 0
                            })
            
            # Detectar archivos eliminados
            for archivo_inicial in self.archivos_iniciales:
                if archivo_inicial not in archivos_actuales:
                    if archivo_inicial not in [a['ruta'] for a in self.archivos_eliminados]:
                        self.archivos_eliminados.append({
                            'ruta': archivo_inicial,
                            'timestamp': datetime.now().isoformat()
                        })
        except:
            pass
    
    def _monitorear_procesos(self):
        """Monitorea nuevos procesos."""
        try:
            resultado = subprocess.run(['ps', 'aux'], capture_output=True, text=True, timeout=5)
            if resultado.returncode == 0:
                procesos_actuales = set()
                for linea in resultado.stdout.split('\n')[1:]:
                    if linea.strip():
                        partes = linea.split(None, 10)
                        if len(partes) >= 11:
                            pid = partes[1]
                            comando = partes[10]
                            proceso_tuple = (pid, comando)
                            procesos_actuales.add(proceso_tuple)
                            
                            # Verificar si es un proceso nuevo
                            if proceso_tuple not in self.procesos_iniciales:
                                if not any(p['pid'] == pid for p in self.procesos_nuevos):
                                    self.procesos_nuevos.append({
                                        'pid': pid,
                                        'comando': comando,
                                        'timestamp': datetime.now().isoformat(),
                                        'usuario': partes[0] if len(partes) > 0 else 'unknown'
                                    })
        except:
            pass
    
    def _monitorear_red(self):
        """Monitorea conexiones de red."""
        try:
            # Usar netstat para monitorear conexiones
            resultado = subprocess.run(['netstat', '-tuln'], capture_output=True, text=True, timeout=5)
            if resultado.returncode == 0:
                for linea in resultado.stdout.split('\n'):
                    if 'ESTABLISHED' in linea or 'LISTEN' in linea:
                        partes = linea.split()
                        if len(partes) >= 4:
                            protocolo = partes[0]
                            direccion_local = partes[3]
                            direccion_remota = partes[4] if len(partes) > 4 else ''
                            estado = partes[5] if len(partes) > 5 else ''
                            
                            conexion = {
                                'protocolo': protocolo,
                                'local': direccion_local,
                                'remota': direccion_remota,
                                'estado': estado,
                                'timestamp': datetime.now().isoformat()
                            }
                            
                            # Verificar si es una conexión nueva
                            if not any(c['local'] == direccion_local and c['remota'] == direccion_remota 
                                     for c in self.conexiones_red):
                                self.conexiones_red.append(conexion)
        except:
            pass
    
    def obtener_reporte_actividad(self) -> Dict[str, Any]:
        """Obtiene un reporte completo de la actividad detectada."""
        return {
            'archivos': {
                'creados': self.archivos_creados,
                'modificados': self.archivos_modificados,
                'eliminados': self.archivos_eliminados
            },
            'procesos': {
                'nuevos': self.procesos_nuevos
            },
            'red': {
                'conexiones': self.conexiones_red
            },
            'estadisticas': {
                'total_archivos_creados': len(self.archivos_creados),
                'total_archivos_eliminados': len(self.archivos_eliminados),
                'total_procesos_nuevos': len(self.procesos_nuevos),
                'total_conexiones': len(self.conexiones_red)
            }
        }


class AnalizadorDinamico:
    """Analizador dinámico principal con capacidades de sandbox."""
    
    def __init__(self, siem=None):
        """
        Inicializa el analizador dinámico.
        
        Args:
            siem: Sistema SIEM para logging (opcional)
        """
        self.siem = siem
        self.sandbox: Optional[EntornoSandbox] = None
        self.monitor: Optional[MonitorActividad] = None
    
    def analizar_archivo_dinamico(self, ruta_archivo: str, tiempo_limite: int = 30, 
                                argumentos: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Realiza análisis dinámico de un archivo ejecutable.
        
        Args:
            ruta_archivo: Ruta al archivo a analizar
            tiempo_limite: Tiempo límite de ejecución en segundos
            argumentos: Argumentos adicionales para la ejecución
            
        Returns:
            Dict con resultados del análisis dinámico
        """
        if self.siem:
            self.siem.log_evento('INFO', 'analizador_dinamico', 
                               f'Iniciando análisis dinámico de {ruta_archivo}')
        
        inicio_analisis = datetime.now()
        
        try:
            # Crear entorno de sandbox
            self.sandbox = EntornoSandbox()
            self.sandbox.limite_tiempo = tiempo_limite
            
            # Preparar archivo
            archivo_sandbox = self.sandbox.preparar_archivo(ruta_archivo)
            
            # Inicializar monitor
            self.monitor = MonitorActividad(self.sandbox)
            
            # Ejecutar análisis
            resultado_ejecucion = self._ejecutar_en_sandbox(
                archivo_sandbox, argumentos or []
            )
            
            # Obtener reporte de actividad
            reporte_actividad = self.monitor.obtener_reporte_actividad()
            
            # Analizar comportamiento
            analisis_comportamiento = self._analizar_comportamiento(reporte_actividad)
            
            fin_analisis = datetime.now()
            tiempo_total = (fin_analisis - inicio_analisis).total_seconds()
            
            resultado = {
                'timestamp_analisis': inicio_analisis.isoformat(),
                'archivo_analizado': ruta_archivo,
                'tiempo_analisis': tiempo_total,
                'ejecucion': resultado_ejecucion,
                'actividad_detectada': reporte_actividad,
                'analisis_comportamiento': analisis_comportamiento,
                'nivel_riesgo': self._calcular_nivel_riesgo(analisis_comportamiento),
                'recomendaciones': self._generar_recomendaciones(analisis_comportamiento)
            }
            
            if self.siem:
                riesgo = resultado['nivel_riesgo']
                self.siem.log_evento('INFO', 'analizador_dinamico', 
                                   f'Análisis dinámico completado. Nivel de riesgo: {riesgo}')
            
            return resultado
            
        except Exception as e:
            error_msg = f'Error en análisis dinámico: {str(e)}'
            if self.siem:
                self.siem.log_evento('ERROR', 'analizador_dinamico', error_msg)
            
            return {
                'error': error_msg,
                'timestamp_analisis': inicio_analisis.isoformat(),
                'archivo_analizado': ruta_archivo
            }
        
        finally:
            # Limpiar sandbox
            if self.sandbox:
                self.sandbox.limpiar()
            if self.monitor:
                self.monitor.detener_monitoreo()
    
    def _ejecutar_en_sandbox(self, archivo_sandbox: str, argumentos: List[str]) -> Dict[str, Any]:
        """Ejecuta el archivo en el entorno de sandbox."""
        if not self.monitor:
            raise RuntimeError("Monitor no inicializado")
        if not self.sandbox:
            raise RuntimeError("Sandbox no inicializado")
            
        self.monitor.iniciar_monitoreo()
        
        try:
            # Preparar comando
            comando = [archivo_sandbox] + argumentos
            entorno = self.sandbox.crear_entorno_restringido()
            
            # Configurar archivos de salida
            stdout_file = os.path.join(self.sandbox.directorio_logs, "stdout.log")
            stderr_file = os.path.join(self.sandbox.directorio_logs, "stderr.log")
            
            inicio_ejecucion = datetime.now()
            
            # Ejecutar proceso con límites
            with open(stdout_file, 'w') as stdout, open(stderr_file, 'w') as stderr:
                proceso = subprocess.Popen(
                    comando,
                    stdout=stdout,
                    stderr=stderr,
                    env=entorno,
                    cwd=self.sandbox.directorio_trabajo,
                    preexec_fn=os.setsid  # Crear nuevo grupo de procesos
                )
                
                self.sandbox.proceso_activo = proceso
                self.sandbox.esta_ejecutando = True
                self.sandbox.tiempo_inicio = inicio_ejecucion
                
                try:
                    # Esperar con timeout
                    codigo_salida = proceso.wait(timeout=self.sandbox.limite_tiempo)
                    terminacion = 'normal'
                    
                except subprocess.TimeoutExpired:
                    # Terminar proceso por timeout
                    try:
                        os.killpg(os.getpgid(proceso.pid), signal.SIGTERM)
                        time.sleep(2)
                        if proceso.poll() is None:
                            os.killpg(os.getpgid(proceso.pid), signal.SIGKILL)
                    except:
                        pass
                    
                    codigo_salida = -1
                    terminacion = 'timeout'
            
            fin_ejecucion = datetime.now()
            tiempo_ejecucion = (fin_ejecucion - inicio_ejecucion).total_seconds()
            
            # Leer salidas
            stdout_contenido = ""
            stderr_contenido = ""
            
            try:
                with open(stdout_file, 'r') as f:
                    stdout_contenido = f.read()
            except:
                pass
            
            try:
                with open(stderr_file, 'r') as f:
                    stderr_contenido = f.read()
            except:
                pass
            
            return {
                'codigo_salida': codigo_salida,
                'terminacion': terminacion,
                'tiempo_ejecucion': tiempo_ejecucion,
                'stdout': stdout_contenido[:1000],  # Limitar salida
                'stderr': stderr_contenido[:1000],
                'comando_ejecutado': ' '.join(comando)
            }
            
        finally:
            if self.sandbox:
                self.sandbox.esta_ejecutando = False
            if self.monitor:
                self.monitor.detener_monitoreo()
    
    def _analizar_comportamiento(self, reporte_actividad: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza el comportamiento basado en la actividad detectada."""
        comportamiento = {
            'actividad_archivos': False,
            'actividad_red': False,
            'actividad_procesos': False,
            'patrones_sospechosos': [],
            'indicadores_malware': []
        }
        
        # Analizar actividad de archivos
        archivos = reporte_actividad['archivos']
        if archivos['creados'] or archivos['eliminados']:
            comportamiento['actividad_archivos'] = True
            
            # Detectar patrones sospechosos en archivos
            for archivo in archivos['creados']:
                ruta = archivo['ruta'].lower()
                if any(ext in ruta for ext in ['.exe', '.bat', '.cmd', '.ps1', '.vbs']):
                    comportamiento['patrones_sospechosos'].append(
                        f"Creación de archivo ejecutable: {archivo['ruta']}"
                    )
                
                if any(dir_sospechoso in ruta for dir_sospechoso in ['/tmp/', '/var/tmp/', 'temp']):
                    comportamiento['indicadores_malware'].append(
                        f"Archivo creado en directorio temporal: {archivo['ruta']}"
                    )
        
        # Analizar actividad de procesos
        procesos = reporte_actividad['procesos']
        if procesos['nuevos']:
            comportamiento['actividad_procesos'] = True
            
            for proceso in procesos['nuevos']:
                comando = proceso['comando'].lower()
                
                # Detectar comandos sospechosos
                comandos_sospechosos = [
                    'wget', 'curl', 'nc', 'netcat', 'bash', 'sh', 'python', 'perl'
                ]
                
                if any(cmd in comando for cmd in comandos_sospechosos):
                    comportamiento['patrones_sospechosos'].append(
                        f"Proceso sospechoso ejecutado: {proceso['comando']}"
                    )
        
        # Analizar actividad de red
        red = reporte_actividad['red']
        if red['conexiones']:
            comportamiento['actividad_red'] = True
            
            for conexion in red['conexiones']:
                if conexion['estado'] == 'ESTABLISHED':
                    comportamiento['indicadores_malware'].append(
                        f"Conexión de red establecida: {conexion['local']} -> {conexion['remota']}"
                    )
        
        return comportamiento
    
    def _calcular_nivel_riesgo(self, analisis_comportamiento: Dict[str, Any]) -> str:
        """Calcula el nivel de riesgo basado en el comportamiento."""
        puntuacion_riesgo = 0
        
        # Actividad básica (puntuación baja)
        if analisis_comportamiento['actividad_archivos']:
            puntuacion_riesgo += 1
        if analisis_comportamiento['actividad_procesos']:
            puntuacion_riesgo += 1
        if analisis_comportamiento['actividad_red']:
            puntuacion_riesgo += 2
        
        # Patrones sospechosos (puntuación media)
        puntuacion_riesgo += len(analisis_comportamiento['patrones_sospechosos']) * 2
        
        # Indicadores de malware (puntuación alta)
        puntuacion_riesgo += len(analisis_comportamiento['indicadores_malware']) * 3
        
        # Determinar nivel
        if puntuacion_riesgo == 0:
            return 'BAJO'
        elif puntuacion_riesgo <= 3:
            return 'MEDIO'
        elif puntuacion_riesgo <= 7:
            return 'ALTO'
        else:
            return 'CRITICO'
    
    def _generar_recomendaciones(self, analisis_comportamiento: Dict[str, Any]) -> List[str]:
        """Genera recomendaciones basadas en el comportamiento."""
        recomendaciones = []
        
        if analisis_comportamiento['actividad_archivos']:
            recomendaciones.append("Revisar archivos creados o modificados durante la ejecución")
        
        if analisis_comportamiento['actividad_red']:
            recomendaciones.append("Monitorear conexiones de red establecidas")
            recomendaciones.append("Verificar destinos de conexiones externas")
        
        if analisis_comportamiento['actividad_procesos']:
            recomendaciones.append("Analizar procesos secundarios ejecutados")
        
        if analisis_comportamiento['patrones_sospechosos']:
            recomendaciones.append("Investigar patrones de comportamiento sospechoso detectados")
        
        if analisis_comportamiento['indicadores_malware']:
            recomendaciones.append("ALERTA: Indicadores de malware detectados - Análisis inmediato requerido")
            recomendaciones.append("Aislar sistema y realizar análisis forense completo")
        
        if not recomendaciones:
            recomendaciones.append("El archivo parece seguro basado en el análisis dinámico")
        
        return recomendaciones
    
    def generar_reporte_markdown(self, resultado_analisis: Dict[str, Any]) -> str:
        """
        Genera un reporte en formato Markdown del análisis dinámico.
        
        Args:
            resultado_analisis: Resultado del análisis dinámico
            
        Returns:
            String con el reporte en formato Markdown
        """
        if 'error' in resultado_analisis:
            return f"""# Error en Análisis Dinámico

**Error:** {resultado_analisis['error']}
**Archivo:** {resultado_analisis['archivo_analizado']}
**Timestamp:** {resultado_analisis['timestamp_analisis']}
"""
        
        archivo = Path(resultado_analisis['archivo_analizado']).name
        nivel_riesgo = resultado_analisis['nivel_riesgo']
        
        # Emoji para nivel de riesgo
        emoji_riesgo = {
            'BAJO': '🟢',
            'MEDIO': '🟡', 
            'ALTO': '🟠',
            'CRITICO': '🔴'
        }.get(nivel_riesgo, '⚪')
        
        reporte = f"""# 🔬 Análisis Dinámico: {archivo}

## Resumen Ejecutivo
- **Archivo:** `{resultado_analisis['archivo_analizado']}`
- **Nivel de Riesgo:** {emoji_riesgo} **{nivel_riesgo}**
- **Tiempo de Análisis:** {resultado_analisis['tiempo_analisis']:.2f} segundos
- **Fecha:** {resultado_analisis['timestamp_analisis']}

## Ejecución en Sandbox
"""
        
        ejecucion = resultado_analisis['ejecucion']
        reporte += f"""- **Código de Salida:** {ejecucion['codigo_salida']}
- **Terminación:** {ejecucion['terminacion']}
- **Tiempo de Ejecución:** {ejecucion['tiempo_ejecucion']:.2f} segundos
- **Comando:** `{ejecucion['comando_ejecutado']}`

"""
        
        if ejecucion['stdout']:
            reporte += f"""### Salida Estándar
```
{ejecucion['stdout'][:500]}
```

"""
        
        if ejecucion['stderr']:
            reporte += f"""### Errores
```
{ejecucion['stderr'][:500]}
```

"""
        
        # Actividad detectada
        actividad = resultado_analisis['actividad_detectada']
        estadisticas = actividad['estadisticas']
        
        reporte += f"""## Actividad Detectada
- **Archivos Creados:** {estadisticas['total_archivos_creados']}
- **Archivos Eliminados:** {estadisticas['total_archivos_eliminados']}
- **Procesos Nuevos:** {estadisticas['total_procesos_nuevos']}
- **Conexiones de Red:** {estadisticas['total_conexiones']}

"""
        
        # Análisis de comportamiento
        comportamiento = resultado_analisis['analisis_comportamiento']
        
        if comportamiento['patrones_sospechosos']:
            reporte += "## ⚠️ Patrones Sospechosos\n"
            for patron in comportamiento['patrones_sospechosos']:
                reporte += f"- {patron}\n"
            reporte += "\n"
        
        if comportamiento['indicadores_malware']:
            reporte += "## 🚨 Indicadores de Malware\n"
            for indicador in comportamiento['indicadores_malware']:
                reporte += f"- **{indicador}**\n"
            reporte += "\n"
        
        # Recomendaciones
        reporte += "## 📋 Recomendaciones\n"
        for rec in resultado_analisis['recomendaciones']:
            reporte += f"- {rec}\n"
        
        reporte += f"\n---\n*Análisis dinámico realizado el {resultado_analisis['timestamp_analisis']} por Ares Aegis*\n"
        
        return reporte
