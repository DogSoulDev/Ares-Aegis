#!/usr/bin/env python3
"""
Copyright (c) 2025 DogSoulDev (https://github.com/DogSoulDev)
Todos los derechos reservados. Este código es propietario y confidencial.

Escaneador de Malware Avanzado - Ares Aegis
Sistema de detección de amenazas con análisis multicapa y motor heurístico
"""

import os
import hashlib
import re
import time
import threading
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Callable
from datetime import datetime, timedelta
from collections import defaultdict, deque

from .siem import SIEM, TipoEvento, NivelCriticidad
from ..utilidades.validaciones import (
    validar_ruta_archivo, validar_ruta_directorio, 
    validar_permisos_lectura, es_ruta_segura
)
from ..utilidades.ayuda_rutas import (
    listar_archivos_recursivo, obtener_tamaño_archivo,
    obtener_rutas_sistema
)
from ..utilidades.ayuda_logging import configurar_logger_modulo


class TipoAmenaza:
    """Constantes para tipos de amenazas detectadas."""
    VIRUS = "VIRUS"
    TROJAN = "TROJAN"
    ROOTKIT = "ROOTKIT"
    BACKDOOR = "BACKDOOR"
    MALWARE = "MALWARE"
    SCRIPT_MALICIOSO = "SCRIPT"
    RANSOMWARE = "RANSOMWARE"
    KEYLOGGER = "KEYLOGGER"
    EXPLOIT = "EXPLOIT"
    SUSPICIOUS = "SUSPICIOUS"
    BYPASS = "BYPASS"
    DANGEROUS = "DANGEROUS"
    SPYWARE = "SPYWARE"
    ADWARE = "ADWARE"
    PHISHING = "PHISHING"
    CRYPTOMINER = "CRYPTOMINER"


class NivelRiesgo:
    """Niveles de riesgo para amenazas detectadas."""
    CRITICO = "CRÍTICO"          # Amenaza inmediata y peligrosa
    ALTO = "ALTO"                # Amenaza significativa
    MEDIO = "MEDIO"              # Sospechoso, requiere atención
    BAJO = "BAJO"                # Posible falso positivo
    INFORMATIVO = "INFORMATIVO"  # Solo información


class FirmaDeteccion:
    """Representa una firma de detección de malware."""
    
    def __init__(self, tipo: str, patron: str, descripcion: str, 
                 nivel_riesgo: str, familia: str = "Genérico"):
        """
        Inicializa una firma de detección.
        
        Args:
            tipo: Tipo de amenaza (usar constantes TipoAmenaza)
            patron: Patrón de detección (texto, regex, hash)
            descripcion: Descripción de la amenaza
            nivel_riesgo: Nivel de riesgo (usar constantes NivelRiesgo)
            familia: Familia de malware
        """
        self.tipo = tipo
        self.patron = patron
        self.descripcion = descripcion
        self.nivel_riesgo = nivel_riesgo
        self.familia = familia
        self.detectado_veces = 0
        self.ultima_deteccion = None
        self.patron_compilado = None
        
        # Compilar regex si es necesario
        if patron.startswith('REGEX:'):
            try:
                self.patron_compilado = re.compile(patron[6:], re.IGNORECASE | re.MULTILINE)
            except re.error:
                self.patron_compilado = None
    
    def detectar(self, contenido: str) -> bool:
        """Detecta si el patrón coincide en el contenido."""
        try:
            if self.patron_compilado:
                match = self.patron_compilado.search(contenido)
            else:
                match = self.patron.lower() in contenido.lower()
            
            if match:
                self.detectado_veces += 1
                self.ultima_deteccion = datetime.now()
                return True
            return False
        except Exception:
            return False


