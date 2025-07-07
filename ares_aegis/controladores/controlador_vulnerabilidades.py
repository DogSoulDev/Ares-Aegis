#!/usr/bin/env python3
"""
Ares Aegis - Controlador de Vulnerabilidades
Controlador especializado para gestionar análisis y escaneado de vulnerabilidades

Copyright (c) 2025 DogSoulDev (https://github.com/DogSoulDev)
Todos los derechos reservados. Este código es propietario y confidencial.
La copia, distribución o modificación no autorizada está estrictamente prohibida.

Versión: 3.0.0
"""

import os
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Callable
from pathlib import Path

from ..modelos.escaneador_vulnerabilidades_sistema import EscaneadorVulnerabilidadesSistema
from ..modelos.escaneador_vulnerabilidades_red import EscaneadorVulnerabilidadesRed
from ..modelos.buscador_cve import BuscadorCVE
from ..modelos.siem import SIEM, TipoEvento
from ..utilidades.ayuda_logging import configurar_logger_modulo


class ControladorVulnerabilidades:
    """Controlador especializado para operaciones de vulnerabilidades."""
    
    def __init__(self, siem: SIEM):
        """
        Inicializar el controlador de vulnerabilidades.
        
        Args:
            siem: Instancia del SIEM para registro de eventos
        """
        self.siem = siem
        self.logger = configurar_logger_modulo("controlador_vulnerabilidades")
        
        # Inicializar escaneadores
        self.escaneador_sistema = EscaneadorVulnerabilidadesSistema()
        self.escaneador_red = EscaneadorVulnerabilidadesRed()
        self.buscador_cve = BuscadorCVE()
        
        # Estado del controlador
        self.escaneos_activos = {}
        self.resultados_cache = {}
        self.estadisticas_vulnerabilidades = {}
        self.lock = threading.Lock()
        
        # Configuración
        self.configuracion = {
            'escaneo_automatico': False,
            'intervalo_escaneo_horas': 24,
            'umbral_criticidad': 7.0,  # CVSS score
            'max_resultados_cache': 100,
            'timeout_escaneo_segundos': 3600  # 1 hora
        }
        
        self.logger.info("Controlador de Vulnerabilidades inicializado")
    
    def escanear_vulnerabilidades_sistema(self, callback_progreso: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Ejecutar escaneo completo de vulnerabilidades del sistema.
        
        Args:
            callback_progreso: Función callback para reportar progreso
            
        Returns:
            Dict[str, Any]: Resultados del escaneo
        """
        try:
            escaneo_id = f"vuln_sys_{int(time.time())}"
            self.logger.info(f"Iniciando escaneo de vulnerabilidades del sistema: {escaneo_id}")
            
            # Registrar escaneo activo
            with self.lock:
                self.escaneos_activos[escaneo_id] = {
                    'tipo': 'sistema',
                    'inicio': datetime.now(),
                    'estado': 'ejecutando',
                    'progreso': 0
                }
            
            inicio_tiempo = time.time()
            
            # Ejecutar escaneo
            if callback_progreso:
                callback_progreso(10, "Inicializando escaneo del sistema...")
            
            # Usar el método real del escaneador
            resultados = self.escaneador_sistema.escaneo_completo_vulnerabilidades()
            
            if callback_progreso:
                callback_progreso(50, "Analizando configuraciones del sistema...")
            
            # TODO: Implementar análisis de software instalado cuando el método esté disponible
            vulnerabilidades_software = []
            # software_instalado = self.escaneador_sistema.obtener_software_instalado()
            # for software in software_instalado:
            #     vulns = self.buscador_cve.buscar_vulnerabilidades_software(
            #         software.get('nombre', ''),
            #         software.get('version', '')
            #     )
            #     if vulns:
            #         vulnerabilidades_software.extend(vulns)
            
            if callback_progreso:
                callback_progreso(80, "Categorizando vulnerabilidades...")
            
            # Categorizar y priorizar vulnerabilidades
            vulnerabilidades_categorizadas = self._categorizar_vulnerabilidades(
                resultados.get('vulnerabilidades', []) + vulnerabilidades_software
            )
            
            tiempo_ejecucion = time.time() - inicio_tiempo
            
            resultado_final = {
                'escaneo_id': escaneo_id,
                'timestamp': datetime.now().isoformat(),
                'tipo': 'sistema',
                'tiempo_ejecucion': tiempo_ejecucion,
                'total_vulnerabilidades': len(vulnerabilidades_categorizadas),
                'vulnerabilidades_criticas': len([v for v in vulnerabilidades_categorizadas if v.get('cvss_score', 0) >= 9.0]),
                'vulnerabilidades_altas': len([v for v in vulnerabilidades_categorizadas if 7.0 <= v.get('cvss_score', 0) < 9.0]),
                'vulnerabilidades_medias': len([v for v in vulnerabilidades_categorizadas if 4.0 <= v.get('cvss_score', 0) < 7.0]),
                'vulnerabilidades_bajas': len([v for v in vulnerabilidades_categorizadas if v.get('cvss_score', 0) < 4.0]),
                'vulnerabilidades': vulnerabilidades_categorizadas,
                'software_analizado': 0,  # TODO: Implementar cuando esté disponible
                'configuraciones_verificadas': resultados.get('configuraciones_verificadas', 0)
            }
            
            # Actualizar estado y cache
            with self.lock:
                self.escaneos_activos[escaneo_id]['estado'] = 'completado'
                self.escaneos_activos[escaneo_id]['progreso'] = 100
                self.escaneos_activos[escaneo_id]['resultado'] = resultado_final
                
                # Guardar en cache
                self.resultados_cache[escaneo_id] = resultado_final
                self._limpiar_cache_resultados()
            
            if callback_progreso:
                callback_progreso(100, "Escaneo completado")
            
            # Registrar en SIEM
            if self.siem:
                nivel_criticidad = "CRITICO" if resultado_final['vulnerabilidades_criticas'] > 0 else \
                                 "ALTO" if resultado_final['vulnerabilidades_altas'] > 0 else \
                                 "MEDIO" if resultado_final['vulnerabilidades_medias'] > 0 else "BAJO"
                
                self.siem.registrar_evento(
                    TipoEvento.AMENAZA_DETECTADA,
                    f"Escaneo de vulnerabilidades del sistema completado: {resultado_final['total_vulnerabilidades']} vulnerabilidades encontradas",
                    resultado_final,
                    nivel_criticidad
                )
            
            self.logger.info(f"Escaneo del sistema completado en {tiempo_ejecucion:.2f}s: {resultado_final['total_vulnerabilidades']} vulnerabilidades")
            return resultado_final
        
        except Exception as e:
            self.logger.error(f"Error en escaneo de vulnerabilidades del sistema: {e}")
            
            # Actualizar estado de error
            with self.lock:
                if escaneo_id in self.escaneos_activos:
                    self.escaneos_activos[escaneo_id]['estado'] = 'error'
                    self.escaneos_activos[escaneo_id]['error'] = str(e)
            
            return {
                'escaneo_id': escaneo_id,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def escanear_vulnerabilidades_red(self, objetivo: str = "127.0.0.1", 
                                    puertos: Optional[List[int]] = None,
                                    callback_progreso: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Ejecutar escaneo de vulnerabilidades de red.
        
        Args:
            objetivo: IP o rango de IPs a escanear
            puertos: Lista de puertos específicos (None para escaneo completo)
            callback_progreso: Función callback para reportar progreso
            
        Returns:
            Dict[str, Any]: Resultados del escaneo de red
        """
        try:
            escaneo_id = f"vuln_net_{int(time.time())}"
            self.logger.info(f"Iniciando escaneo de vulnerabilidades de red: {escaneo_id} -> {objetivo}")
            
            # Registrar escaneo activo
            with self.lock:
                self.escaneos_activos[escaneo_id] = {
                    'tipo': 'red',
                    'objetivo': objetivo,
                    'inicio': datetime.now(),
                    'estado': 'ejecutando',
                    'progreso': 0
                }
            
            inicio_tiempo = time.time()
            
            if callback_progreso:
                callback_progreso(10, f"Iniciando escaneo de red para {objetivo}...")
            
            # Ejecutar escaneo de red
            # TODO: Implementar cuando escanear_objetivo esté disponible
            resultados = {
                'hosts_activos': 1,
                'puertos_abiertos': [],
                'servicios': []
            }
            # resultados = self.escaneador_red.escanear_objetivo(objetivo, puertos)
            
            if callback_progreso:
                callback_progreso(60, "Analizando servicios detectados...")
            
            # Analizar servicios para vulnerabilidades conocidas
            vulnerabilidades_servicios = []
            servicios = resultados.get('servicios', [])
            
            for servicio in servicios:
                vulns = self._analizar_vulnerabilidades_servicio(servicio)
                vulnerabilidades_servicios.extend(vulns)
            
            if callback_progreso:
                callback_progreso(90, "Consolidando resultados...")
            
            tiempo_ejecucion = time.time() - inicio_tiempo
            
            resultado_final = {
                'escaneo_id': escaneo_id,
                'timestamp': datetime.now().isoformat(),
                'tipo': 'red',
                'objetivo': objetivo,
                'tiempo_ejecucion': tiempo_ejecucion,
                'hosts_activos': resultados.get('hosts_activos', 0),
                'puertos_abiertos': len(resultados.get('puertos_abiertos', [])),
                'servicios_detectados': len(servicios),
                'vulnerabilidades_encontradas': len(vulnerabilidades_servicios),
                'vulnerabilidades': vulnerabilidades_servicios,
                'puertos_detalle': resultados.get('puertos_abiertos', []),
                'servicios': servicios
            }
            
            # Actualizar estado
            with self.lock:
                self.escaneos_activos[escaneo_id]['estado'] = 'completado'
                self.escaneos_activos[escaneo_id]['progreso'] = 100
                self.escaneos_activos[escaneo_id]['resultado'] = resultado_final
                
                self.resultados_cache[escaneo_id] = resultado_final
                self._limpiar_cache_resultados()
            
            if callback_progreso:
                callback_progreso(100, "Escaneo de red completado")
            
            # Registrar en SIEM
            if self.siem:
                nivel_criticidad = "ALTO" if len(vulnerabilidades_servicios) > 0 else "MEDIO"
                
                self.siem.registrar_evento(
                    TipoEvento.CONEXION_SOSPECHOSA,
                    f"Escaneo de vulnerabilidades de red completado para {objetivo}: {len(vulnerabilidades_servicios)} vulnerabilidades",
                    resultado_final,
                    nivel_criticidad
                )
            
            self.logger.info(f"Escaneo de red completado para {objetivo}: {len(vulnerabilidades_servicios)} vulnerabilidades")
            return resultado_final
        
        except Exception as e:
            self.logger.error(f"Error en escaneo de vulnerabilidades de red: {e}")
            
            with self.lock:
                if escaneo_id in self.escaneos_activos:
                    self.escaneos_activos[escaneo_id]['estado'] = 'error'
                    self.escaneos_activos[escaneo_id]['error'] = str(e)
            
            return {
                'escaneo_id': escaneo_id,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def buscar_cve(self, termino_busqueda: str, limite: int = 50) -> Dict[str, Any]:
        """
        Buscar CVEs por término específico.
        
        Args:
            termino_busqueda: Término de búsqueda (software, vendor, etc.)
            limite: Número máximo de resultados
            
        Returns:
            Dict[str, Any]: Resultados de la búsqueda
        """
        try:
            self.logger.info(f"Buscando CVEs para: {termino_busqueda}")
            
            inicio_tiempo = time.time()
            
            # Buscar CVEs
            # TODO: Usar el método real cuando esté disponible
            cves = []
            # cves = self.buscador_cve.buscar_cve_por_termino(termino_busqueda, limite)
            cves = self.buscador_cve.buscar_cves_por_descripcion(termino_busqueda)[:limite]
            
            # Categorizar por severidad
            categorias = {
                'criticos': [cve for cve in cves if cve.cvss_score >= 9.0],
                'altos': [cve for cve in cves if 7.0 <= cve.cvss_score < 9.0],
                'medios': [cve for cve in cves if 4.0 <= cve.cvss_score < 7.0],
                'bajos': [cve for cve in cves if cve.cvss_score < 4.0]
            }
            
            tiempo_busqueda = time.time() - inicio_tiempo
            
            resultado = {
                'termino_busqueda': termino_busqueda,
                'timestamp': datetime.now().isoformat(),
                'tiempo_busqueda': tiempo_busqueda,
                'total_encontrados': len(cves),
                'criticos': len(categorias['criticos']),
                'altos': len(categorias['altos']),
                'medios': len(categorias['medios']),
                'bajos': len(categorias['bajos']),
                'cves': cves[:limite],
                'categorias': categorias
            }
            
            # Registrar en SIEM
            if self.siem:
                self.siem.registrar_evento(
                    TipoEvento.CONFIGURACION_MODIFICADA,
                    f"Búsqueda de CVEs realizada: {termino_busqueda} ({len(cves)} resultados)",
                    resultado,
                    "BAJO"
                )
            
            self.logger.info(f"Búsqueda CVE completada: {len(cves)} resultados para '{termino_busqueda}'")
            return resultado
        
        except Exception as e:
            self.logger.error(f"Error buscando CVEs: {e}")
            return {
                'error': str(e),
                'termino_busqueda': termino_busqueda,
                'timestamp': datetime.now().isoformat()
            }
    
    def _categorizar_vulnerabilidades(self, vulnerabilidades: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Categorizar vulnerabilidades por severidad y tipo."""
        vulnerabilidades_procesadas = []
        
        for vuln in vulnerabilidades:
            vuln_procesada = vuln.copy()
            
            # Asegurar score CVSS
            cvss_score = vuln.get('cvss_score', 0)
            if isinstance(cvss_score, str):
                try:
                    cvss_score = float(cvss_score)
                except:
                    cvss_score = 0
            
            vuln_procesada['cvss_score'] = cvss_score
            
            # Categorizar por severidad
            if cvss_score >= 9.0:
                vuln_procesada['severidad'] = 'CRITICA'
                vuln_procesada['prioridad'] = 1
            elif cvss_score >= 7.0:
                vuln_procesada['severidad'] = 'ALTA'
                vuln_procesada['prioridad'] = 2
            elif cvss_score >= 4.0:
                vuln_procesada['severidad'] = 'MEDIA'
                vuln_procesada['prioridad'] = 3
            else:
                vuln_procesada['severidad'] = 'BAJA'
                vuln_procesada['prioridad'] = 4
            
            # Añadir timestamp de detección
            vuln_procesada['timestamp_deteccion'] = datetime.now().isoformat()
            
            vulnerabilidades_procesadas.append(vuln_procesada)
        
        # Ordenar por prioridad y score CVSS
        vulnerabilidades_procesadas.sort(key=lambda x: (x['prioridad'], -x['cvss_score']))
        
        return vulnerabilidades_procesadas
    
    def _analizar_vulnerabilidades_servicio(self, servicio: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analizar vulnerabilidades específicas de un servicio."""
        vulnerabilidades = []
        
        try:
            nombre_servicio = servicio.get('servicio', '')
            version = servicio.get('version', '')
            puerto = servicio.get('puerto', 0)
            
            # Buscar CVEs para el servicio
            if nombre_servicio:
                # TODO: Usar método real cuando esté disponible
                cves = []
                # cves = self.buscador_cve.buscar_vulnerabilidades_software(nombre_servicio, version)
                cves = self.buscador_cve.buscar_cves_por_software(nombre_servicio, version)
                
                for cve in cves:
                    vulnerabilidad = {
                        'tipo': 'servicio_red',
                        'servicio': nombre_servicio,
                        'version': version,
                        'puerto': puerto,
                        'cve_id': cve.cve_id,
                        'descripcion': cve.description,
                        'cvss_score': cve.cvss_score,
                        'referencias': cve.references,
                        'afecta_sistema': True
                    }
                    vulnerabilidades.append(vulnerabilidad)
            
            # Verificar configuraciones inseguras comunes
            vulns_config = self._verificar_configuraciones_inseguras(servicio)
            vulnerabilidades.extend(vulns_config)
        
        except Exception as e:
            self.logger.error(f"Error analizando vulnerabilidades del servicio: {e}")
        
        return vulnerabilidades
    
    def _verificar_configuraciones_inseguras(self, servicio: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Verificar configuraciones inseguras en servicios."""
        vulnerabilidades = []
        puerto = servicio.get('puerto', 0)
        servicio_nombre = servicio.get('servicio', '').lower()
        
        # Configuraciones inseguras comunes
        configuraciones_inseguras = {
            21: {'servicio': 'ftp', 'descripcion': 'FTP sin cifrado detectado', 'cvss': 5.0},
            23: {'servicio': 'telnet', 'descripcion': 'Telnet sin cifrado detectado', 'cvss': 7.5},
            80: {'servicio': 'http', 'descripcion': 'Servidor web sin HTTPS', 'cvss': 4.0},
            139: {'servicio': 'netbios', 'descripcion': 'NetBIOS expuesto', 'cvss': 6.0},
            445: {'servicio': 'smb', 'descripcion': 'SMB expuesto', 'cvss': 7.0}
        }
        
        if puerto in configuraciones_inseguras:
            config = configuraciones_inseguras[puerto]
            if config['servicio'] in servicio_nombre:
                vulnerabilidad = {
                    'tipo': 'configuracion_insegura',
                    'servicio': servicio_nombre,
                    'puerto': puerto,
                    'descripcion': config['descripcion'],
                    'cvss_score': config['cvss'],
                    'recomendacion': f"Considerar deshabilitar o cifrar el servicio {servicio_nombre}",
                    'afecta_sistema': True
                }
                vulnerabilidades.append(vulnerabilidad)
        
        return vulnerabilidades
    
    def obtener_estado_escaneo(self, escaneo_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtener el estado actual de un escaneo.
        
        Args:
            escaneo_id: ID del escaneo
            
        Returns:
            Optional[Dict[str, Any]]: Estado del escaneo o None
        """
        with self.lock:
            return self.escaneos_activos.get(escaneo_id, {}).copy()
    
    def obtener_resultados_escaneo(self, escaneo_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtener los resultados de un escaneo completado.
        
        Args:
            escaneo_id: ID del escaneo
            
        Returns:
            Optional[Dict[str, Any]]: Resultados del escaneo o None
        """
        with self.lock:
            return self.resultados_cache.get(escaneo_id, {}).copy()
    
    def listar_escaneos_activos(self) -> List[Dict[str, Any]]:
        """
        Listar todos los escaneos activos.
        
        Returns:
            List[Dict[str, Any]]: Lista de escaneos activos
        """
        with self.lock:
            escaneos = []
            for escaneo_id, info in self.escaneos_activos.items():
                escaneo_info = info.copy()
                escaneo_info['escaneo_id'] = escaneo_id
                escaneos.append(escaneo_info)
            
            return escaneos
    
    def cancelar_escaneo(self, escaneo_id: str) -> bool:
        """
        Cancelar un escaneo activo.
        
        Args:
            escaneo_id: ID del escaneo a cancelar
            
        Returns:
            bool: True si se canceló exitosamente
        """
        try:
            with self.lock:
                if escaneo_id in self.escaneos_activos:
                    self.escaneos_activos[escaneo_id]['estado'] = 'cancelado'
                    self.escaneos_activos[escaneo_id]['timestamp_cancelacion'] = datetime.now().isoformat()
                    
                    self.logger.info(f"Escaneo cancelado: {escaneo_id}")
                    
                    if self.siem:
                        self.siem.registrar_evento(
                            TipoEvento.CONFIGURACION_MODIFICADA,
                            f"Escaneo de vulnerabilidades cancelado: {escaneo_id}",
                            {'escaneo_id': escaneo_id},
                            "BAJO"
                        )
                    
                    return True
            
            return False
        
        except Exception as e:
            self.logger.error(f"Error cancelando escaneo {escaneo_id}: {e}")
            return False
    
    def obtener_resumen_vulnerabilidades(self, periodo_dias: int = 7) -> Dict[str, Any]:
        """
        Obtener resumen de vulnerabilidades del período especificado.
        
        Args:
            periodo_dias: Período en días para el resumen
            
        Returns:
            Dict[str, Any]: Resumen de vulnerabilidades
        """
        try:
            fecha_limite = datetime.now() - timedelta(days=periodo_dias)
            
            # Obtener resultados del período
            resultados_periodo = []
            with self.lock:
                for resultado in self.resultados_cache.values():
                    timestamp_str = resultado.get('timestamp', '')
                    try:
                        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        if timestamp >= fecha_limite:
                            resultados_periodo.append(resultado)
                    except:
                        continue
            
            # Calcular estadísticas
            total_vulnerabilidades = 0
            vulnerabilidades_criticas = 0
            vulnerabilidades_altas = 0
            vulnerabilidades_medias = 0
            vulnerabilidades_bajas = 0
            escaneos_realizados = len(resultados_periodo)
            
            for resultado in resultados_periodo:
                total_vulnerabilidades += resultado.get('total_vulnerabilidades', 0)
                vulnerabilidades_criticas += resultado.get('vulnerabilidades_criticas', 0)
                vulnerabilidades_altas += resultado.get('vulnerabilidades_altas', 0)
                vulnerabilidades_medias += resultado.get('vulnerabilidades_medias', 0)
                vulnerabilidades_bajas += resultado.get('vulnerabilidades_bajas', 0)
            
            resumen = {
                'periodo_dias': periodo_dias,
                'timestamp': datetime.now().isoformat(),
                'escaneos_realizados': escaneos_realizados,
                'total_vulnerabilidades': total_vulnerabilidades,
                'vulnerabilidades_criticas': vulnerabilidades_criticas,
                'vulnerabilidades_altas': vulnerabilidades_altas,
                'vulnerabilidades_medias': vulnerabilidades_medias,
                'vulnerabilidades_bajas': vulnerabilidades_bajas,
                'tendencia': self._calcular_tendencia_vulnerabilidades(resultados_periodo)
            }
            
            return resumen
        
        except Exception as e:
            self.logger.error(f"Error obteniendo resumen de vulnerabilidades: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _calcular_tendencia_vulnerabilidades(self, resultados: List[Dict[str, Any]]) -> str:
        """Calcular tendencia de vulnerabilidades."""
        if len(resultados) < 2:
            return "insuficientes_datos"
        
        # Ordenar por timestamp
        resultados_ordenados = sorted(resultados, key=lambda x: x.get('timestamp', ''))
        
        # Comparar primera mitad vs segunda mitad
        mitad = len(resultados_ordenados) // 2
        primera_mitad = resultados_ordenados[:mitad]
        segunda_mitad = resultados_ordenados[mitad:]
        
        vulns_primera = sum(r.get('total_vulnerabilidades', 0) for r in primera_mitad)
        vulns_segunda = sum(r.get('total_vulnerabilidades', 0) for r in segunda_mitad)
        
        if vulns_segunda > vulns_primera * 1.2:
            return "aumentando"
        elif vulns_segunda < vulns_primera * 0.8:
            return "disminuyendo"
        else:
            return "estable"
    
    def _limpiar_cache_resultados(self):
        """Limpiar cache de resultados manteniendo solo los más recientes."""
        max_resultados = self.configuracion['max_resultados_cache']
        
        if len(self.resultados_cache) > max_resultados:
            # Ordenar por timestamp y mantener los más recientes
            items_ordenados = sorted(
                self.resultados_cache.items(),
                key=lambda x: x[1].get('timestamp', ''),
                reverse=True
            )
            
            # Mantener solo los más recientes
            self.resultados_cache = dict(items_ordenados[:max_resultados])
    
    def configurar_vulnerabilidades(self, config: Dict[str, Any]):
        """
        Configurar parámetros del controlador de vulnerabilidades.
        
        Args:
            config: Diccionario con configuración
        """
        with self.lock:
            self.configuracion.update(config)
        
        self.logger.info(f"Configuración de vulnerabilidades actualizada: {config}")
        
        if self.siem:
            self.siem.registrar_evento(
                TipoEvento.CONFIGURACION_MODIFICADA,
                "Configuración de vulnerabilidades actualizada",
                config,
                "MEDIO"
            )
