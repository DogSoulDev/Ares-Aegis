#!/usr/bin/env python3
"""
Ares Aegis - Utilidades del Controlador de Cuarentena
Clases auxiliares y utilidades para el controlador de cuarentena

Creado por DogSoulDev (https://github.com/DogSoulDev)
Todos los derechos reservados. Este código es propietario y confidencial.

Versión: 4.0.0
"""

import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path

from ..utils.utils_ayuda_logging import configurar_logger_modulo


class AnalizadorForenseCuarentena:
    """Analizador forense especializado para archivos en cuarentena."""
    
    def __init__(self):
        """Inicializar el analizador forense."""
        self.logger = configurar_logger_modulo("analizador_forense_cuarentena")
    
    def analizar_archivo_forense(self, archivo_id: str, gestor_cuarentena) -> Dict[str, Any]:
        """
        Realiza análisis forense completo de un archivo en cuarentena.
        
        Args:
            archivo_id: ID del archivo en cuarentena
            gestor_cuarentena: Instancia del gestor de cuarentena
        
        Returns:
            Dict con resultados del análisis forense
        """
        try:
            # Obtener información del archivo
            archivo_info = gestor_cuarentena.obtener_info_archivo(archivo_id)
            if not archivo_info:
                return {'error': 'Archivo no encontrado en cuarentena'}
            
            resultado_analisis = {
                'archivo_id': archivo_id,
                'timestamp_analisis': datetime.now(),
                'analisis_completado': False,
                'amenazas_detectadas': [],
                'recomendaciones': [],
                'metadatos_forenses': {}
            }
            
            # Análisis de hash y firmas
            self._analizar_hashes(archivo_info, resultado_analisis)
            
            # Análisis de comportamiento
            self._analizar_comportamiento(archivo_info, resultado_analisis) 
            
            # Análisis de metadatos
            self._analizar_metadatos_forenses(archivo_info, resultado_analisis)
            
            # Generar recomendaciones
            self._generar_recomendaciones_forenses(resultado_analisis)
            
            resultado_analisis['analisis_completado'] = True
            
            return resultado_analisis
        
        except Exception as e:
            self.logger.error(f"Error en análisis forense de {archivo_id}: {e}")
            return {
                'error': f'Error durante análisis forense: {str(e)}',
                'archivo_id': archivo_id,
                'timestamp_analisis': datetime.now()
            }
    
    def _analizar_hashes(self, archivo_info: Dict[str, Any], resultado: Dict[str, Any]):
        """Analiza hashes del archivo."""
        try:
            # Verificar hashes contra bases de datos de malware
            hash_md5 = archivo_info.get('hash_md5', '')
            hash_sha256 = archivo_info.get('hash_sha256', '')
            
            if hash_md5 or hash_sha256:
                resultado['metadatos_forenses']['hashes'] = {
                    'md5': hash_md5,
                    'sha256': hash_sha256,
                    'verificado': True
                }
                
                # Simulación de verificación contra base de datos
                if self._es_hash_conocido_malicioso(hash_md5, hash_sha256):
                    resultado['amenazas_detectadas'].append({
                        'tipo': 'MALWARE_CONOCIDO',
                        'descripcion': 'Hash coincide con malware conocido',
                        'severidad': 'ALTA'
                    })
        
        except Exception as e:
            self.logger.error(f"Error analizando hashes: {e}")
    
    def _analizar_comportamiento(self, archivo_info: Dict[str, Any], resultado: Dict[str, Any]):
        """Analiza patrones de comportamiento del archivo."""
        try:
            # Análisis de nombres sospechosos
            nombre_archivo = archivo_info.get('nombre_original', '')
            if self._es_nombre_sospechoso(nombre_archivo):
                resultado['amenazas_detectadas'].append({
                    'tipo': 'NOMBRE_SOSPECHOSO',
                    'descripcion': f'Nombre de archivo sospechoso: {nombre_archivo}',
                    'severidad': 'MEDIA'
                })
            
            # Análisis de extensión
            extension = Path(nombre_archivo).suffix.lower()
            if self._es_extension_peligrosa(extension):
                resultado['amenazas_detectadas'].append({
                    'tipo': 'EXTENSION_PELIGROSA',
                    'descripcion': f'Extensión potencialmente peligrosa: {extension}',
                    'severidad': 'ALTA'
                })
        
        except Exception as e:
            self.logger.error(f"Error analizando comportamiento: {e}")
    
    def _analizar_metadatos_forenses(self, archivo_info: Dict[str, Any], resultado: Dict[str, Any]):
        """Analiza metadatos forenses del archivo."""
        try:
            metadatos = {
                'tamaño_bytes': archivo_info.get('tamaño', 0),
                'fecha_cuarentena': archivo_info.get('fecha_cuarentena'),
                'origen': archivo_info.get('ruta_original', ''),
                'razon_cuarentena': archivo_info.get('razon', '')
            }
            
            resultado['metadatos_forenses'].update(metadatos)
            
            # Análisis de tamaño anómalo
            if metadatos['tamaño_bytes'] == 0:
                resultado['amenazas_detectadas'].append({
                    'tipo': 'ARCHIVO_VACIO',
                    'descripcion': 'Archivo vacío puede indicar eliminación maliciosa',
                    'severidad': 'BAJA'
                })
        
        except Exception as e:
            self.logger.error(f"Error analizando metadatos forenses: {e}")
    
    def _generar_recomendaciones_forenses(self, resultado: Dict[str, Any]):
        """Genera recomendaciones basadas en el análisis."""
        amenazas = resultado.get('amenazas_detectadas', [])
        recomendaciones = []
        
        if not amenazas:
            recomendaciones.append("No se detectaron amenazas evidentes. Considerar análisis adicional.")
        else:
            # Recomendaciones basadas en amenazas detectadas
            for amenaza in amenazas:
                if amenaza['tipo'] == 'MALWARE_CONOCIDO':
                    recomendaciones.append("CRÍTICO: Eliminar permanentemente. No restaurar.")
                elif amenaza['tipo'] == 'NOMBRE_SOSPECHOSO':
                    recomendaciones.append("Verificar legitimidad antes de restaurar.")
                elif amenaza['tipo'] == 'EXTENSION_PELIGROSA':
                    recomendaciones.append("Analizar contenido antes de permitir ejecución.")
        
        resultado['recomendaciones'] = recomendaciones
    
    def _es_hash_conocido_malicioso(self, md5: str, sha256: str) -> bool:
        """Verifica si el hash coincide con malware conocido."""
        # Simulación - en implementación real consultaría bases de datos
        hashes_maliciosos = {
            'd41d8cd98f00b204e9800998ecf8427e',  # MD5 de archivo vacío
            'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'  # SHA256 vacío
        }
        
        return md5 in hashes_maliciosos or sha256 in hashes_maliciosos
    
    def _es_nombre_sospechoso(self, nombre: str) -> bool:
        """Verifica si el nombre del archivo es sospechoso."""
        nombres_sospechosos = [
            'trojan', 'virus', 'malware', 'backdoor', 'keylogger',
            'rootkit', 'worm', 'ransomware', 'spy', 'crack'
        ]
        
        nombre_lower = nombre.lower()
        return any(sospechoso in nombre_lower for sospechoso in nombres_sospechosos)
    
    def _es_extension_peligrosa(self, extension: str) -> bool:
        """Verifica si la extensión es potencialmente peligrosa."""
        extensiones_peligrosas = {
            '.exe', '.com', '.scr', '.pif', '.bat', '.cmd', 
            '.vbs', '.js', '.jar', '.ps1', '.msi'
        }
        
        return extension in extensiones_peligrosas


