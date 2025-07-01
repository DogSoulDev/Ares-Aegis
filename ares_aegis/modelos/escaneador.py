#!/usr/bin/env python3
"""
Escaneador Principal - Ares Aegis
Módulo principal de escaneo con lógica para escaneos completos y personalizados

Autor: DogSoulDev
Versión: 2.0.0
"""

import os
import hashlib
import re
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from datetime import datetime

from .siem import SIEM, TipoEvento
from ..utilidades.validaciones import (
    validar_ruta_archivo, validar_ruta_directorio, 
    validar_permisos_lectura, es_ruta_segura
)
from ..utilidades.ayuda_rutas import (
    listar_archivos_recursivo, obtener_tamaño_archivo,
    obtener_rutas_sistema
)
from ..utilidades.ayuda_logging import configurar_logger_modulo


class ResultadoEscaneo:
    """Representa el resultado del escaneo de un archivo."""
    
    def __init__(self, ruta: str, es_limpio: bool = True, 
                 amenazas_detectadas: Optional[List[str]] = None,
                 detalles_adicionales: Optional[Dict[str, Any]] = None):
        """
        Inicializa un resultado de escaneo.
        
        Args:
            ruta: Ruta del archivo escaneado
            es_limpio: True si el archivo está limpio, False si hay amenazas
            amenazas_detectadas: Lista de amenazas encontradas
            detalles_adicionales: Información adicional del escaneo
        """
        self.ruta = ruta
        self.es_limpio = es_limpio
        self.amenazas_detectadas = amenazas_detectadas or []
        self.detalles_adicionales = detalles_adicionales or {}
        self.timestamp_escaneo = datetime.now()
        self.hash_sha256 = self._calcular_hash()
        self.tamaño_archivo = self._obtener_tamaño()
    
    def _calcular_hash(self) -> str:
        """Calcula el hash SHA256 del archivo."""
        try:
            with open(self.ruta, 'rb') as archivo:
                contenido = archivo.read()
                return hashlib.sha256(contenido).hexdigest()
        except Exception:
            return ""
    
    def _obtener_tamaño(self) -> int:
        """Obtiene el tamaño del archivo en bytes."""
        try:
            return obtener_tamaño_archivo(self.ruta)
        except Exception:
            return 0
    
    def tiene_amenazas(self) -> bool:
        """Verifica si el archivo tiene amenazas."""
        return not self.es_limpio and len(self.amenazas_detectadas) > 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el resultado a diccionario."""
        return {
            'ruta': self.ruta,
            'es_limpio': self.es_limpio,
            'amenazas_detectadas': self.amenazas_detectadas,
            'detalles_adicionales': self.detalles_adicionales,
            'timestamp_escaneo': self.timestamp_escaneo.isoformat(),
            'hash_sha256': self.hash_sha256,
            'tamaño_archivo': self.tamaño_archivo
        }
    
    def to_markdown(self) -> str:
        """Convierte el resultado a formato Markdown."""
        estado = "✅ LIMPIO" if self.es_limpio else "⚠️ INFECTADO"
        
        md = f"## Resultado de Escaneo\n\n"
        md += f"**Archivo:** `{self.ruta}`\n"
        md += f"**Estado:** {estado}\n"
        md += f"**Fecha:** {self.timestamp_escaneo.strftime('%Y-%m-%d %H:%M:%S')}\n"
        md += f"**Tamaño:** {self.tamaño_archivo} bytes\n"
        
        if self.hash_sha256:
            md += f"**SHA256:** `{self.hash_sha256}`\n"
        
        if self.tiene_amenazas():
            md += f"\n### 🚨 Amenazas Detectadas\n\n"
            for amenaza in self.amenazas_detectadas:
                md += f"- {amenaza}\n"
        
        if self.detalles_adicionales:
            md += f"\n### Detalles Adicionales\n\n"
            for clave, valor in self.detalles_adicionales.items():
                md += f"- **{clave}:** {valor}\n"
        
        md += "\n"
        return md


class Escaneador:
    """Escaneador principal de Ares Aegis."""
    
    def __init__(self, siem: SIEM):
        """
        Inicializa el escaneador.
        
        Args:
            siem: Instancia del SIEM para registro de eventos
        """
        self.siem = siem
        self.logger = configurar_logger_modulo("escaneador")
        
        # Cargar firmas de malware
        self.firmas_texto: List[str] = []
        self.firmas_regex: List[re.Pattern] = []
        self.firmas_hash: List[str] = []
        
        self._cargar_firmas()
        
        # Estadísticas de escaneo
        self.estadisticas = {
            'archivos_escaneados': 0,
            'amenazas_detectadas': 0,
            'tiempo_total_escaneo': 0,
            'ultimo_escaneo': None
        }
        
        # Contadores globales
        self.total_archivos_escaneados = 0
        self.total_amenazas_detectadas = 0
        self.ultimo_escaneo = None
        
        self.logger.info("Escaneador inicializado correctamente")
    
    def _cargar_firmas(self):
        """Carga las firmas de malware desde el archivo de configuración."""
        try:
            rutas_sistema = obtener_rutas_sistema()
            archivo_firmas = rutas_sistema['archivo_firmas']
            
            # Si no existe el archivo del sistema, usar archivo local
            if not os.path.exists(archivo_firmas):
                archivo_firmas = Path.cwd() / "recursos" / "firmas.txt"
            
            if os.path.exists(archivo_firmas):
                with open(archivo_firmas, 'r', encoding='utf-8') as archivo:
                    for linea in archivo:
                        linea = linea.strip()
                        
                        # Saltar líneas vacías y comentarios
                        if not linea or linea.startswith('#'):
                            continue
                        
                        # Procesar diferentes tipos de firmas
                        if linea.startswith('HASH:'):
                            hash_valor = linea[5:].strip()
                            self.firmas_hash.append(hash_valor)
                        
                        elif linea.startswith('REGEX:'):
                            patron_regex = linea[6:].strip()
                            try:
                                regex_compilado = re.compile(patron_regex, re.IGNORECASE)
                                self.firmas_regex.append(regex_compilado)
                            except re.error as e:
                                self.logger.warning(f"Error compilando regex '{patron_regex}': {e}")
                        
                        else:
                            # Firma de texto simple
                            self.firmas_texto.append(linea.lower())
                
                self.logger.info(f"Firmas cargadas: {len(self.firmas_texto)} texto, "
                               f"{len(self.firmas_hash)} hash, {len(self.firmas_regex)} regex")
            else:
                self.logger.warning(f"Archivo de firmas no encontrado: {archivo_firmas}")
                self._crear_firmas_por_defecto()
        
        except Exception as e:
            self.logger.error(f"Error cargando firmas: {e}")
            self._crear_firmas_por_defecto()
    
    def _crear_firmas_por_defecto(self):
        """Crea firmas básicas por defecto si no se puede cargar el archivo."""
        self.firmas_texto = [
            'eval(base64_decode',
            'system($_get',
            'shell_exec(',
            'backdoor',
            'malware',
            'virus',
            'trojan'
        ]
        
        # Algunas regex básicas
        try:
            self.firmas_regex = [
                re.compile(r'eval\s*\(\s*base64_decode', re.IGNORECASE),
                re.compile(r'\$_[A-Z]+\[[\'"][^\'"]*[\'\"]\]', re.IGNORECASE),
                re.compile(r'system\s*\([^)]*\$_', re.IGNORECASE)
            ]
        except Exception as e:
            self.logger.error(f"Error creando regex por defecto: {e}")
            self.firmas_regex = []
        
        self.logger.info("Usando firmas por defecto")
    
    def escanear_archivo(self, ruta_archivo: str) -> ResultadoEscaneo:
        """
        Escanea un archivo individual.
        
        Args:
            ruta_archivo: Ruta del archivo a escanear
            
        Returns:
            ResultadoEscaneo: Resultado del escaneo
        """
        inicio_tiempo = time.time()
        
        # Validaciones básicas
        if not validar_ruta_archivo(ruta_archivo):
            return ResultadoEscaneo(
                ruta_archivo, 
                es_limpio=True,
                detalles_adicionales={'error': 'Archivo no válido o no existe'}
            )
        
        if not validar_permisos_lectura(ruta_archivo):
            return ResultadoEscaneo(
                ruta_archivo,
                es_limpio=True,
                detalles_adicionales={'error': 'Sin permisos de lectura'}
            )
        
        if not es_ruta_segura(ruta_archivo):
            return ResultadoEscaneo(
                ruta_archivo,
                es_limpio=True,
                detalles_adicionales={'error': 'Ruta no segura'}
            )
        
        self.logger.info(f"Iniciando escaneo de archivo: {ruta_archivo}")
        self.siem.registrar_evento(
            TipoEvento.ESCANEO_INICIADO,
            f"Escaneo de archivo iniciado: {ruta_archivo}",
            {'tipo_escaneo': 'archivo_individual', 'ruta': ruta_archivo},
            "BAJO"
        )
        
        amenazas_detectadas = []
        detalles = {}
        
        try:
            # Leer contenido del archivo
            with open(ruta_archivo, 'rb') as archivo:
                contenido_bytes = archivo.read()
                contenido_texto = contenido_bytes.decode('utf-8', errors='ignore').lower()
            
            # Verificar hash del archivo
            hash_archivo = hashlib.sha256(contenido_bytes).hexdigest()
            if hash_archivo in self.firmas_hash:
                amenazas_detectadas.append(f"Hash malicioso detectado: {hash_archivo[:16]}...")
            
            # Verificar firmas de texto
            for firma in self.firmas_texto:
                if firma in contenido_texto:
                    amenazas_detectadas.append(f"Firma maliciosa detectada: {firma}")
            
            # Verificar firmas regex
            for regex in self.firmas_regex:
                if regex.search(contenido_texto):
                    amenazas_detectadas.append(f"Patrón malicioso detectado: {regex.pattern[:50]}...")
            
            # Análisis heurístico básico
            amenazas_heuristicas = self._analisis_heuristico(contenido_texto, ruta_archivo)
            amenazas_detectadas.extend(amenazas_heuristicas)
            
            detalles = {
                'tamaño_archivo': len(contenido_bytes),
                'hash_sha256': hash_archivo,
                'firmas_verificadas': len(self.firmas_texto) + len(self.firmas_regex) + len(self.firmas_hash)
            }
        
        except UnicodeDecodeError:
            # Archivo binario, análisis limitado
            try:
                with open(ruta_archivo, 'rb') as archivo:
                    contenido_bytes = archivo.read()
                
                hash_archivo = hashlib.sha256(contenido_bytes).hexdigest()
                if hash_archivo in self.firmas_hash:
                    amenazas_detectadas.append(f"Hash malicioso detectado: {hash_archivo[:16]}...")
                
                detalles = {
                    'tamaño_archivo': len(contenido_bytes),
                    'hash_sha256': hash_archivo,
                    'tipo_archivo': 'binario'
                }
            
            except Exception as e:
                self.logger.error(f"Error procesando archivo binario {ruta_archivo}: {e}")
                detalles['error'] = f"Error procesando archivo: {e}"
        
        except Exception as e:
            self.logger.error(f"Error escaneando archivo {ruta_archivo}: {e}")
            detalles['error'] = f"Error durante escaneo: {e}"
        
        # Crear resultado
        es_limpio = len(amenazas_detectadas) == 0
        resultado = ResultadoEscaneo(
            ruta_archivo,
            es_limpio=es_limpio,
            amenazas_detectadas=amenazas_detectadas,
            detalles_adicionales=detalles
        )
        
        # Actualizar estadísticas
        self.estadisticas['archivos_escaneados'] += 1
        if not es_limpio:
            self.estadisticas['amenazas_detectadas'] += len(amenazas_detectadas)
        
        tiempo_transcurrido = time.time() - inicio_tiempo
        self.estadisticas['tiempo_total_escaneo'] += tiempo_transcurrido
        self.estadisticas['ultimo_escaneo'] = datetime.now()
        
        # Registrar resultado en SIEM
        if es_limpio:
            self.siem.registrar_evento(
                TipoEvento.ESCANEO_FINALIZADO,
                f"Archivo limpio: {ruta_archivo}",
                {'ruta': ruta_archivo, 'tiempo_escaneo': tiempo_transcurrido},
                "BAJO"
            )
        else:
            self.siem.registrar_evento(
                TipoEvento.AMENAZA_DETECTADA,
                f"Amenazas detectadas en: {ruta_archivo}",
                {
                    'ruta': ruta_archivo,
                    'amenazas': amenazas_detectadas,
                    'cantidad_amenazas': len(amenazas_detectadas)
                },
                "ALTO"
            )
        
        self.logger.info(f"Escaneo completado: {ruta_archivo} - "
                        f"{'LIMPIO' if es_limpio else f'{len(amenazas_detectadas)} amenaza(s)'}")
        
        return resultado
    
    def _analisis_heuristico(self, contenido: str, ruta_archivo: str) -> List[str]:
        """
        Realiza análisis heurístico básico del contenido.
        
        Args:
            contenido: Contenido del archivo en texto
            ruta_archivo: Ruta del archivo
            
        Returns:
            List[str]: Lista de amenazas heurísticas detectadas
        """
        amenazas = []
        
        try:
            # Detectar alta concentración de código ofuscado
            if self._detectar_ofuscacion(contenido):
                amenazas.append("Posible código ofuscado detectado")
            
            # Detectar patrones de shell reverso
            if self._detectar_shell_reverso(contenido):
                amenazas.append("Posible shell reverso detectado")
            
            # Detectar keyloggers básicos
            if self._detectar_keylogger(contenido):
                amenazas.append("Posible keylogger detectado")
            
            # Análisis por extensión de archivo
            extension = Path(ruta_archivo).suffix.lower()
            if extension in ['.php', '.jsp', '.asp']:
                if self._detectar_webshell(contenido):
                    amenazas.append("Posible webshell detectado")
        
        except Exception as e:
            self.logger.warning(f"Error en análisis heurístico: {e}")
        
        return amenazas
    
    def _detectar_ofuscacion(self, contenido: str) -> bool:
        """Detecta posible código ofuscado."""
        # Buscar alta densidad de caracteres especiales
        caracteres_especiales = sum(1 for c in contenido if c in '!@#$%^&*(){}[]|\\:";\'<>?,./~`')
        densidad = caracteres_especiales / len(contenido) if len(contenido) > 0 else 0
        
        return densidad > 0.15  # Más del 15% de caracteres especiales
    
    def _detectar_shell_reverso(self, contenido: str) -> bool:
        """Detecta patrones de shell reverso."""
        patrones_shell = [
            'nc -e',
            'bash -i',
            '/bin/sh -i',
            'python -c',
            'perl -e',
            'ruby -e'
        ]
        
        return any(patron in contenido for patron in patrones_shell)
    
    def _detectar_keylogger(self, contenido: str) -> bool:
        """Detecta patrones de keylogger."""
        patrones_keylogger = [
            'keylog',
            'getkeystate',
            'setwindowshook',
            'rawinput',
            'keyboard',
            'keystroke'
        ]
        
        return sum(1 for patron in patrones_keylogger if patron in contenido) >= 2
    
    def _detectar_webshell(self, contenido: str) -> bool:
        """Detecta patrones de webshell."""
        patrones_webshell = [
            '$_post',
            '$_get',
            'system(',
            'exec(',
            'shell_exec(',
            'passthru(',
            'eval(',
            'file_get_contents'
        ]
        
        return sum(1 for patron in patrones_webshell if patron in contenido) >= 3
    
    def escanear_directorio(self, ruta_directorio: str, recursivo: bool = True,
                           extensiones_filtro: Optional[List[str]] = None) -> List[ResultadoEscaneo]:
        """
        Escanea un directorio completo.
        
        Args:
            ruta_directorio: Ruta del directorio a escanear
            recursivo: Si debe escanear subdirectorios
            extensiones_filtro: Lista de extensiones a escanear (opcional)
            
        Returns:
            List[ResultadoEscaneo]: Lista de resultados de escaneo
        """
        if not validar_ruta_directorio(ruta_directorio):
            self.logger.error(f"Directorio no válido: {ruta_directorio}")
            return []
        
        self.logger.info(f"Iniciando escaneo de directorio: {ruta_directorio}")
        self.siem.registrar_evento(
            TipoEvento.ESCANEO_INICIADO,
            f"Escaneo de directorio iniciado: {ruta_directorio}",
            {
                'tipo_escaneo': 'directorio',
                'ruta': ruta_directorio,
                'recursivo': recursivo,
                'extensiones_filtro': extensiones_filtro
            },
            "MEDIO"
        )
        
        resultados = []
        
        try:
            if recursivo:
                archivos = listar_archivos_recursivo(ruta_directorio, extensiones_filtro)
            else:
                directorio_path = Path(ruta_directorio)
                archivos = [f for f in directorio_path.iterdir() if f.is_file()]
                
                if extensiones_filtro:
                    archivos = [f for f in archivos if f.suffix.lower() in 
                              [ext.lower() for ext in extensiones_filtro]]
            
            total_archivos = len(archivos)
            self.logger.info(f"Escaneando {total_archivos} archivos en {ruta_directorio}")
            
            for i, archivo in enumerate(archivos, 1):
                try:
                    resultado = self.escanear_archivo(str(archivo))
                    resultados.append(resultado)
                    
                    # Log de progreso cada 100 archivos
                    if i % 100 == 0:
                        self.logger.info(f"Progreso: {i}/{total_archivos} archivos escaneados")
                
                except Exception as e:
                    self.logger.error(f"Error escaneando archivo {archivo}: {e}")
                    resultado_error = ResultadoEscaneo(
                        str(archivo),
                        es_limpio=True,
                        detalles_adicionales={'error': f"Error durante escaneo: {e}"}
                    )
                    resultados.append(resultado_error)
        
        except Exception as e:
            self.logger.error(f"Error durante escaneo de directorio {ruta_directorio}: {e}")
            self.siem.registrar_evento(
                TipoEvento.ERROR_SISTEMA,
                f"Error escaneando directorio: {ruta_directorio}",
                {'error': str(e)},
                "ALTO"
            )
        
        # Registrar finalización
        amenazas_totales = sum(len(r.amenazas_detectadas) for r in resultados if not r.es_limpio)
        archivos_infectados = len([r for r in resultados if not r.es_limpio])
        
        self.siem.registrar_evento(
            TipoEvento.ESCANEO_FINALIZADO,
            f"Escaneo de directorio completado: {ruta_directorio}",
            {
                'archivos_escaneados': len(resultados),
                'archivos_infectados': archivos_infectados,
                'amenazas_detectadas': amenazas_totales
            },
            "MEDIO" if amenazas_totales == 0 else "ALTO"
        )
        
        self.logger.info(f"Escaneo de directorio completado: {len(resultados)} archivos, "
                        f"{archivos_infectados} infectados, {amenazas_totales} amenazas")
        
        return resultados
    
    def escaneo_completo_sistema(self) -> Dict[str, Any]:
        """
        Realiza un escaneo completo del sistema.
        
        Returns:
            Dict[str, Any]: Resumen del escaneo completo
        """
        self.logger.info("Iniciando escaneo completo del sistema")
        self.siem.registrar_evento(
            TipoEvento.ESCANEO_INICIADO,
            "Escaneo completo del sistema iniciado",
            {'tipo_escaneo': 'sistema_completo'},
            "ALTO"
        )
        
        inicio_tiempo = time.time()
        
        # Directorios críticos a escanear
        directorios_criticos = [
            '/home',
            '/tmp',
            '/var/tmp',
            '/usr/local',
            '/opt'
        ]
        
        # Extensiones de archivos sospechosos
        extensiones_sospechosas = [
            '.php', '.jsp', '.asp', '.py', '.sh', '.pl', '.rb',
            '.exe', '.bat', '.cmd', '.scr', '.pif', '.jar'
        ]
        
        resultados_por_directorio = {}
        resumen_global = {
            'total_archivos_escaneados': 0,
            'total_amenazas_detectadas': 0,
            'archivos_infectados': 0,
            'directorios_escaneados': 0,
            'tiempo_total': 0,
            'directorios_con_problemas': []
        }
        
        for directorio in directorios_criticos:
            if os.path.exists(directorio) and os.access(directorio, os.R_OK):
                try:
                    self.logger.info(f"Escaneando directorio crítico: {directorio}")
                    resultados = self.escanear_directorio(directorio, True, extensiones_sospechosas)
                    
                    resultados_por_directorio[directorio] = resultados
                    resumen_global['total_archivos_escaneados'] += len(resultados)
                    resumen_global['directorios_escaneados'] += 1
                    
                    archivos_infectados_dir = [r for r in resultados if not r.es_limpio]
                    resumen_global['archivos_infectados'] += len(archivos_infectados_dir)
                    
                    amenazas_dir = sum(len(r.amenazas_detectadas) for r in archivos_infectados_dir)
                    resumen_global['total_amenazas_detectadas'] += amenazas_dir
                    
                except Exception as e:
                    self.logger.error(f"Error escaneando directorio {directorio}: {e}")
                    resumen_global['directorios_con_problemas'].append(directorio)
            else:
                self.logger.warning(f"Directorio no accesible: {directorio}")
                resumen_global['directorios_con_problemas'].append(directorio)
        
        tiempo_total = time.time() - inicio_tiempo
        resumen_global['tiempo_total'] = tiempo_total
        
        # Registrar finalización
        self.siem.registrar_evento(
            TipoEvento.ESCANEO_FINALIZADO,
            "Escaneo completo del sistema finalizado",
            resumen_global,
            "ALTO" if resumen_global['total_amenazas_detectadas'] > 0 else "MEDIO"
        )
        
        self.logger.info(f"Escaneo completo finalizado: {resumen_global['total_archivos_escaneados']} archivos, "
                        f"{resumen_global['total_amenazas_detectadas']} amenazas en {tiempo_total:.2f}s")
        
        return {
            'resumen_global': resumen_global,
            'resultados_por_directorio': resultados_por_directorio,
            'estadisticas_escaneador': self.estadisticas.copy()
        }
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """
        Obtiene las estadísticas del escaneador.
        
        Returns:
            Dict[str, Any]: Estadísticas del escaneador
        """
        return self.estadisticas.copy()
    
    def generar_reporte_markdown(self, resultados: List[ResultadoEscaneo]) -> str:
        """
        Genera un reporte en formato Markdown de los resultados de escaneo.
        
        Args:
            resultados: Lista de resultados de escaneo
            
        Returns:
            str: Reporte en formato Markdown
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        md = f"# Reporte de Escaneo - Ares Aegis\n\n"
        md += f"**Fecha:** {timestamp}\n\n"
        
        # Resumen general
        total_archivos = len(resultados)
        archivos_infectados = len([r for r in resultados if not r.es_limpio])
        total_amenazas = sum(len(r.amenazas_detectadas) for r in resultados if not r.es_limpio)
        
        md += "## Resumen General\n\n"
        md += f"- **Total de archivos escaneados:** {total_archivos}\n"
        md += f"- **Archivos infectados:** {archivos_infectados}\n"
        md += f"- **Total de amenazas detectadas:** {total_amenazas}\n"
        md += f"- **Porcentaje de archivos limpios:** {((total_archivos - archivos_infectados) / total_archivos * 100):.2f}%\n\n"
        
        # Archivos infectados
        if archivos_infectados > 0:
            md += "## 🚨 Archivos Infectados\n\n"
            for resultado in resultados:
                if not resultado.es_limpio:
                    md += f"### {resultado.ruta}\n\n"
                    md += f"**Amenazas detectadas:**\n"
                    for amenaza in resultado.amenazas_detectadas:
                        md += f"- {amenaza}\n"
                    md += f"\n**Hash SHA256:** `{resultado.hash_sha256}`\n\n"
                    md += "---\n\n"
        else:
            md += "## ✅ Resultado Limpio\n\n"
            md += "No se detectaron amenazas en ningún archivo escaneado.\n\n"
        
        return md
    
    def escanear_multiples_rutas(self, rutas: List[str], 
                                recursivo: bool = True) -> Dict[str, Any]:
        """
        Escanea múltiples rutas y devuelve estadísticas consolidadas.
        
        Args:
            rutas: Lista de rutas a escanear
            recursivo: Si debe escanear subdirectorios
            
        Returns:
            Dict[str, Any]: Estadísticas consolidadas del escaneo
        """
        resultados_totales = []
        archivos_escaneados = 0
        amenazas_detectadas = 0
        tiempo_inicio = time.time()
        
        for ruta in rutas:
            try:
                if Path(ruta).exists():
                    self.logger.info(f"Escaneando ruta: {ruta}")
                    resultados_ruta = self.escanear_directorio(ruta, recursivo)
                    resultados_totales.extend(resultados_ruta)
                    
                    # Contar estadísticas
                    archivos_escaneados += len(resultados_ruta)
                    amenazas_ruta = sum(len(r.amenazas_detectadas) for r in resultados_ruta)
                    amenazas_detectadas += amenazas_ruta
                    
                    self.logger.info(f"Ruta {ruta}: {len(resultados_ruta)} archivos, {amenazas_ruta} amenazas")
                else:
                    self.logger.warning(f"Ruta no existe: {ruta}")
            
            except Exception as e:
                self.logger.error(f"Error escaneando ruta {ruta}: {e}")
        
        tiempo_total = time.time() - tiempo_inicio
        
        # Actualizar estadísticas del escaneador
        self.total_archivos_escaneados += archivos_escaneados
        self.total_amenazas_detectadas += amenazas_detectadas
        self.ultimo_escaneo = datetime.now()
        
        # Registrar archivos infectados (la cuarentena se maneja desde el controlador)
        archivos_infectados = [r for r in resultados_totales if not r.es_limpio]
        
        # Registrar en SIEM
        self.siem.registrar_evento(
            TipoEvento.ESCANEO_FINALIZADO,
            f"Escaneo múltiple completado: {archivos_escaneados} archivos, {amenazas_detectadas} amenazas",
            {
                'rutas_escaneadas': rutas,
                'archivos_escaneados': archivos_escaneados,
                'amenazas_detectadas': amenazas_detectadas,
                'archivos_infectados': len(archivos_infectados),
                'tiempo_escaneo': tiempo_total
            },
            "ALTO" if amenazas_detectadas > 0 else "MEDIO"
        )
        
        return {
            'archivos_escaneados': archivos_escaneados,
            'amenazas_detectadas': amenazas_detectadas,
            'archivos_infectados': len(archivos_infectados),
            'tiempo_escaneo': tiempo_total,
            'rutas_escaneadas': rutas,
            'resultados_detallados': resultados_totales
        }
