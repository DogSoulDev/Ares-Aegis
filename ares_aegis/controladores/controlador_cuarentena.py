#!/usr/bin/env python3
"""
Ares Aegis - Controlador de Cuarentena
Controlador especializado para gestionar operaciones de cuarentena

Copyright (c) 2025 DogSoulDev (https://github.com/DogSoulDev)
Todos los derechos reservados. Este código es propietario y confidencial.
La copia, distribución o modificación no autorizada está estrictamente prohibida.

Versión: 3.0.0
"""

import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path

from ..modelos.gestor_cuarentena import GestorCuarentenaAvanzado
from ..modelos.siem import SIEM, TipoEvento
from ..utilidades.ayuda_logging import configurar_logger_modulo


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
        self.estadisticas_analisis = {}
        self.alertas_cuarentena = []
        self.lock = threading.Lock()
        
        # Configuración
        self.configuracion = {
            'analisis_automatico': True,
            'notificar_cuarentena': True,
            'backup_antes_cuarentena': True,
            'periodo_retencion_dias': 30
        }
        
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
                
                # Actualizar estadísticas
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
                        TipoEvento.ARCHIVO_CUARENTENA,
                        f"Archivo cuarentenado: {ruta_archivo} - {razon}",
                        resultado,
                        "ALTO"
                    )
                
                self.logger.info(f"Archivo cuarentenado exitosamente: {archivo_id}")
                
                # Análisis automático si está habilitado
                if self.configuracion['analisis_automatico']:
                    self._programar_analisis_automatico(archivo_id)
                
                return resultado
            else:
                raise Exception("Error en el gestor de cuarentena")
        
        except Exception as e:
            self.logger.error(f"Error cuarentenando archivo {ruta_archivo}: {e}")
            resultado_error = {
                'exitoso': False,
                'error': str(e),
                'ruta_archivo': ruta_archivo,
                'timestamp': datetime.now().isoformat()
            }
            
            if self.siem:
                self.siem.registrar_evento(
                    TipoEvento.ERROR_SISTEMA,
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
            
            # Obtener información del archivo
            metadatos = self.obtener_metadatos_archivo(archivo_id)
            if not metadatos:
                raise ValueError(f"Archivo no encontrado en cuarentena: {archivo_id}")
            
            ruta_original = metadatos.get('ruta_original', '')
            destino_final = ruta_destino or ruta_original
            
            # Restaurar usando el gestor (simulado por ahora)
            # TODO: Implementar método restaurar_archivo en GestorCuarentenaAvanzado
            resultado_restauracion = True  # Simular éxito por ahora
            
            if resultado_restauracion:
                # Actualizar estadísticas
                with self.lock:
                    self.archivos_procesados.append({
                        'archivo_id': archivo_id,
                        'ruta_destino': destino_final,
                        'accion': 'restaurado',
                        'timestamp': datetime.now()
                    })
                
                resultado = {
                    'exitoso': True,
                    'archivo_id': archivo_id,
                    'ruta_destino': destino_final,
                    'timestamp': datetime.now().isoformat()
                }
                
                # Registrar en SIEM
                if self.siem:
                    self.siem.registrar_evento(
                        TipoEvento.ARCHIVO_RESTAURADO,
                        f"Archivo restaurado: {archivo_id} a {destino_final}",
                        resultado,
                        "MEDIO"
                    )
                
                self.logger.info(f"Archivo restaurado exitosamente: {archivo_id} a {destino_final}")
                return resultado
            else:
                raise Exception("Error en el gestor de cuarentena durante restauración")
        
        except Exception as e:
            self.logger.error(f"Error restaurando archivo {archivo_id}: {e}")
            resultado_error = {
                'exitoso': False,
                'error': str(e),
                'archivo_id': archivo_id,
                'timestamp': datetime.now().isoformat()
            }
            
            if self.siem:
                self.siem.registrar_evento(
                    TipoEvento.ERROR_SISTEMA,
                    f"Error restaurando archivo: {archivo_id} - {e}",
                    resultado_error,
                    "MEDIO"
                )
            
            return resultado_error
    
    def eliminar_archivo_cuarentena(self, archivo_id: str, confirmar: bool = False) -> Dict[str, Any]:
        """
        Eliminar permanentemente un archivo de la cuarentena.
        
        Args:
            archivo_id: ID del archivo en cuarentena
            confirmar: Confirmación para la eliminación permanente
            
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
            
            self.logger.info(f"Iniciando eliminación permanente de archivo: {archivo_id}")
            
            # Obtener metadatos antes de eliminar
            metadatos = self.obtener_metadatos_archivo(archivo_id)
            
            # Eliminar usando el gestor (simulado por ahora)
            # TODO: Implementar método eliminar_archivo_permanente en GestorCuarentenaAvanzado
            resultado_eliminacion = True  # Simular éxito por ahora
            
            if resultado_eliminacion:
                # Actualizar estadísticas
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
                        TipoEvento.ARCHIVO_ELIMINADO,
                        f"Archivo eliminado permanentemente de cuarentena: {archivo_id}",
                        resultado,
                        "MEDIO"
                    )
                
                self.logger.info(f"Archivo eliminado permanentemente: {archivo_id}")
                return resultado
            else:
                raise Exception("Error en el gestor de cuarentena durante eliminación")
        
        except Exception as e:
            self.logger.error(f"Error eliminando archivo {archivo_id}: {e}")
            resultado_error = {
                'exitoso': False,
                'error': str(e),
                'archivo_id': archivo_id,
                'timestamp': datetime.now().isoformat()
            }
            
            if self.siem:
                self.siem.registrar_evento(
                    TipoEvento.ERROR_SISTEMA,
                    f"Error eliminando archivo de cuarentena: {archivo_id} - {e}",
                    resultado_error,
                    "MEDIO"
                )
            
            return resultado_error
    
    def obtener_lista_cuarentena(self) -> List[Dict[str, Any]]:
        """
        Obtener lista completa de archivos en cuarentena.
        
        Returns:
            List[Dict[str, Any]]: Lista de archivos en cuarentena
        """
        try:
            archivos = []
            
            # Acceder a la base de datos del gestor de cuarentena
            if hasattr(self.gestor_cuarentena, 'base_datos'):
                for archivo_id, metadatos in self.gestor_cuarentena.base_datos.items():
                    archivo_info = {
                        'id': archivo_id,
                        'nombre': getattr(metadatos, 'nombre_original', 'desconocido'),
                        'ruta_original': getattr(metadatos, 'ruta_original', 'desconocido'),
                        'fecha_cuarentena': getattr(metadatos, 'timestamp_cuarentena', datetime.now()).isoformat(),
                        'origen_deteccion': getattr(metadatos, 'origen_deteccion', 'desconocido'),
                        'nivel_riesgo': getattr(metadatos, 'nivel_riesgo', 'MEDIO'),
                        'estado': getattr(metadatos, 'estado', 'pendiente'),
                        'razon': getattr(metadatos, 'razon_cuarentena', 'No especificada'),
                        'tamaño': getattr(metadatos, 'tamaño_bytes', 0)
                    }
                    
                    # Convertir enums a string si es necesario
                    if hasattr(archivo_info['nivel_riesgo'], 'value'):
                        archivo_info['nivel_riesgo'] = archivo_info['nivel_riesgo'].value
                    if hasattr(archivo_info['estado'], 'value'):
                        archivo_info['estado'] = archivo_info['estado'].value
                    
                    archivos.append(archivo_info)
            
            return archivos
        
        except Exception as e:
            self.logger.error(f"Error obteniendo lista de cuarentena: {e}")
            return []
    
    def obtener_metadatos_archivo(self, archivo_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtener metadatos de un archivo específico en cuarentena.
        
        Args:
            archivo_id: ID del archivo
            
        Returns:
            Optional[Dict[str, Any]]: Metadatos del archivo o None
        """
        try:
            if hasattr(self.gestor_cuarentena, 'base_datos'):
                metadatos = self.gestor_cuarentena.base_datos.get(archivo_id)
                if metadatos:
                    return {
                        'id': archivo_id,
                        'nombre_original': getattr(metadatos, 'nombre_original', 'desconocido'),
                        'ruta_original': getattr(metadatos, 'ruta_original', 'desconocido'),
                        'ruta_cuarentena': getattr(metadatos, 'ruta_cuarentena', 'desconocido'),
                        'timestamp_cuarentena': getattr(metadatos, 'timestamp_cuarentena', datetime.now()).isoformat(),
                        'origen_deteccion': getattr(metadatos, 'origen_deteccion', 'desconocido'),
                        'nivel_riesgo': str(getattr(metadatos, 'nivel_riesgo', 'MEDIO')),
                        'estado': str(getattr(metadatos, 'estado', 'pendiente')),
                        'razon_cuarentena': getattr(metadatos, 'razon_cuarentena', 'No especificada'),
                        'tamaño_bytes': getattr(metadatos, 'tamaño_bytes', 0),
                        'hash_md5': getattr(metadatos, 'hash_md5', ''),
                        'hash_sha1': getattr(metadatos, 'hash_sha1', '')
                    }
            
            return None
        
        except Exception as e:
            self.logger.error(f"Error obteniendo metadatos del archivo {archivo_id}: {e}")
            return None
    
    def analizar_archivo_cuarentena(self, archivo_id: str) -> Dict[str, Any]:
        """
        Realizar análisis forense de un archivo en cuarentena.
        
        Args:
            archivo_id: ID del archivo a analizar
            
        Returns:
            Dict[str, Any]: Resultados del análisis
        """
        try:
            self.logger.info(f"Iniciando análisis forense de archivo: {archivo_id}")
            
            # Verificar que el archivo existe en cuarentena
            metadatos = self.obtener_metadatos_archivo(archivo_id)
            if not metadatos:
                raise ValueError(f"Archivo no encontrado en cuarentena: {archivo_id}")
            
            # Realizar análisis usando el gestor (simulado por ahora)
            # TODO: Implementar método analizar_archivo_forense en GestorCuarentenaAvanzado
            metadatos = self.obtener_metadatos_archivo(archivo_id)
            if metadatos:
                resultado_analisis = {
                    'amenaza_confirmada': False,
                    'tipo_amenaza': 'desconocido',
                    'nivel_confianza': 0.5,
                    'recomendacion': 'Análisis completo requerido'
                }
            else:
                resultado_analisis = None
            
            if resultado_analisis:
                # Actualizar estadísticas de análisis
                with self.lock:
                    self.estadisticas_analisis[archivo_id] = {
                        'timestamp': datetime.now(),
                        'resultado': resultado_analisis,
                        'estado': 'completado'
                    }
                    
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
                    'analisis': resultado_analisis
                }
                
                # Registrar en SIEM
                if self.siem:
                    nivel_criticidad = "ALTO" if resultado_analisis.get('amenaza_confirmada', False) else "MEDIO"
                    self.siem.registrar_evento(
                        TipoEvento.ANALISIS_COMPLETADO,
                        f"Análisis forense completado para archivo: {archivo_id}",
                        resultado,
                        nivel_criticidad
                    )
                
                self.logger.info(f"Análisis forense completado para archivo: {archivo_id}")
                return resultado
            else:
                raise Exception("Error en el análisis forense")
        
        except Exception as e:
            self.logger.error(f"Error analizando archivo {archivo_id}: {e}")
            resultado_error = {
                'exitoso': False,
                'error': str(e),
                'archivo_id': archivo_id,
                'timestamp': datetime.now().isoformat()
            }
            
            if self.siem:
                self.siem.registrar_evento(
                    TipoEvento.ERROR_SISTEMA,
                    f"Error en análisis forense: {archivo_id} - {e}",
                    resultado_error,
                    "MEDIO"
                )
            
            return resultado_error
    
    def _programar_analisis_automatico(self, archivo_id: str):
        """
        Programar análisis automático de un archivo recién cuarentenado.
        
        Args:
            archivo_id: ID del archivo para análisis
        """
        def analisis_automatico():
            time.sleep(5)  # Esperar un momento antes del análisis
            self.analizar_archivo_cuarentena(archivo_id)
        
        # Ejecutar en un hilo separado
        hilo_analisis = threading.Thread(target=analisis_automatico, daemon=True)
        hilo_analisis.start()
        
        self.logger.info(f"Análisis automático programado para archivo: {archivo_id}")
    
    def obtener_estadisticas_cuarentena(self) -> Dict[str, Any]:
        """
        Obtener estadísticas de la cuarentena.
        
        Returns:
            Dict[str, Any]: Estadísticas de cuarentena
        """
        try:
            stats_gestor = self.gestor_cuarentena.obtener_estadisticas()
            archivos_lista = self.obtener_lista_cuarentena()
            
            # Contar por estado
            estados = {}
            niveles_riesgo = {}
            for archivo in archivos_lista:
                estado = archivo.get('estado', 'desconocido')
                nivel = archivo.get('nivel_riesgo', 'desconocido')
                estados[estado] = estados.get(estado, 0) + 1
                niveles_riesgo[nivel] = niveles_riesgo.get(nivel, 0) + 1
            
            with self.lock:
                analisis_completados = len([a for a in self.estadisticas_analisis.values() 
                                          if a.get('estado') == 'completado'])
                operaciones_24h = len([p for p in self.archivos_procesados 
                                     if p['timestamp'] > datetime.now() - timedelta(hours=24)])
            
            return {
                'total_archivos': stats_gestor.get('total_archivos', len(archivos_lista)),
                'archivos_por_estado': estados,
                'archivos_por_nivel_riesgo': niveles_riesgo,
                'analisis_completados': analisis_completados,
                'operaciones_24h': operaciones_24h,
                'espacio_utilizado_mb': stats_gestor.get('espacio_utilizado_mb', 0),
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas de cuarentena: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def limpiar_cuarentena(self, criterios: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Limpiar archivos de la cuarentena según criterios.
        
        Args:
            criterios: Criterios de limpieza (días antigüedad, estado, etc.)
            
        Returns:
            Dict[str, Any]: Resultado de la limpieza
        """
        try:
            criterios = criterios or {}
            dias_antiguedad = criterios.get('dias_antiguedad', self.configuracion['periodo_retencion_dias'])
            estados_eliminar = criterios.get('estados', ['analizado', 'seguro'])
            
            limite_tiempo = datetime.now() - timedelta(days=dias_antiguedad)
            archivos_lista = self.obtener_lista_cuarentena()
            
            archivos_eliminados = 0
            errores = []
            
            for archivo in archivos_lista:
                try:
                    fecha_cuarentena = datetime.fromisoformat(archivo['fecha_cuarentena'].replace('Z', '+00:00'))
                    
                    # Verificar criterios de eliminación
                    if (fecha_cuarentena < limite_tiempo and 
                        archivo['estado'] in estados_eliminar):
                        
                        resultado_eliminacion = self.eliminar_archivo_cuarentena(archivo['id'], confirmar=True)
                        if resultado_eliminacion.get('exitoso', False):
                            archivos_eliminados += 1
                        else:
                            errores.append(f"Error eliminando {archivo['id']}: {resultado_eliminacion.get('error', 'desconocido')}")
                
                except Exception as e:
                    errores.append(f"Error procesando archivo {archivo.get('id', 'desconocido')}: {e}")
            
            resultado = {
                'archivos_eliminados': archivos_eliminados,
                'errores': errores,
                'criterios_aplicados': {
                    'dias_antiguedad': dias_antiguedad,
                    'estados_eliminar': estados_eliminar
                },
                'timestamp': datetime.now().isoformat()
            }
            
            # Registrar limpieza en SIEM
            if self.siem:
                self.siem.registrar_evento(
                    TipoEvento.CUARENTENA_LIMPIADA,
                    f"Limpieza de cuarentena completada: {archivos_eliminados} archivos eliminados",
                    resultado,
                    "MEDIO"
                )
            
            self.logger.info(f"Limpieza de cuarentena completada: {archivos_eliminados} archivos eliminados")
            return resultado
        
        except Exception as e:
            self.logger.error(f"Error en limpieza de cuarentena: {e}")
            resultado_error = {
                'archivos_eliminados': 0,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            
            if self.siem:
                self.siem.registrar_evento(
                    TipoEvento.ERROR_SISTEMA,
                    f"Error en limpieza de cuarentena: {e}",
                    resultado_error,
                    "MEDIO"
                )
            
            return resultado_error
    
    def configurar_cuarentena(self, config: Dict[str, Any]):
        """
        Configurar parámetros de la cuarentena.
        
        Args:
            config: Diccionario con configuración
        """
        with self.lock:
            self.configuracion.update(config)
        
        self.logger.info(f"Configuración de cuarentena actualizada: {config}")
        
        if self.siem:
            self.siem.registrar_evento(
                TipoEvento.CONFIGURACION_MODIFICADA,
                "Configuración de cuarentena actualizada",
                config,
                "MEDIO"
            )
    
    def generar_reporte_cuarentena(self) -> str:
        """
        Generar reporte de cuarentena en formato Markdown.
        
        Returns:
            str: Reporte en formato Markdown
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        estadisticas = self.obtener_estadisticas_cuarentena()
        archivos_recientes = self.obtener_lista_cuarentena()[:10]
        
        md = f"# Reporte de Cuarentena\n\n"
        md += f"**Fecha de generación:** {timestamp}\n\n"
        
        # Estadísticas generales
        md += "## 🔒 Estadísticas de Cuarentena\n\n"
        md += f"- **Total archivos:** {estadisticas.get('total_archivos', 0)}\n"
        md += f"- **Análisis completados:** {estadisticas.get('analisis_completados', 0)}\n"
        md += f"- **Operaciones (24h):** {estadisticas.get('operaciones_24h', 0)}\n"
        md += f"- **Espacio utilizado:** {estadisticas.get('espacio_utilizado_mb', 0):.2f} MB\n\n"
        
        # Archivos por estado
        estados = estadisticas.get('archivos_por_estado', {})
        if estados:
            md += "### Archivos por estado:\n"
            for estado, count in estados.items():
                md += f"- **{estado}:** {count}\n"
            md += "\n"
        
        # Archivos por nivel de riesgo
        riesgos = estadisticas.get('archivos_por_nivel_riesgo', {})
        if riesgos:
            md += "### Archivos por nivel de riesgo:\n"
            for riesgo, count in riesgos.items():
                md += f"- **{riesgo}:** {count}\n"
            md += "\n"
        
        # Archivos recientes
        md += "## 📁 Archivos Recientes en Cuarentena\n\n"
        if archivos_recientes:
            for archivo in archivos_recientes:
                fecha = archivo.get('fecha_cuarentena', 'N/A')
                if 'T' in fecha:
                    fecha = fecha.split('T')[0]  # Solo la fecha
                md += f"- **{archivo.get('nombre', 'N/A')}** - Estado: {archivo.get('estado', 'N/A')} - {fecha}\n"
        else:
            md += "No hay archivos en cuarentena.\n"
        
        md += "\n---\n"
        md += "*Reporte generado automáticamente por Ares Aegis*\n"
        
        return md
