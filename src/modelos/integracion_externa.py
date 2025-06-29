"""
Módulo de Integración con Herramientas Externas
Permite la integración con herramientas de seguridad externas como ClamAV.

Este módulo maneja la ejecución de comandos externos y procesa sus resultados
para integrarse con el ecosistema de Ares Aegis.
"""

import os
import subprocess
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from .siem import SIEM, TipoEvento


class ResultadoHerramientaExterna:
    """Clase para representar el resultado de una herramienta externa."""
    
    def __init__(self, herramienta: str, comando: str, exitoso: bool, 
                 salida: str = "", error: str = "", codigo_salida: int = 0):
        """
        Inicializa un resultado de herramienta externa.
        
        Args:
            herramienta: Nombre de la herramienta ejecutada
            comando: Comando ejecutado
            exitoso: Si la ejecución fue exitosa
            salida: Salida estándar del comando
            error: Error estándar del comando
            codigo_salida: Código de salida del proceso
        """
        self.herramienta = herramienta
        self.comando = comando
        self.exitoso = exitoso
        self.salida = salida
        self.error = error
        self.codigo_salida = codigo_salida
        self.timestamp = datetime.now()
    
    def to_markdown(self) -> str:
        """Convierte el resultado a formato Markdown."""
        estado = "✅ EXITOSO" if self.exitoso else "❌ FALLIDO"
        
        markdown = f"### Resultado de Herramienta Externa: {self.herramienta}\n\n"
        markdown += f"- **Estado:** {estado}\n"
        markdown += f"- **Comando:** `{self.comando}`\n"
        markdown += f"- **Código de Salida:** {self.codigo_salida}\n"
        markdown += f"- **Timestamp:** {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        if self.salida:
            markdown += "**Salida:**\n```\n"
            markdown += self.salida[:1000]  # Limitar longitud para legibilidad
            if len(self.salida) > 1000:
                markdown += "\n... (salida truncada)"
            markdown += "\n```\n\n"
        
        if self.error:
            markdown += "**Error:**\n```\n"
            markdown += self.error[:500]  # Limitar longitud de errores
            if len(self.error) > 500:
                markdown += "\n... (error truncado)"
            markdown += "\n```\n\n"
        
        return markdown