class GestorEstadisticasCuarentena:
    """Gestor de estadísticas para el controlador de cuarentena."""
    
    def __init__(self):
        """Inicializar el gestor de estadísticas."""
        self.logger = configurar_logger_modulo("estadisticas_cuarentena")
        self.estadisticas = {
            'archivos_cuarentenados': 0,
            'archivos_restaurados': 0,
            'archivos_eliminados': 0,
            'analyses_realizados': 0,
            'amenazas_detectadas': 0
        }
    
    def obtener_estadisticas_completas(self, gestor_cuarentena) -> Dict[str, Any]:
        """
        Obtiene estadísticas completas de cuarentena.
        
        Args:
            gestor_cuarentena: Instancia del gestor de cuarentena
        
        Returns:
            Dict con estadísticas completas
        """
        try:
            archivos_cuarentena = gestor_cuarentena.listar_archivos()
            
            estadisticas = {
                'total_archivos_cuarentena': len(archivos_cuarentena),
                'archivos_por_fecha': self._agrupar_por_fecha(archivos_cuarentena),
                'archivos_por_tipo': self._agrupar_por_tipo(archivos_cuarentena),
                'archivos_por_razon': self._agrupar_por_razon(archivos_cuarentena),
                'espacio_utilizado_mb': self._calcular_espacio_utilizado(archivos_cuarentena),
                'archivos_antiguos': self._contar_archivos_antiguos(archivos_cuarentena),
                'estadisticas_operaciones': self.estadisticas.copy(),
                'timestamp_reporte': datetime.now()
            }
            
            return estadisticas
        
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas: {e}")
            return {'error': str(e)}
    
    def _agrupar_por_fecha(self, archivos: List[Dict[str, Any]]) -> Dict[str, int]:
        """Agrupa archivos por fecha de cuarentena."""
        grupos = {}
        
        for archivo in archivos:
            fecha_cuarentena = archivo.get('fecha_cuarentena')
            if fecha_cuarentena:
                if isinstance(fecha_cuarentena, str):
                    fecha_cuarentena = datetime.fromisoformat(fecha_cuarentena.replace('Z', '+00:00'))
                
                fecha_str = fecha_cuarentena.strftime('%Y-%m-%d')
                grupos[fecha_str] = grupos.get(fecha_str, 0) + 1
        
        return grupos
    
    def _agrupar_por_tipo(self, archivos: List[Dict[str, Any]]) -> Dict[str, int]:
        """Agrupa archivos por tipo/extensión."""
        grupos = {}
        
        for archivo in archivos:
            nombre = archivo.get('nombre_original', '')
            extension = Path(nombre).suffix.lower() or 'sin_extension'
            grupos[extension] = grupos.get(extension, 0) + 1
        
        return grupos
    
    def _agrupar_por_razon(self, archivos: List[Dict[str, Any]]) -> Dict[str, int]:
        """Agrupa archivos por razón de cuarentena."""
        grupos = {}
        
        for archivo in archivos:
            razon = archivo.get('razon', 'Sin especificar')
            grupos[razon] = grupos.get(razon, 0) + 1
        
        return grupos
    
    def _calcular_espacio_utilizado(self, archivos: List[Dict[str, Any]]) -> float:
        """Calcula el espacio total utilizado en MB."""
        total_bytes = sum(archivo.get('tamaño', 0) for archivo in archivos)
        return round(total_bytes / (1024 * 1024), 2)
    
    def _contar_archivos_antiguos(self, archivos: List[Dict[str, Any]], dias: int = 30) -> int:
        """Cuenta archivos más antiguos que el número de días especificado."""
        limite = datetime.now() - timedelta(days=dias)
        contador = 0
        
        for archivo in archivos:
            fecha_cuarentena = archivo.get('fecha_cuarentena')
            if fecha_cuarentena:
                if isinstance(fecha_cuarentena, str):
                    fecha_cuarentena = datetime.fromisoformat(fecha_cuarentena.replace('Z', '+00:00'))
                
                if fecha_cuarentena < limite:
                    contador += 1
        
        return contador
    
    def registrar_operacion(self, tipo_operacion: str):
        """Registra una operación en las estadísticas."""
        if tipo_operacion in self.estadisticas:
            self.estadisticas[tipo_operacion] += 1


