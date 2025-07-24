#!/usr/bin/env python3
"""
Analizadores Unificados de Ares Aegis
Todos los analizadores de archivos, cadenas, comportamiento, etc. en un solo módulo

Creado por DogSoulDev
Versión: 4.0.0
"""

import os
import re
import hashlib
import subprocess
import time
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime


class AnalizadorArchivos:
    """Analizador unificado de archivos y contenido"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.firmas_malware = self._cargar_firmas()
        self.extensiones_peligrosas = {
            '.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', 
            '.js', '.jar', '.ps1', '.sh', '.bin', '.dll'
        }
    
    def _cargar_firmas(self) -> List[str]:
        """Cargar firmas de malware desde archivo"""
        try:
            ruta_firmas = Path(__file__).parent.parent.parent / "configuracion" / "firmas.txt"
            if ruta_firmas.exists():
                with open(ruta_firmas, 'r', encoding='utf-8') as f:
                    return [linea.strip() for linea in f if linea.strip()]
            return []
        except Exception as e:
            self.logger.warning(f"No se pudieron cargar firmas: {e}")
            return []
    
    def analizar_archivo(self, ruta_archivo: str) -> Dict[str, Any]:
        """Análisis completo de un archivo"""
        if not os.path.exists(ruta_archivo):
            return {"error": "Archivo no encontrado"}
        
        try:
            resultado = {
                "archivo": ruta_archivo,
                "tamaño": os.path.getsize(ruta_archivo),
                "extension": Path(ruta_archivo).suffix.lower(),
                "hash_md5": self._calcular_hash(ruta_archivo, "md5"),
                "hash_sha256": self._calcular_hash(ruta_archivo, "sha256"),
                "es_ejecutable": self._es_ejecutable(ruta_archivo),
                "extension_peligrosa": Path(ruta_archivo).suffix.lower() in self.extensiones_peligrosas,
                "firmas_detectadas": [],
                "cadenas_sospechosas": [],
                "nivel_riesgo": "bajo"
            }
            
            # Análisis de contenido si el archivo no es demasiado grande
            if resultado["tamaño"] < 50 * 1024 * 1024:  # 50MB
                resultado["firmas_detectadas"] = self._buscar_firmas(ruta_archivo)
                resultado["cadenas_sospechosas"] = self._analizar_cadenas(ruta_archivo)
            
            # Calcular nivel de riesgo
            resultado["nivel_riesgo"] = self._calcular_riesgo(resultado)
            
            return resultado
            
        except Exception as e:
            self.logger.error(f"Error analizando archivo {ruta_archivo}: {e}")
            return {"error": str(e)}
    
    def _calcular_hash(self, ruta_archivo: str, algoritmo: str) -> str:
        """Calcular hash de archivo"""
        try:
            hash_obj = hashlib.new(algoritmo)
            with open(ruta_archivo, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_obj.update(chunk)
            return hash_obj.hexdigest()
        except Exception:
            return ""
    
    def _es_ejecutable(self, ruta_archivo: str) -> bool:
        """Verificar si es un archivo ejecutable"""
        return os.access(ruta_archivo, os.X_OK) or Path(ruta_archivo).suffix.lower() in self.extensiones_peligrosas
    
    def _buscar_firmas(self, ruta_archivo: str) -> List[str]:
        """Buscar firmas de malware en el archivo"""
        firmas_encontradas = []
        try:
            with open(ruta_archivo, 'rb') as f:
                contenido = f.read(1024 * 1024)  # Leer primer MB
                contenido_str = contenido.decode('utf-8', errors='ignore').lower()
                
                for firma in self.firmas_malware:
                    if firma.lower() in contenido_str:
                        firmas_encontradas.append(firma)
                        
        except Exception as e:
            self.logger.warning(f"Error buscando firmas en {ruta_archivo}: {e}")
        
        return firmas_encontradas
    
    def _analizar_cadenas(self, ruta_archivo: str) -> List[str]:
        """Analizar cadenas sospechosas en el archivo"""
        cadenas_sospechosas = []
        patrones_peligrosos = [
            r'eval\s*\(',
            r'exec\s*\(',
            r'system\s*\(',
            r'shell_exec\s*\(',
            r'base64_decode\s*\(',
            r'bash\s+-i',
            r'/bin/sh\s+-c',
            r'wget\s+',
            r'curl\s+',
            r'nc\s+-',
            r'/bin/sh',
            r'rm\s+-rf',
            r'mktemp'
        ]
        
        try:
            with open(ruta_archivo, 'rb') as f:
                contenido = f.read(1024 * 1024)  # Leer primer MB
                contenido_str = contenido.decode('utf-8', errors='ignore')
                
                for patron in patrones_peligrosos:
                    if re.search(patron, contenido_str, re.IGNORECASE):
                        cadenas_sospechosas.append(patron)
                        
        except Exception as e:
            self.logger.warning(f"Error analizando cadenas en {ruta_archivo}: {e}")
        
        return cadenas_sospechosas
    
    def _calcular_riesgo(self, resultado: Dict[str, Any]) -> str:
        """Calcular nivel de riesgo basado en los resultados"""
        puntos_riesgo = 0
        
        if resultado["extension_peligrosa"]:
            puntos_riesgo += 3
        if resultado["es_ejecutable"]:
            puntos_riesgo += 2
        if resultado["firmas_detectadas"]:
            puntos_riesgo += 5
        if resultado["cadenas_sospechosas"]:
            puntos_riesgo += len(resultado["cadenas_sospechosas"])
        
        if puntos_riesgo >= 7:
            return "alto"
        elif puntos_riesgo >= 4:
            return "medio"
        else:
            return "bajo"


class AnalizadorComportamiento:
    """Analizador de comportamiento de procesos y red"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.procesos_monitoreados = {}
        self.conexiones_sospechosas = []
    
    def analizar_proceso(self, pid: int) -> Dict[str, Any]:
        """Analizar comportamiento de un proceso usando herramientas del sistema"""
        try:
            # Usar comandos del sistema para obtener información del proceso
            resultado = {
                "pid": pid,
                "nombre": "desconocido",
                "cpu_percent": 0.0,
                "memoria_mb": 0.0,
                "conexiones_red": 0,
                "archivos_abiertos": 0,
                "tiempo_creacion": datetime.now(),
                "sospechoso": False,
                "razones": []
            }
            
            # Obtener información usando ps (disponible en Kali Linux)
            try:
                ps_cmd = f"ps -p {pid} -o pid,comm,%cpu,%mem,etime --no-headers"
                ps_output = subprocess.check_output(ps_cmd, shell=True, text=True).strip()
                if ps_output:
                    parts = ps_output.split()
                    if len(parts) >= 4:
                        resultado["nombre"] = parts[1]
                        resultado["cpu_percent"] = float(parts[2])
                        resultado["memoria_mb"] = float(parts[3]) * 1024 / 100  # Aproximación
            except subprocess.CalledProcessError:
                pass
            
            # Verificar conexiones de red usando netstat
            try:
                netstat_cmd = f"netstat -anp 2>/dev/null | grep {pid} | wc -l"
                netstat_output = subprocess.check_output(netstat_cmd, shell=True, text=True).strip()
                resultado["conexiones_red"] = int(netstat_output) if netstat_output.isdigit() else 0
            except subprocess.CalledProcessError:
                pass
            
            # Verificar archivos abiertos usando lsof
            try:
                lsof_cmd = f"lsof -p {pid} 2>/dev/null | wc -l"
                lsof_output = subprocess.check_output(lsof_cmd, shell=True, text=True).strip()
                resultado["archivos_abiertos"] = int(lsof_output) if lsof_output.isdigit() else 0
            except subprocess.CalledProcessError:
                pass
            
            # Analizar comportamiento sospechoso
            if resultado["cpu_percent"] > 80:
                resultado["sospechoso"] = True
                resultado["razones"].append("Alto uso de CPU")
            
            if resultado["memoria_mb"] > 1000:
                resultado["sospechoso"] = True
                resultado["razones"].append("Alto uso de memoria")
            
            if resultado["conexiones_red"] > 50:
                resultado["sospechoso"] = True
                resultado["razones"].append("Muchas conexiones de red")
            
            return resultado
            
        except Exception as e:
            self.logger.error(f"Error analizando proceso {pid}: {e}")
            return {"error": str(e)}
    
    def analizar_conexiones_red(self) -> List[Dict[str, Any]]:
        """Analizar conexiones de red sospechosas usando herramientas del sistema"""
        conexiones_sospechosas = []
        
        try:
            # Usar netstat para obtener conexiones establecidas
            netstat_cmd = "netstat -tuln 2>/dev/null | grep ESTABLISHED"
            netstat_output = subprocess.check_output(netstat_cmd, shell=True, text=True)
            
            for linea in netstat_output.split('\n'):
                if linea.strip():
                    partes = linea.split()
                    if len(partes) >= 5:
                        local_addr = partes[3]
                        remote_addr = partes[4]
                        
                        if ':' in remote_addr:
                            ip_remota = remote_addr.split(':')[0]
                            puerto_remoto = remote_addr.split(':')[1]
                            
                            # Verificar si la IP es sospechosa
                            if self._es_ip_sospechosa(ip_remota):
                                conexiones_sospechosas.append({
                                    "ip_local": local_addr.split(':')[0] if ':' in local_addr else local_addr,
                                    "puerto_local": local_addr.split(':')[1] if ':' in local_addr else "0",
                                    "ip_remota": ip_remota,
                                    "puerto_remoto": puerto_remoto,
                                    "estado": "ESTABLISHED",
                                    "pid": "desconocido"
                                })
        
        except Exception as e:
            self.logger.error(f"Error analizando conexiones: {e}")
        
        return conexiones_sospechosas
    
    def _es_ip_sospechosa(self, ip: str) -> bool:
        """Verificar si una IP es sospechosa"""
        # IPs privadas no son sospechosas por defecto
        if ip.startswith(('192.168.', '10.', '172.16.')):
            return False
        
        # Cargar lista de IPs maliciosas
        try:
            ruta_ips = Path(__file__).parent.parent.parent / "recursos" / "ips_maliciosas_local.txt"
            if ruta_ips.exists():
                with open(ruta_ips, 'r') as f:
                    ips_maliciosas = [linea.strip() for linea in f if linea.strip()]
                    return ip in ips_maliciosas
        except Exception:
            pass
        
        return False