class ClamAVIntegracion:
    """Integración específica con ClamAV."""
    
    def __init__(self, siem: SIEM):
        """
        Inicializa la integración con ClamAV.
        
        Args:
            siem: Instancia del SIEM para logging
        """
        self.siem = siem
        self.logger = logging.getLogger(__name__)
        self.disponible = self._verificar_disponibilidad()
        
        if self.disponible:
            self.siem.log_evento(TipoEvento.SISTEMA_EVENTO, "ClamAV detectado y disponible")
        else:
            self.siem.log_evento(TipoEvento.ADVERTENCIA, "ClamAV no está disponible")
    
    def _verificar_disponibilidad(self) -> bool:
        """Verifica si ClamAV está instalado y disponible."""
        try:
            resultado = subprocess.run(['which', 'clamscan'], 
                                     capture_output=True, text=True, timeout=5)
            return resultado.returncode == 0
        except Exception:
            return False
    
    def escanear_archivo(self, ruta_archivo: str) -> ResultadoHerramientaExterna:
        """
        Escanea un archivo con ClamAV.
        
        Args:
            ruta_archivo: Ruta del archivo a escanear
            
        Returns:
            Resultado del escaneo con ClamAV
        """
        if not self.disponible:
            return ResultadoHerramientaExterna(
                "ClamAV", "clamscan", False,
                error="ClamAV no está disponible en el sistema"
            )
        
        comando = ['clamscan', '--no-summary', '--infected', ruta_archivo]
        comando_str = ' '.join(comando)
        
        try:
            self.logger.info(f"Ejecutando ClamAV en archivo: {ruta_archivo}")
            
            resultado = subprocess.run(
                comando,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos timeout
            )
            
            # ClamAV devuelve código 0 si no hay virus, 1 si encuentra virus
            exitoso = resultado.returncode in [0, 1]
            
            resultado_obj = ResultadoHerramientaExterna(
                "ClamAV", comando_str, exitoso,
                resultado.stdout, resultado.stderr, resultado.returncode
            )
            
            # Parsear resultado para detectar amenazas
            amenazas = self._parsear_salida_clamscan(resultado.stdout)
            if amenazas:
                self.siem.log_evento(TipoEvento.AMENAZA_DETECTADA,
                                   f"ClamAV detectó amenaza en: {ruta_archivo}",
                                   {"amenazas": amenazas})
            
            return resultado_obj
            
        except subprocess.TimeoutExpired:
            error_msg = f"Timeout ejecutando ClamAV en {ruta_archivo}"
            self.logger.error(error_msg)
            return ResultadoHerramientaExterna(
                "ClamAV", comando_str, False, error=error_msg
            )
        except Exception as e:
            error_msg = f"Error ejecutando ClamAV: {e}"
            self.logger.error(error_msg)
            return ResultadoHerramientaExterna(
                "ClamAV", comando_str, False, error=error_msg
            )
    
    def escanear_directorio(self, ruta_directorio: str, recursivo: bool = True) -> ResultadoHerramientaExterna:
        """
        Escanea un directorio con ClamAV.
        
        Args:
            ruta_directorio: Ruta del directorio a escanear
            recursivo: Si escanear recursivamente
            
        Returns:
            Resultado del escaneo con ClamAV
        """
        if not self.disponible:
            return ResultadoHerramientaExterna(
                "ClamAV", "clamscan", False,
                error="ClamAV no está disponible en el sistema"
            )
        
        comando = ['clamscan', '--no-summary']
        if recursivo:
            comando.append('--recursive')
        comando.extend(['--infected', ruta_directorio])
        
        comando_str = ' '.join(comando)
        
        try:
            self.logger.info(f"Ejecutando ClamAV en directorio: {ruta_directorio}")
            
            resultado = subprocess.run(
                comando,
                capture_output=True,
                text=True,
                timeout=1800  # 30 minutos timeout para directorios
            )
            
            exitoso = resultado.returncode in [0, 1]
            
            resultado_obj = ResultadoHerramientaExterna(
                "ClamAV", comando_str, exitoso,
                resultado.stdout, resultado.stderr, resultado.returncode
            )
            
            # Parsear resultado para detectar amenazas
            amenazas = self._parsear_salida_clamscan(resultado.stdout)
            if amenazas:
                self.siem.log_evento(TipoEvento.AMENAZA_DETECTADA,
                                   f"ClamAV detectó {len(amenazas)} amenaza(s) en: {ruta_directorio}",
                                   {"amenazas": amenazas})
            
            return resultado_obj
            
        except subprocess.TimeoutExpired:
            error_msg = f"Timeout ejecutando ClamAV en directorio {ruta_directorio}"
            self.logger.error(error_msg)
            return ResultadoHerramientaExterna(
                "ClamAV", comando_str, False, error=error_msg
            )
        except Exception as e:
            error_msg = f"Error ejecutando ClamAV: {e}"
            self.logger.error(error_msg)
            return ResultadoHerramientaExterna(
                "ClamAV", comando_str, False, error=error_msg
            )
    
    def actualizar_base_datos(self) -> ResultadoHerramientaExterna:
        """
        Actualiza la base de datos de virus de ClamAV.
        
        Returns:
            Resultado de la actualización
        """
        if not self.disponible:
            return ResultadoHerramientaExterna(
                "ClamAV", "freshclam", False,
                error="ClamAV no está disponible en el sistema"
            )
        
        comando = ['freshclam']
        comando_str = ' '.join(comando)
        
        try:
            self.logger.info("Actualizando base de datos de ClamAV")
            
            resultado = subprocess.run(
                comando,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutos timeout
            )
            
            exitoso = resultado.returncode == 0
            
            resultado_obj = ResultadoHerramientaExterna(
                "ClamAV", comando_str, exitoso,
                resultado.stdout, resultado.stderr, resultado.returncode
            )
            
            if exitoso:
                self.siem.log_evento(TipoEvento.SISTEMA_EVENTO, "Base de datos de ClamAV actualizada")
            else:
                self.siem.log_evento(TipoEvento.ERROR, "Error actualizando base de datos de ClamAV",
                                   {"error": resultado.stderr})
            
            return resultado_obj
            
        except subprocess.TimeoutExpired:
            error_msg = "Timeout actualizando base de datos de ClamAV"
            self.logger.error(error_msg)
            return ResultadoHerramientaExterna(
                "ClamAV", comando_str, False, error=error_msg
            )
        except Exception as e:
            error_msg = f"Error actualizando base de datos de ClamAV: {e}"
            self.logger.error(error_msg)
            return ResultadoHerramientaExterna(
                "ClamAV", comando_str, False, error=error_msg
            )
    
    def _parsear_salida_clamscan(self, salida: str) -> List[str]:
        """Parsea la salida de clamscan para extraer amenazas detectadas."""
        amenazas = []
        
        for linea in salida.split('\n'):
            if 'FOUND' in linea:
                # Formato típico: /ruta/archivo: Virus.Name FOUND
                match = re.search(r'(.+): (.+) FOUND', linea)
                if match:
                    archivo, virus = match.groups()
                    amenazas.append(f"{virus} en {archivo}")
        
        return amenazas


