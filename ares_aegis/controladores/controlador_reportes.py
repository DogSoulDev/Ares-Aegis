#!/usr/bin/env python3
"""
Ares Aegis - Controlador de Reportes
Controlador especializado para gestionar generación y exportación de reportes

Copyright (c) 2025 DogSoulDev (https://github.com/DogSoulDev)
Todos los derechos reservados. Este código es propietario y confidencial.
La copia, distribución o modificación no autorizada está estrictamente prohibida.

Versión: 3.0.0
"""

import os
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from pathlib import Path

from ..modelos.siem import SIEM, TipoEvento
from ..utilidades.ayuda_logging import configurar_logger_modulo
from ..utilidades.ayuda_rutas import crear_ruta_segura


class ControladorReportes:
    """Controlador especializado para operaciones de reportes."""
    
    def __init__(self, siem: SIEM):
        """
        Inicializar el controlador de reportes.
        
        Args:
            siem: Instancia del SIEM para registro de eventos
        """
        self.siem = siem
        self.logger = configurar_logger_modulo("controlador_reportes")
        
        # Estado del controlador
        self.reportes_generados = []
        self.plantillas_reportes = {}
        self.configuracion_exportacion = {}
        self.lock = threading.Lock()
        
        # Configuración
        self.configuracion = {
            'directorio_reportes': 'reportes',
            'formato_por_defecto': 'markdown',
            'incluir_graficos': False,
            'periodo_por_defecto_dias': 7,
            'auto_cleanup_dias': 30
        }
        
        # Inicializar directorio de reportes
        self._inicializar_directorio_reportes()
        
        self.logger.info("Controlador de Reportes inicializado")
    
    def _inicializar_directorio_reportes(self):
        """Inicializar el directorio de reportes."""
        try:
            directorio = Path(self.configuracion['directorio_reportes'])
            directorio.mkdir(exist_ok=True)
            self.logger.info(f"Directorio de reportes inicializado: {directorio}")
        except Exception as e:
            self.logger.error(f"Error inicializando directorio de reportes: {e}")
    
    def generar_reporte_seguridad_general(self, periodo_dias: int = 7, 
                                         incluir_detalles: bool = True) -> Dict[str, Any]:
        """
        Generar reporte general de seguridad del sistema.
        
        Args:
            periodo_dias: Período de tiempo para el reporte en días
            incluir_detalles: Si incluir secciones detalladas
            
        Returns:
            Dict[str, Any]: Información del reporte generado
        """
        try:
            self.logger.info(f"Generando reporte general de seguridad ({periodo_dias} días)")
            
            inicio_tiempo = time.time()
            timestamp = datetime.now()
            fecha_inicio = timestamp - timedelta(days=periodo_dias)
            
            # Obtener datos del período
            eventos = self._obtener_eventos_periodo(fecha_inicio, timestamp)
            estadisticas = self._calcular_estadisticas_periodo(eventos)
            
            # Construir contenido del reporte
            contenido = self._construir_reporte_seguridad(
                estadisticas, eventos, periodo_dias, incluir_detalles
            )
            
            # Generar archivo
            nombre_archivo = f"seguridad_general_{timestamp.strftime('%Y%m%d_%H%M%S')}.md"
            ruta_archivo = Path(self.configuracion['directorio_reportes']) / nombre_archivo
            
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                f.write(contenido)
            
            tiempo_generacion = time.time() - inicio_tiempo
            
            # Guardar información del reporte
            info_reporte = {
                'id': f"seg_gen_{int(time.time())}",
                'tipo': 'seguridad_general',
                'nombre_archivo': nombre_archivo,
                'ruta_archivo': str(ruta_archivo),
                'timestamp_generacion': timestamp.isoformat(),
                'periodo_dias': periodo_dias,
                'total_eventos': len(eventos),
                'tiempo_generacion': tiempo_generacion,
                'tamaño_archivo_bytes': ruta_archivo.stat().st_size
            }
            
            with self.lock:
                self.reportes_generados.append(info_reporte)
            
            # Registrar en SIEM
            if self.siem:
                self.siem.registrar_evento(
                    TipoEvento.CONFIGURACION_MODIFICADA,
                    f"Reporte de seguridad general generado: {nombre_archivo}",
                    info_reporte,
                    "MEDIO"
                )
            
            self.logger.info(f"Reporte generado: {nombre_archivo} en {tiempo_generacion:.2f}s")
            return info_reporte
        
        except Exception as e:
            self.logger.error(f"Error generando reporte de seguridad: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def generar_reporte_incidentes(self, periodo_dias: int = 30, 
                                  solo_criticos: bool = False) -> Dict[str, Any]:
        """
        Generar reporte de incidentes de seguridad.
        
        Args:
            periodo_dias: Período de tiempo para el reporte
            solo_criticos: Si incluir solo incidentes críticos
            
        Returns:
            Dict[str, Any]: Información del reporte generado
        """
        try:
            self.logger.info(f"Generando reporte de incidentes ({periodo_dias} días)")
            
            inicio_tiempo = time.time()
            timestamp = datetime.now()
            fecha_inicio = timestamp - timedelta(days=periodo_dias)
            
            # Obtener eventos de incidentes
            eventos = self._obtener_eventos_periodo(fecha_inicio, timestamp)
            
            # Filtrar incidentes
            tipos_incidentes = [
                TipoEvento.AMENAZA_DETECTADA,
                TipoEvento.MALWARE_DETECTADO,
                TipoEvento.VIRUS_ENCONTRADO,
                TipoEvento.RANSOMWARE_DETECTADO,
                TipoEvento.CONEXION_SOSPECHOSA,
                TipoEvento.INTEGRIDAD_VIOLADA
            ]
            
            incidentes = [e for e in eventos if e.get('tipo') in tipos_incidentes]
            
            if solo_criticos:
                incidentes = [i for i in incidentes if i.get('nivel_criticidad') in ['CRITICO', 'ALTO']]
            
            # Construir reporte
            contenido = self._construir_reporte_incidentes(incidentes, periodo_dias, solo_criticos)
            
            # Generar archivo
            sufijo = "_criticos" if solo_criticos else ""
            nombre_archivo = f"incidentes{sufijo}_{timestamp.strftime('%Y%m%d_%H%M%S')}.md"
            ruta_archivo = Path(self.configuracion['directorio_reportes']) / nombre_archivo
            
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                f.write(contenido)
            
            tiempo_generacion = time.time() - inicio_tiempo
            
            info_reporte = {
                'id': f"inc_{int(time.time())}",
                'tipo': 'incidentes',
                'nombre_archivo': nombre_archivo,
                'ruta_archivo': str(ruta_archivo),
                'timestamp_generacion': timestamp.isoformat(),
                'periodo_dias': periodo_dias,
                'total_incidentes': len(incidentes),
                'solo_criticos': solo_criticos,
                'tiempo_generacion': tiempo_generacion,
                'tamaño_archivo_bytes': ruta_archivo.stat().st_size
            }
            
            with self.lock:
                self.reportes_generados.append(info_reporte)
            
            if self.siem:
                self.siem.registrar_evento(
                    TipoEvento.CONFIGURACION_MODIFICADA,
                    f"Reporte de incidentes generado: {nombre_archivo}",
                    info_reporte,
                    "MEDIO"
                )
            
            self.logger.info(f"Reporte de incidentes generado: {nombre_archivo}")
            return info_reporte
        
        except Exception as e:
            self.logger.error(f"Error generando reporte de incidentes: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def generar_reporte_personalizado(self, config_reporte: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generar reporte personalizado según configuración.
        
        Args:
            config_reporte: Configuración del reporte personalizado
            
        Returns:
            Dict[str, Any]: Información del reporte generado
        """
        try:
            titulo = config_reporte.get('titulo', 'Reporte Personalizado')
            periodo_dias = config_reporte.get('periodo_dias', 7)
            filtros = config_reporte.get('filtros', {})
            secciones = config_reporte.get('secciones', ['resumen', 'eventos', 'estadisticas'])
            
            self.logger.info(f"Generando reporte personalizado: {titulo}")
            
            inicio_tiempo = time.time()
            timestamp = datetime.now()
            fecha_inicio = timestamp - timedelta(days=periodo_dias)
            
            # Obtener y filtrar eventos
            eventos = self._obtener_eventos_periodo(fecha_inicio, timestamp)
            eventos_filtrados = self._aplicar_filtros_eventos(eventos, filtros)
            
            # Construir contenido
            contenido = self._construir_reporte_personalizado(
                titulo, eventos_filtrados, secciones, config_reporte
            )
            
            # Generar archivo
            nombre_archivo = f"personalizado_{timestamp.strftime('%Y%m%d_%H%M%S')}.md"
            ruta_archivo = Path(self.configuracion['directorio_reportes']) / nombre_archivo
            
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                f.write(contenido)
            
            tiempo_generacion = time.time() - inicio_tiempo
            
            info_reporte = {
                'id': f"pers_{int(time.time())}",
                'tipo': 'personalizado',
                'titulo': titulo,
                'nombre_archivo': nombre_archivo,
                'ruta_archivo': str(ruta_archivo),
                'timestamp_generacion': timestamp.isoformat(),
                'configuracion': config_reporte,
                'eventos_incluidos': len(eventos_filtrados),
                'tiempo_generacion': tiempo_generacion,
                'tamaño_archivo_bytes': ruta_archivo.stat().st_size
            }
            
            with self.lock:
                self.reportes_generados.append(info_reporte)
            
            if self.siem:
                self.siem.registrar_evento(
                    TipoEvento.CONFIGURACION_MODIFICADA,
                    f"Reporte personalizado generado: {titulo}",
                    info_reporte,
                    "MEDIO"
                )
            
            self.logger.info(f"Reporte personalizado generado: {nombre_archivo}")
            return info_reporte
        
        except Exception as e:
            self.logger.error(f"Error generando reporte personalizado: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _obtener_eventos_periodo(self, fecha_inicio: datetime, fecha_fin: datetime) -> List[Dict[str, Any]]:
        """Obtener eventos del SIEM en un período específico."""
        try:
            if self.siem:
                eventos_siem = self.siem.obtener_eventos(limite=10000)
                eventos = []
                
                for evento in eventos_siem:
                    # Convertir evento a diccionario usando to_dict()
                    if hasattr(evento, 'to_dict'):
                        evento_dict = evento.to_dict()
                    else:
                        # Si no tiene to_dict, asumir que ya es un dict
                        evento_dict = evento if isinstance(evento, dict) else {}
                    
                    # Filtrar por fecha si tiene timestamp
                    timestamp_evento = evento_dict.get('timestamp')
                    if timestamp_evento:
                        try:
                            if isinstance(timestamp_evento, str):
                                timestamp_evento = datetime.fromisoformat(timestamp_evento.replace('Z', '+00:00'))
                            
                            if isinstance(timestamp_evento, datetime) and fecha_inicio <= timestamp_evento <= fecha_fin:
                                eventos.append(evento_dict)
                        except:
                            continue
                
                return eventos
            
            return []
        
        except Exception as e:
            self.logger.error(f"Error obteniendo eventos del período: {e}")
            return []
    
    def _calcular_estadisticas_periodo(self, eventos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcular estadísticas de eventos para un período."""
        from collections import defaultdict
        
        stats = {
            'total_eventos': len(eventos),
            'eventos_por_tipo': defaultdict(int),
            'eventos_por_criticidad': defaultdict(int),
            'eventos_por_dia': defaultdict(int),
            'tipos_mas_frecuentes': [],
            'horas_mas_activas': defaultdict(int)
        }
        
        for evento in eventos:
            tipo = evento.get('tipo', 'desconocido')
            criticidad = evento.get('nivel_criticidad', 'MEDIO')
            timestamp = evento.get('timestamp')
            
            stats['eventos_por_tipo'][tipo] += 1
            stats['eventos_por_criticidad'][criticidad] += 1
            
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            
            if isinstance(timestamp, datetime):
                dia = timestamp.strftime('%Y-%m-%d')
                hora = timestamp.hour
                stats['eventos_por_dia'][dia] += 1
                stats['horas_mas_activas'][hora] += 1
        
        # Convertir defaultdict a dict normal y obtener tops
        stats['eventos_por_tipo'] = dict(stats['eventos_por_tipo'])
        stats['eventos_por_criticidad'] = dict(stats['eventos_por_criticidad'])
        stats['eventos_por_dia'] = dict(stats['eventos_por_dia'])
        stats['horas_mas_activas'] = dict(stats['horas_mas_activas'])
        
        # Top 5 tipos más frecuentes
        stats['tipos_mas_frecuentes'] = sorted(
            stats['eventos_por_tipo'].items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]
        
        return stats
    
    def _construir_reporte_seguridad(self, estadisticas: Dict[str, Any], 
                                   eventos: List[Dict[str, Any]], 
                                   periodo_dias: int, 
                                   incluir_detalles: bool) -> str:
        """Construir contenido del reporte de seguridad general."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        md = f"# Reporte General de Seguridad\n\n"
        md += f"**Fecha de generación:** {timestamp}\n"
        md += f"**Período analizado:** {periodo_dias} días\n"
        md += f"**Total de eventos:** {estadisticas['total_eventos']}\n\n"
        
        # Resumen ejecutivo
        md += "## 📊 Resumen Ejecutivo\n\n"
        eventos_criticos = estadisticas['eventos_por_criticidad'].get('CRITICO', 0)
        eventos_altos = estadisticas['eventos_por_criticidad'].get('ALTO', 0)
        
        if eventos_criticos > 0:
            md += f"⚠️ **{eventos_criticos} eventos críticos** requieren atención inmediata\n"
        if eventos_altos > 0:
            md += f"🔶 **{eventos_altos} eventos de alta prioridad** detectados\n"
        
        if eventos_criticos == 0 and eventos_altos == 0:
            md += "✅ No se detectaron eventos críticos en el período\n"
        
        md += "\n"
        
        # Estadísticas por criticidad
        md += "## 🎯 Distribución por Criticidad\n\n"
        for criticidad, count in estadisticas['eventos_por_criticidad'].items():
            porcentaje = (count / estadisticas['total_eventos']) * 100 if estadisticas['total_eventos'] > 0 else 0
            md += f"- **{criticidad}:** {count} eventos ({porcentaje:.1f}%)\n"
        md += "\n"
        
        # Tipos de eventos más frecuentes
        if estadisticas['tipos_mas_frecuentes']:
            md += "## 📈 Tipos de Eventos Más Frecuentes\n\n"
            for tipo, count in estadisticas['tipos_mas_frecuentes']:
                md += f"- **{tipo}:** {count} eventos\n"
            md += "\n"
        
        # Actividad por día
        if estadisticas['eventos_por_dia']:
            md += "## 📅 Actividad por Día\n\n"
            for dia, count in sorted(estadisticas['eventos_por_dia'].items()):
                md += f"- **{dia}:** {count} eventos\n"
            md += "\n"
        
        # Detalles de eventos críticos si se solicita
        if incluir_detalles:
            eventos_criticos_lista = [e for e in eventos if e.get('nivel_criticidad') == 'CRITICO']
            if eventos_criticos_lista:
                md += "## 🚨 Eventos Críticos Detallados\n\n"
                for evento in eventos_criticos_lista[:10]:  # Máximo 10
                    timestamp_evento = evento.get('timestamp', 'N/A')
                    if isinstance(timestamp_evento, datetime):
                        timestamp_evento = timestamp_evento.strftime('%Y-%m-%d %H:%M:%S')
                    md += f"### {evento.get('tipo', 'Evento')}\n"
                    md += f"- **Tiempo:** {timestamp_evento}\n"
                    md += f"- **Mensaje:** {evento.get('mensaje', 'No disponible')}\n"
                    md += f"- **Criticidad:** {evento.get('nivel_criticidad', 'N/A')}\n\n"
        
        md += "---\n"
        md += "*Reporte generado automáticamente por Ares Aegis*\n"
        
        return md
    
    def _construir_reporte_incidentes(self, incidentes: List[Dict[str, Any]], 
                                    periodo_dias: int, solo_criticos: bool) -> str:
        """Construir contenido del reporte de incidentes."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        md = f"# Reporte de Incidentes de Seguridad\n\n"
        md += f"**Fecha de generación:** {timestamp}\n"
        md += f"**Período analizado:** {periodo_dias} días\n"
        md += f"**Filtro aplicado:** {'Solo críticos' if solo_criticos else 'Todos los incidentes'}\n"
        md += f"**Total de incidentes:** {len(incidentes)}\n\n"
        
        if not incidentes:
            md += "✅ No se registraron incidentes en el período especificado.\n"
            return md
        
        # Resumen por tipo
        from collections import defaultdict
        incidentes_por_tipo = defaultdict(int)
        for incidente in incidentes:
            incidentes_por_tipo[incidente.get('tipo', 'desconocido')] += 1
        
        md += "## 📊 Incidentes por Tipo\n\n"
        for tipo, count in sorted(incidentes_por_tipo.items(), key=lambda x: x[1], reverse=True):
            md += f"- **{tipo}:** {count} incidentes\n"
        md += "\n"
        
        # Lista detallada de incidentes
        md += "## 📋 Lista de Incidentes\n\n"
        for i, incidente in enumerate(incidentes[:20], 1):  # Máximo 20
            timestamp_incidente = incidente.get('timestamp', 'N/A')
            if isinstance(timestamp_incidente, datetime):
                timestamp_incidente = timestamp_incidente.strftime('%Y-%m-%d %H:%M:%S')
            
            md += f"### {i}. {incidente.get('tipo', 'Incidente')}\n"
            md += f"- **Tiempo:** {timestamp_incidente}\n"
            md += f"- **Criticidad:** {incidente.get('nivel_criticidad', 'N/A')}\n"
            md += f"- **Descripción:** {incidente.get('mensaje', 'No disponible')}\n\n"
        
        if len(incidentes) > 20:
            md += f"*... y {len(incidentes) - 20} incidentes adicionales*\n\n"
        
        md += "---\n"
        md += "*Reporte generado automáticamente por Ares Aegis*\n"
        
        return md
    
    def _construir_reporte_personalizado(self, titulo: str, eventos: List[Dict[str, Any]], 
                                       secciones: List[str], config: Dict[str, Any]) -> str:
        """Construir contenido del reporte personalizado."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        md = f"# {titulo}\n\n"
        md += f"**Fecha de generación:** {timestamp}\n"
        md += f"**Eventos incluidos:** {len(eventos)}\n\n"
        
        if 'resumen' in secciones:
            md += "## 📄 Resumen\n\n"
            md += f"Este reporte contiene {len(eventos)} eventos que cumplen los criterios especificados.\n\n"
        
        if 'estadisticas' in secciones:
            stats = self._calcular_estadisticas_periodo(eventos)
            md += "## 📊 Estadísticas\n\n"
            
            if stats['eventos_por_criticidad']:
                md += "### Por Criticidad:\n"
                for criticidad, count in stats['eventos_por_criticidad'].items():
                    md += f"- **{criticidad}:** {count}\n"
                md += "\n"
            
            if stats['tipos_mas_frecuentes']:
                md += "### Tipos Más Frecuentes:\n"
                for tipo, count in stats['tipos_mas_frecuentes']:
                    md += f"- **{tipo}:** {count}\n"
                md += "\n"
        
        if 'eventos' in secciones:
            md += "## 📋 Lista de Eventos\n\n"
            limite_eventos = config.get('limite_eventos', 50)
            
            for i, evento in enumerate(eventos[:limite_eventos], 1):
                timestamp_evento = evento.get('timestamp', 'N/A')
                if isinstance(timestamp_evento, datetime):
                    timestamp_evento = timestamp_evento.strftime('%Y-%m-%d %H:%M:%S')
                
                md += f"### {i}. {evento.get('tipo', 'Evento')}\n"
                md += f"- **Tiempo:** {timestamp_evento}\n"
                md += f"- **Criticidad:** {evento.get('nivel_criticidad', 'N/A')}\n"
                md += f"- **Mensaje:** {evento.get('mensaje', 'No disponible')}\n\n"
            
            if len(eventos) > limite_eventos:
                md += f"*... y {len(eventos) - limite_eventos} eventos adicionales*\n\n"
        
        md += "---\n"
        md += "*Reporte generado automáticamente por Ares Aegis*\n"
        
        return md
    
    def _aplicar_filtros_eventos(self, eventos: List[Dict[str, Any]], 
                               filtros: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Aplicar filtros a la lista de eventos."""
        eventos_filtrados = eventos.copy()
        
        # Filtro por tipo
        if 'tipos' in filtros and filtros['tipos']:
            eventos_filtrados = [e for e in eventos_filtrados if e.get('tipo') in filtros['tipos']]
        
        # Filtro por criticidad
        if 'criticidad' in filtros and filtros['criticidad']:
            eventos_filtrados = [e for e in eventos_filtrados if e.get('nivel_criticidad') in filtros['criticidad']]
        
        # Filtro por texto en mensaje
        if 'texto' in filtros and filtros['texto']:
            texto_buscar = filtros['texto'].lower()
            eventos_filtrados = [e for e in eventos_filtrados 
                               if texto_buscar in e.get('mensaje', '').lower()]
        
        return eventos_filtrados
    
    def obtener_lista_reportes(self, limite: int = 50) -> List[Dict[str, Any]]:
        """
        Obtener lista de reportes generados.
        
        Args:
            limite: Número máximo de reportes a devolver
            
        Returns:
            List[Dict[str, Any]]: Lista de reportes
        """
        with self.lock:
            reportes = self.reportes_generados.copy()
        
        # Ordenar por timestamp descendente
        reportes.sort(key=lambda x: x.get('timestamp_generacion', ''), reverse=True)
        return reportes[:limite]
    
    def obtener_reporte_info(self, reporte_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtener información de un reporte específico.
        
        Args:
            reporte_id: ID del reporte
            
        Returns:
            Optional[Dict[str, Any]]: Información del reporte o None
        """
        with self.lock:
            for reporte in self.reportes_generados:
                if reporte.get('id') == reporte_id:
                    return reporte.copy()
        
        return None
    
    def eliminar_reporte(self, reporte_id: str) -> bool:
        """
        Eliminar un reporte generado.
        
        Args:
            reporte_id: ID del reporte a eliminar
            
        Returns:
            bool: True si se eliminó exitosamente
        """
        try:
            reporte_info = self.obtener_reporte_info(reporte_id)
            if not reporte_info:
                return False
            
            # Eliminar archivo
            ruta_archivo = Path(reporte_info['ruta_archivo'])
            if ruta_archivo.exists():
                ruta_archivo.unlink()
            
            # Eliminar de la lista
            with self.lock:
                self.reportes_generados = [r for r in self.reportes_generados if r.get('id') != reporte_id]
            
            self.logger.info(f"Reporte eliminado: {reporte_id}")
            
            if self.siem:
                self.siem.registrar_evento(
                    TipoEvento.CONFIGURACION_MODIFICADA,
                    f"Reporte eliminado: {reporte_id}",
                    {'reporte_id': reporte_id},
                    "BAJO"
                )
            
            return True
        
        except Exception as e:
            self.logger.error(f"Error eliminando reporte {reporte_id}: {e}")
            return False
    
    def limpiar_reportes_antiguos(self, dias_retencion: int = 30) -> Dict[str, Any]:
        """
        Limpiar reportes antiguos según política de retención.
        
        Args:
            dias_retencion: Días de retención de reportes
            
        Returns:
            Dict[str, Any]: Resultado de la limpieza
        """
        try:
            limite_tiempo = datetime.now() - timedelta(days=dias_retencion)
            reportes_eliminados = 0
            errores = []
            
            with self.lock:
                reportes_a_mantener = []
                
                for reporte in self.reportes_generados:
                    timestamp_str = reporte.get('timestamp_generacion', '')
                    try:
                        timestamp_reporte = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        
                        if timestamp_reporte < limite_tiempo:
                            # Eliminar archivo
                            ruta_archivo = Path(reporte['ruta_archivo'])
                            if ruta_archivo.exists():
                                ruta_archivo.unlink()
                            reportes_eliminados += 1
                        else:
                            reportes_a_mantener.append(reporte)
                    
                    except Exception as e:
                        errores.append(f"Error procesando reporte {reporte.get('id', 'desconocido')}: {e}")
                        reportes_a_mantener.append(reporte)  # Mantener en caso de error
                
                self.reportes_generados = reportes_a_mantener
            
            resultado = {
                'reportes_eliminados': reportes_eliminados,
                'errores': errores,
                'dias_retencion': dias_retencion,
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"Limpieza de reportes completada: {reportes_eliminados} reportes eliminados")
            
            if self.siem:
                self.siem.registrar_evento(
                    TipoEvento.CONFIGURACION_MODIFICADA,
                    f"Limpieza de reportes: {reportes_eliminados} reportes eliminados",
                    resultado,
                    "BAJO"
                )
            
            return resultado
        
        except Exception as e:
            self.logger.error(f"Error en limpieza de reportes: {e}")
            return {
                'reportes_eliminados': 0,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def configurar_reportes(self, config: Dict[str, Any]):
        """
        Configurar parámetros de generación de reportes.
        
        Args:
            config: Diccionario con configuración
        """
        with self.lock:
            self.configuracion.update(config)
        
        self.logger.info(f"Configuración de reportes actualizada: {config}")
        
        if self.siem:
            self.siem.registrar_evento(
                TipoEvento.CONFIGURACION_MODIFICADA,
                "Configuración de reportes actualizada",
                config,
                "MEDIO"
            )