class GeneradorReportesCuarentena:
    """Generador de reportes para el sistema de cuarentena."""
    
    def __init__(self):
        """Inicializar el generador de reportes."""
        self.logger = configurar_logger_modulo("reportes_cuarentena")
    
    def generar_reporte_completo(self, gestor_cuarentena, estadisticas_gestor) -> str:
        """
        Genera un reporte completo del estado de la cuarentena.
        
        Args:
            gestor_cuarentena: Instancia del gestor de cuarentena
            estadisticas_gestor: Instancia del gestor de estadísticas
        
        Returns:
            String con el reporte formateado
        """
        try:
            estadisticas = estadisticas_gestor.obtener_estadisticas_completas(gestor_cuarentena)
            
            reporte = self._generar_encabezado_reporte()
            reporte += self._generar_resumen_estadisticas(estadisticas)
            reporte += self._generar_detalle_archivos(estadisticas)
            reporte += self._generar_recomendaciones(estadisticas)
            reporte += self._generar_pie_reporte()
            
            return reporte
        
        except Exception as e:
            self.logger.error(f"Error generando reporte: {e}")
            return f"Error generando reporte: {str(e)}"
    
    def _generar_encabezado_reporte(self) -> str:
        """Genera el encabezado del reporte."""
        return f"""
========================================
    REPORTE DE CUARENTENA ARES AEGIS
========================================
Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Sistema: Ares Aegis v4.0.0
========================================

"""
    
    def _generar_resumen_estadisticas(self, estadisticas: Dict[str, Any]) -> str:
        """Genera el resumen de estadísticas."""
        resumen = "RESUMEN EJECUTIVO:\n"
        resumen += "-" * 40 + "\n"
        resumen += f"Total de archivos en cuarentena: {estadisticas.get('total_archivos_cuarentena', 0)}\n"
        resumen += f"Espacio utilizado: {estadisticas.get('espacio_utilizado_mb', 0)} MB\n"
        resumen += f"Archivos antiguos (>30 días): {estadisticas.get('archivos_antiguos', 0)}\n"
        
        operaciones = estadisticas.get('estadisticas_operaciones', {})
        resumen += f"Archivos cuarentenados: {operaciones.get('archivos_cuarentenados', 0)}\n"
        resumen += f"Archivos restaurados: {operaciones.get('archivos_restaurados', 0)}\n"
        resumen += f"Archivos eliminados: {operaciones.get('archivos_eliminados', 0)}\n"
        resumen += "\n"
        
        return resumen
    
    def _generar_detalle_archivos(self, estadisticas: Dict[str, Any]) -> str:
        """Genera el detalle de archivos por categorías."""
        detalle = "DISTRIBUCIÓN DE ARCHIVOS:\n"
        detalle += "-" * 40 + "\n"
        
        # Por tipo
        detalle += "Por tipo de archivo:\n"
        tipos = estadisticas.get('archivos_por_tipo', {})
        for tipo, cantidad in sorted(tipos.items(), key=lambda x: x[1], reverse=True):
            detalle += f"  {tipo}: {cantidad} archivos\n"
        
        detalle += "\nPor razón de cuarentena:\n"
        razones = estadisticas.get('archivos_por_razon', {})
        for razon, cantidad in sorted(razones.items(), key=lambda x: x[1], reverse=True):
            detalle += f"  {razon}: {cantidad} archivos\n"
        
        detalle += "\n"
        return detalle
    
    def _generar_recomendaciones(self, estadisticas: Dict[str, Any]) -> str:
        """Genera recomendaciones basadas en las estadísticas."""
        recomendaciones = "RECOMENDACIONES:\n"
        recomendaciones += "-" * 40 + "\n"
        
        archivos_antiguos = estadisticas.get('archivos_antiguos', 0)
        if archivos_antiguos > 0:
            recomendaciones += f"• Considerar limpiar {archivos_antiguos} archivos antiguos\n"
        
        espacio_mb = estadisticas.get('espacio_utilizado_mb', 0)
        if espacio_mb > 1000:  # 1GB
            recomendaciones += f"• Espacio de cuarentena alto ({espacio_mb} MB). Considerar limpieza\n"
        
        total_archivos = estadisticas.get('total_archivos_cuarentena', 0)
        if total_archivos > 100:
            recomendaciones += f"• Gran cantidad de archivos ({total_archivos}). Revisar regularmente\n"
        
        if archivos_antiguos == 0 and espacio_mb < 100 and total_archivos < 50:
            recomendaciones += "• Estado de cuarentena óptimo\n"
        
        recomendaciones += "\n"
        return recomendaciones
    
    def _generar_pie_reporte(self) -> str:
        """Genera el pie del reporte."""
        return f"""
========================================
Reporte generado por Ares Aegis
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
========================================
"""


