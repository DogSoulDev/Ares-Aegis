#!/usr/bin/env python3
"""
Utilidades para Generación de Reportes - Ares Aegis
Funciones auxiliares para la generación de reportes del sistema

Creado por DogSoulDev
Versión: 4.0.0 - Arquitectura MVC Optimizada
"""

import os
import subprocess
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path


class GeneradorMarkdown:
    """Generador de reportes en formato Markdown."""
    
    @staticmethod
    def generar_header(titulo: str, subtitulo: str = "") -> List[str]:
        """Generar header del reporte."""
        lineas = [
            f"# {titulo}",
            "",
            f"**Generado el:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            ""
        ]
        
        if subtitulo:
            lineas.insert(2, f"## {subtitulo}")
            lineas.insert(3, "")
        
        return lineas
    
    @staticmethod
    def generar_seccion_resumen(datos: Dict) -> List[str]:
        """Generar sección de resumen."""
        return [
            "## 📊 Resumen Ejecutivo",
            "",
            f"- **Sistema Operativo:** {datos.get('sistema_operativo', 'No detectado')}",
            f"- **Tiempo de actividad:** {datos.get('uptime', 'No disponible')}",
            f"- **Uso de CPU:** {datos.get('cpu_usage', 0):.1f}%",
            f"- **Memoria utilizada:** {datos.get('memoria_usada_gb', 0):.1f} GB de {datos.get('memoria_total_gb', 0):.1f} GB",
            f"- **Procesos activos:** {datos.get('numero_procesos', 0)}",
            f"- **Conexiones de red:** {datos.get('numero_conexiones', 0)}",
            ""
        ]
    
    @staticmethod
    def generar_seccion_amenazas(datos: Dict) -> List[str]:
        """Generar sección de amenazas."""
        lineas = [
            "## 🛡️ Estado de Seguridad",
            ""
        ]
        
        amenazas = datos.get('amenazas_detectadas', [])
        if amenazas:
            lineas.append(f"**⚠️ {len(amenazas)} amenaza(s) detectada(s):**")
            lineas.append("")
            
            for amenaza in amenazas[:10]:  # Máximo 10 amenazas
                severidad = amenaza.get('severidad', 'Desconocida')
                descripcion = amenaza.get('descripcion', 'Sin descripción')
                lineas.append(f"- **{severidad}:** {descripcion}")
            
            if len(amenazas) > 10:
                lineas.append(f"- ... y {len(amenazas) - 10} amenaza(s) más")
        else:
            lineas.append("✅ **No se detectaron amenazas inmediatas**")
        
        lineas.append("")
        return lineas
    
    @staticmethod
    def generar_seccion_escaneos(datos: Dict) -> List[str]:
        """Generar sección de escaneos."""
        return [
            "## 🔍 Análisis de Escaneos",
            "",
            f"- **Archivos escaneados:** {datos.get('archivos_escaneados', 0):,}",
            f"- **Vulnerabilidades encontradas:** {len(datos.get('vulnerabilidades', []))}",
            f"- **Último escaneo:** {datos.get('ultimo_escaneo', 'Nunca')}",
            ""
        ]
    
    @staticmethod
    def generar_seccion_sistema(datos: Dict) -> List[str]:
        """Generar sección de información del sistema."""
        return [
            "## 💻 Información del Sistema",
            "",
            f"- **Interfaces de red:** {', '.join(datos.get('interfaces_red', []))}",
            f"- **Puertos abiertos:** {len(datos.get('puertos_abiertos', []))}",
            f"- **Estado de integridad:** {datos.get('integridad_estado', 'Desconocido')}",
            ""
        ]
    
    @staticmethod
    def generar_seccion_cuarentena(datos: Dict) -> List[str]:
        """Generar sección de cuarentena."""
        return [
            "## 🔒 Estado de Cuarentena",
            "",
            f"- **Archivos en cuarentena:** {datos.get('archivos_cuarentena', 0)}",
            f"- **Espacio utilizado:** {datos.get('espacio_cuarentena', '0 MB')}",
            ""
        ]
    
    @staticmethod
    def generar_seccion_metricas(datos: Dict) -> List[str]:
        """Generar sección de métricas."""
        return [
            "## 📈 Métricas de Rendimiento",
            "",
            "### CPU y Memoria",
            f"- Uso promedio de CPU: {datos.get('cpu_usage', 0):.1f}%",
            f"- Memoria disponible: {datos.get('memoria_disponible_gb', 0):.1f} GB",
            "",
            "### Red",
            f"- Interfaces activas: {len(datos.get('interfaces_red', []))}",
            f"- Conexiones establecidas: {datos.get('numero_conexiones', 0)}",
            ""
        ]
    
    @staticmethod
    def generar_seccion_recomendaciones(datos: Dict) -> List[str]:
        """Generar sección de recomendaciones."""
        lineas = [
            "## 💡 Recomendaciones de Seguridad",
            ""
        ]
        
        recomendaciones = []
        
        # Recomendaciones basadas en datos
        if datos.get('cpu_usage', 0) > 80:
            recomendaciones.append("Revisar procesos con alto uso de CPU")
        
        if datos.get('memoria_usada_gb', 0) / datos.get('memoria_total_gb', 1) > 0.9:
            recomendaciones.append("Considerar aumentar memoria RAM")
        
        if len(datos.get('amenazas_detectadas', [])) > 0:
            recomendaciones.append("Investigar y remediar amenazas detectadas")
        
        if datos.get('archivos_cuarentena', 0) > 0:
            recomendaciones.append("Revisar archivos en cuarentena")
        
        # Recomendaciones generales
        recomendaciones.extend([
            "Mantener el sistema actualizado",
            "Realizar escaneos regulares",
            "Revisar logs de seguridad periódicamente",
            "Configurar respaldos automáticos"
        ])
        
        for i, rec in enumerate(recomendaciones, 1):
            lineas.append(f"{i}. {rec}")
        
        lineas.append("")
        return lineas


