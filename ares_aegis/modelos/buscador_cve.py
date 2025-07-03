#!/usr/bin/env python3
"""
Buscador de CVE - Ares Aegis
Módulo para búsqueda y análisis de vulnerabilidades CVE

Este módulo permite buscar vulnerabilidades conocidas por CVE,
analizar software instalado y correlacionar con bases de datos offline.

Autor: DogSoulDev
Versión: 2.0.0 - "Los Oráculos de Delfos"
"""

import os
import re
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, NamedTuple, Set
from dataclasses import dataclass
from ..utilidades.ayuda_logging import configurar_logger_modulo


@dataclass
class CVEInfo:
    """Información de una vulnerabilidad CVE."""
    cve_id: str
    description: str
    cvss_score: float
    severity: str
    published_date: datetime
    modified_date: datetime
    affected_products: List[str]
    references: List[str]
    cwe_ids: List[str]
    vector: str
    exploitation_available: bool
    metadatos: Dict[str, Any]


@dataclass
class SoftwareInfo:
    """Información de software instalado."""
    nombre: str
    version: str
    vendor: str
    tipo: str  # system, package, service
    origen: str  # dpkg, rpm, snap, etc.
    instalacion_fecha: Optional[datetime]
    metadatos: Dict[str, Any]


class ResultadoBusquedaCVE(NamedTuple):
    """Resultado de búsqueda de CVEs."""
    software: SoftwareInfo
    cves_encontrados: List[CVEInfo]
    nivel_riesgo: str
    recomendaciones: List[str]