class AnalizadorDinamico:
    """Analizador dinámico para ejecución en entornos controlados"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.sandbox_activo = False
    
    def ejecutar_en_sandbox(self, ruta_archivo: str, tiempo_ejecucion: int = 30) -> Dict[str, Any]:
        """Ejecutar archivo en entorno controlado"""
        if not os.path.exists(ruta_archivo):
            return {"error": "Archivo no encontrado"}
        
        resultado = {
            "archivo": ruta_archivo,
            "tiempo_ejecucion": tiempo_ejecucion,
            "procesos_creados": [],
            "archivos_modificados": [],
            "conexiones_red": [],
            "registro_modificado": False,
            "comportamiento_malicioso": False
        }
        
        # NOTA: Para un entorno real, aquí se implementaría la ejecución en sandbox
        # Por seguridad, esta implementación solo simula el análisis
        self.logger.warning("Análisis dinámico en modo simulación - no se ejecuta el archivo")
        
        return resultado


# Clase unificada que combina todos los analizadores
class AnalizadoresUnificados:
    """Clase principal que unifica todos los analizadores"""
    
    def __init__(self):
        self.analizador_archivos = AnalizadorArchivos()
        self.analizador_comportamiento = AnalizadorComportamiento()
        self.analizador_dinamico = AnalizadorDinamico()
        self.logger = logging.getLogger(__name__)
    
    def analisis_completo(self, ruta_archivo: str) -> Dict[str, Any]:
        """Realizar análisis completo de un archivo"""
        resultado = {
            "archivo": ruta_archivo,
            "timestamp": datetime.now().isoformat(),
            "analisis_estatico": self.analizador_archivos.analizar_archivo(ruta_archivo),
            "analisis_dinamico": self.analizador_dinamico.ejecutar_en_sandbox(ruta_archivo),
            "riesgo_final": "bajo"
        }
        
        # Determinar riesgo final
        if resultado["analisis_estatico"].get("nivel_riesgo") == "alto":
            resultado["riesgo_final"] = "alto"
        elif resultado["analisis_estatico"].get("nivel_riesgo") == "medio":
            resultado["riesgo_final"] = "medio"
        
        return resultado


