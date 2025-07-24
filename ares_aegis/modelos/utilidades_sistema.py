#!/usr/bin/env python3
"""
Creado por DogSoulDev (https://github.com/DogSoulDev)
Todos los derechos reservados. Este código es propietario y confidencial.

Utilidades del Sistema para Kali Linux - Ares Aegis
"""

import os
import stat
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

# Importaciones específicas de Unix (solo para Kali Linux)
try:
    import pwd
    import grp
    UNIX_AVAILABLE = True
except ImportError:
    # En Windows para desarrollo
    pwd = None
    grp = None
    UNIX_AVAILABLE = False

from ..utils.ayuda_logging import configurar_logger_modulo


class UtilidadesSistema:
    """
    Utilidades comunes para operaciones del sistema en Kali Linux.
    Centraliza funciones reutilizables siguiendo el principio DRY.
    """
    
    def __init__(self):
        """Inicializa las utilidades del sistema."""
        self.logger = configurar_logger_modulo("utilidades_sistema")
    
    def leer_contenido_archivo(self, ruta: str, encoding: str = 'utf-8') -> Optional[str]:
        """
        Lee el contenido completo de un archivo de texto.
        
        Args:
            ruta: Ruta del archivo a leer
            encoding: Codificación del archivo (por defecto utf-8)
            
        Returns:
            Contenido del archivo o None si hay error
        """
        try:
            ruta_obj = Path(ruta)
            if not ruta_obj.exists():
                self.logger.warning(f"El pergamino {ruta} no existe en el reino")
                return None
            
            if not ruta_obj.is_file():
                self.logger.warning(f"La ruta {ruta} no es un pergamino válido")
                return None
                
            with open(ruta_obj, 'r', encoding=encoding) as archivo:
                contenido = archivo.read()
                self.logger.debug(f"Pergamino {ruta} leído exitosamente ({len(contenido)} caracteres)")
                return contenido
                
        except PermissionError:
            self.logger.error(f"Permisos insuficientes para leer el pergamino sagrado {ruta}")
            return None
        except UnicodeDecodeError as e:
            self.logger.error(f"Error de codificación al leer {ruta}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error inesperado leyendo {ruta}: {e}")
            return None
    
    def obtener_informacion_permisos(self, ruta: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene información detallada de permisos de un archivo o directorio.
        
        Args:
            ruta: Ruta del archivo/directorio
            
        Returns:
            Diccionario con información de permisos o None si hay error
        """
        try:
            ruta_obj = Path(ruta)
            if not ruta_obj.exists():
                return None
            
            stat_info = ruta_obj.stat()
            
            # Obtener permisos en formato octal
            permisos_octales = oct(stat_info.st_mode)[-3:]
            
            # Obtener información del propietario y grupo
            if UNIX_AVAILABLE:
                try:
                    propietario = pwd.getpwuid(stat_info.st_uid).pw_name
                except KeyError:
                    propietario = str(stat_info.st_uid)
                
                try:
                    grupo = grp.getgrgid(stat_info.st_gid).gr_name
                except KeyError:
                    grupo = str(stat_info.st_gid)
            else:
                # En Windows, usar información básica
                propietario = os.getlogin() if hasattr(os, 'getlogin') else 'user'
                grupo = 'users'
            
            # Convertir permisos a formato legible
            permisos_legibles = stat.filemode(stat_info.st_mode)
            
            informacion = {
                'ruta': str(ruta_obj),
                'permisos_octales': permisos_octales,
                'permisos_legibles': permisos_legibles,
                'propietario': propietario,
                'grupo': grupo,
                'uid': stat_info.st_uid,
                'gid': stat_info.st_gid,
                'tamaño': stat_info.st_size,
                'fecha_modificacion': datetime.fromtimestamp(stat_info.st_mtime),
                'es_directorio': ruta_obj.is_dir(),
                'es_archivo': ruta_obj.is_file(),
                'es_enlace': ruta_obj.is_symlink()
            }
            
            self.logger.debug(f"Información de permisos obtenida para {ruta}")
            return informacion
            
        except Exception as e:
            self.logger.error(f"Error obteniendo información de permisos para {ruta}: {e}")
            return None
    
    def validar_permisos_archivo_critico(self, ruta: str, 
                                       permisos_esperados: str = "644",
                                       propietario_esperado: str = "root") -> Dict[str, Any]:
        """
        Valida si un archivo crítico tiene los permisos correctos.
        
        Args:
            ruta: Ruta del archivo a validar
            permisos_esperados: Permisos en formato octal (ej: "644")
            propietario_esperado: Propietario esperado (ej: "root")
            
        Returns:
            Diccionario con resultado de la validación
        """
        resultado = {
            'ruta': ruta,
            'es_valido': False,
            'problemas': [],
            'informacion': None
        }
        
        info_permisos = self.obtener_informacion_permisos(ruta)
        if not info_permisos:
            resultado['problemas'].append("No se pudo obtener información del archivo")
            return resultado
        
        resultado['informacion'] = info_permisos
        
        # Verificar permisos
        if info_permisos['permisos_octales'] != permisos_esperados:
            problema = (f"Permisos incorrectos: encontrados {info_permisos['permisos_octales']}, "
                       f"esperados {permisos_esperados}")
            resultado['problemas'].append(problema)
        
        # Verificar propietario
        if info_permisos['propietario'] != propietario_esperado:
            problema = (f"Propietario incorrecto: encontrado {info_permisos['propietario']}, "
                       f"esperado {propietario_esperado}")
            resultado['problemas'].append(problema)
        
        # Si no hay problemas, es válido
        resultado['es_valido'] = len(resultado['problemas']) == 0
        
        return resultado
    
    def ejecutar_comando_sistema(self, comando: List[str], timeout: int = 30) -> Dict[str, Any]:
        """
        Ejecuta un comando del sistema de forma segura.
        
        Args:
            comando: Lista con el comando y argumentos
            timeout: Tiempo límite en segundos
            
        Returns:
            Diccionario con resultado de la ejecución
        """
        resultado = {
            'comando': ' '.join(comando),
            'exitoso': False,
            'codigo_salida': -1,
            'stdout': '',
            'stderr': '',
            'tiempo_ejecucion': 0
        }
        
        try:
            inicio = datetime.now()
            
            proceso = subprocess.run(
                comando,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False
            )
            
            fin = datetime.now()
            resultado['tiempo_ejecucion'] = (fin - inicio).total_seconds()
            
            resultado['codigo_salida'] = proceso.returncode
            resultado['stdout'] = proceso.stdout
            resultado['stderr'] = proceso.stderr
            resultado['exitoso'] = proceso.returncode == 0
            
            if resultado['exitoso']:
                self.logger.debug(f"Comando ejecutado exitosamente: {resultado['comando']}")
            else:
                self.logger.warning(f"Comando falló (código {proceso.returncode}): {resultado['comando']}")
            
        except subprocess.TimeoutExpired:
            self.logger.error(f"Comando excedió tiempo límite: {resultado['comando']}")
            resultado['stderr'] = f"Comando excedió tiempo límite de {timeout} segundos"
        except FileNotFoundError:
            self.logger.error(f"Comando no encontrado: {comando[0]}")
            resultado['stderr'] = f"Comando no encontrado: {comando[0]}"
        except Exception as e:
            self.logger.error(f"Error ejecutando comando {resultado['comando']}: {e}")
            resultado['stderr'] = str(e)
        
        return resultado
    
    def verificar_disponibilidad_comando(self, comando: str) -> bool:
        """
        Verifica si un comando está disponible en el sistema.
        
        Args:
            comando: Nombre del comando a verificar
            
        Returns:
            True si el comando está disponible
        """
        try:
            resultado = subprocess.run(
                ['which', comando],
                capture_output=True,
                text=True,
                timeout=5
            )
            disponible = resultado.returncode == 0
            
            if disponible:
                self.logger.debug(f"Comando {comando} está disponible en el sistema")
            else:
                self.logger.warning(f"Comando {comando} no está disponible en el sistema")
            
            return disponible
            
        except Exception as e:
            self.logger.error(f"Error verificando disponibilidad del comando {comando}: {e}")
            return False
    
    def obtener_servicios_systemd(self) -> List[Dict[str, str]]:
        """
        Obtiene lista de servicios systemd activos.
        
        Returns:
            Lista de servicios con su información
        """
        servicios = []
        
        try:
            resultado = self.ejecutar_comando_sistema([
                'systemctl', 'list-units', '--type=service', '--state=active', '--no-pager'
            ])
            
            if resultado['exitoso']:
                lineas = resultado['stdout'].split('\n')
                for linea in lineas:
                    if '.service' in linea and 'loaded active' in linea:
                        partes = linea.split()
                        if len(partes) >= 4:
                            servicio = {
                                'nombre': partes[0],
                                'estado_carga': partes[1],
                                'estado_activo': partes[2],
                                'estado_sub': partes[3],
                                'descripcion': ' '.join(partes[4:]) if len(partes) > 4 else ''
                            }
                            servicios.append(servicio)
            
        except Exception as e:
            self.logger.error(f"Error obteniendo servicios systemd: {e}")
        
        return servicios
    
    def obtener_puertos_escuchando(self) -> List[Dict[str, Any]]:
        """
        Obtiene lista de puertos que están escuchando en el sistema.
        
        Returns:
            Lista de puertos con su información
        """
        puertos = []
        
        try:
            # Usar netstat para obtener puertos escuchando
            resultado = self.ejecutar_comando_sistema([
                'netstat', '-tuln'
            ])
            
            if resultado['exitoso']:
                lineas = resultado['stdout'].split('\n')
                for linea in lineas:
                    if 'LISTEN' in linea:
                        partes = linea.split()
                        if len(partes) >= 4:
                            direccion_local = partes[3]
                            if ':' in direccion_local:
                                partes_direccion = direccion_local.split(':')
                                puerto = partes_direccion[-1]
                                if puerto.isdigit():
                                    puerto_info = {
                                        'protocolo': partes[0].lower(),
                                        'direccion': direccion_local,
                                        'puerto': int(puerto),
                                        'solo_local': direccion_local.startswith('127.') or direccion_local.startswith('::1')
                                    }
                                    puertos.append(puerto_info)
            
        except Exception as e:
            self.logger.error(f"Error obteniendo puertos escuchando: {e}")
        
        return puertos
    
    def obtener_procesos_usuario(self, usuario: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Obtiene procesos en ejecución, opcionalmente filtrados por usuario.
        
        Args:
            usuario: Usuario para filtrar (None para todos)
            
        Returns:
            Lista de procesos con su información
        """
        procesos = []
        
        try:
            comando = ['ps', 'aux']
            if usuario:
                comando.extend(['--user', usuario])
            
            resultado = self.ejecutar_comando_sistema(comando)
            
            if resultado['exitoso']:
                lineas = resultado['stdout'].split('\n')[1:]  # Saltar encabezado
                for linea in lineas:
                    if linea.strip():
                        partes = linea.split(None, 10)  # Dividir en máximo 11 partes
                        if len(partes) >= 11:
                            proceso = {
                                'usuario': partes[0],
                                'pid': int(partes[1]) if partes[1].isdigit() else 0,
                                'cpu_percent': float(partes[2]) if partes[2].replace('.', '').isdigit() else 0.0,
                                'mem_percent': float(partes[3]) if partes[3].replace('.', '').isdigit() else 0.0,
                                'comando': partes[10]
                            }
                            procesos.append(proceso)
            
        except Exception as e:
            self.logger.error(f"Error obteniendo procesos: {e}")
        
        return procesos


# Instancia global para reutilización
utilidades_sistema = UtilidadesSistema()


# Funciones específicas para Kali Linux agregadas por el optimizador
def verificar_herramientas_kali() -> Dict[str, bool]:
    """Verifica disponibilidad de herramientas de Kali Linux"""
    import subprocess
    
    herramientas_disponibles = {}
    for herramienta, ruta in HERRAMIENTAS_KALI.items():
        try:
            resultado = subprocess.run(['which', herramienta], 
                                     capture_output=True, text=True)
            herramientas_disponibles[herramienta] = resultado.returncode == 0
        except:
            herramientas_disponibles[herramienta] = False
    
    return herramientas_disponibles

def ejecutar_comando_kali(comando: str, usar_sudo: bool = False) -> Tuple[int, str, str]:
    """Ejecuta comandos optimizados para Kali Linux"""
    import subprocess
    
    if usar_sudo and os.geteuid() != 0:
        comando = f"sudo {comando}"
    
    try:
        resultado = subprocess.run(
            comando, 
            shell=True, 
            capture_output=True, 
            text=True,
            timeout=30
        )
        return resultado.returncode, resultado.stdout, resultado.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Timeout en comando"
    except Exception as e:
        return -1, "", str(e)

def obtener_info_sistema_kali() -> Dict[str, Any]:
    """Obtiene información específica del sistema Kali Linux"""
    info = {}
    
    try:
        # Verificar si es Kali Linux
        with open('/etc/os-release', 'r') as f:
            contenido = f.read()
            if 'kali' in contenido.lower():
                info['es_kali'] = True
                for linea in contenido.split('\n'):
                    if linea.startswith('PRETTY_NAME='):
                        info['version'] = linea.split('=')[1].strip('"')
            else:
                info['es_kali'] = False
    except:
        info['es_kali'] = False
    
    # Información de permisos
    info['es_root'] = os.geteuid() == 0
    info['uid'] = os.geteuid()
    info['gid'] = os.getegid()
    
    # Herramientas disponibles
    info['herramientas'] = verificar_herramientas_kali()
    
    return info