class AnalizadorHeuristico:
    """Motor de análisis heurístico para detección de amenazas desconocidas."""
    
    def __init__(self):
        """Inicializa el analizador heurístico."""
        self.patrones_sospechosos = [
            # Patrones de obfuscación
            r'eval\s*\(\s*["\'].*["\']',
            r'base64_decode\s*\(',
            r'gzinflate\s*\(',
            r'str_rot13\s*\(',
            
            # Patrones de ejecución remota
            r'system\s*\(\s*\$',
            r'exec\s*\(\s*\$',
            r'shell_exec\s*\(',
            r'passthru\s*\(',
            
            # Patrones de red sospechosos
            r'fsockopen\s*\(',
            r'socket_create\s*\(',
            r'curl_exec\s*\(',
            
            # Patrones de manipulación de archivos
            r'file_get_contents\s*\(\s*["\']https?://',
            r'fwrite\s*\(\s*.*\$_',
            r'file_put_contents\s*\(\s*.*\$_'
        ]
        
        self.patrones_compilados = []
        for patron in self.patrones_sospechosos:
            try:
                self.patrones_compilados.append(re.compile(patron, re.IGNORECASE))
            except re.error:
                continue
    
    def analizar(self, contenido: str, extension: str = "") -> Dict[str, Any]:
        """
        Realiza análisis heurístico del contenido.
        
        Returns:
            Diccionario con resultados del análisis heurístico
        """
        resultado = {
            'puntuacion_riesgo': 0,
            'patrones_detectados': [],
            'es_sospechoso': False,
            'recomendacion': 'SEGURO'
        }
        
        # Analizar patrones sospechosos
        for i, patron in enumerate(self.patrones_compilados):
            if patron.search(contenido):
                resultado['patrones_detectados'].append(self.patrones_sospechosos[i])
                resultado['puntuacion_riesgo'] += 10
        
        # Análisis de entropía (detectar código ofuscado)
        entropia = self._calcular_entropia(contenido)
        if entropia > 7.5:  # Alta entropía indica posible ofuscación
            resultado['puntuacion_riesgo'] += 15
            resultado['patrones_detectados'].append('Alta entropía detectada')
        
        # Análisis específico por extensión
        if extension.lower() in ['.exe', '.dll', '.so']:
            resultado['puntuacion_riesgo'] += 5  # Archivos ejecutables son más riesgosos
        
        # Determinar si es sospechoso
        if resultado['puntuacion_riesgo'] >= 20:
            resultado['es_sospechoso'] = True
            resultado['recomendacion'] = 'CUARENTENA'
        elif resultado['puntuacion_riesgo'] >= 10:
            resultado['recomendacion'] = 'REVISAR'
        
        return resultado
    
    def _calcular_entropia(self, datos: str) -> float:
        """Calcula la entropía de Shannon de los datos."""
        if not datos:
            return 0.0
        
        # Contar frecuencia de caracteres
        frecuencias = {}
        for char in datos:
            frecuencias[char] = frecuencias.get(char, 0) + 1
        
        # Calcular entropía
        entropia = 0.0
        longitud = len(datos)
        
        for freq in frecuencias.values():
            probabilidad = freq / longitud
            if probabilidad > 0:
                import math
                entropia -= probabilidad * math.log2(probabilidad)
        
        return entropia


