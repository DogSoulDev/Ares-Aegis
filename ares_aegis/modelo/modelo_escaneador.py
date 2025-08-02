#!/usr/bin/env python3
"""
Creado por DogSoulDev (https://github.com/DogSoulDev)
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

from .modelo_siem import SIEM, TipoEvento, NivelCriticidad
from ..utils.validaciones import (
    validar_ruta_archivo, validar_ruta_directorio, 
    validar_permisos_lectura, es_ruta_segura
)
from ..utils.ayuda_rutas import (
    listar_archivos_recursivo, obtener_tamaño_archivo,
    obtener_rutas_sistema
)
from ..utils.ayuda_logging import configurar_logger_modulo


class TipoAmenaza:
    """Tipos de amenazas que puede detectar el escaneador."""
    VIRUS = "virus"
    TROYANO = "troyano"
    GUSANO = "gusano"
    ADWARE = "adware"
    SPYWARE = "spyware"
    ROOTKIT = "rootkit"
    RANSOMWARE = "ransomware"
    BACKDOOR = "backdoor"
    KEYLOGGER = "keylogger"
    BOTNET = "botnet"
    EXPLOITS = "exploits"
    SOSPECHOSO = "sospechoso"
    UNKNOWN = "desconocido"


class NivelAmenaza:
    """Niveles de criticidad de las amenazas."""
    BAJO = 1
    MEDIO = 2
    ALTO = 3
    CRITICO = 4
    EXTREMO = 5


class ResultadoEscaneo:
    """Resultado de un escaneo individual."""
    
    def __init__(self, ruta: str, amenaza_detectada: bool = False, 
                 tipo_amenaza: Optional[str] = None, nivel_criticidad: int = 1,
                 hash_archivo: str = "", descripcion: str = "",
                 metadatos: Optional[Dict[str, Any]] = None):
        self.ruta = ruta
        self.amenaza_detectada = amenaza_detectada
        self.tipo_amenaza = tipo_amenaza or TipoAmenaza.UNKNOWN
        self.nivel_criticidad = nivel_criticidad
        self.hash_archivo = hash_archivo
        self.descripcion = descripcion
        self.metadatos = metadatos or {}
        self.timestamp = datetime.now()
    
    def __str__(self):
        estado = "🚨 AMENAZA" if self.amenaza_detectada else "✅ LIMPIO"
        return f"{estado} - {self.ruta} ({self.tipo_amenaza})"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el resultado a diccionario."""
        return {
            'ruta': self.ruta,
            'amenaza_detectada': self.amenaza_detectada,
            'tipo_amenaza': self.tipo_amenaza,
            'nivel_criticidad': self.nivel_criticidad,
            'hash_archivo': self.hash_archivo,
            'descripcion': self.descripcion,
            'metadatos': self.metadatos,
            'timestamp': self.timestamp.isoformat()
        }
    
    def tiene_amenazas(self) -> bool:
        """Verifica si se detectó alguna amenaza en el resultado."""
        return self.amenaza_detectada
    
    def obtener_tamaño(self) -> int:
        """Obtiene el tamaño del archivo."""
        try:
            return obtener_tamaño_archivo(self.ruta)
        except Exception:
            return 0