class BuscadorCVE:
    """Buscador principal de vulnerabilidades CVE."""
    
    def __init__(self, siem=None):
        """
        Inicializa el buscador de CVE.
        
        Args:
            siem: Instancia del SIEM para registro de eventos
        """
        self.logger = configurar_logger_modulo("buscador_cve")
        self.siem = siem
        
        # Configuración de rutas
        self.directorio_datos = Path("/home/dogsoul/Ares-Aegis/recursos")
        self.archivo_cve_db = self.directorio_datos / "cve_database.json"
        self.archivo_software_cache = self.directorio_datos / "software_cache.json"
        
        # Base de datos CVE en memoria
        self.cve_database: Dict[str, CVEInfo] = {}
        self.software_instalado: List[SoftwareInfo] = []
        self.cache_busquedas: Dict[str, List[CVEInfo]] = {}
        
        # Configuración de severidad
        self.mapeo_severidad = {
            (0.0, 3.9): "BAJO",
            (4.0, 6.9): "MEDIO", 
            (7.0, 8.9): "ALTO",
            (9.0, 10.0): "CRITICO"
        }
        
        # Patrones para detección de versiones
        self.patrones_version = {
            'version_simple': re.compile(r'(\d+\.?\d*\.?\d*\.?\d*)'),
            'version_completa': re.compile(r'(\d+\.\d+\.\d+(?:\.\d+)?(?:-\w+)?(?:\+\w+)?)'),
            'version_ubuntu': re.compile(r'(\d+\.\d+\.\d+)-(\d+)ubuntu(\d+)'),
            'version_debian': re.compile(r'(\d+\.\d+\.\d+)-(\d+)'),
        }
        
        # Productos críticos para monitoreo especial
        self.productos_criticos = {
            'openssh', 'openssl', 'apache2', 'nginx', 'mysql', 'postgresql',
            'php', 'python3', 'nodejs', 'docker', 'kernel', 'systemd',
            'sudo', 'bash', 'curl', 'wget', 'git', 'vim', 'nano'
        }
        
        self.logger.info("Los Oráculos de Delfos despiertan para revelar las vulnerabilidades")
        
        # Inicializar datos
        self._inicializar_datos()
    
    def _inicializar_datos(self):
        """Inicializa la base de datos CVE y escanea software."""
        try:
            # Crear directorio de recursos si no existe
            self.directorio_datos.mkdir(exist_ok=True)
            
            # Cargar base de datos CVE
            self._cargar_base_datos_cve()
            
            # Escanear software instalado
            self._escanear_software_instalado()
            
            self.logger.info(f"Base de datos inicializada: {len(self.cve_database)} CVEs, {len(self.software_instalado)} paquetes")
            
        except Exception as e:
            self.logger.error(f"Error inicializando datos: {e}")
    
    def _cargar_base_datos_cve(self):
        """Carga la base de datos CVE desde archivo o crea una básica."""
        if self.archivo_cve_db.exists():
            try:
                with open(self.archivo_cve_db, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for cve_id, cve_data in data.items():
                    self.cve_database[cve_id] = CVEInfo(
                        cve_id=cve_data['cve_id'],
                        description=cve_data['description'],
                        cvss_score=cve_data['cvss_score'],
                        severity=cve_data['severity'],
                        published_date=datetime.fromisoformat(cve_data['published_date']),
                        modified_date=datetime.fromisoformat(cve_data['modified_date']),
                        affected_products=cve_data['affected_products'],
                        references=cve_data['references'],
                        cwe_ids=cve_data['cwe_ids'],
                        vector=cve_data['vector'],
                        exploitation_available=cve_data['exploitation_available'],
                        metadatos=cve_data.get('metadatos', {})
                    )
                
                self.logger.info(f"Base de datos CVE cargada: {len(self.cve_database)} entradas")
                
            except Exception as e:
                self.logger.error(f"Error cargando base de datos CVE: {e}")
                self._crear_base_datos_ejemplo()
        else:
            self._crear_base_datos_ejemplo()
    
    def _crear_base_datos_ejemplo(self):
        """Crea una base de datos CVE de ejemplo con vulnerabilidades conocidas."""
        self.logger.info("Creando base de datos CVE de ejemplo")
        
        # CVEs de ejemplo basados en vulnerabilidades reales conocidas
        cves_ejemplo = [
            {
                'cve_id': 'CVE-2021-44228',
                'description': 'Apache Log4j2 JNDI features do not protect against attacker controlled LDAP and other JNDI related endpoints',
                'cvss_score': 10.0,
                'severity': 'CRITICO',
                'published_date': '2021-12-10',
                'modified_date': '2023-11-07',
                'affected_products': ['log4j', 'apache-log4j', 'log4j-core'],
                'references': ['https://nvd.nist.gov/vuln/detail/CVE-2021-44228'],
                'cwe_ids': ['CWE-502', 'CWE-400', 'CWE-20'],
                'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H',
                'exploitation_available': True,
                'metadatos': {'log4shell': True, 'rce': True}
            },
            {
                'cve_id': 'CVE-2022-0778',
                'description': 'Infinite loop in BN_mod_sqrt() reachable when parsing certificates',
                'cvss_score': 7.5,
                'severity': 'ALTO',
                'published_date': '2022-03-15',
                'modified_date': '2023-11-07',
                'affected_products': ['openssl'],
                'references': ['https://nvd.nist.gov/vuln/detail/CVE-2022-0778'],
                'cwe_ids': ['CWE-835'],
                'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H',
                'exploitation_available': False,
                'metadatos': {'dos': True}
            },
            {
                'cve_id': 'CVE-2021-4034',
                'description': 'A local privilege escalation vulnerability was found on polkit',
                'cvss_score': 7.8,
                'severity': 'ALTO',
                'published_date': '2022-01-26',
                'modified_date': '2023-11-07',
                'affected_products': ['polkit', 'policykit-1'],
                'references': ['https://nvd.nist.gov/vuln/detail/CVE-2021-4034'],
                'cwe_ids': ['CWE-269'],
                'vector': 'CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H',
                'exploitation_available': True,
                'metadatos': {'privilege_escalation': True, 'pwnkit': True}
            },
            {
                'cve_id': 'CVE-2022-22965',
                'description': 'Spring Framework RCE via Data Binding on JDK 9+',
                'cvss_score': 9.8,
                'severity': 'CRITICO',
                'published_date': '2022-04-01',
                'modified_date': '2023-11-07',
                'affected_products': ['spring-framework', 'spring-core'],
                'references': ['https://nvd.nist.gov/vuln/detail/CVE-2022-22965'],
                'cwe_ids': ['CWE-94'],
                'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H',
                'exploitation_available': True,
                'metadatos': {'spring4shell': True, 'rce': True}
            },
            {
                'cve_id': 'CVE-2021-3156',
                'description': 'Heap-based buffer overflow in sudo',
                'cvss_score': 7.8,
                'severity': 'ALTO',
                'published_date': '2021-01-26',
                'modified_date': '2023-11-07',
                'affected_products': ['sudo'],
                'references': ['https://nvd.nist.gov/vuln/detail/CVE-2021-3156'],
                'cwe_ids': ['CWE-122'],
                'vector': 'CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H',
                'exploitation_available': True,
                'metadatos': {'baron_samedit': True, 'privilege_escalation': True}
            },
            {
                'cve_id': 'CVE-2022-0847',
                'description': 'Improper permission validation in Linux kernel',
                'cvss_score': 7.8,
                'severity': 'ALTO',
                'published_date': '2022-03-07',
                'modified_date': '2023-11-07',
                'affected_products': ['linux-kernel'],
                'references': ['https://nvd.nist.gov/vuln/detail/CVE-2022-0847'],
                'cwe_ids': ['CWE-269'],
                'vector': 'CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H',
                'exploitation_available': True,
                'metadatos': {'dirty_pipe': True, 'privilege_escalation': True}
            }
        ]
        
        # Convertir a objetos CVEInfo
        for cve_data in cves_ejemplo:
            cve_info = CVEInfo(
                cve_id=cve_data['cve_id'],
                description=cve_data['description'],
                cvss_score=cve_data['cvss_score'],
                severity=cve_data['severity'],
                published_date=datetime.fromisoformat(cve_data['published_date']),
                modified_date=datetime.fromisoformat(cve_data['modified_date']),
                affected_products=cve_data['affected_products'],
                references=cve_data['references'],
                cwe_ids=cve_data['cwe_ids'],
                vector=cve_data['vector'],
                exploitation_available=cve_data['exploitation_available'],
                metadatos=cve_data['metadatos']
            )
            self.cve_database[cve_info.cve_id] = cve_info
        
        # Guardar base de datos
        self._guardar_base_datos_cve()
    
    def _guardar_base_datos_cve(self):
        """Guarda la base de datos CVE en archivo."""
        try:
            data = {}
            for cve_id, cve_info in self.cve_database.items():
                data[cve_id] = {
                    'cve_id': cve_info.cve_id,
                    'description': cve_info.description,
                    'cvss_score': cve_info.cvss_score,
                    'severity': cve_info.severity,
                    'published_date': cve_info.published_date.isoformat(),
                    'modified_date': cve_info.modified_date.isoformat(),
                    'affected_products': cve_info.affected_products,
                    'references': cve_info.references,
                    'cwe_ids': cve_info.cwe_ids,
                    'vector': cve_info.vector,
                    'exploitation_available': cve_info.exploitation_available,
                    'metadatos': cve_info.metadatos
                }
            
            with open(self.archivo_cve_db, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.info("Base de datos CVE guardada")
            
        except Exception as e:
            self.logger.error(f"Error guardando base de datos CVE: {e}")
    
    def _escanear_software_instalado(self):
        """Escanea el software instalado en el sistema."""
        self.software_instalado.clear()
        
        # Escanear paquetes dpkg (Debian/Ubuntu)
        self._escanear_dpkg()
        
        # Escanear paquetes snap
        self._escanear_snap()
        
        # Escanear servicios systemd
        self._escanear_servicios_systemd()
        
        # Escanear versión del kernel
        self._escanear_kernel()
        
        # Guardar cache
        self._guardar_cache_software()
        
        self.logger.info(f"Escaneado completado: {len(self.software_instalado)} paquetes encontrados")
    
    def _escanear_dpkg(self):
        """Escanea paquetes instalados con dpkg."""
        try:
            resultado = subprocess.run(
                ['dpkg-query', '-W', '-f=${Package}\t${Version}\t${Status}\n'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if resultado.returncode == 0:
                for linea in resultado.stdout.strip().split('\n'):
                    if not linea:
                        continue
                    
                    partes = linea.split('\t')
                    if len(partes) >= 3 and 'installed' in partes[2]:
                        nombre = partes[0]
                        version = partes[1]
                        
                        software = SoftwareInfo(
                            nombre=nombre,
                            version=version,
                            vendor='debian',
                            tipo='package',
                            origen='dpkg',
                            instalacion_fecha=None,
                            metadatos={'status': partes[2]}
                        )
                        self.software_instalado.append(software)
        
        except Exception as e:
            self.logger.error(f"Error escaneando dpkg: {e}")
    
    def _escanear_snap(self):
        """Escanea paquetes snap instalados."""
        try:
            resultado = subprocess.run(
                ['snap', 'list'],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if resultado.returncode == 0:
                lineas = resultado.stdout.strip().split('\n')[1:]  # Skip header
                for linea in lineas:
                    if not linea:
                        continue
                    
                    partes = linea.split()
                    if len(partes) >= 3:
                        nombre = partes[0]
                        version = partes[1]
                        
                        software = SoftwareInfo(
                            nombre=nombre,
                            version=version,
                            vendor='canonical',
                            tipo='package',
                            origen='snap',
                            instalacion_fecha=None,
                            metadatos={'channel': partes[3] if len(partes) > 3 else 'stable'}
                        )
                        self.software_instalado.append(software)
        
        except (subprocess.CalledProcessError, FileNotFoundError):
            # snap no está instalado o no disponible
            pass
        except Exception as e:
            self.logger.error(f"Error escaneando snap: {e}")
    
    def _escanear_servicios_systemd(self):
        """Escanea servicios systemd activos."""
        try:
            resultado = subprocess.run(
                ['systemctl', 'list-units', '--type=service', '--state=active', '--no-pager', '--plain'],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if resultado.returncode == 0:
                for linea in resultado.stdout.strip().split('\n'):
                    if '.service' in linea and 'active' in linea:
                        partes = linea.split()
                        if partes:
                            nombre_servicio = partes[0].replace('.service', '')
                            
                            software = SoftwareInfo(
                                nombre=nombre_servicio,
                                version='unknown',
                                vendor='system',
                                tipo='service',
                                origen='systemd',
                                instalacion_fecha=None,
                                metadatos={'estado': 'active'}
                            )
                            self.software_instalado.append(software)
        
        except Exception as e:
            self.logger.error(f"Error escaneando servicios systemd: {e}")
    
    def _escanear_kernel(self):
        """Escanea la versión del kernel."""
        try:
            resultado = subprocess.run(
                ['uname', '-r'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if resultado.returncode == 0:
                version_kernel = resultado.stdout.strip()
                
                software = SoftwareInfo(
                    nombre='linux-kernel',
                    version=version_kernel,
                    vendor='linux',
                    tipo='system',
                    origen='kernel',
                    instalacion_fecha=None,
                    metadatos={'arch': 'x86_64'}  # Simplificado
                )
                self.software_instalado.append(software)
        
        except Exception as e:
            self.logger.error(f"Error obteniendo versión del kernel: {e}")
    
    def _guardar_cache_software(self):
        """Guarda el cache de software instalado."""
        try:
            data = []
            for software in self.software_instalado:
                data.append({
                    'nombre': software.nombre,
                    'version': software.version,
                    'vendor': software.vendor,
                    'tipo': software.tipo,
                    'origen': software.origen,
                    'instalacion_fecha': software.instalacion_fecha.isoformat() if software.instalacion_fecha else None,
                    'metadatos': software.metadatos
                })
            
            with open(self.archivo_software_cache, 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'software': data
                }, f, indent=2, ensure_ascii=False)
        
        except Exception as e:
            self.logger.error(f"Error guardando cache de software: {e}")
    
    def buscar_cves_por_software(self, nombre_software: str, version: Optional[str] = None) -> List[CVEInfo]:
        """
        Busca CVEs para un software específico.
        
        Args:
            nombre_software: Nombre del software
            version: Versión específica (opcional)
            
        Returns:
            Lista de CVEs encontrados
        """
        clave_cache = f"{nombre_software}:{version}" if version else nombre_software
        
        if clave_cache in self.cache_busquedas:
            return self.cache_busquedas[clave_cache]
        
        cves_encontrados = []
        
        for cve_info in self.cve_database.values():
            if self._software_afectado(cve_info, nombre_software, version):
                cves_encontrados.append(cve_info)
        
        # Ordenar por CVSS score (mayor a menor)
        cves_encontrados.sort(key=lambda cve: cve.cvss_score, reverse=True)
        
        # Guardar en cache
        self.cache_busquedas[clave_cache] = cves_encontrados
        
        return cves_encontrados
    
    def _software_afectado(self, cve_info: CVEInfo, nombre_software: str, version: Optional[str] = None) -> bool:
        """
        Verifica si un software está afectado por un CVE.
        
        Args:
            cve_info: Información del CVE
            nombre_software: Nombre del software
            version: Versión del software
            
        Returns:
            True si el software está afectado
        """
        # Buscar coincidencias en productos afectados
        nombre_lower = nombre_software.lower()
        
        for producto in cve_info.affected_products:
            producto_lower = producto.lower()
            
            # Coincidencia exacta o parcial
            if (nombre_lower == producto_lower or 
                nombre_lower in producto_lower or 
                producto_lower in nombre_lower):
                
                # Si no se especifica versión, considerar afectado
                if not version:
                    return True
                
                # Aquí se podría implementar lógica más compleja de comparación de versiones
                # Por simplicidad, asumir que está afectado
                return True
        
        return False
    
    def analizar_sistema_completo(self) -> List[ResultadoBusquedaCVE]:
        """
        Analiza todo el sistema en busca de vulnerabilidades.
        
        Returns:
            Lista de resultados de búsqueda para cada software
        """
        self.logger.info("Los Oráculos inician la revelación de vulnerabilidades del reino")
        
        resultados = []
        software_analizado = 0
        
        for software in self.software_instalado:
            try:
                cves_encontrados = self.buscar_cves_por_software(software.nombre, software.version)
                
                if cves_encontrados or software.nombre.lower() in self.productos_criticos:
                    nivel_riesgo = self._calcular_nivel_riesgo(cves_encontrados)
                    recomendaciones = self._generar_recomendaciones(software, cves_encontrados)
                    
                    resultado = ResultadoBusquedaCVE(
                        software=software,
                        cves_encontrados=cves_encontrados,
                        nivel_riesgo=nivel_riesgo,
                        recomendaciones=recomendaciones
                    )
                    resultados.append(resultado)
                
                software_analizado += 1
                
            except Exception as e:
                self.logger.error(f"Error analizando software {software.nombre}: {e}")
        
        # Ordenar resultados por nivel de riesgo
        orden_riesgo = {"CRITICO": 4, "ALTO": 3, "MEDIO": 2, "BAJO": 1, "SIN_RIESGO": 0}
        resultados.sort(key=lambda r: orden_riesgo.get(r.nivel_riesgo, 0), reverse=True)
        
        # Registrar en SIEM
        if self.siem:
            from .siem import TipoEvento
            vulnerabilidades_criticas = sum(1 for r in resultados if r.nivel_riesgo == "CRITICO")
            
            self.siem.registrar_evento(
                TipoEvento.PROCESO_SOSPECHOSO,
                f"Los Oráculos revelan {len(resultados)} vulnerabilidades en {software_analizado} componentes",
                {
                    "software_analizado": software_analizado,
                    "vulnerabilidades_encontradas": len(resultados),
                    "vulnerabilidades_criticas": vulnerabilidades_criticas,
                    "componente": "buscador_cve"
                },
                "ALTO" if vulnerabilidades_criticas > 0 else "MEDIO"
            )
        
        self.logger.info(f"Análisis completado: {len(resultados)} vulnerabilidades encontradas en {software_analizado} paquetes")
        
        return resultados
    
    def _calcular_nivel_riesgo(self, cves: List[CVEInfo]) -> str:
        """Calcula el nivel de riesgo basado en los CVEs encontrados."""
        if not cves:
            return "SIN_RIESGO"
        
        # Obtener el CVSS score más alto
        max_score = max(cve.cvss_score for cve in cves)
        
        # Mapear score a nivel de riesgo
        for (min_score, max_score_range), nivel in self.mapeo_severidad.items():
            if min_score <= max_score <= max_score_range:
                return nivel
        
        return "BAJO"
    
    def _generar_recomendaciones(self, software: SoftwareInfo, cves: List[CVEInfo]) -> List[str]:
        """Genera recomendaciones de seguridad para un software."""
        recomendaciones = []
        
        if not cves:
            if software.nombre.lower() in self.productos_criticos:
                recomendaciones.append("Mantener actualizado - componente crítico del sistema")
            return recomendaciones
        
        # Recomendaciones basadas en CVEs
        cves_criticos = [cve for cve in cves if cve.cvss_score >= 9.0]
        cves_altos = [cve for cve in cves if 7.0 <= cve.cvss_score < 9.0]
        
        if cves_criticos:
            recomendaciones.append(f"URGENTE: Actualizar inmediatamente - {len(cves_criticos)} vulnerabilidades críticas")
        
        if cves_altos:
            recomendaciones.append(f"Prioridad alta: Actualizar pronto - {len(cves_altos)} vulnerabilidades de riesgo alto")
        
        # Recomendaciones específicas por tipo de software
        if software.tipo == 'service':
            recomendaciones.append("Considerar deshabilitar el servicio si no es esencial")
        
        if software.origen == 'dpkg':
            recomendaciones.append(f"Ejecutar: sudo apt update && sudo apt upgrade {software.nombre}")
        elif software.origen == 'snap':
            recomendaciones.append(f"Ejecutar: sudo snap refresh {software.nombre}")
        
        # Verificar si hay exploits disponibles
        exploits_disponibles = any(cve.exploitation_available for cve in cves)
        if exploits_disponibles:
            recomendaciones.append("⚠️ ATENCIÓN: Exploits públicos disponibles - riesgo inmediato")
        
        return recomendaciones
    
    def buscar_cve_por_id(self, cve_id: str) -> Optional[CVEInfo]:
        """
        Busca un CVE específico por ID.
        
        Args:
            cve_id: ID del CVE (ej: CVE-2021-44228)
            
        Returns:
            Información del CVE o None si no se encuentra
        """
        return self.cve_database.get(cve_id.upper())
    
    def buscar_cves_por_descripcion(self, termino_busqueda: str) -> List[CVEInfo]:
        """
        Busca CVEs por término en la descripción.
        
        Args:
            termino_busqueda: Término a buscar en las descripciones
            
        Returns:
            Lista de CVEs que contienen el término
        """
        termino_lower = termino_busqueda.lower()
        cves_encontrados = []
        
        for cve_info in self.cve_database.values():
            if termino_lower in cve_info.description.lower():
                cves_encontrados.append(cve_info)
        
        # Ordenar por relevancia (CVSS score)
        cves_encontrados.sort(key=lambda cve: cve.cvss_score, reverse=True)
        
        return cves_encontrados
    
    def obtener_cves_recientes(self, dias: int = 30) -> List[CVEInfo]:
        """
        Obtiene CVEs publicados en los últimos días.
        
        Args:
            dias: Número de días hacia atrás
            
        Returns:
            Lista de CVEs recientes
        """
        fecha_limite = datetime.now() - timedelta(days=dias)
        
        cves_recientes = [
            cve for cve in self.cve_database.values()
            if cve.published_date > fecha_limite
        ]
        
        # Ordenar por fecha de publicación (más reciente primero)
        cves_recientes.sort(key=lambda cve: cve.published_date, reverse=True)
        
        return cves_recientes
    
    def obtener_cves_criticos(self) -> List[CVEInfo]:
        """Obtiene todos los CVEs con nivel crítico."""
        return [
            cve for cve in self.cve_database.values()
            if cve.cvss_score >= 9.0
        ]
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas del buscador CVE."""
        total_cves = len(self.cve_database)
        total_software = len(self.software_instalado)
        
        # Contar por severidad
        conteo_severidad = {"CRITICO": 0, "ALTO": 0, "MEDIO": 0, "BAJO": 0}
        for cve in self.cve_database.values():
            conteo_severidad[cve.severity] += 1
        
        # Software crítico instalado
        software_critico = [
            s for s in self.software_instalado
            if s.nombre.lower() in self.productos_criticos
        ]
        
        return {
            'total_cves_database': total_cves,
            'total_software_instalado': total_software,
            'software_critico_instalado': len(software_critico),
            'conteo_por_severidad': conteo_severidad,
            'cache_busquedas': len(self.cache_busquedas),
            'ultima_actualizacion': datetime.now().isoformat()
        }
    
    def generar_reporte_vulnerabilidades(self) -> str:
        """Genera un reporte completo de vulnerabilidades en formato Markdown."""
        resultados = self.analizar_sistema_completo()
        stats = self.obtener_estadisticas()
        
        md = "# 🔮 Revelaciones de los Oráculos de Delfos\n\n"
        md += f"**Total de CVEs en Base:** {stats['total_cves_database']}\n"
        md += f"**Software Analizado:** {stats['total_software_instalado']}\n"
        md += f"**Componentes Críticos:** {stats['software_critico_instalado']}\n"
        md += f"**Vulnerabilidades Encontradas:** {len(resultados)}\n"
        md += f"**Fecha de Análisis:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # Resumen por nivel de riesgo
        resumen_riesgo = {}
        for resultado in resultados:
            nivel = resultado.nivel_riesgo
            resumen_riesgo[nivel] = resumen_riesgo.get(nivel, 0) + 1
        
        if resumen_riesgo:
            md += "## 📊 Resumen por Nivel de Riesgo\n\n"
            md += "| Nivel | Cantidad |\n"
            md += "|-------|----------|\n"
            
            emoji_riesgo = {
                "CRITICO": "🔴",
                "ALTO": "🟠", 
                "MEDIO": "🟡",
                "BAJO": "🟢",
                "SIN_RIESGO": "⚪"
            }
            
            for nivel in ["CRITICO", "ALTO", "MEDIO", "BAJO", "SIN_RIESGO"]:
                if nivel in resumen_riesgo:
                    emoji = emoji_riesgo.get(nivel, "⚪")
                    md += f"| {emoji} {nivel} | {resumen_riesgo[nivel]} |\n"
            md += "\n"
        
        # Vulnerabilidades críticas
        vulnerabilidades_criticas = [r for r in resultados if r.nivel_riesgo == "CRITICO"]
        if vulnerabilidades_criticas:
            md += "## 🚨 Vulnerabilidades Críticas\n\n"
            
            for resultado in vulnerabilidades_criticas[:10]:  # Top 10
                software = resultado.software
                cves = resultado.cves_encontrados
                
                md += f"### {software.nombre} ({software.version})\n\n"
                
                if cves:
                    md += "| CVE | CVSS | Descripción |\n"
                    md += "|-----|------|-------------|\n"
                    
                    for cve in cves[:3]:  # Top 3 CVEs por software
                        desc_corta = cve.description[:80] + "..." if len(cve.description) > 80 else cve.description
                        md += f"| {cve.cve_id} | {cve.cvss_score} | {desc_corta} |\n"
                    md += "\n"
                
                # Recomendaciones
                if resultado.recomendaciones:
                    md += "**Recomendaciones:**\n"
                    for rec in resultado.recomendaciones:
                        md += f"- {rec}\n"
                    md += "\n"
        
        # Software sin vulnerabilidades pero crítico
        software_critico_seguro = [
            s for s in self.software_instalado
            if (s.nombre.lower() in self.productos_criticos and
                not any(r.software.nombre == s.nombre for r in resultados))
        ]
        
        if software_critico_seguro:
            md += "## ✅ Componentes Críticos Sin Vulnerabilidades Conocidas\n\n"
            md += "| Software | Versión | Origen |\n"
            md += "|----------|---------|--------|\n"
            
            for software in software_critico_seguro[:10]:
                md += f"| {software.nombre} | {software.version} | {software.origen} |\n"
            md += "\n"
        
        # CVEs recientes
        cves_recientes = self.obtener_cves_recientes(7)  # Última semana
        if cves_recientes:
            md += "## 🆕 CVEs Recientes (Última Semana)\n\n"
            md += "| CVE | CVSS | Severidad | Producto |\n"
            md += "|-----|------|-----------|----------|\n"
            
            for cve in cves_recientes[:10]:
                productos = ', '.join(cve.affected_products[:2])
                if len(cve.affected_products) > 2:
                    productos += "..."
                md += f"| {cve.cve_id} | {cve.cvss_score} | {cve.severity} | {productos} |\n"
            md += "\n"
        
        md += "---\n"
        md += "*Revelaciones proporcionadas por los Oráculos de Delfos de Ares Aegis*\n"
        
        return md
    
    def exportar_resultados_json(self, resultados: List[ResultadoBusquedaCVE]) -> Dict[str, Any]:
        """Exporta los resultados de búsqueda en formato JSON."""
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'total_resultados': len(resultados),
            'estadisticas': self.obtener_estadisticas(),
            'resultados': []
        }
        
        for resultado in resultados:
            resultado_dict = {
                'software': {
                    'nombre': resultado.software.nombre,
                    'version': resultado.software.version,
                    'vendor': resultado.software.vendor,
                    'tipo': resultado.software.tipo,
                    'origen': resultado.software.origen
                },
                'nivel_riesgo': resultado.nivel_riesgo,
                'recomendaciones': resultado.recomendaciones,
                'cves': []
            }
            
            for cve in resultado.cves_encontrados:
                resultado_dict['cves'].append({
                    'cve_id': cve.cve_id,
                    'cvss_score': cve.cvss_score,
                    'severity': cve.severity,
                    'description': cve.description,
                    'published_date': cve.published_date.isoformat(),
                    'affected_products': cve.affected_products,
                    'exploitation_available': cve.exploitation_available
                })
            
            export_data['resultados'].append(resultado_dict)
        
        return export_data