class ResultadoEscaneo:
    """Representa el resultado del escaneo de un archivo con información detallada."""
    
    def __init__(self, ruta: str, es_limpio: bool = True, 
                 amenazas_detectadas: Optional[List[Dict[str, Any]]] = None,
                 detalles_adicionales: Optional[Dict[str, Any]] = None):
        """
        Inicializa un resultado de escaneo con información completa.
        
        Args:
            ruta: Ruta del archivo escaneado
            es_limpio: True si el archivo está limpio, False si hay amenazas
            amenazas_detectadas: Lista de amenazas encontradas con detalles
            detalles_adicionales: Información adicional del escaneo
        """
        self.ruta = ruta
        self.es_limpio = es_limpio
        self.amenazas_detectadas = amenazas_detectadas or []
        self.detalles_adicionales = detalles_adicionales or {}
        self.timestamp_escaneo = datetime.now()
        self.hash_sha256 = self._calcular_hash()
        self.hash_md5 = self._calcular_hash_md5()
        self.tamaño_archivo = self._obtener_tamaño()
        self.tiempo_escaneo = 0.0
        self.nivel_riesgo_maximo = self._determinar_nivel_riesgo()
        self.recomendacion = self._generar_recomendacion()
    
    def _calcular_hash(self) -> str:
        """Calcula el hash SHA256 del archivo."""
        try:
            with open(self.ruta, 'rb') as archivo:
                contenido = archivo.read()
                return hashlib.sha256(contenido).hexdigest()
        except Exception:
            return ""
    
    def _calcular_hash_md5(self) -> Optional[str]:
        """Calcula el hash MD5 del archivo."""
        try:
            if not os.path.exists(self.ruta):
                return None
            
            hash_md5 = hashlib.md5()
            with open(self.ruta, 'rb') as archivo:
                for chunk in iter(lambda: archivo.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return None
    
    def _obtener_tamaño(self) -> int:
        """Obtiene el tamaño del archivo en bytes."""
        try:
            return obtener_tamaño_archivo(self.ruta)
        except Exception:
            return 0
    
    def _determinar_nivel_riesgo(self) -> str:
        """Determina el nivel de riesgo máximo basado en las amenazas detectadas."""
        if not self.amenazas_detectadas:
            return NivelRiesgo.INFORMATIVO
        
        niveles_orden = [
            NivelRiesgo.CRITICO,
            NivelRiesgo.ALTO,
            NivelRiesgo.MEDIO,
            NivelRiesgo.BAJO,
            NivelRiesgo.INFORMATIVO
        ]
        
        for nivel in niveles_orden:
            if any(amenaza.get('nivel_riesgo') == nivel for amenaza in self.amenazas_detectadas):
                return nivel
        
        return NivelRiesgo.INFORMATIVO
    
    def _generar_recomendacion(self) -> str:
        """Genera una recomendación basada en el resultado del escaneo."""
        if self.es_limpio:
            return "✅ Archivo seguro - No se requiere acción"
        
        if self.nivel_riesgo_maximo == NivelRiesgo.CRITICO:
            return "🚨 ELIMINAR INMEDIATAMENTE - Amenaza crítica detectada"
        elif self.nivel_riesgo_maximo == NivelRiesgo.ALTO:
            return "⚠️ CUARENTENA RECOMENDADA - Amenaza de alto riesgo"
        elif self.nivel_riesgo_maximo == NivelRiesgo.MEDIO:
            return "🔍 REVISAR MANUALMENTE - Actividad sospechosa"
        else:
            return "📋 MONITOREAR - Posible falso positivo"
    
    def tiene_amenazas(self) -> bool:
        """Verifica si el archivo tiene amenazas."""
        return not self.es_limpio and len(self.amenazas_detectadas) > 0
    
    def obtener_resumen(self) -> str:
        """Obtiene un resumen del resultado del escaneo."""
        estado = "LIMPIO" if self.es_limpio else "INFECTADO"
        amenazas_count = len(self.amenazas_detectadas)
        
        resumen = f"[{estado}] {self.ruta}"
        if not self.es_limpio:
            resumen += f" - {amenazas_count} amenaza(s) - Riesgo: {self.nivel_riesgo_maximo}"
        
        return resumen
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el resultado a diccionario para serialización."""
        return {
            'ruta': self.ruta,
            'es_limpio': self.es_limpio,
            'amenazas_detectadas': self.amenazas_detectadas,
            'detalles_adicionales': self.detalles_adicionales,
            'timestamp_escaneo': self.timestamp_escaneo.isoformat(),
            'hash_sha256': self.hash_sha256,
            'hash_md5': self.hash_md5,
            'tamaño_archivo': self.tamaño_archivo,
            'tiempo_escaneo': self.tiempo_escaneo,
            'nivel_riesgo_maximo': self.nivel_riesgo_maximo,
            'recomendacion': self.recomendacion
        }


class EscaneadorMalware:
    """
    Escaneador de Malware Avanzado de Ares Aegis.
    
    Características principales:
    - Motor de detección multicapa con firmas avanzadas
    - Análisis heurístico para detección de amenazas desconocidas
    - Sistema de puntuación de riesgo adaptativo
    - Cache inteligente para optimización de rendimiento
    - Correlación con SIEM para análisis de patrones
    """
    
    def __init__(self, siem: SIEM):
        """
        Inicializa el escaneador avanzado.
        
        Args:
            siem: Instancia del SIEM para registro de eventos
        """
        self.siem = siem
        self.logger = configurar_logger_modulo("escaneador_malware")
        
        # Base de datos de firmas avanzada
        self.firmas_deteccion: List[FirmaDeteccion] = []
        self.firmas_por_tipo: Dict[str, List[FirmaDeteccion]] = defaultdict(list)
        self.firmas_hash: Dict[str, FirmaDeteccion] = {}
        
        # Motor heurístico
        self.analizador_heuristico = AnalizadorHeuristico()
        
        # Cache de resultados
        self.cache_escaneos: Dict[str, ResultadoEscaneo] = {}
        self.cache_max_size = 1000
        
        # Estadísticas avanzadas
        self.estadisticas = {
            'archivos_escaneados': 0,
            'amenazas_detectadas': 0,
            'detecciones_por_tipo': defaultdict(int),
            'tiempo_total_escaneo': 0.0,
            'ultimo_escaneo': None,
            'cache_hits': 0,
            'analisis_heuristico_activado': 0
        }
        
        # Configuración del escaneador
        self.configuracion = {
            'max_tamaño_archivo': 500 * 1024 * 1024,  # 500MB
            'usar_cache': True,
            'analisis_heuristico': True,
            'nivel_sensibilidad': 'MEDIO',  # BAJO, MEDIO, ALTO
            'extensiones_peligrosas': {
                '.exe', '.scr', '.bat', '.cmd', '.com', '.pif', 
                '.vbs', '.js', '.jar', '.app', '.deb', '.rpm'
            },
            'extensiones_ejecutables': {
                '.exe', '.dll', '.so', '.dylib', '.sys', '.bin'
            }
        }
        
        # Inicializar componentes
        self._cargar_firmas_avanzadas()
        
        # Registrar inicio en SIEM
        self.siem.registrar_evento(
            TipoEvento.SISTEMA_INICIADO,
            "Escaneador de Malware Avanzado inicializado",
            {
                'firmas_cargadas': len(self.firmas_deteccion),
                'tipos_amenaza': len(self.firmas_por_tipo),
                'motor_heuristico': True,
                'cache_habilitado': self.configuracion['usar_cache']
            },
            NivelCriticidad.INFORMATIVO
        )
        
        self.logger.info(f"Escaneador avanzado inicializado con {len(self.firmas_deteccion)} firmas")
    
    def _cargar_firmas_avanzadas(self):
        """Carga firmas avanzadas desde el archivo de configuración."""
        try:
            # Usar configuración local
            archivo_firmas = Path.cwd() / "configuracion" / "firmas.txt"
            
            if os.path.exists(archivo_firmas):
                self._procesar_archivo_firmas(str(archivo_firmas))
            else:
                self._crear_firmas_por_defecto()
                
            self.logger.info(f"Firmas cargadas: {len(self.firmas_deteccion)} total")
            
        except Exception as e:
            self.logger.error(f"Error cargando firmas: {e}")
            self._crear_firmas_por_defecto()
    
    def _procesar_archivo_firmas(self, archivo_firmas: str):
        """Procesa el archivo de firmas y crea objetos FirmaDeteccion."""
        with open(archivo_firmas, 'r', encoding='utf-8') as archivo:
            for numero_linea, linea in enumerate(archivo, 1):
                linea = linea.strip()
                
                # Saltar líneas vacías y comentarios
                if not linea or linea.startswith('#'):
                    continue
                
                try:
                    # Formato: tipo|patrón|descripción|severidad
                    partes = linea.split('|')
                    if len(partes) >= 4:
                        tipo = partes[0].strip()
                        patron = partes[1].strip()
                        descripcion = partes[2].strip()
                        severidad = partes[3].strip()
                        
                        # Mapear severidad a nivel de riesgo
                        nivel_riesgo = self._mapear_severidad(severidad)
                        
                        # Crear firma de detección
                        firma = FirmaDeteccion(tipo, patron, descripcion, nivel_riesgo)
                        self.firmas_deteccion.append(firma)
                        self.firmas_por_tipo[tipo].append(firma)
                        
                        # Si es un hash, agregarlo al diccionario de hashes
                        if patron.startswith('HASH:'):
                            hash_valor = patron[5:].strip()
                            self.firmas_hash[hash_valor] = firma
                            
                except Exception as e:
                    self.logger.warning(f"Error procesando línea {numero_linea}: {e}")
                    continue
    
    def _mapear_severidad(self, severidad: str) -> str:
        """Mapea severidad del archivo a nivel de riesgo."""
        mapeo = {
            'ALTA': NivelRiesgo.ALTO,
            'MEDIA': NivelRiesgo.MEDIO,
            'BAJA': NivelRiesgo.BAJO,
            'CRITICA': NivelRiesgo.CRITICO
        }
        return mapeo.get(severidad.upper(), NivelRiesgo.MEDIO)
    
    def _crear_firmas_por_defecto(self):
        """Crea firmas básicas por defecto."""
        firmas_base = [
            (TipoAmenaza.VIRUS, "X5O!P%@AP[4\\PZX54(P^)7CC)7}$", "EICAR Test File", NivelRiesgo.MEDIO),
            (TipoAmenaza.TROJAN, "BEGIN PGP MESSAGE", "Mensaje cifrado sospechoso", NivelRiesgo.MEDIO),
            (TipoAmenaza.BACKDOOR, "cmd.exe /c", "Ejecución de comando sospechosa", NivelRiesgo.ALTO),
            (TipoAmenaza.MALWARE, "CreateRemoteThread", "Inyección de código", NivelRiesgo.ALTO),
            (TipoAmenaza.SCRIPT_MALICIOSO, "eval(", "Ejecución dinámica", NivelRiesgo.MEDIO),
            (TipoAmenaza.SCRIPT_MALICIOSO, "base64_decode", "Decodificación sospechosa", NivelRiesgo.MEDIO),
            (TipoAmenaza.SCRIPT_MALICIOSO, "shell_exec", "Ejecución de shell", NivelRiesgo.ALTO),
            (TipoAmenaza.RANSOMWARE, "Your files have been encrypted", "Mensaje ransomware", NivelRiesgo.CRITICO),
            (TipoAmenaza.KEYLOGGER, "GetAsyncKeyState", "Captura de teclas", NivelRiesgo.ALTO),
            (TipoAmenaza.ROOTKIT, "ZwQueryDirectoryFile", "Hook API sospechoso", NivelRiesgo.ALTO)
        ]
        
        for tipo, patron, descripcion, nivel in firmas_base:
            firma = FirmaDeteccion(tipo, patron, descripcion, nivel)
            self.firmas_deteccion.append(firma)
            self.firmas_por_tipo[tipo].append(firma)
        
        self.logger.info(f"Usando {len(firmas_base)} firmas por defecto")
    
    def escanear_archivo(self, ruta_archivo: str) -> ResultadoEscaneo:
        """
        Escanea un archivo en busca de malware con análisis multicapa.
        
        Args:
            ruta_archivo: Ruta del archivo a escanear
            
        Returns:
            ResultadoEscaneo: Resultado del escaneo
        """
        inicio_tiempo = time.time()
        hash_archivo = None
        
        # Verificar cache primero
        if self.configuracion['usar_cache']:
            hash_archivo = self._calcular_hash_rapido(ruta_archivo)
            if hash_archivo and hash_archivo in self.cache_escaneos:
                self.estadisticas['cache_hits'] += 1
                return self.cache_escaneos[hash_archivo]
        
        try:
            # Validaciones iniciales
            if not validar_ruta_archivo(ruta_archivo):
                return ResultadoEscaneo(
                    ruta_archivo, 
                    False, 
                    [{'tipo': 'ERROR', 'descripcion': 'Archivo no válido o no accesible'}]
                )
            
            # Verificar tamaño
            tamaño_archivo = obtener_tamaño_archivo(ruta_archivo)
            if tamaño_archivo > self.configuracion['max_tamaño_archivo']:
                return ResultadoEscaneo(
                    ruta_archivo,
                    True,
                    [],
                    {'motivo_salto': 'Archivo demasiado grande', 'tamaño': tamaño_archivo}
                )
            
            amenazas_detectadas = []
            detalles_escaneo = {
                'metodo_deteccion': [],
                'tiempo_escaneo': 0.0,
                'tamaño_archivo': tamaño_archivo
            }
            
            # Registrar inicio de escaneo
            self.siem.registrar_evento(
                TipoEvento.ESCANEO_INICIADO,
                f"Iniciando escaneo de malware: {ruta_archivo}",
                {'ruta': ruta_archivo, 'tamaño': tamaño_archivo},
                NivelCriticidad.INFORMATIVO
            )
            
            # 1. Verificación por hash (más rápida)
            hash_sha256 = self._calcular_hash_completo(ruta_archivo)
            if hash_sha256 in self.firmas_hash:
                firma = self.firmas_hash[hash_sha256]
                amenazas_detectadas.append({
                    'tipo': firma.tipo,
                    'descripcion': firma.descripcion,
                    'nivel_riesgo': firma.nivel_riesgo,
                    'metodo_deteccion': 'HASH',
                    'firma_id': hash_sha256
                })
                detalles_escaneo['metodo_deteccion'].append('HASH')
            
            # 2. Análisis de contenido (firmas de patrón)
            try:
                with open(ruta_archivo, 'r', encoding='utf-8', errors='ignore') as archivo:
                    contenido = archivo.read()
                
                # Verificar firmas de detección
                for firma in self.firmas_deteccion:
                    if firma.detectar(contenido):
                        amenazas_detectadas.append({
                            'tipo': firma.tipo,
                            'descripcion': firma.descripcion,
                            'nivel_riesgo': firma.nivel_riesgo,
                            'metodo_deteccion': 'PATRON',
                            'patron': firma.patron
                        })
                        
                        # Actualizar estadísticas de firma
                        self.estadisticas['detecciones_por_tipo'][firma.tipo] += 1
                
                detalles_escaneo['metodo_deteccion'].append('PATRON')
                
                # 3. Análisis heurístico si está habilitado
                if self.configuracion['analisis_heuristico']:
                    extension = Path(ruta_archivo).suffix
                    resultado_heuristico = self.analizador_heuristico.analizar(contenido, extension)
                    
                    if resultado_heuristico['es_sospechoso']:
                        amenazas_detectadas.append({
                            'tipo': 'HEURISTICO',
                            'descripcion': f"Análisis heurístico: {', '.join(resultado_heuristico['patrones_detectados'])}",
                            'nivel_riesgo': NivelRiesgo.MEDIO,
                            'metodo_deteccion': 'HEURISTICO',
                            'puntuacion_riesgo': resultado_heuristico['puntuacion_riesgo']
                        })
                        
                        self.estadisticas['analisis_heuristico_activado'] += 1
                    
                    detalles_escaneo['analisis_heuristico'] = resultado_heuristico
                    detalles_escaneo['metodo_deteccion'].append('HEURISTICO')
                
            except UnicodeDecodeError:
                # Archivo binario - solo análisis por hash
                detalles_escaneo['tipo_archivo'] = 'binario'
                pass
            
            # Calcular tiempo de escaneo
            tiempo_transcurrido = time.time() - inicio_tiempo
            detalles_escaneo['tiempo_escaneo'] = tiempo_transcurrido
            
            # Crear resultado
            es_limpio = len(amenazas_detectadas) == 0
            resultado = ResultadoEscaneo(
                ruta_archivo,
                es_limpio,
                amenazas_detectadas,
                detalles_escaneo
            )
            resultado.tiempo_escaneo = tiempo_transcurrido
            
            # Actualizar estadísticas
            self.estadisticas['archivos_escaneados'] += 1
            if not es_limpio:
                self.estadisticas['amenazas_detectadas'] += len(amenazas_detectadas)
            self.estadisticas['tiempo_total_escaneo'] += tiempo_transcurrido
            self.estadisticas['ultimo_escaneo'] = datetime.now()
            
            # Registrar resultado en SIEM
            if not es_limpio:
                self.siem.registrar_evento(
                    TipoEvento.MALWARE_DETECTADO,
                    f"Malware detectado en {ruta_archivo}",
                    {
                        'ruta': ruta_archivo,
                        'amenazas': len(amenazas_detectadas),
                        'nivel_riesgo': resultado.nivel_riesgo_maximo,
                        'hash_sha256': hash_sha256
                    },
                    NivelCriticidad.ALTO if resultado.nivel_riesgo_maximo in [NivelRiesgo.ALTO, NivelRiesgo.CRITICO] else NivelCriticidad.MEDIO
                )
            
            # Guardar en cache
            if self.configuracion['usar_cache'] and hash_archivo:
                if len(self.cache_escaneos) >= self.cache_max_size:
                    # Limpiar cache (FIFO)
                    oldest_key = next(iter(self.cache_escaneos))
                    del self.cache_escaneos[oldest_key]
                
                self.cache_escaneos[hash_archivo] = resultado
            
            return resultado
            
        except Exception as e:
            self.logger.error(f"Error escaneando archivo {ruta_archivo}: {e}")
            return ResultadoEscaneo(
                ruta_archivo,
                False,
                [{'tipo': 'ERROR', 'descripcion': f'Error de escaneo: {str(e)}'}],
                {'error': str(e)}
            )
    
    def _calcular_hash_rapido(self, ruta_archivo: str) -> Optional[str]:
        """Calcula un hash rápido para el cache."""
        try:
            stat = os.stat(ruta_archivo)
            # Usar tamaño + tiempo de modificación como hash rápido
            return hashlib.md5(f"{stat.st_size}_{stat.st_mtime}".encode()).hexdigest()
        except Exception:
            return None
    
    def _calcular_hash_completo(self, ruta_archivo: str) -> str:
        """Calcula el hash SHA256 completo del archivo."""
        try:
            hash_sha256 = hashlib.sha256()
            with open(ruta_archivo, 'rb') as archivo:
                for chunk in iter(lambda: archivo.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception:
            return ""
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas completas del escaneador."""
        return {
            **self.estadisticas,
            'firmas_cargadas': len(self.firmas_deteccion),
            'tipos_amenaza_conocidos': len(self.firmas_por_tipo),
            'cache_size': len(self.cache_escaneos),
            'configuracion': self.configuracion.copy()
        }
    
    def limpiar_cache(self):
        """Limpia el cache de escaneos."""
        self.cache_escaneos.clear()
        self.logger.info("Cache de escaneos limpiado")
    
    def actualizar_configuracion(self, nueva_config: Dict[str, Any]):
        """Actualiza la configuración del escaneador."""
        self.configuracion.update(nueva_config)
        self.logger.info("Configuración del escaneador actualizada")