class EscaneadorMalware:
    """Sistema de detección de malware avanzado con múltiples capas de análisis."""
    
    def __init__(self, configuracion: Optional[Dict[str, Any]] = None):
        """Inicializa el escaneador con configuración personalizada."""
        self.configuracion = configuracion or self._configuracion_por_defecto()
        self.logger = configurar_logger_modulo(__name__)
        
        # Estado interno
        self.firmas_deteccion = {}
        self.firmas_por_tipo = defaultdict(list)
        self.patrones_heuristicos = []
        self.cache_escaneos = {}
        self.estadisticas = defaultdict(int)
        
        # Control de threading
        self.detener_evento = threading.Event()
        self.lock_estado = threading.Lock()
        
        # SIEM para reportes
        self.siem = None
        
        # Configuración avanzada
        self.tamaño_maximo_analisis = self.configuracion.get('tamaño_maximo_mb', 100) * 1024 * 1024
        self.usar_cache = self.configuracion.get('usar_cache', True)
        self.analisis_heuristico = self.configuracion.get('heuristico_activo', True)
        
        # Inicializar componentes
        self._cargar_firmas_deteccion()
        self._configurar_patrones_heuristicos()
        
        self.logger.info("🛡️ Escaneador de malware inicializado correctamente")
    
    def _configuracion_por_defecto(self) -> Dict[str, Any]:
        """Configuración por defecto del escaneador."""
        return {
            'tamaño_maximo_mb': 100,
            'usar_cache': True,
            'heuristico_activo': True,
            'analisis_profundo': True,
            'timeout_archivo_seg': 30,
            'extensiones_ejecutables': [
                '.exe', '.dll', '.bat', '.cmd', '.ps1', '.sh', '.py', '.js',
                '.vbs', '.jar', '.apk', '.deb', '.rpm', '.msi', '.scr'
            ]
        }
    
    def _cargar_firmas_deteccion(self):
        """Carga las firmas de detección desde archivos."""
        try:
            ruta_firmas = os.path.join(obtener_rutas_sistema()['configuracion'], 'firmas.txt')
            
            if os.path.exists(ruta_firmas):
                with open(ruta_firmas, 'r', encoding='utf-8') as f:
                    for linea in f:
                        linea = linea.strip()
                        if linea and not linea.startswith('#'):
                            partes = linea.split('|')
                            if len(partes) >= 3:
                                hash_firma = partes[0]
                                tipo_amenaza = partes[1]
                                descripcion = partes[2]
                                
                                self.firmas_deteccion[hash_firma] = {
                                    'tipo': tipo_amenaza,
                                    'descripcion': descripcion,
                                    'criticidad': NivelAmenaza.ALTO
                                }
                                self.firmas_por_tipo[tipo_amenaza].append(hash_firma)
            
            # Firmas básicas incorporadas
            self._cargar_firmas_incorporadas()
            
            self.logger.info(f"📚 Cargadas {len(self.firmas_deteccion)} firmas de detección")
            
        except Exception as e:
            self.logger.error(f"❌ Error cargando firmas: {e}")
            self._cargar_firmas_incorporadas()
    
    def _cargar_firmas_incorporadas(self):
        """Carga firmas básicas incorporadas en el código."""
        firmas_basicas = {
            # Hashes conocidos de malware (ejemplos educativos)
            "44d88612fea8a8f36de82e1278abb02f": {
                'tipo': TipoAmenaza.VIRUS,
                'descripcion': "Muestra de virus conocido",
                'criticidad': NivelAmenaza.ALTO
            },
            "275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f": {
                'tipo': TipoAmenaza.TROYANO,
                'descripcion': "Troyano genérico",
                'criticidad': NivelAmenaza.CRITICO
            }
        }
        
        for hash_firma, info in firmas_basicas.items():
            if hash_firma not in self.firmas_deteccion:
                self.firmas_deteccion[hash_firma] = info
                self.firmas_por_tipo[info['tipo']].append(hash_firma)
    
    def _configurar_patrones_heuristicos(self):
        """Configura patrones heurísticos para detección de comportamientos sospechosos."""
        self.patrones_heuristicos = [
            # Patrones de strings sospechosos
            {
                'patron': rb'(?i)(malware|virus|trojan|backdoor|rootkit)',
                'tipo': TipoAmenaza.SOSPECHOSO,
                'peso': 3
            },
            {
                'patron': rb'(?i)(keylogger|password.*steal|credit.*card)',
                'tipo': TipoAmenaza.SPYWARE,
                'peso': 4
            },
            {
                'patron': rb'(?i)(encrypt.*files|ransom|bitcoin|pay.*unlock)',
                'tipo': TipoAmenaza.RANSOMWARE,
                'peso': 5
            },
            # Patrones de APIs peligrosas
            {
                'patron': rb'(?i)(createfile|writeprocessmemory|virtualalloc)',
                'tipo': TipoAmenaza.SOSPECHOSO,
                'peso': 2
            },
            {
                'patron': rb'(?i)(regsetvalue|createservice|setwindowshook)',
                'tipo': TipoAmenaza.ROOTKIT,
                'peso': 4
            }
        ]
        
        self.logger.info(f"🧠 Configurados {len(self.patrones_heuristicos)} patrones heurísticos")
    
    def conectar_siem(self, siem: SIEM):
        """Conecta el escaneador al sistema SIEM."""
        self.siem = siem
        self.logger.info("🔗 Escaneador conectado al SIEM")
    
    def escanear_archivo(self, ruta_archivo: str) -> Optional[ResultadoEscaneo]:
        """
        Escanea un archivo individual en busca de malware.
        
        Args:
            ruta_archivo (str): Ruta del archivo a escanear
            
        Returns:
            Optional[ResultadoEscaneo]: Resultado del escaneo o None si hay error
        """
        try:
            # Validaciones básicas
            if not validar_ruta_archivo(ruta_archivo):
                return None
            
            if not validar_permisos_lectura(ruta_archivo):
                self.logger.warning(f"⚠️ Sin permisos de lectura: {ruta_archivo}")
                return None
            
            # Verificar tamaño del archivo
            tamaño_archivo = obtener_tamaño_archivo(ruta_archivo)
            if tamaño_archivo > self.tamaño_maximo_analisis:
                self.logger.warning(f"⚠️ Archivo demasiado grande para análisis: {ruta_archivo}")
                return ResultadoEscaneo(
                    ruta_archivo, False, TipoAmenaza.UNKNOWN, NivelAmenaza.BAJO,
                    descripcion="Archivo demasiado grande para análisis"
                )
            
            # Verificar cache
            if self.usar_cache:
                cache_key = f"{ruta_archivo}_{tamaño_archivo}"
                if cache_key in self.cache_escaneos:
                    self.estadisticas['archivos_cache'] += 1
                    return self.cache_escaneos[cache_key]
            
            # Calcular hash del archivo
            hash_archivo = self._calcular_hash_archivo(ruta_archivo)
            
            # Análisis por firmas
            resultado_firmas = self._analizar_por_firmas(ruta_archivo, hash_archivo)
            if resultado_firmas:
                return self._guardar_resultado_cache(ruta_archivo, resultado_firmas)
            
            # Análisis heurístico
            if self.analisis_heuristico:
                resultado_heuristico = self._analizar_heuristico(ruta_archivo, hash_archivo)
                if resultado_heuristico:
                    return self._guardar_resultado_cache(ruta_archivo, resultado_heuristico)
            
            # Archivo limpio
            resultado_limpio = ResultadoEscaneo(
                ruta_archivo, False, TipoAmenaza.UNKNOWN, NivelAmenaza.BAJO,
                hash_archivo, "Archivo limpio"
            )
            
            self.estadisticas['archivos_limpios'] += 1
            return self._guardar_resultado_cache(ruta_archivo, resultado_limpio)
            
        except Exception as e:
            self.logger.error(f"❌ Error escaneando archivo {ruta_archivo}: {e}")
            return None
    
    def escanear_directorio(self, ruta_directorio: str, recursivo: bool = True, 
                           callback_progreso: Optional[Callable] = None) -> List[ResultadoEscaneo]:
        """
        Escanea un directorio completo en busca de malware.
        
        Args:
            ruta_directorio (str): Ruta del directorio a escanear
            recursivo (bool): Si incluir subdirectorios
            callback_progreso (Callable): Función callback para progreso
            
        Returns:
            List[ResultadoEscaneo]: Lista de resultados del escaneo
        """
        self.logger.info(f"🔍 Iniciando escaneo de directorio: {ruta_directorio}")
        
        if not validar_ruta_directorio(ruta_directorio):
            self.logger.error(f"❌ Directorio inválido o no accesible: {ruta_directorio}")
            return []
        
        try:
            # Obtener lista de archivos
            archivos = list(listar_archivos_recursivo(ruta_directorio) if recursivo
                          else Path(ruta_directorio).iterdir())
            
            total_archivos = len(archivos)
            resultados = []
            
            self.logger.info(f"📊 Se van a escanear {total_archivos} archivos")
            
            for i, archivo in enumerate(archivos):
                if self.detener_evento.is_set():
                    self.logger.info("⏹️ Escaneo detenido por solicitud del usuario")
                    break
                
                if archivo.is_file():
                    resultado = self.escanear_archivo(str(archivo))
                    if resultado:
                        resultados.append(resultado)
                        
                        # Reportar al SIEM si hay amenaza
                        if resultado.amenaza_detectada and self.siem:
                            self.siem.registrar_evento(
                                TipoEvento.MALWARE_DETECTADO,
                                f"Malware detectado: {resultado.descripcion}",
                                {'ruta': resultado.ruta, 'tipo': resultado.tipo_amenaza},
                                NivelCriticidad.ALTO
                            )
                
                # Callback de progreso
                if callback_progreso:
                    callback_progreso(i + 1, total_archivos)
            
            amenazas_encontradas = sum(1 for r in resultados if r.amenaza_detectada)
            self.logger.info(f"✅ Escaneo completado. {amenazas_encontradas} amenazas detectadas de {len(resultados)} archivos")
            
            return resultados
            
        except Exception as e:
            self.logger.error(f"❌ Error durante escaneo de directorio: {e}")
            return []
    
    def _calcular_hash_archivo(self, ruta_archivo: str) -> str:
        """Calcula el hash SHA-256 de un archivo."""
        try:
            hash_sha256 = hashlib.sha256()
            with open(ruta_archivo, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            self.logger.error(f"❌ Error calculando hash de {ruta_archivo}: {e}")
            return ""
    
    def _analizar_por_firmas(self, ruta_archivo: str, hash_archivo: str) -> Optional[ResultadoEscaneo]:
        """Analiza un archivo usando firmas conocidas."""
        try:
            # Buscar por hash completo
            if hash_archivo in self.firmas_deteccion:
                firma = self.firmas_deteccion[hash_archivo]
                self.estadisticas['amenazas_detectadas'] += 1
                self.logger.warning(f"🚨 Amenaza detectada por firma: {ruta_archivo}")
                
                return ResultadoEscaneo(
                    ruta_archivo, True, firma['tipo'], firma['criticidad'],
                    hash_archivo, f"Amenaza conocida: {firma['descripcion']}"
                )
            
            # Buscar por hash parcial (primeros 32 caracteres - MD5 equivalente)
            hash_parcial = hash_archivo[:32] if len(hash_archivo) >= 32 else hash_archivo
            if hash_parcial in self.firmas_deteccion:
                firma = self.firmas_deteccion[hash_parcial]
                self.estadisticas['amenazas_detectadas'] += 1
                self.logger.warning(f"🚨 Amenaza detectada por firma parcial: {ruta_archivo}")
                
                return ResultadoEscaneo(
                    ruta_archivo, True, firma['tipo'], firma['criticidad'],
                    hash_archivo, f"Amenaza conocida (parcial): {firma['descripcion']}"
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Error en análisis por firmas: {e}")
            return None
    
    def _analizar_heuristico(self, ruta_archivo: str, hash_archivo: str) -> Optional[ResultadoEscaneo]:
        """Análisis heurístico del archivo."""
        try:
            puntuacion_sospecha = 0
            patrones_encontrados = []
            
            # Leer contenido del archivo
            with open(ruta_archivo, 'rb') as f:
                contenido = f.read(1024 * 1024)  # Leer primer MB
            
            # Aplicar patrones heurísticos
            for patron_config in self.patrones_heuristicos:
                patron = patron_config['patron']
                if re.search(patron, contenido):
                    puntuacion_sospecha += patron_config['peso']
                    patrones_encontrados.append(patron_config['tipo'])
            
            # Análisis adicional por extensión
            extension = Path(ruta_archivo).suffix.lower()
            if extension in self.configuracion['extensiones_ejecutables']:
                puntuacion_sospecha += 1
            
            # Decidir si es sospechoso
            if puntuacion_sospecha >= 5:
                tipo_predominante = max(set(patrones_encontrados), key=patrones_encontrados.count) if patrones_encontrados else TipoAmenaza.SOSPECHOSO
                nivel = min(puntuacion_sospecha, NivelAmenaza.EXTREMO)
                
                self.estadisticas['sospechosos_detectados'] += 1
                self.logger.warning(f"🤔 Archivo sospechoso detectado: {ruta_archivo} (puntuación: {puntuacion_sospecha})")
                
                return ResultadoEscaneo(
                    ruta_archivo, True, tipo_predominante, nivel,
                    hash_archivo, f"Comportamiento sospechoso detectado (puntuación: {puntuacion_sospecha})"
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Error en análisis heurístico: {e}")
            return None
    
    def _guardar_resultado_cache(self, ruta_archivo: str, resultado: ResultadoEscaneo) -> ResultadoEscaneo:
        """Guarda el resultado en cache y devuelve el resultado."""
        if self.usar_cache:
            try:
                tamaño = obtener_tamaño_archivo(ruta_archivo)
                cache_key = f"{ruta_archivo}_{tamaño}"
                self.cache_escaneos[cache_key] = resultado
            except Exception:
                pass  # Si falla el cache, continuar normal
        
        return resultado
    
    def detener_escaneo(self):
        """Detiene el escaneo en curso."""
        self.detener_evento.set()
        self.logger.info("⏹️ Solicitud de detención de escaneo enviada")
    
    def reiniciar_escaneo(self):
        """Reinicia el estado del escaneador."""
        self.detener_evento.clear()
        self.logger.info("🔄 Escaneador reiniciado")
    
    def limpiar_cache(self):
        """Limpia el cache de escaneos."""
        self.cache_escaneos.clear()
        self.logger.info("🧹 Cache de escaneos limpiado")
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas completas del escaneador."""
        return {
            **self.estadisticas,
            'firmas_cargadas': len(self.firmas_deteccion),
            'tipos_amenaza_conocidos': len(self.firmas_por_tipo),
            'cache_size': len(self.cache_escaneos),
            'configuracion': self.configuracion.copy()
        }
    
    def agregar_firma_personalizada(self, hash_archivo: str, tipo_amenaza: str, 
                                  descripcion: str, criticidad: int = NivelAmenaza.MEDIO):
        """Agrega una firma personalizada al escaneador."""
        self.firmas_deteccion[hash_archivo] = {
            'tipo': tipo_amenaza,
            'descripcion': descripcion,
            'criticidad': criticidad
        }
        self.firmas_por_tipo[tipo_amenaza].append(hash_archivo)
        
        self.logger.info(f"➕ Firma personalizada agregada: {hash_archivo} ({tipo_amenaza})")
    
    def generar_reporte(self, resultados: List[ResultadoEscaneo]) -> Dict[str, Any]:
        """Genera un reporte completo de los resultados de escaneo."""
        amenazas = [r for r in resultados if r.amenaza_detectada]
        limpios = [r for r in resultados if not r.amenaza_detectada]
        
        # Estadísticas por tipo
        tipos_amenaza = defaultdict(int)
        niveles_criticidad = defaultdict(int)
        
        for amenaza in amenazas:
            tipos_amenaza[amenaza.tipo_amenaza] += 1
            niveles_criticidad[amenaza.nivel_criticidad] += 1
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_archivos': len(resultados),
            'amenazas_detectadas': len(amenazas),
            'archivos_limpios': len(limpios),
            'tipos_amenaza': dict(tipos_amenaza),
            'niveles_criticidad': dict(niveles_criticidad),
            'estadisticas_escaneador': self.obtener_estadisticas(),
            'amenazas_detalle': [a.to_dict() for a in amenazas[:100]]  # Limitar detalles
        }
