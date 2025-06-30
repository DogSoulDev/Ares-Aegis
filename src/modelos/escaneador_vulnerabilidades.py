#!/usr/bin/env python3
"""
Escaneador de Vulnerabilidades
Módulo para detección de vulnerabilidades conocidas en software instalado.

Autor: DogSoulDev
Versión: 2.0.0
"""

import re
import os
import subprocess
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import urllib.request
import urllib.parse
import socket


class VulnerabilidadDetectada:
    """Representa una vulnerabilidad detectada en el sistema."""
    
    def __init__(self, cve_id: str, software: str, version: str, descripcion: str, severidad: str):
        """
        Inicializa una vulnerabilidad detectada.
        
        Args:
            cve_id: Identificador CVE de la vulnerabilidad
            software: Nombre del software afectado
            version: Versión del software afectada
            descripcion: Descripción de la vulnerabilidad
            severidad: Nivel de severidad (CRITICA, ALTA, MEDIA, BAJA)
        """
        self.cve_id = cve_id
        self.software = software
        self.version = version
        self.descripcion = descripcion
        self.severidad = severidad.upper()
        self.fecha_descubrimiento = datetime.now()
        self.puntuacion_cvss = self._calcular_puntuacion_cvss()
        self.recomendaciones = self._generar_recomendaciones()
    
    def _calcular_puntuacion_cvss(self) -> float:
        """Calcula una puntuación CVSS estimada basada en la severidad."""
        puntuaciones = {
            'CRITICA': 9.5,
            'ALTA': 7.5,
            'MEDIA': 5.0,
            'BAJA': 2.5
        }
        return puntuaciones.get(self.severidad, 0.0)
    
    def _generar_recomendaciones(self) -> List[str]:
        """Genera recomendaciones de mitigación."""
        recomendaciones = [
            f"Actualizar {self.software} a la versión más reciente",
            "Aplicar parches de seguridad disponibles",
            "Revisar configuraciones de seguridad"
        ]
        
        if self.severidad in ['CRITICA', 'ALTA']:
            recomendaciones.extend([
                "Considerar deshabilitar el servicio temporalmente",
                "Implementar controles adicionales de acceso",
                "Monitorear activamente el sistema afectado"
            ])
        
        return recomendaciones
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la vulnerabilidad a diccionario."""
        return {
            'cve_id': self.cve_id,
            'software': self.software,
            'version': self.version,
            'descripcion': self.descripcion,
            'severidad': self.severidad,
            'puntuacion_cvss': self.puntuacion_cvss,
            'fecha_descubrimiento': self.fecha_descubrimiento.isoformat(),
            'recomendaciones': self.recomendaciones
        }


class DetectorSoftware:
    """Detector de software instalado en el sistema."""
    
    def __init__(self):
        """Inicializa el detector de software."""
        self.software_detectado = []
        self.metodos_deteccion = {
            'dpkg': self._detectar_dpkg,
            'rpm': self._detectar_rpm,
            'pip': self._detectar_pip,
            'npm': self._detectar_npm,
            'snap': self._detectar_snap,
            'flatpak': self._detectar_flatpak,
            'binarios': self._detectar_binarios_comunes
        }
    
    def detectar_todo_el_software(self) -> List[Dict[str, Any]]:
        """
        Detecta todo el software instalado usando múltiples métodos.
        
        Returns:
            Lista de software detectado
        """
        software_encontrado = []
        software_visto = set()
        
        for metodo, funcion in self.metodos_deteccion.items():
            try:
                software_metodo = funcion()
                for item in software_metodo:
                    # Evitar duplicados
                    clave_unica = f"{item['nombre']}:{item['version']}"
                    if clave_unica not in software_visto:
                        item['metodo_deteccion'] = metodo
                        software_encontrado.append(item)
                        software_visto.add(clave_unica)
            except Exception as e:
                # Continuar con otros métodos si uno falla
                continue
        
        self.software_detectado = software_encontrado
        return software_encontrado
    
    def _detectar_dpkg(self) -> List[Dict[str, Any]]:
        """Detecta software usando dpkg (Debian/Ubuntu)."""
        software = []
        
        try:
            resultado = subprocess.run(
                ['dpkg', '-l'], 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            if resultado.returncode == 0:
                lineas = resultado.stdout.strip().split('\n')
                for linea in lineas[5:]:  # Saltar headers
                    if linea.startswith('ii'):  # Solo paquetes instalados
                        partes = linea.split()
                        if len(partes) >= 3:
                            nombre = partes[1]
                            version = partes[2]
                            descripcion = ' '.join(partes[3:]) if len(partes) > 3 else ''
                            
                            software.append({
                                'nombre': nombre,
                                'version': version,
                                'descripcion': descripcion,
                                'tipo': 'package'
                            })
        
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        return software
    
    def _detectar_rpm(self) -> List[Dict[str, Any]]:
        """Detecta software usando rpm (Red Hat/CentOS/Fedora)."""
        software = []
        
        try:
            resultado = subprocess.run(
                ['rpm', '-qa', '--queryformat', '%{NAME}|%{VERSION}|%{SUMMARY}\n'], 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            if resultado.returncode == 0:
                lineas = resultado.stdout.strip().split('\n')
                for linea in lineas:
                    if '|' in linea:
                        partes = linea.split('|', 2)
                        if len(partes) >= 2:
                            nombre = partes[0]
                            version = partes[1]
                            descripcion = partes[2] if len(partes) > 2 else ''
                            
                            software.append({
                                'nombre': nombre,
                                'version': version,
                                'descripcion': descripcion,
                                'tipo': 'package'
                            })
        
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        return software
    
    def _detectar_pip(self) -> List[Dict[str, Any]]:
        """Detecta paquetes Python usando pip."""
        software = []
        
        for comando_pip in ['pip3', 'pip']:
            try:
                resultado = subprocess.run(
                    [comando_pip, 'list', '--format=json'], 
                    capture_output=True, 
                    text=True, 
                    timeout=30
                )
                
                if resultado.returncode == 0:
                    paquetes = json.loads(resultado.stdout)
                    for paquete in paquetes:
                        software.append({
                            'nombre': f"python-{paquete['name']}",
                            'version': paquete['version'],
                            'descripcion': f"Paquete Python: {paquete['name']}",
                            'tipo': 'python_package'
                        })
                    break  # Si pip3 funciona, no probar pip
                    
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError, 
                    FileNotFoundError, json.JSONDecodeError):
                continue
        
        return software
    
    def _detectar_npm(self) -> List[Dict[str, Any]]:
        """Detecta paquetes Node.js usando npm."""
        software = []
        
        try:
            resultado = subprocess.run(
                ['npm', 'list', '-g', '--depth=0', '--json'], 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            if resultado.returncode == 0:
                data = json.loads(resultado.stdout)
                dependencies = data.get('dependencies', {})
                
                for nombre, info in dependencies.items():
                    version = info.get('version', 'unknown')
                    software.append({
                        'nombre': f"node-{nombre}",
                        'version': version,
                        'descripcion': f"Paquete Node.js: {nombre}",
                        'tipo': 'npm_package'
                    })
                    
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, 
                FileNotFoundError, json.JSONDecodeError):
            pass
        
        return software
    
    def _detectar_snap(self) -> List[Dict[str, Any]]:
        """Detecta paquetes Snap."""
        software = []
        
        try:
            resultado = subprocess.run(
                ['snap', 'list'], 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            if resultado.returncode == 0:
                lineas = resultado.stdout.strip().split('\n')[1:]  # Saltar header
                for linea in lineas:
                    partes = linea.split()
                    if len(partes) >= 2:
                        nombre = partes[0]
                        version = partes[1]
                        
                        software.append({
                            'nombre': f"snap-{nombre}",
                            'version': version,
                            'descripcion': f"Paquete Snap: {nombre}",
                            'tipo': 'snap_package'
                        })
                        
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        return software
    
    def _detectar_flatpak(self) -> List[Dict[str, Any]]:
        """Detecta aplicaciones Flatpak."""
        software = []
        
        try:
            resultado = subprocess.run(
                ['flatpak', 'list', '--app'], 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            if resultado.returncode == 0:
                lineas = resultado.stdout.strip().split('\n')
                for linea in lineas:
                    partes = linea.split('\t')
                    if len(partes) >= 2:
                        nombre = partes[0]
                        app_id = partes[1]
                        version = partes[2] if len(partes) > 2 else 'latest'
                        
                        software.append({
                            'nombre': f"flatpak-{nombre}",
                            'version': version,
                            'descripcion': f"Aplicación Flatpak: {app_id}",
                            'tipo': 'flatpak_app'
                        })
                        
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        return software
    
    def _detectar_binarios_comunes(self) -> List[Dict[str, Any]]:
        """Detecta binarios comunes y sus versiones."""
        software = []
        
        # Lista de binarios comunes a verificar
        binarios_comunes = {
            'apache2': ['apache2', '-v'],
            'nginx': ['nginx', '-v'],
            'mysql': ['mysql', '--version'],
            'postgresql': ['psql', '--version'],
            'php': ['php', '--version'],
            'python3': ['python3', '--version'],
            'python': ['python', '--version'],
            'node': ['node', '--version'],
            'docker': ['docker', '--version'],
            'git': ['git', '--version'],
            'openssh': ['ssh', '-V']
        }
        
        for nombre, comando in binarios_comunes.items():
            try:
                resultado = subprocess.run(
                    comando, 
                    capture_output=True, 
                    text=True, 
                    timeout=10
                )
                
                if resultado.returncode == 0:
                    output = resultado.stdout + resultado.stderr
                    version = self._extraer_version(output)
                    
                    if version:
                        software.append({
                            'nombre': nombre,
                            'version': version,
                            'descripcion': f"Binario del sistema: {nombre}",
                            'tipo': 'system_binary'
                        })
                        
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
                continue
        
        return software
    
    def _extraer_version(self, output: str) -> Optional[str]:
        """Extrae número de versión de la salida de comando."""
        # Patrones comunes de versión
        patrones = [
            r'version\s+(\d+\.\d+(?:\.\d+)?)',
            r'v(\d+\.\d+(?:\.\d+)?)',
            r'(\d+\.\d+(?:\.\d+)?)',
            r'Version\s+(\d+\.\d+(?:\.\d+)?)',
            r'Server\s+version:\s+(\S+)',
            r'(\d+\.\d+\.\d+)'
        ]
        
        for patron in patrones:
            match = re.search(patron, output, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None


class BaseDatosVulnerabilidades:
    """Base de datos local de vulnerabilidades conocidas."""
    
    def __init__(self):
        """Inicializa la base de datos de vulnerabilidades."""
        self.vulnerabilidades = self._cargar_vulnerabilidades_estaticas()
        self.ultima_actualizacion = datetime.now()
    
    def _cargar_vulnerabilidades_estaticas(self) -> Dict[str, List[Dict[str, Any]]]:
        """Carga vulnerabilidades conocidas estáticas."""
        # Base de datos estática con vulnerabilidades comunes
        vulnerabilidades = {
            'apache2': [
                {
                    'cve_id': 'CVE-2021-44228',
                    'versiones_afectadas': ['< 2.4.52'],
                    'descripcion': 'Vulnerabilidad de inyección en Log4j',
                    'severidad': 'CRITICA'
                },
                {
                    'cve_id': 'CVE-2021-41773',
                    'versiones_afectadas': ['2.4.49', '2.4.50'],
                    'descripcion': 'Path Traversal en Apache HTTP Server',
                    'severidad': 'ALTA'
                }
            ],
            'nginx': [
                {
                    'cve_id': 'CVE-2021-23017',
                    'versiones_afectadas': ['< 1.20.1'],
                    'descripcion': 'Resolver Off-by-one en nginx',
                    'severidad': 'ALTA'
                }
            ],
            'openssh': [
                {
                    'cve_id': 'CVE-2020-14145',
                    'versiones_afectadas': ['< 8.3'],
                    'descripcion': 'Información de usuario observable en OpenSSH',
                    'severidad': 'MEDIA'
                }
            ],
            'mysql': [
                {
                    'cve_id': 'CVE-2021-2471',
                    'versiones_afectadas': ['< 8.0.27'],
                    'descripcion': 'Vulnerabilidad en componente Server: Replication',
                    'severidad': 'MEDIA'
                }
            ],
            'php': [
                {
                    'cve_id': 'CVE-2021-21703',
                    'versiones_afectadas': ['< 8.0.12', '< 7.4.25'],
                    'descripcion': 'Local privilege escalation via PHP-FPM',
                    'severidad': 'ALTA'
                }
            ]
        }
        
        return vulnerabilidades
    
    def buscar_vulnerabilidades(self, software: str, version: str) -> List[Dict[str, Any]]:
        """
        Busca vulnerabilidades para un software y versión específicos.
        
        Args:
            software: Nombre del software
            version: Versión del software
            
        Returns:
            Lista de vulnerabilidades encontradas
        """
        # Normalizar nombre del software
        software_normalizado = software.lower().replace('-', '').replace('_', '')
        
        vulnerabilidades_encontradas = []
        
        # Buscar en la base de datos estática
        for soft_db, vulns in self.vulnerabilidades.items():
            if soft_db in software_normalizado or software_normalizado in soft_db:
                for vuln in vulns:
                    if self._version_vulnerable(version, vuln['versiones_afectadas']):
                        vulnerabilidades_encontradas.append(vuln)
        
        return vulnerabilidades_encontradas
    
    def _version_vulnerable(self, version: str, versiones_afectadas: List[str]) -> bool:
        """
        Determina si una versión es vulnerable.
        
        Args:
            version: Versión a verificar
            versiones_afectadas: Lista de patrones de versiones afectadas
            
        Returns:
            True si la versión es vulnerable
        """
        try:
            version_numerica = self._convertir_version_a_numero(version)
            
            for patron in versiones_afectadas:
                if self._coincide_patron_version(version_numerica, patron):
                    return True
            
            return False
            
        except Exception:
            # En caso de error, asumir que es vulnerable por precaución
            return True
    
    def _convertir_version_a_numero(self, version: str) -> Tuple[int, ...]:
        """Convierte string de versión a tupla numérica."""
        # Extraer solo números de la versión
        numeros = re.findall(r'\d+', version)
        return tuple(int(n) for n in numeros[:3])  # Tomar máximo 3 números
    
    def _coincide_patron_version(self, version: Tuple[int, ...], patron: str) -> bool:
        """Verifica si la versión coincide con el patrón."""
        if patron.startswith('< '):
            version_limite = self._convertir_version_a_numero(patron[2:])
            return version < version_limite
        elif patron.startswith('<= '):
            version_limite = self._convertir_version_a_numero(patron[3:])
            return version <= version_limite
        elif patron.startswith('> '):
            version_limite = self._convertir_version_a_numero(patron[2:])
            return version > version_limite
        elif patron.startswith('>= '):
            version_limite = self._convertir_version_a_numero(patron[3:])
            return version >= version_limite
        else:
            # Coincidencia exacta
            version_exacta = self._convertir_version_a_numero(patron)
            return version == version_exacta


class EscaneadorVulnerabilidades:
    """Escaneador principal de vulnerabilidades."""
    
    def __init__(self, siem=None):
        """
        Inicializa el escaneador de vulnerabilidades.
        
        Args:
            siem: Sistema SIEM para logging (opcional)
        """
        self.siem = siem
        self.detector_software = DetectorSoftware()
        self.base_datos = BaseDatosVulnerabilidades()
    
    def escanear_sistema_completo(self) -> Dict[str, Any]:
        """
        Realiza un escaneo completo del sistema en busca de vulnerabilidades.
        
        Returns:
            Dict con resultados del escaneo
        """
        if self.siem:
            self.siem.log_evento('INFO', 'escaneador_vulnerabilidades', 
                               'Iniciando escaneo completo de vulnerabilidades')
        
        inicio = datetime.now()
        
        # Detectar software instalado
        software_instalado = self.detector_software.detectar_todo_el_software()
        
        # Buscar vulnerabilidades
        vulnerabilidades_encontradas = []
        software_vulnerable = []
        
        for software in software_instalado:
            vulnerabilidades = self.base_datos.buscar_vulnerabilidades(
                software['nombre'], 
                software['version']
            )
            
            if vulnerabilidades:
                software_vulnerable.append(software)
                
                for vuln_data in vulnerabilidades:
                    vulnerabilidad = VulnerabilidadDetectada(
                        cve_id=vuln_data['cve_id'],
                        software=software['nombre'],
                        version=software['version'],
                        descripcion=vuln_data['descripcion'],
                        severidad=vuln_data['severidad']
                    )
                    vulnerabilidades_encontradas.append(vulnerabilidad)
        
        fin = datetime.now()
        tiempo_escaneo = (fin - inicio).total_seconds()
        
        # Calcular estadísticas
        estadisticas = self._calcular_estadisticas(
            software_instalado, 
            vulnerabilidades_encontradas
        )
        
        resultado = {
            'timestamp_escaneo': inicio.isoformat(),
            'tiempo_escaneo_segundos': tiempo_escaneo,
            'total_software': len(software_instalado),
            'software_vulnerable': len(software_vulnerable),
            'total_vulnerabilidades': len(vulnerabilidades_encontradas),
            'estadisticas': estadisticas,
            'software_instalado': [soft for soft in software_instalado],
            'vulnerabilidades': [vuln.to_dict() for vuln in vulnerabilidades_encontradas],
            'software_con_vulnerabilidades': software_vulnerable
        }
        
        if self.siem:
            self.siem.log_evento('INFO', 'escaneador_vulnerabilidades', 
                               f'Escaneo completado: {len(vulnerabilidades_encontradas)} vulnerabilidades encontradas')
        
        return resultado
    
    def escanear_software_especifico(self, nombre_software: str) -> Dict[str, Any]:
        """
        Escanea vulnerabilidades en un software específico.
        
        Args:
            nombre_software: Nombre del software a escanear
            
        Returns:
            Dict con vulnerabilidades encontradas
        """
        if self.siem:
            self.siem.log_evento('INFO', 'escaneador_vulnerabilidades', 
                               f'Escaneando vulnerabilidades en {nombre_software}')
        
        software_instalado = self.detector_software.detectar_todo_el_software()
        software_coincidente = [
            soft for soft in software_instalado 
            if nombre_software.lower() in soft['nombre'].lower()
        ]
        
        vulnerabilidades_encontradas = []
        
        for software in software_coincidente:
            vulnerabilidades = self.base_datos.buscar_vulnerabilidades(
                software['nombre'], 
                software['version']
            )
            
            for vuln_data in vulnerabilidades:
                vulnerabilidad = VulnerabilidadDetectada(
                    cve_id=vuln_data['cve_id'],
                    software=software['nombre'],
                    version=software['version'],
                    descripcion=vuln_data['descripcion'],
                    severidad=vuln_data['severidad']
                )
                vulnerabilidades_encontradas.append(vulnerabilidad)
        
        return {
            'software_buscado': nombre_software,
            'software_encontrado': software_coincidente,
            'vulnerabilidades': [vuln.to_dict() for vuln in vulnerabilidades_encontradas],
            'timestamp_escaneo': datetime.now().isoformat()
        }
    
    def _calcular_estadisticas(self, software_instalado: List[Dict], 
                             vulnerabilidades: List[VulnerabilidadDetectada]) -> Dict[str, Any]:
        """Calcula estadísticas del escaneo."""
        if not vulnerabilidades:
            return {
                'por_severidad': {},
                'software_mas_vulnerable': None,
                'puntuacion_riesgo_promedio': 0.0,
                'porcentaje_software_vulnerable': 0.0
            }
        
        # Contar por severidad
        severidades = {}
        puntuaciones = []
        
        for vuln in vulnerabilidades:
            severidad = vuln.severidad
            severidades[severidad] = severidades.get(severidad, 0) + 1
            puntuaciones.append(vuln.puntuacion_cvss)
        
        # Software más vulnerable
        vulnerabilidades_por_software = {}
        for vuln in vulnerabilidades:
            software = vuln.software
            if software not in vulnerabilidades_por_software:
                vulnerabilidades_por_software[software] = 0
            vulnerabilidades_por_software[software] += 1
        
        software_mas_vulnerable = None
        if vulnerabilidades_por_software:
            software_mas_vulnerable = max(
                vulnerabilidades_por_software.items(), 
                key=lambda x: x[1]
            )
        
        return {
            'por_severidad': severidades,
            'software_mas_vulnerable': software_mas_vulnerable,
            'puntuacion_riesgo_promedio': sum(puntuaciones) / len(puntuaciones),
            'porcentaje_software_vulnerable': (
                len(set(vuln.software for vuln in vulnerabilidades)) / 
                len(software_instalado) * 100 if software_instalado else 0
            )
        }
    
    def generar_reporte_markdown(self, resultado_escaneo: Dict[str, Any]) -> str:
        """
        Genera un reporte en formato Markdown del escaneo.
        
        Args:
            resultado_escaneo: Resultado del escaneo de vulnerabilidades
            
        Returns:
            String con el reporte en formato Markdown
        """
        estadisticas = resultado_escaneo['estadisticas']
        
        reporte = f"""# Reporte de Escaneo de Vulnerabilidades

