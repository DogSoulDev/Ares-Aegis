#!/usr/bin/env python3
"""
Ares Aegis - Controlador de Cuarentena Optimizado
Controlador especializado para gestionar operaciones de cuarentena

Creado por DogSoulDev (https://github.com/DogSoulDev)
Todos los derechos reservados. Este código es propietario y confidencial.

Versión: 4.0.0
"""

import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path

from ..modelo.modelo_gestor_cuarentena import GestorCuarentenaAvanzado
from ..modelo.modelo_siem import SIEM, TipoEvento
from ..utils.utils_ayuda_logging import configurar_logger_modulo
from ..utils.utils_controlador_cuarentena import (
    AnalizadorForenseCuarentena, GestorEstadisticasCuarentena,
    GeneradorReportesCuarentena, HelperOperacionesCuarentena
)


class ControladorCuarentena:
    """Controlador especializado para operaciones de cuarentena."""
    
    def __init__(self, gestor_cuarentena: GestorCuarentenaAvanzado, siem: SIEM):
        """
        Inicializar el controlador de cuarentena.
        
        Args:
            gestor_cuarentena: Instancia del gestor de cuarentena
            siem: Instancia del SIEM para registro de eventos
        """
        self.gestor_cuarentena = gestor_cuarentena
        self.siem = siem
        self.logger = configurar_logger_modulo("controlador_cuarentena")
        
        # Estado del controlador
        self.archivos_procesados = []
        self.alertas_cuarentena = []
        self.lock = threading.Lock()
        
        # Configuración
        self.configuracion = {
            'analisis_automatico': True,
            'notificar_cuarentena': True,
            'backup_antes_cuarentena': True,
            'periodo_retencion_dias': 30
        }
        
        # Componentes especializados
        self.analizador_forense = AnalizadorForenseCuarentena()
        self.gestor_estadisticas = GestorEstadisticasCuarentena()
        self.generador_reportes = GeneradorReportesCuarentena()
        self.helper_operaciones = HelperOperacionesCuarentena()
        
        self.logger.info("Controlador de Cuarentena inicializado")
    
    def cuarentenar_archivo(self, ruta_archivo: str, razon: str = "Archivo sospechoso", 
                           origen_deteccion: str = "Manual") -> Dict[str, Any]:
        """
        Cuarentenar un archivo específico.
        
        Args:
            ruta_archivo: Ruta del archivo a cuarentenar
            razon: Razón de la cuarentena
            origen_deteccion: Origen de la detección
            
        Returns:
            Dict[str, Any]: Resultado de la operación
        """
        try:
            if not Path(ruta_archivo).exists():
                raise FileNotFoundError(f"El archivo no existe: {ruta_archivo}")
            
            self.logger.info(f"Iniciando cuarentena de archivo: {ruta_archivo}")
            
            # Cuarentenar usando el gestor
            archivo_id = self.gestor_cuarentena.poner_en_cuarentena(
                ruta_archivo, origen_deteccion, razon
            )
            
            if archivo_id:
                # Registrar estadísticas
                self.gestor_estadisticas.registrar_operacion('archivos_cuarentenados')
                
                with self.lock:
                    self.archivos_procesados.append({
                        'archivo_id': archivo_id,
                        'ruta_original': ruta_archivo,
                        'accion': 'cuarentenado',
                        'timestamp': datetime.now(),
                        'razon': razon
                    })
                
                resultado = {
                    'exitoso': True,
                    'archivo_id': archivo_id,
                    'ruta_original': ruta_archivo,
                    'timestamp': datetime.now().isoformat(),
                    'razon': razon,
                    'origen_deteccion': origen_deteccion
                }
                
                # Registrar en SIEM
                if self.siem:
                    self.siem.registrar_evento(
                        "ARCHIVO_CUARENTENADO",
                        f"Archivo cuarentenado: {ruta_archivo}",
                        resultado,
                        "MEDIO"
                    )
                
                # Programar análisis automático si está habilitado
                if self.configuracion.get('analisis_automatico', False):
                    self._programar_analisis_automatico(archivo_id)
                
                self.logger.info(f"Archivo cuarentenado exitosamente: {archivo_id}")
                return resultado
            
            else:
                resultado_error = {
                    'exitoso': False,
                    'error': 'No se pudo cuarentenar el archivo',
                    'ruta_archivo': ruta_archivo
                }
                
                # Registrar en SIEM
                if self.siem:
                    self.siem.registrar_evento(
                        "ERROR_SISTEMA",
                        f"Error cuarentenando archivo: {ruta_archivo}",
                        resultado_error,
                        "ALTO"
                    )
                
                return resultado_error
        
        except Exception as e:
            self.logger.error(f"Error cuarentenando archivo {ruta_archivo}: {e}")
            resultado_error = {
                'exitoso': False,
                'error': str(e),
                'ruta_archivo': ruta_archivo,
                'timestamp': datetime.now().isoformat()
            }
            
            # Registrar en SIEM
            if self.siem:
                self.siem.registrar_evento(
                    "ERROR_SISTEMA",
                    f"Error cuarentenando archivo: {ruta_archivo} - {e}",
                    resultado_error,
                    "ALTO"
                )
            
            return resultado_error
    
    def restaurar_archivo(self, archivo_id: str, ruta_destino: Optional[str] = None) -> Dict[str, Any]:
        """
        Restaurar un archivo de la cuarentena.
        
        Args:
            archivo_id: ID del archivo en cuarentena
            ruta_destino: Ruta de destino (opcional, usa la original por defecto)
            
        Returns:
            Dict[str, Any]: Resultado de la operación
        """
        try:
            self.logger.info(f"Iniciando restauración de archivo: {archivo_id}")
            
            # Validar operación usando el helper
            validacion = self.helper_operaciones.validar_operacion_restauracion(
                archivo_id, 
                self.gestor_cuarentena
            )
            
            if not validacion['valido']:
                return {
                    'exitoso': False,
                    'error': validacion.get('error', 'Validación fallida'),
                    'advertencias': validacion.get('advertencias', [])
                }
            
            archivo_info = validacion['archivo_info']
            ruta_original = archivo_info.get('ruta_original', '')
            destino_final = ruta_destino or ruta_original
            
            # Restaurar usando el gestor
            resultado_restauracion = self.gestor_cuarentena.restaurar_archivo(archivo_id)
            
            if resultado_restauracion:
                # Registrar estadísticas
                self.gestor_estadisticas.registrar_operacion('archivos_restaurados')
                
                with self.lock:
                    self.archivos_procesados.append({
                        'archivo_id': archivo_id,
                        'accion': 'restaurado',
                        'timestamp': datetime.now(),
                        'ruta_destino': destino_final
                    })
                
                resultado = {
                    'exitoso': True,
                    'archivo_id': archivo_id,
                    'ruta_destino': destino_final,
                    'timestamp': datetime.now().isoformat(),
                    'accion': 'restaurado'
                }
                
                # Registrar en SIEM
                if self.siem:
                    self.siem.registrar_evento(
                        "ARCHIVO_RESTAURADO",
                        f"Archivo restaurado: {archivo_id} -> {destino_final}",
                        resultado,
                        "MEDIO"
                    )
                
                self.logger.info(f"Archivo restaurado exitosamente: {archivo_id}")
                return resultado
            
            else:
                resultado_error = {
                    'exitoso': False,
                    'error': 'No se pudo restaurar el archivo',
                    'archivo_id': archivo_id
                }
                
                return resultado_error
        
        except Exception as e:
            self.logger.error(f"Error restaurando archivo {archivo_id}: {e}")
            return {
                'exitoso': False,
                'error': str(e),
                'archivo_id': archivo_id,
                'timestamp': datetime.now().isoformat()
            }
    
    def eliminar_archivo_cuarentena(self, archivo_id: str, confirmar: bool = False) -> Dict[str, Any]:
        """
        Eliminar permanentemente un archivo de la cuarentena.
        
        Args:
            archivo_id: ID del archivo en cuarentena
            confirmar: Confirmación de eliminación permanente
            
        Returns:
            Dict[str, Any]: Resultado de la operación
        """
        try:
            if not confirmar:
                return {
                    'exitoso': False,
                    'error': 'Se requiere confirmación para eliminación permanente',
                    'archivo_id': archivo_id
                }
            
            self.logger.info(f"Iniciando eliminación permanente: {archivo_id}")
            
            # Obtener metadatos antes de eliminar
            metadatos = self.obtener_metadatos_archivo(archivo_id)
            
            # Eliminar usando el gestor
            resultado_eliminacion = self.gestor_cuarentena.eliminar_archivo(archivo_id)
            
            if resultado_eliminacion:
                # Registrar estadísticas
                self.gestor_estadisticas.registrar_operacion('archivos_eliminados')
                
                with self.lock:
                    self.archivos_procesados.append({
                        'archivo_id': archivo_id,
                        'accion': 'eliminado_permanente',
                        'timestamp': datetime.now(),
                        'metadatos_originales': metadatos
                    })
                
                resultado = {
                    'exitoso': True,
                    'archivo_id': archivo_id,
                    'timestamp': datetime.now().isoformat(),
                    'accion': 'eliminado_permanente'
                }
                
                # Registrar en SIEM
                if self.siem:
                    self.siem.registrar_evento(
                        "ARCHIVO_ELIMINADO",
                        f"Archivo eliminado permanentemente: {archivo_id}",
                        resultado,
                        "ALTO"
                    )
                
                self.logger.info(f"Archivo eliminado permanentemente: {archivo_id}")
                return resultado
            
            else:
                return {
                    'exitoso': False,
                    'error': 'No se pudo eliminar el archivo',
                    'archivo_id': archivo_id
                }
        
        except Exception as e:
            self.logger.error(f"Error eliminando archivo {archivo_id}: {e}")
            return {
                'exitoso': False,
                'error': str(e),
                'archivo_id': archivo_id,
                'timestamp': datetime.now().isoformat()
            }
    
    def obtener_lista_cuarentena(self) -> List[Dict[str, Any]]:
        """
        Obtener lista completa de archivos en cuarentena.
        
        Returns:
            List[Dict[str, Any]]: Lista de archivos en cuarentena
        """
        try:
            metadatos_lista = self.gestor_cuarentena.obtener_lista_cuarentena()
            # Convertir metadatos a diccionarios
            return [metadato.to_dict() if hasattr(metadato, 'to_dict') else metadato.__dict__ 
                   for metadato in metadatos_lista]
        
        except Exception as e:
            self.logger.error(f"Error obteniendo lista de cuarentena: {e}")
            return []
    
    def listar_archivos_cuarentena(self) -> List[Dict[str, Any]]:
        """
        Alias para obtener_lista_cuarentena.
        
        Returns:
            List[Dict[str, Any]]: Lista de archivos en cuarentena
        """
        return self.obtener_lista_cuarentena()
    
    def obtener_metadatos_archivo(self, archivo_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtener metadatos de un archivo específico en cuarentena.
        
        Args:
            archivo_id: ID del archivo
            
        Returns:
            Optional[Dict[str, Any]]: Metadatos del archivo o None si no existe
        """
        try:
            # Buscar archivo en la lista de cuarentena usando hash_sha256
            lista_archivos = self.gestor_cuarentena.obtener_lista_cuarentena()
            for archivo in lista_archivos:
                if hasattr(archivo, 'hash_sha256') and archivo.hash_sha256 == archivo_id:
                    return archivo.to_dict() if hasattr(archivo, 'to_dict') else archivo.__dict__
            return None
        
        except Exception as e:
            self.logger.error(f"Error obteniendo metadatos de {archivo_id}: {e}")
            return None
    
    def analizar_archivo_cuarentena(self, archivo_id: str) -> Dict[str, Any]:
        """
        Realizar análisis forense de un archivo en cuarentena.
        
        Args:
            archivo_id: ID del archivo a analizar
            
        Returns:
            Dict[str, Any]: Resultado del análisis
        """
        try:
            self.logger.info(f"Iniciando análisis forense: {archivo_id}")
            
            # Realizar análisis usando el analizador especializado
            resultado_analisis = self.analizador_forense.analizar_archivo_forense(
                archivo_id, 
                self.gestor_cuarentena
            )
            
            if 'error' not in resultado_analisis:
                # Registrar estadísticas
                self.gestor_estadisticas.registrar_operacion('analyses_realizados')
                
                with self.lock:
                    self.archivos_procesados.append({
                        'archivo_id': archivo_id,
                        'accion': 'analizado',
                        'timestamp': datetime.now(),
                        'resultado_analisis': resultado_analisis
                    })
                
                resultado = {
                    'exitoso': True,
                    'archivo_id': archivo_id,
                    'timestamp': datetime.now().isoformat(),
                    'resultado_analisis': resultado_analisis
                }
                
                # Registrar en SIEM
                if self.siem:
                    amenazas_detectadas = resultado_analisis.get('amenazas_detectadas', [])
                    if amenazas_detectadas:
                        nivel = "ALTO"
                        mensaje = f"Amenazas detectadas en {archivo_id}: {len(amenazas_detectadas)}"
                    else:
                        nivel = "INFO"
                        mensaje = f"Análisis completado para {archivo_id}: sin amenazas"
                    
                    self.siem.registrar_evento(
                        "ANALISIS_COMPLETADO",
                        mensaje,
                        resultado,
                        nivel
                    )
                
                self.logger.info(f"Análisis forense completado: {archivo_id}")
                return resultado
            
            else:
                return {
                    'exitoso': False,
                    'error': resultado_analisis.get('error', 'Error en análisis'),
                    'archivo_id': archivo_id
                }
        
        except Exception as e:
            self.logger.error(f"Error en análisis de {archivo_id}: {e}")
            return {
                'exitoso': False,
                'error': str(e),
                'archivo_id': archivo_id,
                'timestamp': datetime.now().isoformat()
            }
    
    def _programar_analisis_automatico(self, archivo_id: str):
        """Programar análisis automático en hilo separado."""
        def analisis_automatico():
            time.sleep(5)  # Esperar un poco antes del análisis
            self.analizar_archivo_cuarentena(archivo_id)
        
        hilo_analisis = threading.Thread(target=analisis_automatico, daemon=True)
        hilo_analisis.start()
    
    def obtener_estadisticas_cuarentena(self) -> Dict[str, Any]:
        """
        Obtener estadísticas completas de la cuarentena.
        
        Returns:
            Dict[str, Any]: Estadísticas de cuarentena
        """
        try:
            # Usar el gestor especializado de estadísticas
            estadisticas_completas = self.gestor_estadisticas.obtener_estadisticas_completas(self.gestor_cuarentena)
            
            # Agregar estadísticas específicas del controlador
            with self.lock:
                operaciones_24h = len([p for p in self.archivos_procesados 
                                     if p['timestamp'] > datetime.now() - timedelta(hours=24)])
                total_alertas = len(self.alertas_cuarentena)
            
            estadisticas_completas.update({
                'operaciones_24h': operaciones_24h,
                'total_alertas': total_alertas,
                'configuracion_activa': self.configuracion.copy()
            })
            
            return estadisticas_completas
        
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas: {e}")
            return {'error': str(e)}
    
    def limpiar_cuarentena(self, criterios: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Limpiar archivos de la cuarentena según criterios.
        
        Args:
            criterios: Criterios de limpieza (días antigüedad, estado, etc.)
            
        Returns:
            Dict[str, Any]: Resultado de la limpieza
        """
        try:
            # Validar criterios usando el helper
            criterios = criterios or {}
            validacion = self.helper_operaciones.validar_criterios_limpieza(criterios)
            
            if not validacion['valido']:
                return {
                    'exitoso': False,
                    'error': 'Criterios de limpieza inválidos',
                    'detalles': validacion['criterios_validos']
                }
            
            criterios_norm = validacion['criterios_normalizados']
            
            # Ejecutar limpieza
            dias_antiguedad = criterios_norm.get('dias_antiguedad', 30)
            limite_tiempo = datetime.now() - timedelta(days=dias_antiguedad)
            archivos_lista = self.obtener_lista_cuarentena()
            
            archivos_eliminados = 0
            errores = []
            
            for archivo in archivos_lista:
                try:
                    fecha_cuarentena = archivo.get('fecha_cuarentena', '')
                    if isinstance(fecha_cuarentena, str):
                        fecha_cuarentena = datetime.fromisoformat(
                            fecha_cuarentena.replace('Z', '+00:00')
                        )
                    
                    if fecha_cuarentena < limite_tiempo:
                        hash_archivo = archivo.get('hash_sha256', '')
                        resultado = self.eliminar_archivo_cuarentena(
                            hash_archivo, 
                            confirmar=criterios_norm.get('confirmar_eliminacion', True)
                        )
                        
                        if resultado.get('exitoso'):
                            archivos_eliminados += 1
                        else:
                            errores.append(f"Error eliminando {hash_archivo}: {resultado.get('error')}")
                
                except Exception as e:
                    hash_archivo = archivo.get('hash_sha256', 'desconocido')
                    errores.append(f"Error procesando archivo {hash_archivo}: {str(e)}")
            
            resultado = {
                'exitoso': True,
                'archivos_eliminados': archivos_eliminados,
                'errores': errores,
                'criterios_aplicados': criterios_norm,
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"Limpieza completada: {archivos_eliminados} archivos eliminados")
            return resultado
        
        except Exception as e:
            self.logger.error(f"Error en limpieza de cuarentena: {e}")
            return {
                'exitoso': False,
                'error': str(e)
            }
    
    def configurar_cuarentena(self, config: Dict[str, Any]):
        """
        Configurar parámetros del controlador de cuarentena.
        
        Args:
            config: Configuración nueva
        """
        try:
            self.configuracion.update(config)
            self.logger.info(f"Configuración actualizada: {config}")
        
        except Exception as e:
            self.logger.error(f"Error actualizando configuración: {e}")
    
    def generar_reporte_cuarentena(self) -> str:
        """
        Generar reporte completo de cuarentena.
        
        Returns:
            str: Reporte formateado
        """
        try:
            # Usar el generador especializado de reportes
            return self.generador_reportes.generar_reporte_completo(
                self.gestor_cuarentena, 
                self.gestor_estadisticas
            )
        
        except Exception as e:
            self.logger.error(f"Error generando reporte: {e}")
            return f"Error generando reporte de cuarentena: {str(e)}"