class IntegracionExterna:
    """Gestor principal para integraciones con herramientas externas."""
    
    def __init__(self, siem: SIEM):
        """
        Inicializa el gestor de integraciones externas.
        
        Args:
            siem: Instancia del SIEM para logging
        """
        self.siem = siem
        self.logger = logging.getLogger(__name__)
        
        # Inicializar integraciones disponibles
        self.clamav = ClamAVIntegracion(siem)
        
        # Verificar otras herramientas comunes
        self.herramientas_disponibles = self._verificar_herramientas_disponibles()
        
        self.siem.log_evento(TipoEvento.SISTEMA_EVENTO, "Integración externa inicializada",
                           {"herramientas_disponibles": list(self.herramientas_disponibles.keys())})
    
    def _verificar_herramientas_disponibles(self) -> Dict[str, bool]:
        """Verifica qué herramientas externas están disponibles."""
        herramientas = {
            "clamscan": self.clamav.disponible,
            "nmap": self._verificar_comando("nmap"),
            "netstat": self._verificar_comando("netstat"),
            "ss": self._verificar_comando("ss"),
            "lsof": self._verificar_comando("lsof"),
            "chkrootkit": self._verificar_comando("chkrootkit"),
            "rkhunter": self._verificar_comando("rkhunter"),
            "lynis": self._verificar_comando("lynis")
        }
        
        return herramientas
    
    def _verificar_comando(self, comando: str) -> bool:
        """Verifica si un comando está disponible en el sistema."""
        try:
            resultado = subprocess.run(['which', comando], 
                                     capture_output=True, text=True, timeout=5)
            return resultado.returncode == 0
        except Exception:
            return False
    
    def ejecutar_comando_personalizado(self, comando: List[str], 
                                     timeout: int = 60) -> ResultadoHerramientaExterna:
        """
        Ejecuta un comando personalizado de forma segura.
        
        Args:
            comando: Lista con el comando y argumentos
            timeout: Timeout en segundos
            
        Returns:
            Resultado de la ejecución
        """
        if not comando:
            return ResultadoHerramientaExterna(
                "Personalizado", "", False, error="Comando vacío"
            )
        
        comando_str = ' '.join(comando)
        herramienta = comando[0]
        
        # Verificaciones de seguridad básicas
        comandos_peligrosos = ['rm', 'dd', 'mkfs', 'fdisk', 'format']
        if any(cmd in comando[0] for cmd in comandos_peligrosos):
            return ResultadoHerramientaExterna(
                herramienta, comando_str, False,
                error="Comando no permitido por seguridad"
            )
        
        try:
            self.logger.info(f"Ejecutando comando personalizado: {comando_str}")
            
            resultado = subprocess.run(
                comando,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            exitoso = resultado.returncode == 0
            
            resultado_obj = ResultadoHerramientaExterna(
                herramienta, comando_str, exitoso,
                resultado.stdout, resultado.stderr, resultado.returncode
            )
            
            self.siem.log_evento(TipoEvento.SISTEMA_EVENTO,
                               f"Comando personalizado ejecutado: {herramienta}",
                               {"exitoso": exitoso, "codigo_salida": resultado.returncode})
            
            return resultado_obj
            
        except subprocess.TimeoutExpired:
            error_msg = f"Timeout ejecutando comando: {comando_str}"
            self.logger.error(error_msg)
            return ResultadoHerramientaExterna(
                herramienta, comando_str, False, error=error_msg
            )
        except Exception as e:
            error_msg = f"Error ejecutando comando: {e}"
            self.logger.error(error_msg)
            return ResultadoHerramientaExterna(
                herramienta, comando_str, False, error=error_msg
            )
    
    def escanear_puertos(self, objetivo: str = "localhost", 
                        puertos: str = "1-1000") -> ResultadoHerramientaExterna:
        """
        Realiza un escaneo de puertos usando nmap si está disponible.
        
        Args:
            objetivo: Objetivo del escaneo (por defecto localhost)
            puertos: Rango de puertos a escanear
            
        Returns:
            Resultado del escaneo de puertos
        """
        if not self.herramientas_disponibles.get("nmap", False):
            return ResultadoHerramientaExterna(
                "nmap", "nmap", False,
                error="nmap no está disponible en el sistema"
            )
        
        comando = ['nmap', '-sS', '-p', puertos, objetivo]
        return self.ejecutar_comando_personalizado(comando, timeout=300)
    
    def listar_conexiones_red(self) -> ResultadoHerramientaExterna:
        """
        Lista las conexiones de red activas usando netstat o ss.
        
        Returns:
            Resultado del listado de conexiones
        """
        if self.herramientas_disponibles.get("ss", False):
            comando = ['ss', '-tuln']
            return self.ejecutar_comando_personalizado(comando)
        elif self.herramientas_disponibles.get("netstat", False):
            comando = ['netstat', '-tuln']
            return self.ejecutar_comando_personalizado(comando)
        else:
            return ResultadoHerramientaExterna(
                "netstat/ss", "netstat/ss", False,
                error="ni netstat ni ss están disponibles"
            )
    
    def generar_reporte_herramientas_disponibles(self) -> str:
        """
        Genera un reporte en Markdown de las herramientas disponibles.
        
        Returns:
            String con el reporte en formato Markdown
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        markdown = f"# Reporte de Herramientas Externas\n\n"
        markdown += f"**Fecha:** {timestamp}\n\n"
        
        markdown += "## Estado de Herramientas\n\n"
        
        for herramienta, disponible in self.herramientas_disponibles.items():
            estado = "✅ Disponible" if disponible else "❌ No disponible"
            markdown += f"- **{herramienta}:** {estado}\n"
        
        markdown += "\n## Descripciones\n\n"
        
        descripciones = {
            "clamscan": "Antivirus ClamAV para escaneo de malware",
            "nmap": "Escáner de puertos y servicios de red",
            "netstat": "Herramienta para mostrar conexiones de red",
            "ss": "Herramienta moderna para mostrar conexiones de red",
            "lsof": "Lista archivos abiertos y conexiones",
            "chkrootkit": "Detector de rootkits",
            "rkhunter": "Detector avanzado de rootkits",
            "lynis": "Auditor de seguridad del sistema"
        }
        
        for herramienta, descripcion in descripciones.items():
            disponible = self.herramientas_disponibles.get(herramienta, False)
            if disponible:
                markdown += f"### {herramienta}\n"
                markdown += f"{descripcion}\n\n"
        
        return markdown
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas de las integraciones externas."""
        total_herramientas = len(self.herramientas_disponibles)
        herramientas_disponibles = sum(self.herramientas_disponibles.values())
        
        return {
            "total_herramientas": total_herramientas,
            "herramientas_disponibles": herramientas_disponibles,
            "porcentaje_disponibilidad": (herramientas_disponibles / total_herramientas) * 100,
            "clamav_disponible": self.clamav.disponible,
            "lista_herramientas": self.herramientas_disponibles
        }
