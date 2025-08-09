#!/usr/bin/env python3
"""
Ares Aegis - Controlador de Reportes Optimizado
Controlador simplificado para generación de reportes

Creado por DogSoulDev
Versión: 4.0.0 - Arquitectura MVC Optimizada
"""

import os
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from pathlib import Path

from ..modelo.modelo_siem import SIEM, TipoEvento
from ..utils.utils_ayuda_logging import configurar_logger_modulo
from ..utils.utils_ayuda_rutas import crear_ruta_segura
from ..utils.utils_reportes import GeneradorMarkdown, AnalizadorSistema, VerificadorIntegridad


class ControladorReportes:
    """Controlador optimizado para generación de reportes."""
    
    def __init__(self, siem: SIEM):
        """Inicializar el controlador de reportes."""
        self.siem = siem
        self.logger = configurar_logger_modulo("controlador_reportes")
        
        # Estado del controlador
        self.reportes_generados = []
        self.lock = threading.Lock()
        
        # Configuración
        self.configuracion = {
            'directorio_reportes': 'reportes',
            'formato_por_defecto': 'markdown',
            'periodo_por_defecto_dias': 7,
            'auto_cleanup_dias': 30
        }
        
        # Componentes auxiliares
        self.generador_md = GeneradorMarkdown()
        self.analizador_sistema = AnalizadorSistema()
        self.verificador_integridad = VerificadorIntegridad()
        
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
    
    def generar_reporte_real(self, tipo_reporte: str, formato: str = 'markdown', 
                           info_seleccionada: Optional[Dict] = None) -> Optional[str]:
        """Generar reporte real con información actualizada del sistema."""
        try:
            self.logger.info(f"Generando reporte real: {tipo_reporte} en formato {formato}")
            
            # Crear directorio de reportes si no existe
            directorio_reportes = Path(self.configuracion['directorio_reportes'])
            directorio_reportes.mkdir(exist_ok=True)
            
            # Generar timestamp para el archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            extension = 'md' if formato == 'markdown' else 'html'
            nombre_archivo = f"{tipo_reporte}_{timestamp}.{extension}"
            ruta_archivo = directorio_reportes / nombre_archivo
            
            # Obtener datos reales del sistema
            datos_reporte = self._obtener_datos_sistema_optimizado()
            
            # Generar contenido según el formato
            if formato == 'markdown':
                contenido = self._generar_reporte_markdown_optimizado(
                    tipo_reporte, datos_reporte, info_seleccionada or {}
                )
            else:
                contenido = self._generar_reporte_html_simple(tipo_reporte, datos_reporte)
            
            # Escribir archivo
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                f.write(contenido)
            
            # Registrar en el historial
            with self.lock:
                self.reportes_generados.append({
                    'nombre': nombre_archivo,
                    'tipo': tipo_reporte,
                    'formato': formato,
                    'fecha': datetime.now().isoformat(),
                    'ruta': str(ruta_archivo),
                    'tamaño': ruta_archivo.stat().st_size
                })
            
            self.logger.info(f"Reporte generado exitosamente: {ruta_archivo}")
            
            # Registrar en SIEM
            if self.siem:
                self.siem.registrar_evento(
                    tipo=TipoEvento.INFORMACION,
                    mensaje=f"Reporte {tipo_reporte} generado en formato {formato}",
                    detalles={
                        'archivo': nombre_archivo,
                        'timestamp': datetime.now().isoformat()
                    }
                )
            
            return str(ruta_archivo)
            
        except Exception as e:
            self.logger.error(f"Error generando reporte: {e}")
            return None
    
    def _obtener_datos_sistema_optimizado(self) -> Dict[str, Any]:
        """Obtener datos del sistema de forma optimizada."""
        datos = {
            'timestamp': datetime.now().isoformat(),
            'sistema_operativo': os.name,
            'uptime': self.analizador_sistema.obtener_uptime(),
            'cpu_usage': self.analizador_sistema.obtener_cpu_usage(),
            'numero_procesos': self.analizador_sistema.obtener_numero_procesos(),
            'numero_conexiones': self.analizador_sistema.obtener_numero_conexiones(),
            'interfaces_red': self.analizador_sistema.obtener_interfaces_red(),
            'puertos_abiertos': self.analizador_sistema.obtener_puertos_abiertos(),
            'integridad_estado': self.verificador_integridad.verificar_integridad_basica()
        }
        
        # Información de memoria
        memoria_info = self.analizador_sistema.obtener_memoria_info()
        datos.update({
            'memoria_total_gb': memoria_info.get('total_gb', 0),
            'memoria_usada_gb': memoria_info.get('usada_gb', 0),
            'memoria_libre_gb': memoria_info.get('libre_gb', 0),
            'memoria_disponible_gb': memoria_info.get('disponible_gb', 0),
            'porcentaje_memoria_usado': memoria_info.get('porcentaje_usado', 0)
        })
        
        # Datos adicionales del sistema
        datos.update({
            'amenazas_detectadas': self._obtener_amenazas_detectadas(),
            'archivos_escaneados': self._contar_archivos_escaneados(),
            'archivos_cuarentena': self._contar_archivos_cuarentena(),
            'ultimo_escaneo': self._obtener_ultimo_escaneo(),
            'eventos_recientes': self._obtener_eventos_recientes()
        })
        
        return datos
    
    def _generar_reporte_markdown_optimizado(self, tipo_reporte: str, datos: Dict, 
                                           info_seleccionada: Dict) -> str:
        """Generar reporte en formato Markdown usando utilidades."""
        lineas = []
        
        # Header
        titulo = f"Reporte de Seguridad - {tipo_reporte.title()}"
        lineas.extend(self.generador_md.generar_header(titulo, "Ares Aegis Security Framework"))
        
        # Secciones según información seleccionada
        if info_seleccionada.get('resumen', True):
            lineas.extend(self.generador_md.generar_seccion_resumen(datos))
        
        if info_seleccionada.get('amenazas', True):
            lineas.extend(self.generador_md.generar_seccion_amenazas(datos))
        
        if info_seleccionada.get('escaneos', True):
            lineas.extend(self.generador_md.generar_seccion_escaneos(datos))
        
        if info_seleccionada.get('sistema', True):
            lineas.extend(self.generador_md.generar_seccion_sistema(datos))
        
        if info_seleccionada.get('cuarentena', True):
            lineas.extend(self.generador_md.generar_seccion_cuarentena(datos))
        
        if info_seleccionada.get('metricas', True):
            lineas.extend(self.generador_md.generar_seccion_metricas(datos))
        
        if info_seleccionada.get('recomendaciones', True):
            lineas.extend(self.generador_md.generar_seccion_recomendaciones(datos))
        
        # Footer
        lineas.extend([
            "---",
            "",
            f"**Reporte generado por Ares Aegis v4.0.0**",
            f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            ""
        ])
        
        return '\n'.join(lineas)
    
    def _generar_reporte_html_simple(self, tipo_reporte: str, datos: Dict) -> str:
        """Generar reporte HTML simple."""
        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte de Seguridad - {tipo_reporte.title()}</title>
    <style>
        body {{ font-family: 'Consolas', monospace; background-color: #0d1117; color: #c9d1d9; margin: 20px; }}
        .header {{ background-color: #21262d; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .section {{ background-color: #161b22; padding: 15px; border-radius: 8px; margin-bottom: 15px; }}
        .metric {{ display: inline-block; margin: 5px 10px; }}
        .warning {{ color: #f85149; }}
        .success {{ color: #56d364; }}
        .info {{ color: #58a6ff; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>[SHIELD] Reporte de Seguridad - {tipo_reporte.title()}</h1>
        <p><strong>Generado:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Sistema:</strong> {datos.get('sistema_operativo', 'Desconocido')}</p>
    </div>
    
    <div class="section">
        <h2>[STATS] Resumen del Sistema</h2>
        <div class="metric"><strong>Uptime:</strong> {datos.get('uptime', 'N/A')}</div>
        <div class="metric"><strong>CPU:</strong> {datos.get('cpu_usage', 0):.1f}%</div>
        <div class="metric"><strong>Memoria:</strong> {datos.get('memoria_usada_gb', 0):.1f}/{datos.get('memoria_total_gb', 0):.1f} GB</div>
        <div class="metric"><strong>Procesos:</strong> {datos.get('numero_procesos', 0)}</div>
    </div>
    
    <div class="section">
        <h2>[SHIELD] Estado de Seguridad</h2>
        <p><strong>Amenazas detectadas:</strong> <span class="{'warning' if len(datos.get('amenazas_detectadas', [])) > 0 else 'success'}">{len(datos.get('amenazas_detectadas', []))}</span></p>
        <p><strong>Archivos en cuarentena:</strong> {datos.get('archivos_cuarentena', 0)}</p>
        <p><strong>Estado de integridad:</strong> <span class="info">{datos.get('integridad_estado', 'Desconocido')}</span></p>
    </div>
    
    <div class="section">
        <h2> Red</h2>
        <p><strong>Interfaces:</strong> {', '.join(datos.get('interfaces_red', []))}</p>
        <p><strong>Conexiones:</strong> {datos.get('numero_conexiones', 0)}</p>
        <p><strong>Puertos abiertos:</strong> {len(datos.get('puertos_abiertos', []))}</p>
    </div>
    
    <footer style="margin-top: 30px; text-align: center; color: #7d8590;">
        <p>Reporte generado por Ares Aegis v4.0.0</p>
    </footer>
</body>
</html>"""
        return html
    
    def _obtener_amenazas_detectadas(self) -> List[Dict]:
        """Obtener amenazas detectadas del SIEM."""
        amenazas = []
        try:
            if self.siem:
                eventos = self.siem.obtener_eventos_recientes(limite=50)
                for evento in eventos:
                    if evento.get('tipo') in ['amenaza_detectada', 'alerta_critica']:
                        amenazas.append({
                            'severidad': evento.get('nivel', 'Media'),
                            'descripcion': evento.get('descripcion', 'Sin descripción'),
                            'timestamp': evento.get('timestamp')
                        })
        except Exception as e:
            self.logger.debug(f"Error obteniendo amenazas: {e}")
        return amenazas[:10]  # Máximo 10 amenazas
    
    def _contar_archivos_escaneados(self) -> int:
        """Contar archivos escaneados."""
        try:
            if self.siem:
                eventos = self.siem.obtener_eventos_recientes(limite=100)
                return len([e for e in eventos if e.get('tipo') == 'archivo_escaneado'])
        except Exception:
            pass
        return 0
    
    def _contar_archivos_cuarentena(self) -> int:
        """Contar archivos en cuarentena."""
        try:
            directorio_cuarentena = Path('cuarentena')
            if directorio_cuarentena.exists():
                return len(list(directorio_cuarentena.rglob('*')))
        except Exception:
            pass
        return 0
    
    def _obtener_ultimo_escaneo(self) -> str:
        """Obtener fecha del último escaneo."""
        try:
            if self.siem:
                eventos = self.siem.obtener_eventos_recientes(limite=50)
                for evento in eventos:
                    if evento.get('tipo') == 'escaneo_completado':
                        return evento.get('timestamp', 'Nunca')
        except Exception:
            pass
        return 'Nunca'
    
    def _obtener_eventos_recientes(self) -> List[Dict]:
        """Obtener eventos recientes del SIEM."""
        try:
            if self.siem:
                return self.siem.obtener_eventos_recientes(limite=20)
        except Exception:
            pass
        return []
    
    def obtener_reportes_generados(self) -> List[Dict]:
        """Obtener lista de reportes generados."""
        with self.lock:
            return self.reportes_generados.copy()
    
    def limpiar_reportes_antiguos(self, dias: int = 30) -> int:
        """Limpiar reportes antiguos."""
        if dias is None:
            dias = self.configuracion['auto_cleanup_dias']
        
        fecha_limite = datetime.now() - timedelta(days=dias)
        reportes_eliminados = 0
        
        try:
            directorio_reportes = Path(self.configuracion['directorio_reportes'])
            if not directorio_reportes.exists():
                return 0
            
            with self.lock:
                reportes_a_mantener = []
                
                for reporte in self.reportes_generados:
                    fecha_reporte = datetime.fromisoformat(reporte['fecha'])
                    ruta_archivo = Path(reporte['ruta'])
                    
                    if fecha_reporte < fecha_limite:
                        # Eliminar archivo físico
                        if ruta_archivo.exists():
                            ruta_archivo.unlink()
                            reportes_eliminados += 1
                    else:
                        reportes_a_mantener.append(reporte)
                
                self.reportes_generados = reportes_a_mantener
            
            self.logger.info(f"Limpieza completada: {reportes_eliminados} reportes eliminados")
            return reportes_eliminados
            
        except Exception as e:
            self.logger.error(f"Error en limpieza de reportes: {e}")
            return 0
    
    def exportar_reporte_json(self, datos: Dict, ruta_archivo: str) -> bool:
        """Exportar reporte en formato JSON."""
        try:
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"Reporte JSON exportado: {ruta_archivo}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exportando JSON: {e}")
            return False
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtener estadísticas del controlador."""
        with self.lock:
            return {
                'reportes_generados': len(self.reportes_generados),
                'tipos_reportes': list(set(r['tipo'] for r in self.reportes_generados)),
                'formatos_usados': list(set(r['formato'] for r in self.reportes_generados)),
                'tamaño_total_mb': sum(r.get('tamaño', 0) for r in self.reportes_generados) / 1024 / 1024,
                'directorio_reportes': self.configuracion['directorio_reportes']
            }