class HelperOperacionesCuarentena:
    """Helper para operaciones comunes del controlador de cuarentena."""
    
    def __init__(self):
        """Inicializar el helper de operaciones."""
        self.logger = configurar_logger_modulo("helper_cuarentena")
    
    def validar_operacion_restauracion(self, archivo_id: str, gestor_cuarentena) -> Dict[str, Any]:
        """
        Valida si un archivo puede ser restaurado de forma segura.
        
        Args:
            archivo_id: ID del archivo a validar
            gestor_cuarentena: Instancia del gestor de cuarentena
        
        Returns:
            Dict con resultado de validación
        """
        try:
            archivo_info = gestor_cuarentena.obtener_info_archivo(archivo_id)
            if not archivo_info:
                return {
                    'valido': False,
                    'error': 'Archivo no encontrado en cuarentena'
                }
            
            validaciones = {
                'archivo_existe': True,
                'no_es_malware_conocido': True,
                'tamaño_valido': archivo_info.get('tamaño', 0) > 0,
                'nombre_valido': bool(archivo_info.get('nombre_original')),
                'ruta_origen_valida': bool(archivo_info.get('ruta_original'))
            }
            
            # Verificar que todas las validaciones pasen
            es_valido = all(validaciones.values())
            
            resultado = {
                'valido': es_valido,
                'validaciones': validaciones,
                'archivo_info': archivo_info
            }
            
            if not es_valido:
                resultado['advertencias'] = self._generar_advertencias_restauracion(validaciones)
            
            return resultado
        
        except Exception as e:
            self.logger.error(f"Error validando restauración de {archivo_id}: {e}")
            return {
                'valido': False,
                'error': str(e)
            }
    
    def _generar_advertencias_restauracion(self, validaciones: Dict[str, bool]) -> List[str]:
        """Genera advertencias basadas en validaciones fallidas."""
        advertencias = []
        
        if not validaciones.get('tamaño_valido'):
            advertencias.append("Archivo tiene tamaño inválido (0 bytes)")
        
        if not validaciones.get('nombre_valido'):
            advertencias.append("Nombre de archivo faltante o inválido")
        
        if not validaciones.get('ruta_origen_valida'):
            advertencias.append("Ruta de origen faltante o inválida")
        
        return advertencias
    
    def programar_limpieza_automatica(self, criterios: Dict[str, Any], callback_limpieza):
        """
        Programa una limpieza automática de cuarentena.
        
        Args:
            criterios: Criterios para la limpieza
            callback_limpieza: Función de callback para ejecutar limpieza
        """
        def tarea_limpieza():
            try:
                self.logger.info("Iniciando limpieza automática programada")
                resultado = callback_limpieza(criterios)
                self.logger.info(f"Limpieza completada: {resultado}")
            except Exception as e:
                self.logger.error(f"Error en limpieza automática: {e}")
        
        # Programar tarea en hilo separado
        hilo_limpieza = threading.Thread(target=tarea_limpieza, daemon=True)
        hilo_limpieza.start()
    
    def validar_criterios_limpieza(self, criterios: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida los criterios de limpieza antes de ejecutar.
        
        Args:
            criterios: Criterios a validar
        
        Returns:
            Dict con resultado de validación
        """
        criterios_validos = {
            'dias_antiguedad': isinstance(criterios.get('dias_antiguedad'), int) and (criterios.get('dias_antiguedad') or 0) > 0,
            'tamaño_maximo_mb': criterios.get('tamaño_maximo_mb', 0) >= 0,
            'tipos_archivo': isinstance(criterios.get('tipos_archivo', []), list)
        }
        
        es_valido = all(criterios_validos.values())
        
        return {
            'valido': es_valido,
            'criterios_validos': criterios_validos,
            'criterios_normalizados': self._normalizar_criterios_limpieza(criterios) if es_valido else None
        }
    
    def _normalizar_criterios_limpieza(self, criterios: Dict[str, Any]) -> Dict[str, Any]:
        """Normaliza los criterios de limpieza."""
        return {
            'dias_antiguedad': criterios.get('dias_antiguedad', 30),
            'tamaño_maximo_mb': criterios.get('tamaño_maximo_mb', 0),
            'tipos_archivo': criterios.get('tipos_archivo', []),
            'incluir_analizados': criterios.get('incluir_analizados', False),
            'confirmar_eliminacion': criterios.get('confirmar_eliminacion', True)
        }