class AnalizadorSistema:
    """Analizador de información del sistema para reportes."""
    
    @staticmethod
    def obtener_uptime() -> str:
        """Obtener tiempo de actividad del sistema."""
        try:
            if os.name == 'nt':  # Windows
                result = subprocess.run(['systeminfo'], capture_output=True, text=True, timeout=10)
                for line in result.stdout.split('\n'):
                    if 'System Boot Time' in line:
                        return line.split(':', 1)[1].strip()
            else:  # Unix/Linux
                with open('/proc/uptime', 'r') as f:
                    uptime_seconds = float(f.read().split()[0])
                    uptime_str = str(timedelta(seconds=int(uptime_seconds)))
                    return f"{uptime_str}"
        except Exception:
            pass
        return "No disponible"
    
    @staticmethod
    def obtener_cpu_usage() -> float:
        """Obtener uso actual de CPU."""
        try:
            if os.name == 'nt':  # Windows
                result = subprocess.run([
                    'wmic', 'cpu', 'get', 'loadpercentage', '/value'
                ], capture_output=True, text=True, timeout=5)
                
                for line in result.stdout.split('\n'):
                    if 'LoadPercentage' in line and '=' in line:
                        return float(line.split('=')[1].strip())
            else:  # Unix/Linux
                result = subprocess.run([
                    'grep', 'cpu', '/proc/stat'
                ], capture_output=True, text=True, timeout=5)
                
                if result.returncode == 0:
                    # Análisis básico de /proc/stat
                    line = result.stdout.split('\n')[0]
                    values = [int(x) for x in line.split()[1:]]
                    idle = values[3]
                    total = sum(values)
                    return ((total - idle) / total) * 100 if total > 0 else 0.0
        except Exception:
            pass
        return 0.0
    
    @staticmethod
    def obtener_memoria_info() -> Dict[str, Any]:
        """Obtener información de memoria."""
        try:
            if os.name == 'nt':  # Windows
                result = subprocess.run([
                    'wmic', 'OS', 'get', 'TotalVisibleMemorySize,FreePhysicalMemory', '/value'
                ], capture_output=True, text=True, timeout=5)
                
                total_kb = free_kb = 0
                for line in result.stdout.split('\n'):
                    if 'TotalVisibleMemorySize' in line and '=' in line:
                        total_kb = int(line.split('=')[1].strip())
                    elif 'FreePhysicalMemory' in line and '=' in line:
                        free_kb = int(line.split('=')[1].strip())
                
                if total_kb > 0:
                    return {
                        'total_gb': total_kb / 1024 / 1024,
                        'libre_gb': free_kb / 1024 / 1024,
                        'usada_gb': (total_kb - free_kb) / 1024 / 1024,
                        'porcentaje_usado': ((total_kb - free_kb) / total_kb) * 100
                    }
            else:  # Unix/Linux
                with open('/proc/meminfo', 'r') as f:
                    meminfo = f.read()
                
                def extract_kb(pattern):
                    match = re.search(pattern + r':\s+(\d+)', meminfo)
                    return int(match.group(1)) if match else 0
                
                total_kb = extract_kb('MemTotal')
                free_kb = extract_kb('MemFree')
                available_kb = extract_kb('MemAvailable')
                
                if total_kb > 0:
                    used_kb = total_kb - (available_kb if available_kb > 0 else free_kb)
                    return {
                        'total_gb': total_kb / 1024 / 1024,
                        'libre_gb': free_kb / 1024 / 1024,
                        'disponible_gb': available_kb / 1024 / 1024,
                        'usada_gb': used_kb / 1024 / 1024,
                        'porcentaje_usado': (used_kb / total_kb) * 100
                    }
        except Exception:
            pass
        
        return {
            'total_gb': 0.0,
            'libre_gb': 0.0,
            'usada_gb': 0.0,
            'porcentaje_usado': 0.0
        }
    
    @staticmethod
    def obtener_numero_procesos() -> int:
        """Obtener número de procesos activos."""
        try:
            if os.name == 'nt':  # Windows
                result = subprocess.run(['tasklist'], capture_output=True, text=True, timeout=10)
                # Contar líneas menos el header
                return len(result.stdout.split('\n')) - 4
            else:  # Unix/Linux
                result = subprocess.run(['ps', 'aux'], capture_output=True, text=True, timeout=10)
                # Contar líneas menos el header
                return len(result.stdout.split('\n')) - 2
        except Exception:
            pass
        return 0
    
    @staticmethod
    def obtener_numero_conexiones() -> int:
        """Obtener número de conexiones de red."""
        try:
            if os.name == 'nt':  # Windows
                result = subprocess.run(['netstat', '-an'], capture_output=True, text=True, timeout=10)
            else:  # Unix/Linux
                result = subprocess.run(['ss', '-tuln'], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                # Contar líneas que parecen conexiones
                conexiones = 0
                for line in result.stdout.split('\n'):
                    if 'ESTABLISHED' in line or 'LISTEN' in line or 'tcp' in line.lower():
                        conexiones += 1
                return conexiones
        except Exception:
            pass
        return 0
    
    @staticmethod
    def obtener_interfaces_red() -> List[str]:
        """Obtener lista de interfaces de red."""
        interfaces = []
        try:
            if os.name == 'nt':  # Windows
                result = subprocess.run(['ipconfig'], capture_output=True, text=True, timeout=10)
                for line in result.stdout.split('\n'):
                    if 'adapter' in line.lower():
                        # Extraer nombre del adaptador
                        adapter_name = line.split(':')[0].strip()
                        if adapter_name:
                            interfaces.append(adapter_name)
            else:  # Unix/Linux
                result = subprocess.run(['ip', 'link', 'show'], capture_output=True, text=True, timeout=10)
                for line in result.stdout.split('\n'):
                    if ': ' in line and 'state' in line.lower():
                        # Extraer nombre de la interfaz
                        interface_name = line.split(':')[1].strip().split('@')[0]
                        if interface_name and interface_name != 'lo':
                            interfaces.append(interface_name)
        except Exception:
            pass
        return interfaces[:5]  # Máximo 5 interfaces
    
    @staticmethod
    def obtener_puertos_abiertos() -> List[str]:
        """Obtener lista de puertos abiertos."""
        puertos = []
        try:
            if os.name == 'nt':  # Windows
                result = subprocess.run(['netstat', '-an'], capture_output=True, text=True, timeout=10)
            else:  # Unix/Linux
                result = subprocess.run(['ss', '-tuln'], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'LISTEN' in line or 'LISTENING' in line:
                        # Extraer puerto
                        parts = line.split()
                        if len(parts) > 3:
                            addr = parts[3] if os.name != 'nt' else parts[1]
                            if ':' in addr:
                                puerto = addr.split(':')[-1]
                                if puerto.isdigit():
                                    puertos.append(puerto)
        except Exception:
            pass
        return list(set(puertos))[:20]  # Máximo 20 puertos únicos


class VerificadorIntegridad:
    """Verificador básico de integridad del sistema."""
    
    @staticmethod
    def verificar_integridad_basica() -> str:
        """Verificar integridad básica del sistema."""
        problemas = []
        
        try:
            # Verificar archivos críticos del sistema
            archivos_criticos = [
                '/etc/passwd' if os.name != 'nt' else 'C:\\Windows\\System32\\config\\SAM',
                '/etc/shadow' if os.name != 'nt' else 'C:\\Windows\\System32\\config\\SECURITY',
                '/bin/bash' if os.name != 'nt' else 'C:\\Windows\\System32\\cmd.exe'
            ]
            
            for archivo in archivos_criticos:
                if not os.path.exists(archivo):
                    problemas.append(f"Archivo crítico faltante: {archivo}")
            
            # Verificar permisos básicos
            if os.name != 'nt':  # Solo en sistemas Unix
                try:
                    stat_info = os.stat('/etc/passwd')
                    if stat_info.st_mode & 0o077:  # Verificar que no sea world-writable
                        problemas.append("Permisos inseguros en /etc/passwd")
                except Exception:
                    pass
            
            if not problemas:
                return "✅ Integridad básica del sistema: OK"
            else:
                return f"⚠️ {len(problemas)} problema(s) de integridad detectado(s)"
                
        except Exception as e:
            return f"❌ Error verificando integridad: {str(e)}"
