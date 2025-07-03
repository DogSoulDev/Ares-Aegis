#!/usr/bin/env python3
"""
Integración Externa - Ares Aegis
Módulo para integración con herramientas externas como ClamAV

Los mensajes de este módulo siguen el estilo mitológico inspirado en Ares y la Égida.

Autor: DogSoulDev
Versión: 2.0.0 - La Alianza de los Oráculos
"""

import subprocess
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from ..utilidades.ayuda_logging import configurar_logger_modulo
from ..utilidades.validaciones import validar_ruta_archivo


class IntegracionClamAV:
    """Integración con ClamAV - El Oráculo Externo de las Sombras Corruptas."""
    
    def __init__(self):
        """Inicializa la conexión con el oráculo ClamAV."""
        self.logger = configurar_logger_modulo("integracion_clamav")
        self.clamav_disponible = self._verificar_clamav()
        
        if self.clamav_disponible:
            self.logger.info("El oráculo ClamAV ha respondido al llamado divino")
        else:
            self.logger.warning("El oráculo ClamAV permanece en silencio en los vientos del reino")
    
    def _verificar_clamav(self) -> bool:
        """Verifica si ClamAV está disponible en el sistema divino."""
        try:
            # Buscar clamscan en el reino de los ejecutables
            resultado = subprocess.run(
                ['which', 'clamscan'], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            return resultado.returncode == 0
        except Exception as e:
            self.logger.error(f"Error invocando al oráculo ClamAV: {e}")
            return False
    
    def escanear_archivo(self, ruta_archivo: str) -> Dict[str, Any]:
        """
        Consulta al oráculo ClamAV sobre las sombras que acechan en un archivo.
        
        Args:
            ruta_archivo: Sendero hacia el archivo a examinar
            
        Returns:
            Dict con los resultados de la consulta al oráculo
        """
        if not self.clamav_disponible:
            return {
                'exitoso': False,
                'amenaza_detectada': False,
                'mensaje': 'El oráculo ClamAV no responde desde los vientos etéreos',
                'detalles': 'ClamAV no está instalado o disponible en este reino'
            }
        
        if not validar_ruta_archivo(ruta_archivo):
            return {
                'exitoso': False,
                'amenaza_detectada': False,
                'mensaje': 'El sendero especificado no conduce a archivo alguno',
                'detalles': f'Ruta inválida: {ruta_archivo}'
            }
        
        try:
            # Invocar al oráculo ClamAV para que examine el archivo
            comando = ['clamscan', '--no-summary', '--infected', ruta_archivo]
            
            resultado = subprocess.run(
                comando,
                capture_output=True,
                text=True,
                timeout=60  # Los oráculos necesitan tiempo para sus visiones
            )
            
            # Interpretar la respuesta del oráculo
            if resultado.returncode == 0:
                return {
                    'exitoso': True,
                    'amenaza_detectada': False,
                    'mensaje': 'El oráculo declara que no hay sombras en este archivo',
                    'detalles': 'El archivo ha sido examinado y se encuentra libre de corrupción',
                    'salida_oraculo': resultado.stdout.strip()
                }
            elif resultado.returncode == 1:
                # El oráculo ha detectado una sombra corrupta
                amenaza_detectada = 'FOUND' in resultado.stdout
                
                if amenaza_detectada:
                    # Extraer el nombre de la sombra detectada
                    lineas = resultado.stdout.strip().split('\n')
                    nombre_amenaza = "Sombra no identificada"
                    
                    for linea in lineas:
                        if 'FOUND' in linea:
                            partes = linea.split(': ')
                            if len(partes) > 1:
                                nombre_amenaza = partes[1].replace(' FOUND', '')
                            break
                    
                    return {
                        'exitoso': True,
                        'amenaza_detectada': True,
                        'mensaje': f'¡El oráculo ha detectado una sombra corrupta! Nombre: {nombre_amenaza}',
                        'detalles': f'Una entidad malévola se oculta en el archivo: {nombre_amenaza}',
                        'nombre_amenaza': nombre_amenaza,
                        'salida_oraculo': resultado.stdout.strip()
                    }
                else:
                    return {
                        'exitoso': True,
                        'amenaza_detectada': False,
                        'mensaje': 'El oráculo ha completado su examen sin detectar sombras',
                        'detalles': 'Archivo examinado completamente',
                        'salida_oraculo': resultado.stdout.strip()
                    }
            else:
                # Error en la consulta al oráculo
                return {
                    'exitoso': False,
                    'amenaza_detectada': False,
                    'mensaje': 'El oráculo ClamAV ha enviado señales de tormenta',
                    'detalles': f'Error del oráculo: {resultado.stderr.strip()}',
                    'codigo_error': resultado.returncode
                }
        
        except subprocess.TimeoutExpired:
            return {
                'exitoso': False,
                'amenaza_detectada': False,
                'mensaje': 'El oráculo ClamAV no ha respondido en tiempo divino',
                'detalles': 'La consulta al oráculo ha excedido el tiempo de espera celestial'
            }
        
        except Exception as e:
            self.logger.error(f"Error consultando al oráculo ClamAV: {e}")
            return {
                'exitoso': False,
                'amenaza_detectada': False,
                'mensaje': 'Una tormenta inesperada ha perturbado la comunicación con el oráculo',
                'detalles': str(e)
            }
    
    def escanear_directorio(self, ruta_directorio: str) -> Dict[str, Any]:
        """
        Solicita al oráculo ClamAV que examine todo un reino de archivos.
        
        Args:
            ruta_directorio: Sendero del reino a examinar
            
        Returns:
            Dict con los resultados de la consulta masiva al oráculo
        """
        if not self.clamav_disponible:
            return {
                'exitoso': False,
                'archivos_examinados': 0,
                'amenazas_detectadas': 0,
                'mensaje': 'El oráculo ClamAV no responde desde los vientos etéreos',
                'detalles': []
            }
        
        if not os.path.isdir(ruta_directorio):
            return {
                'exitoso': False,
                'archivos_examinados': 0,
                'amenazas_detectadas': 0,
                'mensaje': 'El sendero especificado no conduce a reino alguno',
                'detalles': [f'Ruta inválida: {ruta_directorio}']
            }
        
        try:
            # Invocar al oráculo para examinar todo el reino
            comando = ['clamscan', '-r', '--infected', ruta_directorio]
            
            resultado = subprocess.run(
                comando,
                capture_output=True,
                text=True,
                timeout=300  # Los reinos grandes requieren más tiempo de los oráculos
            )
            
            # Analizar la respuesta del oráculo
            lineas = resultado.stdout.strip().split('\n')
            amenazas = []
            archivos_examinados = 0
            
            for linea in lineas:
                if 'FOUND' in linea:
                    amenazas.append(linea)
                elif 'Scanned files:' in linea:
                    try:
                        archivos_examinados = int(linea.split(':')[1].strip())
                    except:
                        pass
            
            return {
                'exitoso': True,
                'archivos_examinados': archivos_examinados,
                'amenazas_detectadas': len(amenazas),
                'mensaje': f'El oráculo ha completado el examen del reino. Sombras detectadas: {len(amenazas)}',
                'detalles': amenazas,
                'salida_completa': resultado.stdout.strip()
            }
        
        except subprocess.TimeoutExpired:
            return {
                'exitoso': False,
                'archivos_examinados': 0,
                'amenazas_detectadas': 0,
                'mensaje': 'El oráculo ClamAV requiere más tiempo para examinar este vasto reino',
                'detalles': ['La consulta al oráculo ha excedido el tiempo celestial permitido']
            }
        
        except Exception as e:
            self.logger.error(f"Error en escaneo masivo con ClamAV: {e}")
            return {
                'exitoso': False,
                'archivos_examinados': 0,
                'amenazas_detectadas': 0,
                'mensaje': 'Una tormenta ha interrumpido la comunicación con el oráculo',
                'detalles': [str(e)]
            }
    
    def actualizar_firmas(self) -> Dict[str, Any]:
        """
        Solicita al oráculo ClamAV que renueve su conocimiento de las sombras.
        
        Returns:
            Dict con el resultado de la actualización
        """
        if not self.clamav_disponible:
            return {
                'exitoso': False,
                'mensaje': 'El oráculo ClamAV no responde para recibir nueva sabiduría',
                'detalles': 'ClamAV no está disponible en este reino'
            }
        
        try:
            # Verificar si freshclam está disponible
            resultado_which = subprocess.run(
                ['which', 'freshclam'], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            
            if resultado_which.returncode != 0:
                return {
                    'exitoso': False,
                    'mensaje': 'El ritual de renovación del conocimiento no está disponible',
                    'detalles': 'freshclam no se encuentra en los senderos del sistema'
                }
            
            # Ejecutar freshclam para actualizar las firmas
            resultado = subprocess.run(
                ['freshclam'],
                capture_output=True,
                text=True,
                timeout=300  # La sabiduría nueva toma tiempo en llegar
            )
            
            if resultado.returncode == 0:
                return {
                    'exitoso': True,
                    'mensaje': 'El oráculo ha renovado su sabiduría sobre las sombras del mundo',
                    'detalles': 'Las firmas de amenazas han sido actualizadas desde los templos celestiales',
                    'salida_actualizacion': resultado.stdout.strip()
                }
            else:
                return {
                    'exitoso': False,
                    'mensaje': 'Los vientos han traído dificultades para renovar la sabiduría del oráculo',
                    'detalles': resultado.stderr.strip(),
                    'codigo_error': resultado.returncode
                }
        
        except subprocess.TimeoutExpired:
            return {
                'exitoso': False,
                'mensaje': 'El ritual de renovación requiere más tiempo del permitido por los dioses',
                'detalles': 'La actualización ha excedido el tiempo celestial'
            }
        
        except Exception as e:
            self.logger.error(f"Error actualizando firmas de ClamAV: {e}")
            return {
                'exitoso': False,
                'mensaje': 'Una tormenta inesperada ha interrumpido el ritual de renovación',
                'detalles': str(e)
            }
    
    def obtener_informacion_version(self) -> Dict[str, Any]:
        """
        Consulta la versión y estado del oráculo ClamAV.
        
        Returns:
            Dict con información del oráculo
        """
        if not self.clamav_disponible:
            return {
                'disponible': False,
                'mensaje': 'El oráculo ClamAV permanece en el silencio etéreo',
                'version': 'Desconocida'
            }
        
        try:
            resultado = subprocess.run(
                ['clamscan', '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if resultado.returncode == 0:
                version = resultado.stdout.strip()
                return {
                    'disponible': True,
                    'mensaje': 'El oráculo ClamAV responde con sabiduría',
                    'version': version,
                    'detalles': 'Oráculo operativo y listo para consultas'
                }
            else:
                return {
                    'disponible': False,
                    'mensaje': 'El oráculo existe pero sus palabras son confusas',
                    'version': 'Error al obtener versión',
                    'error': resultado.stderr.strip()
                }
        
        except Exception as e:
            self.logger.error(f"Error obteniendo información de ClamAV: {e}")
            return {
                'disponible': False,
                'mensaje': 'Una tormenta impide la comunicación con el oráculo',
                'version': 'Error de comunicación',
                'detalles': str(e)
            }


class IntegracionExterna:
    """Gestor central para todas las integraciones con oráculos externos."""
    
    def __init__(self, siem=None):
        """Inicializa el gestor de oráculos externos."""
        self.logger = configurar_logger_modulo("integraciones_externas")
        self.siem = siem
        self.clamav = IntegracionClamAV()
        
        self.logger.info("El consejo de oráculos externos ha sido convocado")
    
    def obtener_estado_integraciones(self) -> Dict[str, Dict[str, Any]]:
        """
        Obtiene el estado de todos los oráculos externos.
        
        Returns:
            Dict con el estado de cada integración
        """
        return {
            'clamav': self.clamav.obtener_informacion_version(),
            'resumen': {
                'oracles_disponibles': 1 if self.clamav.clamav_disponible else 0,
                'oracles_total': 1,
                'mensaje': 'Los oráculos del Olimpo están siendo consultados'
            }
        }
    
    def escanear_con_todos_oracles(self, ruta: str) -> Dict[str, Dict[str, Any]]:
        """
        Consulta a todos los oráculos disponibles sobre un archivo o directorio.
        
        Args:
            ruta: Sendero a examinar
            
        Returns:
            Dict con resultados de todos los oráculos
        """
        resultados = {}
        
        # Consultar al oráculo ClamAV
        if os.path.isfile(ruta):
            resultados['clamav'] = self.clamav.escanear_archivo(ruta)
        elif os.path.isdir(ruta):
            resultados['clamav'] = self.clamav.escanear_directorio(ruta)
        else:
            resultados['clamav'] = {
                'exitoso': False,
                'mensaje': 'El sendero no conduce a archivo ni reino conocido',
                'detalles': f'Ruta inválida: {ruta}'
            }
        
        # Resumen general
        amenazas_totales = 0
        oracles_exitosos = 0
        
        for oraculo, resultado in resultados.items():
            if resultado.get('exitoso', False):
                oracles_exitosos += 1
                if resultado.get('amenaza_detectada', False):
                    amenazas_totales += 1
                elif 'amenazas_detectadas' in resultado:
                    amenazas_totales += resultado['amenazas_detectadas']
        
        resultados['resumen'] = {
            'oracles_consultados': len(resultados) - 1,  # Excluir el resumen mismo
            'oracles_exitosos': oracles_exitosos,
            'amenazas_total': amenazas_totales,
            'mensaje': f'Los oráculos han hablado: {amenazas_totales} sombras detectadas'
        }
        
        return resultados
    
    def actualizar_todos_oracles(self) -> Dict[str, Dict[str, Any]]:
        """
        Solicita a todos los oráculos que renueven su sabiduría.
        
        Returns:
            Dict con resultados de actualización de cada oráculo
        """
        resultados = {
            'clamav': self.clamav.actualizar_firmas()
        }
        
        actualizaciones_exitosas = sum(
            1 for resultado in resultados.values() 
            if resultado.get('exitoso', False)
        )
        
        resultados['resumen'] = {
            'oracles_actualizados': actualizaciones_exitosas,
            'oracles_total': len(resultados) - 1,
            'mensaje': f'Sabiduría renovada en {actualizaciones_exitosas} oráculos del Olimpo'
        }
        
        return resultados
