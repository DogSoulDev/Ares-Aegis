#!/usr/bin/env python3
"""
Copyright (c) 2025 DogSoulDev (https://github.com/DogSoulDev)
Todos los derechos reservados. Este código es propietario y confidencial.

Analizador Dinámico
"""

import os
import sys
import subprocess
import tempfile
import shutil
import threading
import time
import signal
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
from ..utilidades.ayuda_logging import configurar_logger_modulo
from ..utilidades.ayuda_rutas import crear_ruta_segura


class ResultadoAnalisisDinamico:
    """Resultado del análisis dinámico de un archivo."""
    
    def __init__(self, archivo_analizado: str):
        """
        Inicializa el resultado del análisis.
        
        Args:
            archivo_analizado: Ruta del archivo analizado
        """
        self.archivo_analizado = archivo_analizado
        self.timestamp_inicio = datetime.now()
        self.timestamp_fin: Optional[datetime] = None
        self.exitoso = False
        self.tiempo_ejecucion = 0.0
        
        # Observaciones del comportamiento
        self.procesos_creados: List[Dict[str, Any]] = []
        self.archivos_creados: List[str] = []
        self.archivos_modificados: List[str] = []
        self.archivos_eliminados: List[str] = []
        self.conexiones_red: List[Dict[str, Any]] = []
        self.comandos_ejecutados: List[str] = []
        
        # Análisis de riesgo
        self.nivel_riesgo = "DESCONOCIDO"
        self.comportamientos_sospechosos: List[str] = []
        self.indicadores_malware: List[str] = []
        
        # Metadatos
        self.codigo_salida: Optional[int] = None
        self.stdout_capturado = ""
        self.stderr_capturado = ""
        self.error_analisis: Optional[str] = None
    
    def marcar_completado(self, exitoso: bool = True):
        """Marca el análisis como completado."""
        self.timestamp_fin = datetime.now()
        self.exitoso = exitoso
        if self.timestamp_fin and self.timestamp_inicio:
            self.tiempo_ejecucion = (self.timestamp_fin - self.timestamp_inicio).total_seconds()
    
    def evaluar_riesgo(self):
        """Evalúa el nivel de riesgo basado en los comportamientos observados."""
        riesgo_puntos = 0
        
        # Evaluar comportamientos sospechosos
        if len(self.procesos_creados) > 5:
            riesgo_puntos += 2
            self.comportamientos_sospechosos.append("Creación excesiva de procesos")
        
        if len(self.archivos_creados) > 10:
            riesgo_puntos += 2
            self.comportamientos_sospechosos.append("Creación masiva de archivos")
        
        if self.conexiones_red:
            riesgo_puntos += 3
            self.comportamientos_sospechosos.append("Actividad de red detectada")
        
        # Buscar patrones maliciosos en archivos creados
        for archivo in self.archivos_creados:
            nombre_archivo = os.path.basename(archivo).lower()
            if any(patron in nombre_archivo for patron in ['tmp', 'temp', 'cache', '.exe', '.bat', '.cmd']):
                riesgo_puntos += 1
                self.indicadores_malware.append(f"Archivo sospechoso creado: {nombre_archivo}")
        
        # Evaluar comandos ejecutados
        for comando in self.comandos_ejecutados:
            comando_lower = comando.lower()
            patrones_sospechosos = ['wget', 'curl', 'nc', 'netcat', 'powershell', 'cmd', 'bash', 'sh']
            if any(patron in comando_lower for patron in patrones_sospechosos):
                riesgo_puntos += 2
                self.indicadores_malware.append(f"Comando sospechoso: {comando}")
        
        # Asignar nivel de riesgo
        if riesgo_puntos == 0:
            self.nivel_riesgo = "BAJO"
        elif riesgo_puntos <= 3:
            self.nivel_riesgo = "MEDIO"
        elif riesgo_puntos <= 6:
            self.nivel_riesgo = "ALTO"
        else:
            self.nivel_riesgo = "CRITICO"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el resultado a diccionario."""
        return {
            'archivo_analizado': self.archivo_analizado,
            'timestamp_inicio': self.timestamp_inicio.isoformat() if self.timestamp_inicio else None,
            'timestamp_fin': self.timestamp_fin.isoformat() if self.timestamp_fin else None,
            'exitoso': self.exitoso,
            'tiempo_ejecucion': self.tiempo_ejecucion,
            'nivel_riesgo': self.nivel_riesgo,
            'comportamientos_sospechosos': self.comportamientos_sospechosos,
            'indicadores_malware': self.indicadores_malware,
            'procesos_creados': len(self.procesos_creados),
            'archivos_creados': len(self.archivos_creados),
            'archivos_modificados': len(self.archivos_modificados),
            'conexiones_red': len(self.conexiones_red),
            'codigo_salida': self.codigo_salida,
            'error_analisis': self.error_analisis
        }


class MonitorSandbox:
    """Monitor del entorno sandbox para observar comportamientos."""
    
    def __init__(self, directorio_sandbox: str):
        """
        Inicializa el monitor del sandbox.
        
        Args:
            directorio_sandbox: Directorio del sandbox a monitorear
        """
        self.directorio_sandbox = Path(directorio_sandbox)
        self.logger = configurar_logger_modulo("monitor_sandbox")
        self.monitoreando = False
        self.hilo_monitor: Optional[threading.Thread] = None
        
        # Estado inicial del directorio
        self.archivos_iniciales: Set[str] = set()
        self.procesos_iniciales: Set[int] = set()
        
        # Observaciones
        self.archivos_nuevos: List[str] = []
        self.archivos_modificados: List[str] = []
        self.procesos_nuevos: List[Dict[str, Any]] = []
    
    def capturar_estado_inicial(self):
        """Captura el estado inicial del sistema para comparación."""
        try:
            # Capturar archivos iniciales en el sandbox
            if self.directorio_sandbox.exists():
                for archivo in self.directorio_sandbox.rglob('*'):
                    if archivo.is_file():
                        self.archivos_iniciales.add(str(archivo))
            
            # Capturar procesos iniciales (limitado)
            try:
                resultado = subprocess.run(['ps', 'aux'], capture_output=True, text=True, timeout=5)
                if resultado.returncode == 0:
                    for linea in resultado.stdout.split('\n')[1:]:  # Omitir header
                        if linea.strip():
                            partes = linea.split(None, 10)
                            if len(partes) >= 2:
                                try:
                                    pid = int(partes[1])
                                    self.procesos_iniciales.add(pid)
                                except ValueError:
                                    continue
            except Exception as e:
                self.logger.debug(f"Error capturando procesos iniciales: {e}")
                
        except Exception as e:
            self.logger.error(f"Error capturando estado inicial: {e}")
    
    def iniciar_monitoreo(self):
        """Inicia el monitoreo del sandbox."""
        if self.monitoreando:
            return
        
        self.monitoreando = True
        self.capturar_estado_inicial()
        
        self.hilo_monitor = threading.Thread(target=self._loop_monitoreo, daemon=True)
        self.hilo_monitor.start()
        self.logger.info("Monitor de sandbox iniciado")
    
    def detener_monitoreo(self):
        """Detiene el monitoreo del sandbox."""
        self.monitoreando = False
        if self.hilo_monitor:
            self.hilo_monitor.join(timeout=5)
        self.logger.info("Monitor de sandbox detenido")
    
    def _loop_monitoreo(self):
        """Loop principal de monitoreo."""
        while self.monitoreando:
            try:
                self._detectar_archivos_nuevos()
                self._detectar_procesos_nuevos()
                time.sleep(1)  # Monitoreo cada segundo
            except Exception as e:
                self.logger.error(f"Error en loop de monitoreo: {e}")
                time.sleep(2)
    
    def _detectar_archivos_nuevos(self):
        """Detecta archivos nuevos o modificados en el sandbox."""
        try:
            if not self.directorio_sandbox.exists():
                return
            
            archivos_actuales = set()
            for archivo in self.directorio_sandbox.rglob('*'):
                if archivo.is_file():
                    ruta_archivo = str(archivo)
                    archivos_actuales.add(ruta_archivo)
                    
                    # Verificar si es un archivo nuevo
                    if ruta_archivo not in self.archivos_iniciales:
                        if ruta_archivo not in self.archivos_nuevos:
                            self.archivos_nuevos.append(ruta_archivo)
                            self.logger.info(f"Archivo nuevo detectado: {ruta_archivo}")
            
            # Detectar archivos eliminados (no incluido en archivos_actuales)
            # Por simplicidad, no implementamos detección de eliminación en tiempo real
            
        except Exception as e:
            self.logger.debug(f"Error detectando archivos nuevos: {e}")
    
    def _detectar_procesos_nuevos(self):
        """Detecta procesos nuevos relacionados con el sandbox."""
        try:
            resultado = subprocess.run(['ps', 'aux'], capture_output=True, text=True, timeout=5)
            if resultado.returncode == 0:
                for linea in resultado.stdout.split('\n')[1:]:  # Omitir header
                    if linea.strip() and str(self.directorio_sandbox) in linea:
                        partes = linea.split(None, 10)
                        if len(partes) >= 11:
                            try:
                                pid = int(partes[1])
                                if pid not in self.procesos_iniciales:
                                    proceso_info = {
                                        'pid': pid,
                                        'comando': partes[10],
                                        'usuario': partes[0],
                                        'timestamp': datetime.now().isoformat()
                                    }
                                    
                                    # Evitar duplicados
                                    if not any(p['pid'] == pid for p in self.procesos_nuevos):
                                        self.procesos_nuevos.append(proceso_info)
                                        self.logger.info(f"Proceso nuevo detectado: PID {pid}")
                            except (ValueError, IndexError):
                                continue
        
        except Exception as e:
            self.logger.debug(f"Error detectando procesos nuevos: {e}")


class AnalizadorDinamico:
    """Analizador dinámico para ejecución controlada de archivos sospechosos."""
    
    def __init__(self):
        """Inicializa el analizador dinámico."""
        self.logger = configurar_logger_modulo("analizador_dinamico")
        self.directorio_base_sandbox = "/tmp/ares_aegis_sandbox"
        self.timeout_ejecucion = 30  # 30 segundos máximo
        
        self.logger.info("El laboratorio de Dédalo ha sido construido en el reino digital")
    
    def crear_sandbox(self) -> str:
        """
        Crea un directorio sandbox temporal y aislado.
        
        Returns:
            str: Ruta del directorio sandbox creado
        """
        try:
            # Crear directorio base si no existe
            Path(self.directorio_base_sandbox).mkdir(parents=True, exist_ok=True)
            
            # Crear sandbox único con timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            directorio_sandbox = os.path.join(self.directorio_base_sandbox, f"sandbox_{timestamp}")
            
            Path(directorio_sandbox).mkdir(parents=True, exist_ok=True)
            
            # Establecer permisos restrictivos
            os.chmod(directorio_sandbox, 0o700)
            
            self.logger.info(f"Sandbox creado en el laberinto: {directorio_sandbox}")
            return directorio_sandbox
        
        except Exception as e:
            error_msg = f"Error forjando el laberinto de Dédalo: {e}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def limpiar_sandbox(self, directorio_sandbox: str):
        """
        Limpia y elimina el directorio sandbox.
        
        Args:
            directorio_sandbox: Directorio sandbox a limpiar
        """
        try:
            if os.path.exists(directorio_sandbox):
                # Terminar procesos que puedan estar usando el directorio
                self._terminar_procesos_sandbox(directorio_sandbox)
                
                # Eliminar directorio
                shutil.rmtree(directorio_sandbox, ignore_errors=True)
                
                self.logger.info(f"Laberinto de Dédalo purificado: {directorio_sandbox}")
        
        except Exception as e:
            self.logger.warning(f"Error purificando el laberinto: {e}")
    
    def _terminar_procesos_sandbox(self, directorio_sandbox: str):
        """Termina procesos relacionados con el sandbox."""
        try:
            resultado = subprocess.run(['ps', 'aux'], capture_output=True, text=True, timeout=5)
            if resultado.returncode == 0:
                for linea in resultado.stdout.split('\n')[1:]:
                    if directorio_sandbox in linea:
                        partes = linea.split(None, 10)
                        if len(partes) >= 2:
                            try:
                                pid = int(partes[1])
                                os.kill(pid, signal.SIGTERM)
                                time.sleep(1)
                                try:
                                    os.kill(pid, signal.SIGKILL)
                                except ProcessLookupError:
                                    pass  # El proceso ya terminó
                            except (ValueError, ProcessLookupError):
                                continue
        
        except Exception as e:
            self.logger.debug(f"Error terminando procesos del sandbox: {e}")
    
    def analizar_archivo(self, ruta_archivo: str) -> ResultadoAnalisisDinamico:
        """
        Analiza un archivo en un entorno sandbox controlado.
        
        Args:
            ruta_archivo: Ruta del archivo a analizar
            
        Returns:
            ResultadoAnalisisDinamico: Resultado del análisis
        """
        resultado = ResultadoAnalisisDinamico(ruta_archivo)
        directorio_sandbox = None
        monitor = None
        
        try:
            # Validar archivo
            if not os.path.exists(ruta_archivo):
                raise FileNotFoundError(f"El archivo no existe en este reino: {ruta_archivo}")
            
            if not os.path.isfile(ruta_archivo):
                raise ValueError(f"La entidad no es un archivo: {ruta_archivo}")
            
            # Verificar permisos de ejecución o si es un script
            es_ejecutable = os.access(ruta_archivo, os.X_OK)
            es_script = self._es_script(ruta_archivo)
            
            if not (es_ejecutable or es_script):
                self.logger.info(f"El archivo no parece ejecutable: {ruta_archivo}")
                resultado.error_analisis = "Archivo no ejecutable"
                resultado.marcar_completado(False)
                return resultado
            
            self.logger.info(f"Iniciando análisis dinámico del artefacto: {ruta_archivo}")
            
            # Crear sandbox
            directorio_sandbox = self.crear_sandbox()
            
            # Copiar archivo al sandbox
            nombre_archivo = os.path.basename(ruta_archivo)
            ruta_sandbox = os.path.join(directorio_sandbox, nombre_archivo)
            shutil.copy2(ruta_archivo, ruta_sandbox)
            
            # Inicializar monitor
            monitor = MonitorSandbox(directorio_sandbox)
            monitor.iniciar_monitoreo()
            
            # Ejecutar archivo en sandbox
            self._ejecutar_en_sandbox(ruta_sandbox, resultado, directorio_sandbox)
            
            # Detener monitor y recopilar observaciones
            time.sleep(2)  # Esperar a que se registren los cambios finales
            monitor.detener_monitoreo()
            
            # Transferir observaciones al resultado
            resultado.archivos_creados = monitor.archivos_nuevos.copy()
            resultado.procesos_creados = monitor.procesos_nuevos.copy()
            
            # Evaluar comportamiento y riesgo
            resultado.evaluar_riesgo()
            resultado.marcar_completado(True)
            
            mensaje_resultado = (f"Análisis del Minotauro completado: {ruta_archivo} - "
                               f"Riesgo: {resultado.nivel_riesgo}")
            self.logger.info(mensaje_resultado)
        
        except Exception as e:
            error_msg = f"Error en el laberinto de Dédalo: {e}"
            self.logger.error(error_msg)
            resultado.error_analisis = str(e)
            resultado.marcar_completado(False)
        
        finally:
            # Limpieza
            if monitor:
                monitor.detener_monitoreo()
            
            if directorio_sandbox:
                self.limpiar_sandbox(directorio_sandbox)
        
        return resultado
    
    def _es_script(self, ruta_archivo: str) -> bool:
        """
        Determina si el archivo es un script ejecutable.
        
        Args:
            ruta_archivo: Ruta del archivo a verificar
            
        Returns:
            bool: True si es un script
        """
        try:
            extensiones_script = ['.py', '.sh', '.bash', '.pl', '.rb', '.js']
            extension = Path(ruta_archivo).suffix.lower()
            
            if extension in extensiones_script:
                return True
            
            # Verificar shebang
            with open(ruta_archivo, 'rb') as f:
                primeros_bytes = f.read(2)
                if primeros_bytes == b'#!':
                    return True
            
            return False
        
        except Exception:
            return False
    
    def _ejecutar_en_sandbox(self, ruta_archivo: str, resultado: ResultadoAnalisisDinamico, directorio_sandbox: str):
        """
        Ejecuta el archivo en el entorno sandbox.
        
        Args:
            ruta_archivo: Ruta del archivo en el sandbox
            resultado: Objeto resultado para almacenar observaciones
            directorio_sandbox: Directorio del sandbox
        """
        try:
            # Determinar comando de ejecución
            extension = Path(ruta_archivo).suffix.lower()
            
            if extension == '.py':
                comando = ['python3', ruta_archivo]
            elif extension in ['.sh', '.bash']:
                comando = ['bash', ruta_archivo]
            elif os.access(ruta_archivo, os.X_OK):
                comando = [ruta_archivo]
            else:
                # Intentar ejecución directa
                comando = [ruta_archivo]
            
            # Configurar entorno limitado
            env = os.environ.copy()
            env['HOME'] = directorio_sandbox
            env['TMPDIR'] = directorio_sandbox
            env['PATH'] = '/usr/bin:/bin'  # PATH limitado
            
            self.logger.info(f"Ejecutando en el laberinto: {' '.join(comando)}")
            
            # Ejecutar con timeout
            proceso = subprocess.Popen(
                comando,
                cwd=directorio_sandbox,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=os.setsid  # Crear nuevo grupo de proceso
            )
            
            try:
                stdout, stderr = proceso.communicate(timeout=self.timeout_ejecucion)
                resultado.codigo_salida = proceso.returncode
                resultado.stdout_capturado = stdout[:1000]  # Limitar tamaño
                resultado.stderr_capturado = stderr[:1000]
                
                self.logger.info(f"Ejecución completada - Código de salida: {proceso.returncode}")
                
            except subprocess.TimeoutExpired:
                # Terminar proceso y grupo
                os.killpg(os.getpgid(proceso.pid), signal.SIGTERM)
                time.sleep(2)
                try:
                    os.killpg(os.getpgid(proceso.pid), signal.SIGKILL)
                except ProcessLookupError:
                    pass
                
                resultado.error_analisis = f"Timeout después de {self.timeout_ejecucion}s"
                self.logger.warning("Ejecución terminada por timeout")
        
        except Exception as e:
            resultado.error_analisis = f"Error ejecutando archivo: {e}"
            self.logger.error(f"Error en ejecución sandbox: {e}")
    
    def analizar_multiples_archivos(self, rutas_archivos: List[str]) -> List[ResultadoAnalisisDinamico]:
        """
        Analiza múltiples archivos en secuencia.
        
        Args:
            rutas_archivos: Lista de rutas de archivos a analizar
            
        Returns:
            List[ResultadoAnalisisDinamico]: Lista de resultados
        """
        resultados = []
        
        for ruta in rutas_archivos:
            try:
                resultado = self.analizar_archivo(ruta)
                resultados.append(resultado)
                
                # Pausa entre análisis para evitar interferencias
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Error analizando {ruta}: {e}")
                resultado_error = ResultadoAnalisisDinamico(ruta)
                resultado_error.error_analisis = str(e)
                resultado_error.marcar_completado(False)
                resultados.append(resultado_error)
        
        return resultados
    
    def generar_reporte_markdown(self, resultado: ResultadoAnalisisDinamico) -> str:
        """
        Genera un reporte en formato Markdown del análisis dinámico.
        
        Args:
            resultado: Resultado del análisis
            
        Returns:
            str: Reporte en formato Markdown
        """
        md = "# 🏛️ Informe del Laboratorio de Dédalo\n\n"
        md += f"**Artefacto Analizado:** `{resultado.archivo_analizado}`\n"
        md += f"**Timestamp:** {resultado.timestamp_inicio.strftime('%Y-%m-%d %H:%M:%S')}\n"
        md += f"**Duración:** {resultado.tiempo_ejecucion:.2f}s\n"
        md += f"**Estado:** {'✅ Exitoso' if resultado.exitoso else '❌ Fallido'}\n"
        md += f"**Nivel de Riesgo:** {self._emoji_riesgo(resultado.nivel_riesgo)} {resultado.nivel_riesgo}\n\n"
        
        if resultado.error_analisis:
            md += f"**Error:** {resultado.error_analisis}\n\n"
        
        # Estadísticas de comportamiento
        md += "## 📊 Estadísticas del Comportamiento\n\n"
        md += f"- **Procesos Creados:** {len(resultado.procesos_creados)}\n"
        md += f"- **Archivos Creados:** {len(resultado.archivos_creados)}\n"
        md += f"- **Archivos Modificados:** {len(resultado.archivos_modificados)}\n"
        md += f"- **Conexiones de Red:** {len(resultado.conexiones_red)}\n\n"
        
        # Comportamientos sospechosos
        if resultado.comportamientos_sospechosos:
            md += "## ⚠️ Comportamientos Sospechosos\n\n"
            for comportamiento in resultado.comportamientos_sospechosos:
                md += f"- {comportamiento}\n"
            md += "\n"
        
        # Indicadores de malware
        if resultado.indicadores_malware:
            md += "## 🚨 Indicadores de Malware\n\n"
            for indicador in resultado.indicadores_malware:
                md += f"- {indicador}\n"
            md += "\n"
        
        # Archivos creados
        if resultado.archivos_creados:
            md += "## 📁 Archivos Creados\n\n"
            for archivo in resultado.archivos_creados[:10]:  # Limitar a 10
                md += f"- `{archivo}`\n"
            if len(resultado.archivos_creados) > 10:
                md += f"- ... y {len(resultado.archivos_creados) - 10} más\n"
            md += "\n"
        
        # Procesos creados
        if resultado.procesos_creados:
            md += "## ⚙️ Procesos Creados\n\n"
            for proceso in resultado.procesos_creados[:5]:  # Limitar a 5
                md += f"- **PID {proceso['pid']}:** `{proceso['comando']}`\n"
            if len(resultado.procesos_creados) > 5:
                md += f"- ... y {len(resultado.procesos_creados) - 5} más\n"
            md += "\n"
        
        # Salida del proceso
        if resultado.stdout_capturado:
            md += "## 📝 Salida del Proceso\n\n"
            md += f"```\n{resultado.stdout_capturado}\n```\n\n"
        
        if resultado.stderr_capturado:
            md += "## ❌ Errores del Proceso\n\n"
            md += f"```\n{resultado.stderr_capturado}\n```\n\n"
        
        md += "---\n"
        md += "*Análisis realizado por el Laboratorio de Dédalo de Ares Aegis*\n"
        
        return md
    
    def _emoji_riesgo(self, nivel_riesgo: str) -> str:
        """Retorna el emoji correspondiente al nivel de riesgo."""
        emojis = {
            'BAJO': '🟢',
            'MEDIO': '🟡',
            'ALTO': '🟠',
            'CRITICO': '🔴',
            'DESCONOCIDO': '⚪'
        }
        return emojis.get(nivel_riesgo, '⚪')