## Resumen Ejecutivo
- **Fecha del escaneo:** {resultado_escaneo['timestamp_escaneo']}
- **Tiempo de escaneo:** {resultado_escaneo['tiempo_escaneo_segundos']:.2f} segundos
- **Software analizado:** {resultado_escaneo['total_software']}
- **Software vulnerable:** {resultado_escaneo['software_vulnerable']}
- **Total vulnerabilidades:** {resultado_escaneo['total_vulnerabilidades']}
- **Porcentaje vulnerable:** {estadisticas['porcentaje_software_vulnerable']:.1f}%

## Distribución por Severidad
"""
        
        for severidad, cantidad in estadisticas['por_severidad'].items():
            emoji = {
                'CRITICA': '🔴',
                'ALTA': '🟠', 
                'MEDIA': '🟡',
                'BAJA': '🟢'
            }.get(severidad, '⚪')
            
            reporte += f"- {emoji} **{severidad}:** {cantidad}\n"
        
        if estadisticas['software_mas_vulnerable']:
            software, count = estadisticas['software_mas_vulnerable']
            reporte += f"\n## Software Más Vulnerable\n"
            reporte += f"**{software}** con {count} vulnerabilidades detectadas\n"
        
        reporte += f"\n## Puntuación de Riesgo\n"
        reporte += f"**Promedio CVSS:** {estadisticas['puntuacion_riesgo_promedio']:.1f}/10\n"
        
        # Mostrar vulnerabilidades críticas y altas
        vulns_criticas = [v for v in resultado_escaneo['vulnerabilidades'] 
                         if v['severidad'] in ['CRITICA', 'ALTA']]
        
        if vulns_criticas:
            reporte += f"\n## Vulnerabilidades Críticas y Altas\n\n"
            for vuln in vulns_criticas[:10]:  # Mostrar máximo 10
                emoji = '🔴' if vuln['severidad'] == 'CRITICA' else '🟠'
                reporte += f"### {emoji} {vuln['cve_id']}\n"
                reporte += f"- **Software:** {vuln['software']} v{vuln['version']}\n"
                reporte += f"- **Severidad:** {vuln['severidad']}\n"
                reporte += f"- **CVSS:** {vuln['puntuacion_cvss']}\n"
                reporte += f"- **Descripción:** {vuln['descripcion']}\n"
                reporte += f"- **Recomendaciones:**\n"
                for rec in vuln['recomendaciones'][:3]:
                    reporte += f"  - {rec}\n"
                reporte += "\n"
        
        reporte += f"\n---\n*Reporte generado el {datetime.now().isoformat()} por Ares Aegis*\n"
        
        return reporte
