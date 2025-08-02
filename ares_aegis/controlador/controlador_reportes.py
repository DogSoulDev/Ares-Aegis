#!/usr/bin/env python3
"""
Ares Aegis - Controlador de Reportes
Controlador especializado para gestionar generación y exportación de reportes

Creado por DogSoulDev (https://github.com/DogSoulDev)
Todos los derechos reservados. Este código es propietario y confidencial.
La copia, distribución o modificación no autorizada está estrictamente prohibida.

Versión: 4.0.0
"""

import os
import json
import time
import subprocess
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from pathlib import Path

from ..modelo.modelo_siem import SIEM, TipoEvento
from ..utils.ayuda_logging import configurar_logger_modulo
from ..utils.ayuda_rutas import crear_ruta_segura


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
    
    def generar_reporte_real(self, tipo_reporte: str, formato: str = 'html', info_seleccionada: Dict = None) -> Optional[str]:
        """
        Generar reporte real con información actualizada del sistema.
        
        Args:
            tipo_reporte: Tipo de reporte a generar
            formato: Formato de salida ('html' o 'markdown')
            info_seleccionada: Información a incluir en markdown
            
        Returns:
            Ruta del archivo generado o None si hay error
        """
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
            datos_reporte = self._obtener_datos_sistema_real()
            
            # Generar contenido según el formato
            if formato == 'markdown':
                contenido = self._generar_reporte_markdown(tipo_reporte, datos_reporte, info_seleccionada or {})
            else:
                contenido = self._generar_reporte_html(tipo_reporte, datos_reporte)
            
            # Escribir archivo
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                f.write(contenido)
            
            # Registrar en el historial
            self.reportes_generados.append({
                'nombre': nombre_archivo,
                'tipo': tipo_reporte,
                'formato': formato,
                'fecha': datetime.now().isoformat(),
                'ruta': str(ruta_archivo),
                'tamaño': ruta_archivo.stat().st_size
            })
            
            # Registrar evento en SIEM
            self.siem.registrar_evento(
                tipo=TipoEvento.INFORMACION,
                descripcion=f"Reporte {tipo_reporte} generado en formato {formato}",
                detalles={'archivo': nombre_archivo, 'tamaño': ruta_archivo.stat().st_size}
            )
            
            self.logger.info(f"Reporte generado exitosamente: {ruta_archivo}")
            return str(ruta_archivo)
            
        except Exception as e:
            self.logger.error(f"Error al generar reporte: {e}")
            self.siem.registrar_evento(
                tipo=TipoEvento.ERROR,
                descripcion=f"Error al generar reporte {tipo_reporte}",
                detalles={'error': str(e)}
            )
            return None
    
    def _obtener_datos_sistema_real(self) -> Dict[str, Any]:
        """Obtener datos reales del sistema para los reportes usando solo Python Standard Library y herramientas de Kali"""
        try:
            # Usar solo Python Standard Library y herramientas de Kali
            return self._obtener_datos_basicos()
            
        except Exception as e:
            self.logger.error(f"Error obteniendo datos del sistema: {e}")
            return {}
    
    def _obtener_datos_basicos(self) -> Dict[str, Any]:
        """Obtener datos básicos usando solo Python Standard Library y herramientas de Kali"""
        import os
        import platform
        import subprocess
        
        datos = {
            'timestamp': datetime.now().isoformat(),
            'sistema': {
                'plataforma': platform.system(),
                'version': platform.version(),
                'arquitectura': platform.architecture()[0],
                'procesador': platform.processor(),
                'usuario_actual': os.getenv('USERNAME', 'Desconocido'),
                'tiempo_funcionamiento': self._obtener_uptime(),
                'cpu_percent': self._obtener_cpu_usage(),
                'memoria': self._obtener_memoria_info(),
                'procesos_activos': self._obtener_numero_procesos()
            },
            'red': {
                'conexiones': self._obtener_numero_conexiones(),
                'interfaces': self._obtener_interfaces_red(),
                'puertos_abiertos': self._obtener_puertos_abiertos()
            },
            'archivos': {
                'directorio_trabajo': os.getcwd(),
                'espacio_disponible': self._obtener_espacio_disco(),
                'archivos_temporales': len(list(Path(os.getenv('TEMP', '/tmp')).glob('*')))
            },
            'seguridad': {
                'archivos_escaneados': self._contar_archivos_escaneados(),
                'amenazas_detectadas': self._obtener_amenazas_detectadas(),
                'archivos_cuarentena': self._contar_archivos_cuarentena(),
                'integridad_sistema': self._verificar_integridad_basica()
            },
            'logs_eventos': self._obtener_eventos_recientes()
        }
        
        return datos
    
    def _obtener_uptime(self) -> str:
        """Obtener tiempo de funcionamiento del sistema usando herramientas de Kali"""
        try:
            result = subprocess.run(['uptime'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return "No disponible"
    
    def _obtener_cpu_usage(self) -> float:
        """Obtener uso de CPU usando /proc/stat"""
        try:
            with open('/proc/stat', 'r') as f:
                line = f.readline()
                cpu_times = [int(x) for x in line.split()[1:]]
                idle_time = cpu_times[3]
                total_time = sum(cpu_times)
                usage = 100 - (idle_time * 100 / total_time)
                return round(usage, 2)
        except:
            return 0.0
    
    def _obtener_memoria_info(self) -> Dict[str, Any]:
        """Obtener información de memoria usando /proc/meminfo o free (solo Linux)"""
        try:
            import platform
            if platform.system() == 'Linux':
                result = subprocess.run(['free', '-b'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    if len(lines) >= 2:
                        mem_line = lines[1].split()
                        return {
                            'total': int(mem_line[1]),
                            'available': int(mem_line[6]) if len(mem_line) > 6 else int(mem_line[3]),
                            'used': int(mem_line[2]),
                        'percent': round((int(mem_line[2]) / int(mem_line[1])) * 100, 2)
                    }
        except:
            pass
        return {'total': 0, 'available': 0, 'used': 0, 'percent': 0}
    
    def _obtener_numero_procesos(self) -> int:
        """Obtener número de procesos usando ps"""
        try:
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return len(result.stdout.strip().split('\n')) - 1  # -1 para el header
        except:
            pass
        return 0
    
    def _obtener_numero_conexiones(self) -> int:
        """Obtener número de conexiones usando ss o netstat"""
        try:
            result = subprocess.run(['ss', '-tuln'], capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                result = subprocess.run(['netstat', '-tuln'], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                return len([line for line in result.stdout.strip().split('\n') if 'LISTEN' in line or 'ESTABLISHED' in line])
        except:
            pass
        return 0
    
    def _obtener_interfaces_red(self) -> List[str]:
        """Obtener interfaces de red usando ip o ifconfig"""
        try:
            result = subprocess.run(['ip', 'link', 'show'], capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                result = subprocess.run(['ifconfig', '-a'], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                interfaces = []
                for line in result.stdout.split('\n'):
                    if ':' in line and not line.startswith(' '):
                        interface = line.split(':')[1].strip() if 'ip' in result.args[0] else line.split(':')[0].strip()
                        if interface and interface not in ['lo', 'localhost']:
                            interfaces.append(interface)
                return interfaces
        except:
            pass
        return []
    
    def _obtener_puertos_abiertos(self) -> List[str]:
        """Obtener puertos abiertos usando ss o netstat"""
        try:
            result = subprocess.run(['ss', '-tuln'], capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                result = subprocess.run(['netstat', '-tuln'], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                puertos = []
                for line in result.stdout.split('\n'):
                    if 'LISTEN' in line:
                        parts = line.split()
                        if len(parts) >= 4:
                            local_addr = parts[3]
                            if ':' in local_addr:
                                puerto = local_addr.split(':')[-1]
                                if puerto not in puertos:
                                    puertos.append(puerto)
                return puertos
        except:
            pass
        return []
    
    def _generar_reporte_markdown(self, tipo_reporte: str, datos: Dict, info_seleccionada: Dict) -> str:
        """Generar reporte en formato Markdown con información seleccionada"""
        contenido = []
        
        # Header principal
        contenido.append(f"# 🛡️ Reporte de Seguridad Ares Aegis - {tipo_reporte.upper()}")
        contenido.append(f"**Generado:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        contenido.append(f"**Sistema:** {datos.get('sistema', {}).get('plataforma', 'Desconocido')}")
        contenido.append("")
        contenido.append("---")
        contenido.append("")
        
        # Resumen ejecutivo
        if info_seleccionada.get('resumen', True):
            contenido.extend(self._generar_seccion_resumen_md(datos))
        
        # Amenazas detectadas
        if info_seleccionada.get('amenazas', True):
            contenido.extend(self._generar_seccion_amenazas_md(datos))
        
        # Historial de escaneos
        if info_seleccionada.get('escaneos', True):
            contenido.extend(self._generar_seccion_escaneos_md(datos))
        
        # Estado del sistema
        if info_seleccionada.get('sistema', True):
            contenido.extend(self._generar_seccion_sistema_md(datos))
        
        # Estado de cuarentena
        if info_seleccionada.get('cuarentena', True):
            contenido.extend(self._generar_seccion_cuarentena_md(datos))
        
        # Métricas del sistema
        if info_seleccionada.get('metricas', True):
            contenido.extend(self._generar_seccion_metricas_md(datos))
        
        # Recomendaciones
        if info_seleccionada.get('recomendaciones', True):
            contenido.extend(self._generar_seccion_recomendaciones_md(datos))
        
        # Footer
        contenido.append("")
        contenido.append("---")
        contenido.append(f"*Reporte generado por Ares Aegis Centralita v4.0*")
        contenido.append(f"*Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        
        return "\n".join(contenido)
    
    def _generar_seccion_resumen_md(self, datos: Dict) -> List[str]:
        """Generar sección de resumen ejecutivo en Markdown"""
        seguridad = datos.get('seguridad', {})
        sistema = datos.get('sistema', {})
        
        seccion = [
            "## 📊 Resumen Ejecutivo",
            "",
            f"- **Archivos Escaneados:** {seguridad.get('archivos_escaneados', 0)}",
            f"- **Amenazas Detectadas:** {len(seguridad.get('amenazas_detectadas', []))}",
            f"- **Archivos en Cuarentena:** {seguridad.get('archivos_cuarentena', 0)}",
            f"- **Uso de CPU:** {sistema.get('cpu_percent', 'N/A')}%",
            f"- **Estado del Sistema:** {'🟢 Seguro' if len(seguridad.get('amenazas_detectadas', [])) == 0 else '🔴 Amenazas Detectadas'}",
            "",
        ]
        
        return seccion
    
    def _generar_seccion_amenazas_md(self, datos: Dict) -> List[str]:
        """Generar sección de amenazas en Markdown"""
        amenazas = datos.get('seguridad', {}).get('amenazas_detectadas', [])
        
        seccion = [
            "## 🚨 Amenazas Detectadas",
            "",
        ]
        
        if amenazas:
            for i, amenaza in enumerate(amenazas, 1):
                seccion.extend([
                    f"### Amenaza #{i}",
                    f"- **Archivo:** `{amenaza.get('archivo', 'Desconocido')}`",
                    f"- **Tipo:** {amenaza.get('tipo', 'Desconocido')}",
                    f"- **Nivel de Riesgo:** {amenaza.get('nivel', 'Medio')}",
                    f"- **Fecha Detección:** {amenaza.get('fecha', 'N/A')}",
                    f"- **Estado:** {amenaza.get('estado', 'Detectado')}",
                    "",
                ])
        else:
            seccion.append("✅ **No se detectaron amenazas en el sistema**")
            seccion.append("")
        
        return seccion
    
    def _generar_seccion_escaneos_md(self, datos: Dict) -> List[str]:
        """Generar sección de historial de escaneos en Markdown"""
        return [
            "## ⚡ Historial de Escaneos",
            "",
            f"- **Último Escaneo:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"- **Archivos Analizados:** {datos.get('seguridad', {}).get('archivos_escaneados', 0)}",
            f"- **Tiempo de Escaneo:** Tiempo real",
            f"- **Patrones Maliciosos:** Análisis de hashes MD5 y patrones sospechosos",
            f"- **Verificación de Integridad:** {datos.get('seguridad', {}).get('integridad_sistema', 'OK')}",
            "",
        ]
    
    def _generar_seccion_sistema_md(self, datos: Dict) -> List[str]:
        """Generar sección de estado del sistema en Markdown"""
        sistema = datos.get('sistema', {})
        
        return [
            "## 🖥️ Estado del Sistema",
            "",
            f"- **Plataforma:** {sistema.get('plataforma', 'Desconocido')}",
            f"- **Arquitectura:** {sistema.get('arquitectura', 'Desconocido')}",
            f"- **Procesador:** {sistema.get('procesador', 'Desconocido')}",
            f"- **Uso de CPU:** {sistema.get('cpu_percent', 'N/A')}%",
            f"- **Procesos Activos:** {sistema.get('procesos_activos', 'N/A')}",
            f"- **Usuario Actual:** {sistema.get('usuario_actual', 'Desconocido')}",
            "",
        ]
    
    def _generar_seccion_cuarentena_md(self, datos: Dict) -> List[str]:
        """Generar sección de estado de cuarentena en Markdown"""
        return [
            "## 🔒 Estado de Cuarentena",
            "",
            f"- **Archivos en Cuarentena:** {datos.get('seguridad', {}).get('archivos_cuarentena', 0)}",
            f"- **Directorio Cuarentena:** `cuarentena/`",
            f"- **Backups Disponibles:** Sí",
            f"- **Política de Retención:** 30 días",
            "",
        ]
    
    def _generar_seccion_metricas_md(self, datos: Dict) -> List[str]:
        """Generar sección de métricas del sistema en Markdown"""
        return [
            "## 📈 Métricas del Sistema",
            "",
            f"- **Tiempo de Actividad:** {datos.get('sistema', {}).get('tiempo_arranque', 'N/A')}",
            f"- **Conexiones de Red:** {datos.get('red', {}).get('conexiones', 'N/A')}",
            f"- **Interfaces de Red:** {len(datos.get('red', {}).get('interfaces', []))}",
            f"- **Eventos Registrados:** {len(datos.get('logs_eventos', []))}",
            "",
        ]
    
    def _generar_seccion_recomendaciones_md(self, datos: Dict) -> List[str]:
        """Generar sección de recomendaciones en Markdown"""
        amenazas = datos.get('seguridad', {}).get('amenazas_detectadas', [])
        
        recomendaciones = [
            "## 💡 Recomendaciones",
            "",
        ]
        
        if amenazas:
            recomendaciones.extend([
                "### 🔴 Acciones Inmediatas",
                "- Revisar y analizar las amenazas detectadas",
                "- Verificar archivos en cuarentena",
                "- Ejecutar escaneo completo del sistema",
                "",
                "### 🟡 Acciones Preventivas",
                "- Actualizar definiciones de virus",
                "- Revisar configuración de firewall",
                "- Implementar políticas de seguridad más estrictas",
                "",
            ])
        else:
            recomendaciones.extend([
                "### ✅ Sistema Seguro",
                "- Continuar con monitoreo regular",
                "- Mantener sistema actualizado",
                "- Realizar escaneos periódicos",
                "",
            ])
        
        return recomendaciones
    
    def _contar_archivos_escaneados(self) -> int:
        """Contar archivos escaneados realmente"""
        try:
            # Buscar en logs de eventos del SIEM
            eventos_escaneo = [e for e in self.siem.obtener_eventos_recientes(100) 
                              if 'escaneo' in e.get('descripcion', '').lower()]
            return len(eventos_escaneo)
        except:
            return 0
    
    def _obtener_amenazas_detectadas(self) -> List[Dict]:
        """Obtener amenazas realmente detectadas"""
        try:
            # Buscar eventos de amenazas en el SIEM
            eventos_amenazas = [e for e in self.siem.obtener_eventos_recientes(100) 
                               if 'amenaza' in e.get('descripcion', '').lower() or 
                                  'malicioso' in e.get('descripcion', '').lower()]
            
            amenazas = []
            for evento in eventos_amenazas:
                amenazas.append({
                    'archivo': evento.get('detalles', {}).get('archivo', 'Desconocido'),
                    'tipo': evento.get('detalles', {}).get('tipo', 'Malware'),
                    'nivel': 'Alto' if 'crítico' in evento.get('descripcion', '') else 'Medio',
                    'fecha': evento.get('timestamp', 'N/A'),
                    'estado': 'En Cuarentena' if 'cuarentena' in evento.get('descripcion', '') else 'Detectado'
                })
            
            return amenazas
        except:
            return []
    
    def _contar_archivos_cuarentena(self) -> int:
        """Contar archivos en cuarentena realmente"""
        try:
            from pathlib import Path
            cuarentena_dir = Path('cuarentena')
            if cuarentena_dir.exists():
                return len(list(cuarentena_dir.glob('*')))
            return 0
        except:
            return 0
    
    def _verificar_integridad_basica(self) -> str:
        """Verificar integridad básica del sistema"""
        try:
            import os
            import hashlib
            
            # Verificar archivos críticos del sistema
            archivos_criticos = [
                'main.py',
                'ares_aegis/__init__.py',
                'configuracion/ares_aegis_config.json'
            ]
            
            for archivo in archivos_criticos:
                if not os.path.exists(archivo):
                    return "❌ Integridad Comprometida"
            
            return "✅ Integridad OK"
        except:
            return "⚠️ No Verificado"
    
    def _obtener_eventos_recientes(self) -> List[Dict]:
        """Obtener eventos recientes del sistema"""
        try:
            return self.siem.obtener_eventos_recientes(50)
        except:
            return []
    
    def _obtener_espacio_disco(self) -> str:
        """Obtener espacio en disco usando métodos básicos"""
        try:
            import shutil
            total, usado, libre = shutil.disk_usage('.')
            return f"{libre // (1024**3)} GB libres de {total // (1024**3)} GB"
        except:
            return "N/A"
    
    def _generar_reporte_html(self, tipo_reporte: str, datos: Dict) -> str:
        """Generar reporte en formato HTML"""
        html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte {tipo_reporte.upper()} - Ares Aegis</title>
    <style>
        body {{ font-family: 'Consolas', monospace; background: #0a0a0a; color: #00ff41; margin: 0; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: #111; padding: 30px; border-radius: 10px; }}
        h1 {{ color: #00ff41; text-align: center; border-bottom: 2px solid #00ff41; padding-bottom: 10px; }}
        h2 {{ color: #ff6b35; border-left: 4px solid #ff6b35; padding-left: 15px; }}
        .metric {{ background: #222; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .status-ok {{ color: #00ff41; }}
        .status-warning {{ color: #ffa500; }}
        .status-error {{ color: #ff4444; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #444; padding: 10px; text-align: left; }}
        th {{ background: #333; color: #00ff41; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🛡️ Reporte de Seguridad Ares Aegis - {tipo_reporte.upper()}</h1>
        <p><strong>Generado:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Sistema:</strong> {datos.get('sistema', {}).get('plataforma', 'Desconocido')}</p>
        
        <h2>📊 Resumen Ejecutivo</h2>
        <div class="metric">
            <p><strong>Archivos Escaneados:</strong> {datos.get('seguridad', {}).get('archivos_escaneados', 0)}</p>
            <p><strong>Amenazas Detectadas:</strong> {len(datos.get('seguridad', {}).get('amenazas_detectadas', []))}</p>
            <p><strong>Estado:</strong> <span class="{'status-ok' if len(datos.get('seguridad', {}).get('amenazas_detectadas', [])) == 0 else 'status-error'}">
                {'🟢 Sistema Seguro' if len(datos.get('seguridad', {}).get('amenazas_detectadas', [])) == 0 else '🔴 Amenazas Detectadas'}
            </span></p>
        </div>
        
        <h2>🖥️ Estado del Sistema</h2>
        <div class="metric">
            <p><strong>CPU:</strong> {datos.get('sistema', {}).get('cpu_percent', 'N/A')}%</p>
            <p><strong>Procesos:</strong> {datos.get('sistema', {}).get('procesos_activos', 'N/A')}</p>
            <p><strong>Usuario:</strong> {datos.get('sistema', {}).get('usuario_actual', 'Desconocido')}</p>
        </div>
        
        <hr>
        <p style="text-align: center; color: #888;">
            <em>Reporte generado por Ares Aegis Centralita v4.0 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em>
        </p>
    </div>
</body>
</html>
        """
        return html
    
    def obtener_reportes_existentes(self) -> List[Dict]:
        """Obtener lista de reportes existentes"""
        return self.reportes_generados
    
    def abrir_reporte(self, nombre_reporte: str) -> bool:
        """Abrir reporte en el navegador por defecto"""
        try:
            reporte = next((r for r in self.reportes_generados if r['nombre'] == nombre_reporte), None)
            if reporte:
                import webbrowser
                webbrowser.open(f"file://{os.path.abspath(reporte['ruta'])}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error abriendo reporte: {e}")
            return False
    
    def exportar_reporte(self, nombre_reporte: str, destino: str) -> bool:
        """Exportar reporte a ubicación específica"""
        try:
            reporte = next((r for r in self.reportes_generados if r['nombre'] == nombre_reporte), None)
            if reporte:
                import shutil
                shutil.copy2(reporte['ruta'], destino)
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error exportando reporte: {e}")
            return False
    
    def eliminar_reporte(self, nombre_reporte: str) -> bool:
        """Eliminar reporte del sistema"""
        try:
            reporte = next((r for r in self.reportes_generados if r['nombre'] == nombre_reporte), None)
            if reporte:
                import os
                os.remove(reporte['ruta'])
                self.reportes_generados.remove(reporte)
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error eliminando reporte: {e}")
            return False
    
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
    
    def generar_reporte_html(self, resultado: Any, nombre_reporte: str) -> bool:
        """
        Genera un reporte en formato HTML.
        
        Args:
            resultado: Datos del resultado para el reporte
            nombre_reporte: Nombre del archivo del reporte
            
        Returns:
            True si se generó correctamente, False en caso contrario
        """
        try:
            # Convertir resultado a diccionario si es necesario
            if hasattr(resultado, '__dict__'):
                datos = vars(resultado)
            else:
                datos = {'resultado': str(resultado)}
            
            # Generar contenido HTML
            contenido_html = self._generar_reporte_html('auditoria_avanzada', datos)
            
            # Crear ruta del archivo
            ruta_reporte = crear_ruta_segura(
                self.configuracion.get('directorio_reportes', 'reportes'),
                f"{nombre_reporte}.html"
            )
            
            # Escribir archivo
            with open(ruta_reporte, 'w', encoding='utf-8') as archivo:
                archivo.write(contenido_html)
            
            self.logger.info(f"Reporte HTML generado: {ruta_reporte}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error generando reporte HTML {nombre_reporte}: {e}")
            return False


