#!/usr/bin/env python3
"""
Copyright (c) 2025 DogSoulDev (https://github.com/DogSoulDev)
Todos los derechos reservados. Este código es propietario y confidencial.

Analizadores Especializados - Ares Aegis
Sistema de análisis especializado con múltiples componentes de análisis avanzado
"""

import os
import re
import time
import json
import hashlib
import threading
import subprocess
import mimetypes
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Union, Tuple, Iterator
from dataclasses import dataclass, field
from collections import defaultdict, deque, Counter
from enum import Enum
import tempfile
import stat

from .siem import SIEM, TipoEvento
from ..utilidades.validaciones import validar_ruta_archivo, validar_permisos_lectura
from ..utilidades.ayuda_rutas import crear_ruta_segura, obtener_rutas_sistema
from ..utilidades.ayuda_logging import configurar_logger_modulo


class TipoAnalisisEspecializado(Enum):
    """Tipos de análisis especializados disponibles."""
    STRINGS = "strings"
    DINAMICO = "dinamico"
    REGISTROS = "registros"
    HEXADECIMAL = "hexadecimal"
    COMPORTAMIENTO = "comportamiento"
    FORENSE = "forense"
    METADATA = "metadata"
    FIRMAS = "firmas"


class NivelSeveridadAnalisis(Enum):
    """Niveles de severidad para los análisis."""
    CRITICO = "CRITICO"
    ALTO = "ALTO"
    MEDIO = "MEDIO"
    BAJO = "BAJO"
    INFO = "INFO"


class EstadoAnalisisEspecializado(Enum):
    """Estados del análisis especializado."""
    PENDIENTE = "pendiente"
    EN_PROGRESO = "en_progreso"
    COMPLETADO = "completado"
    ERROR = "error"
    CANCELADO = "cancelado"


@dataclass
class ResultadoAnalisisEspecializado:
    """Resultado de un análisis especializado."""
    tipo_analisis: TipoAnalisisEspecializado
    archivo_analizado: str
    timestamp_inicio: datetime
    timestamp_fin: Optional[datetime]
    estado: EstadoAnalisisEspecializado
    nivel_severidad: NivelSeveridadAnalisis
    hallazgos: List[Dict[str, Any]] = field(default_factory=list)
    detalles_tecnicos: Dict[str, Any] = field(default_factory=dict)
    recomendaciones: List[str] = field(default_factory=list)
    tiempo_analisis: float = 0.0
    errores: List[str] = field(default_factory=list)
    
    def agregar_hallazgo(self, descripcion: str, severidad: NivelSeveridadAnalisis, 
                        detalles: Optional[Dict[str, Any]] = None):
        """Agrega un hallazgo al resultado del análisis."""
        hallazgo = {
            'timestamp': datetime.now().isoformat(),
            'descripcion': descripcion,
            'severidad': severidad.value,
            'detalles': detalles or {}
        }
        self.hallazgos.append(hallazgo)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el resultado a diccionario."""
        return {
            'tipo_analisis': self.tipo_analisis.value,
            'archivo_analizado': self.archivo_analizado,
            'timestamp_inicio': self.timestamp_inicio.isoformat(),
            'timestamp_fin': self.timestamp_fin.isoformat() if self.timestamp_fin else None,
            'estado': self.estado.value,
            'nivel_severidad': self.nivel_severidad.value,
            'hallazgos': self.hallazgos,
            'detalles_tecnicos': self.detalles_tecnicos,
            'recomendaciones': self.recomendaciones,
            'tiempo_analisis': self.tiempo_analisis,
            'errores': self.errores
        }


class AnalizadorCadenas:
    """Analizador especializado de cadenas de texto."""
    
    def __init__(self):
        """Inicializa el analizador de cadenas."""
        self.logger = configurar_logger_modulo("analizador_cadenas")
        
        # Patrones de análisis especializados
        self.patrones_especializados = self._cargar_patrones_especializados()
        self.diccionarios_malware = self._cargar_diccionarios_malware()
        self.encodings_comunes = ['utf-8', 'latin-1', 'ascii', 'utf-16', 'cp1252']
        
        self.logger.info("Analizador de cadenas inicializado")
    
    def _cargar_patrones_especializados(self) -> Dict[str, List[str]]:
        """Carga patrones especializados para detección de amenazas."""
        return {
            'inyeccion_sql': [
                r'union\s+select', r'drop\s+table', r'insert\s+into',
                r'delete\s+from', r'update\s+set', r'alter\s+table',
                r'exec\s*\(', r'sp_executesql', r'xp_cmdshell'
            ],
            'inyeccion_codigo': [
                r'eval\s*\(', r'exec\s*\(', r'system\s*\(',
                r'shell_exec\s*\(', r'passthru\s*\(', r'popen\s*\(',
                r'os\.system', r'subprocess\.', r'__import__'
            ],
            'ofuscacion': [
                r'base64_decode', r'rot13', r'str_rot13', r'gzinflate',
                r'chr\(\d+\)', r'ord\(\w+\)', r'hex2bin', r'pack\(',
                r'\\x[0-9a-f]{2}', r'\\[0-7]{3}', r'%[0-9a-f]{2}'
            ],
            'persistencia': [
                r'HKEY_LOCAL_MACHINE', r'HKEY_CURRENT_USER', r'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run',
                r'autorun\.inf', r'startup', r'scheduled\s+task', r'crontab',
                r'systemd', r'init\.d', r'rc\.local', r'bashrc', r'bash_profile'
            ],
            'red_maliciosa': [
                r'nc\s+-[lep]', r'netcat', r'backdoor', r'reverse\s+shell',
                r'bind\s+shell', r'meterpreter', r'metasploit', r'empire',
                r'cobalt\s+strike', r'beacon', r'payload'
            ],
            'credenciales': [
                r'password\s*=', r'passwd\s*=', r'pwd\s*=', r'token\s*=',
                r'api_key\s*=', r'secret\s*=', r'private_key', r'credential',
                r'username\s*=', r'user\s*=', r'login\s*='
            ],
            'criptografia_sospechosa': [
                r'aes\s*(encrypt|decrypt)', r'rsa\s*(encrypt|decrypt)', r'des\s*(encrypt|decrypt)',
                r'md5\s*\(', r'sha1\s*\(', r'sha256\s*\(', r'bcrypt',
                r'openssl', r'crypto', r'cipher'
            ]
        }
    
    def _cargar_diccionarios_malware(self) -> Dict[str, List[str]]:
        """Carga diccionarios de términos relacionados con malware."""
        return {
            'ransomware': [
                'encrypt', 'decrypt', 'ransom', 'payment', 'bitcoin', 'cryptocurrency',
                'locked', 'encrypted', 'restore', 'files', 'deadline', 'tor'
            ],
            'keylogger': [
                'keylog', 'keystroke', 'keyboard', 'capture', 'monitor',
                'record', 'stealth', 'invisible', 'hidden'
            ],
            'trojan': [
                'backdoor', 'remote', 'control', 'access', 'stealth',
                'hidden', 'persistence', 'escalation'
            ],
            'botnet': [
                'command', 'control', 'c2', 'cnc', 'bot', 'zombie',
                'master', 'slave', 'infected', 'network'
            ]
        }
    
    def analizar_archivo(self, ruta_archivo: str) -> ResultadoAnalisisEspecializado:
        """
        Analiza las cadenas de texto en un archivo.
        
        Args:
            ruta_archivo: Ruta del archivo a analizar
            
        Returns:
            ResultadoAnalisisEspecializado: Resultado del análisis
        """
        resultado = ResultadoAnalisisEspecializado(
            tipo_analisis=TipoAnalisisEspecializado.STRINGS,
            archivo_analizado=ruta_archivo,
            timestamp_inicio=datetime.now(),
            timestamp_fin=None,
            estado=EstadoAnalisisEspecializado.EN_PROGRESO,
            nivel_severidad=NivelSeveridadAnalisis.INFO
        )
        
        inicio_tiempo = time.time()
        
        try:
            self.logger.info(f"Iniciando análisis de cadenas: {ruta_archivo}")
            
            # Extraer cadenas del archivo
            cadenas = self._extraer_cadenas(ruta_archivo)
            resultado.detalles_tecnicos['total_cadenas'] = len(cadenas)
            
            # Análisis de patrones sospechosos
            self._analizar_patrones_sospechosos(cadenas, resultado)
            
            # Análisis de URLs y dominios
            self._analizar_urls_dominios(cadenas, resultado)
            
            # Análisis de direcciones IP
            self._analizar_direcciones_ip(cadenas, resultado)
            
            # Análisis de rutas y archivos
            self._analizar_rutas_archivos(cadenas, resultado)
            
            # Análisis de funciones API sospechosas
            self._analizar_funciones_api(cadenas, resultado)
            
            # Análisis de ofuscación
            self._analizar_ofuscacion(cadenas, resultado)
            
            # Determinar nivel de severidad final
            self._determinar_severidad_final(resultado)
            
            # Generar recomendaciones
            self._generar_recomendaciones(resultado)
            
            resultado.estado = EstadoAnalisisEspecializado.COMPLETADO
            self.logger.info(f"Análisis de cadenas completado: {ruta_archivo}")
            
        except Exception as e:
            self.logger.error(f"Error en análisis de cadenas: {e}")
            resultado.errores.append(str(e))
            resultado.estado = EstadoAnalisisEspecializado.ERROR
        
        finally:
            resultado.timestamp_fin = datetime.now()
            resultado.tiempo_analisis = time.time() - inicio_tiempo
        
        return resultado
    
    def _extraer_cadenas(self, ruta_archivo: str) -> List[str]:
        """Extrae cadenas de texto del archivo."""
        cadenas = []
        
        try:
            # Intentar diferentes encodings
            for encoding in self.encodings_comunes:
                try:
                    with open(ruta_archivo, 'r', encoding=encoding, errors='ignore') as archivo:
                        contenido = archivo.read()
                        
                        # Extraer cadenas imprimibles de al menos 4 caracteres
                        cadenas_encontradas = re.findall(r'[\x20-\x7E]{4,}', contenido)
                        cadenas.extend(cadenas_encontradas)
                        
                        if cadenas:  # Si encontramos cadenas, usar este encoding
                            break
                            
                except Exception:
                    continue
            
            # Si no se pudieron extraer como texto, usar método binario
            if not cadenas:
                with open(ruta_archivo, 'rb') as archivo:
                    contenido = archivo.read()
                    cadenas = re.findall(rb'[\x20-\x7E]{4,}', contenido)
                    cadenas = [cadena.decode('ascii', errors='ignore') for cadena in cadenas]
        
        except Exception as e:
            self.logger.warning(f"Error extrayendo cadenas: {e}")
        
        return list(set(cadenas))  # Eliminar duplicados
    
    def _analizar_patrones_sospechosos(self, cadenas: List[str], resultado: ResultadoAnalisisEspecializado):
        """Analiza patrones sospechosos en las cadenas."""
        patrones_encontrados = defaultdict(list)
        
        for cadena in cadenas:
            cadena_lower = cadena.lower()
            
            for categoria, patrones in self.patrones_especializados.items():
                for patron in patrones:
                    if re.search(patron, cadena_lower, re.IGNORECASE):
                        patrones_encontrados[categoria].append({
                            'patron': patron,
                            'cadena': cadena[:100],  # Limitar longitud
                            'posicion': cadena_lower.find(patron.lower())
                        })
        
        # Agregar hallazgos
        for categoria, coincidencias in patrones_encontrados.items():
            if coincidencias:
                severidad = self._determinar_severidad_patron(categoria)
                resultado.agregar_hallazgo(
                    f"Patrones {categoria} detectados",
                    severidad,
                    {'categoria': categoria, 'coincidencias': coincidencias[:10]}  # Limitar a 10
                )
        
        resultado.detalles_tecnicos['patrones_sospechosos'] = dict(patrones_encontrados)
    
    def _analizar_urls_dominios(self, cadenas: List[str], resultado: ResultadoAnalisisEspecializado):
        """Analiza URLs y dominios en las cadenas."""
        urls_encontradas = []
        dominios_sospechosos = []
        
        patron_url = re.compile(r'https?://[^\s<>"\']+', re.IGNORECASE)
        patron_dominio = re.compile(r'[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*', re.IGNORECASE)
        
        for cadena in cadenas:
            # Buscar URLs
            urls = patron_url.findall(cadena)
            urls_encontradas.extend(urls)
            
            # Buscar dominios
            dominios = patron_dominio.findall(cadena)
            for dominio in dominios:
                if self._es_dominio_sospechoso(dominio):
                    dominios_sospechosos.append(dominio)
        
        if urls_encontradas:
            resultado.agregar_hallazgo(
                f"URLs encontradas: {len(urls_encontradas)}",
                NivelSeveridadAnalisis.MEDIO,
                {'urls': urls_encontradas[:20]}
            )
        
        if dominios_sospechosos:
            resultado.agregar_hallazgo(
                f"Dominios sospechosos: {len(dominios_sospechosos)}",
                NivelSeveridadAnalisis.ALTO,
                {'dominios': dominios_sospechosos}
            )
        
        resultado.detalles_tecnicos['urls_encontradas'] = len(urls_encontradas)
        resultado.detalles_tecnicos['dominios_sospechosos'] = len(dominios_sospechosos)
    
    def _analizar_direcciones_ip(self, cadenas: List[str], resultado: ResultadoAnalisisEspecializado):
        """Analiza direcciones IP en las cadenas."""
        patron_ip = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')
        ips_encontradas = []
        ips_privadas = []
        ips_publicas = []
        
        for cadena in cadenas:
            ips = patron_ip.findall(cadena)
            for ip in ips:
                if self._es_ip_valida(ip):
                    ips_encontradas.append(ip)
                    if self._es_ip_privada(ip):
                        ips_privadas.append(ip)
                    else:
                        ips_publicas.append(ip)
        
        if ips_encontradas:
            severidad = NivelSeveridadAnalisis.ALTO if ips_publicas else NivelSeveridadAnalisis.MEDIO
            resultado.agregar_hallazgo(
                f"Direcciones IP encontradas: {len(ips_encontradas)}",
                severidad,
                {
                    'total': len(ips_encontradas),
                    'publicas': len(ips_publicas),
                    'privadas': len(ips_privadas),
                    'ips': ips_encontradas[:15]
                }
            )
        
        resultado.detalles_tecnicos['ips_encontradas'] = len(ips_encontradas)
    
    def _analizar_rutas_archivos(self, cadenas: List[str], resultado: ResultadoAnalisisEspecializado):
        """Analiza rutas de archivos y directorios sospechosos."""
        rutas_sospechosas = []
        
        patrones_rutas = [
            r'[A-Z]:\\[^\\]+\\[^\\]+',  # Rutas Windows
            r'/[a-zA-Z0-9_\-/]+',       # Rutas Unix/Linux
            r'\\\\[^\\]+\\[^\\]+',      # UNC paths
        ]
        
        directorios_sospechosos = [
            'temp', 'tmp', 'appdata', 'programdata', 'windows\\system32',
            '/tmp', '/var/tmp', '/dev/shm', 'startup', 'autostart'
        ]
        
        for cadena in cadenas:
            for patron in patrones_rutas:
                rutas = re.findall(patron, cadena, re.IGNORECASE)
                for ruta in rutas:
                    if any(directorio in ruta.lower() for directorio in directorios_sospechosos):
                        rutas_sospechosas.append(ruta)
        
        if rutas_sospechosas:
            resultado.agregar_hallazgo(
                f"Rutas sospechosas encontradas: {len(rutas_sospechosas)}",
                NivelSeveridadAnalisis.MEDIO,
                {'rutas': rutas_sospechosas[:10]}
            )
        
        resultado.detalles_tecnicos['rutas_sospechosas'] = len(rutas_sospechosas)
    
    def _analizar_funciones_api(self, cadenas: List[str], resultado: ResultadoAnalisisEspecializado):
        """Analiza funciones API sospechosas."""
        funciones_sospechosas = [
            'VirtualAlloc', 'VirtualProtect', 'CreateRemoteThread', 'WriteProcessMemory',
            'OpenProcess', 'CreateProcess', 'ShellExecute', 'WinExec', 'RegCreateKey',
            'RegSetValue', 'SetWindowsHook', 'GetProcAddress', 'LoadLibrary'
        ]
        
        funciones_encontradas = []
        
        for cadena in cadenas:
            for funcion in funciones_sospechosas:
                if funcion.lower() in cadena.lower():
                    funciones_encontradas.append(funcion)
        
        if funciones_encontradas:
            resultado.agregar_hallazgo(
                f"Funciones API sospechosas: {len(set(funciones_encontradas))}",
                NivelSeveridadAnalisis.ALTO,
                {'funciones': list(set(funciones_encontradas))}
            )
        
        resultado.detalles_tecnicos['funciones_api_sospechosas'] = len(set(funciones_encontradas))
    
    def _analizar_ofuscacion(self, cadenas: List[str], resultado: ResultadoAnalisisEspecializado):
        """Analiza técnicas de ofuscación."""
        indicadores_ofuscacion = 0
        tecnicas_detectadas = []
        
        for cadena in cadenas:
            # Base64 largo
            if re.search(r'[A-Za-z0-9+/]{20,}={0,2}', cadena):
                indicadores_ofuscacion += 1
                tecnicas_detectadas.append('Base64')
            
            # Hex largo
            if re.search(r'[0-9a-fA-F]{20,}', cadena):
                indicadores_ofuscacion += 1
                tecnicas_detectadas.append('Hexadecimal')
            
            # Caracteres de escape
            if re.search(r'\\x[0-9a-fA-F]{2}', cadena):
                indicadores_ofuscacion += 1
                tecnicas_detectadas.append('Escape hexadecimal')
            
            # Unicode
            if re.search(r'\\u[0-9a-fA-F]{4}', cadena):
                indicadores_ofuscacion += 1
                tecnicas_detectadas.append('Unicode')
        
        if indicadores_ofuscacion > 5:
            resultado.agregar_hallazgo(
                f"Posible ofuscación detectada: {indicadores_ofuscacion} indicadores",
                NivelSeveridadAnalisis.ALTO,
                {'indicadores': indicadores_ofuscacion, 'tecnicas': list(set(tecnicas_detectadas))}
            )
        
        resultado.detalles_tecnicos['indicadores_ofuscacion'] = indicadores_ofuscacion
    
    def _es_dominio_sospechoso(self, dominio: str) -> bool:
        """Determina si un dominio es sospechoso."""
        dominios_sospechosos = [
            'bit.ly', 'tinyurl.com', 'short.link', 'ngrok.io',
            'duckdns.org', 'no-ip.com', 'ddns.net'
        ]
        
        # Dominios muy cortos o con muchos números
        if len(dominio) < 4 or dominio.count('.') > 3:
            return True
        
        # Dominios conocidos sospechosos
        if any(sospechoso in dominio.lower() for sospechoso in dominios_sospechosos):
            return True
        
        # Muchos números en el dominio
        if sum(c.isdigit() for c in dominio) > len(dominio) * 0.5:
            return True
        
        return False
    
    def _es_ip_valida(self, ip: str) -> bool:
        """Valida si una dirección IP es válida."""
        try:
            octetos = ip.split('.')
            if len(octetos) != 4:
                return False
            
            for octeto in octetos:
                if not 0 <= int(octeto) <= 255:
                    return False
            
            return True
        except ValueError:
            return False
    
    def _es_ip_privada(self, ip: str) -> bool:
        """Determina si una IP es privada."""
        try:
            octetos = [int(x) for x in ip.split('.')]
            
            # Rangos privados: 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16
            if octetos[0] == 10:
                return True
            elif octetos[0] == 172 and 16 <= octetos[1] <= 31:
                return True
            elif octetos[0] == 192 and octetos[1] == 168:
                return True
            elif octetos[0] == 127:  # Loopback
                return True
            
            return False
        except:
            return False
    
    def _determinar_severidad_patron(self, categoria: str) -> NivelSeveridadAnalisis:
        """Determina la severidad basada en la categoría del patrón."""
        severidades = {
            'inyeccion_sql': NivelSeveridadAnalisis.ALTO,
            'inyeccion_codigo': NivelSeveridadAnalisis.CRITICO,
            'ofuscacion': NivelSeveridadAnalisis.ALTO,
            'persistencia': NivelSeveridadAnalisis.ALTO,
            'red_maliciosa': NivelSeveridadAnalisis.CRITICO,
            'credenciales': NivelSeveridadAnalisis.MEDIO,
            'criptografia_sospechosa': NivelSeveridadAnalisis.MEDIO
        }
        
        return severidades.get(categoria, NivelSeveridadAnalisis.BAJO)
    
    def _determinar_severidad_final(self, resultado: ResultadoAnalisisEspecializado):
        """Determina la severidad final del análisis."""
        if any(h['severidad'] == 'CRITICO' for h in resultado.hallazgos):
            resultado.nivel_severidad = NivelSeveridadAnalisis.CRITICO
        elif any(h['severidad'] == 'ALTO' for h in resultado.hallazgos):
            resultado.nivel_severidad = NivelSeveridadAnalisis.ALTO
        elif any(h['severidad'] == 'MEDIO' for h in resultado.hallazgos):
            resultado.nivel_severidad = NivelSeveridadAnalisis.MEDIO
        elif resultado.hallazgos:
            resultado.nivel_severidad = NivelSeveridadAnalisis.BAJO
        else:
            resultado.nivel_severidad = NivelSeveridadAnalisis.INFO
    
    def _generar_recomendaciones(self, resultado: ResultadoAnalisisEspecializado):
        """Genera recomendaciones basadas en los hallazgos."""
        if resultado.nivel_severidad in [NivelSeveridadAnalisis.CRITICO, NivelSeveridadAnalisis.ALTO]:
            resultado.recomendaciones.extend([
                "🚨 Archivo altamente sospechoso - Aislar inmediatamente",
                "🔍 Realizar análisis forense completo",
                "🛡️ Verificar integridad del sistema",
                "📊 Monitorear actividad de red"
            ])
        elif resultado.nivel_severidad == NivelSeveridadAnalisis.MEDIO:
            resultado.recomendaciones.extend([
                "⚠️ Archivo sospechoso - Análisis adicional requerido",
                "🔬 Ejecutar en entorno aislado",
                "📋 Revisar manualmente los hallazgos"
            ])
        else:
            resultado.recomendaciones.append("ℹ️ Análisis de cadenas completado sin hallazgos críticos")


class GestorAnalizadoresEspecializados:
    """Gestor principal de todos los analizadores especializados."""
    
    def __init__(self, siem: SIEM):
        """
        Inicializa el gestor de analizadores especializados.
        
        Args:
            siem: Instancia del SIEM para registro de eventos
        """
        self.siem = siem
        self.logger = configurar_logger_modulo("gestor_analizadores_especializados")
        
        # Inicializar analizadores
        self.analizador_cadenas = AnalizadorCadenas()
        
        # Configuración
        self.analisis_simultaneos_maximos = 3
        self.timeout_analisis = 300  # 5 minutos
        
        # Estado del sistema
        self.analisis_activos = {}
        self.resultados_cache = {}
        self.estadisticas = {
            'total_analisis': 0,
            'analisis_completados': 0,
            'analisis_con_errores': 0,
            'tiempo_total_analisis': 0.0
        }
        
        self.logger.info("Gestor de analizadores especializados inicializado")
        self.siem.registrar_evento(
            TipoEvento.SISTEMA_INICIADO,
            "Sistema de analizadores especializados inicializado",
            {
                'analizadores_disponibles': ['cadenas'],
                'analisis_simultaneos_maximos': self.analisis_simultaneos_maximos
            },
            "MEDIO"
        )
    
    def ejecutar_analisis_completo(self, ruta_archivo: str, tipos_analisis: Optional[List[TipoAnalisisEspecializado]] = None) -> Dict[str, ResultadoAnalisisEspecializado]:
        """
        Ejecuta un análisis completo con múltiples analizadores.
        
        Args:
            ruta_archivo: Ruta del archivo a analizar
            tipos_analisis: Lista de tipos de análisis a ejecutar
            
        Returns:
            Dict[str, ResultadoAnalisisEspecializado]: Resultados de todos los análisis
        """
        if tipos_analisis is None:
            tipos_analisis = [TipoAnalisisEspecializado.STRINGS]
        
        self.logger.info(f"Iniciando análisis completo: {ruta_archivo}")
        
        resultados = {}
        
        try:
            # Validaciones
            if not os.path.exists(ruta_archivo):
                raise FileNotFoundError(f"Archivo no encontrado: {ruta_archivo}")
            
            if not validar_permisos_lectura(ruta_archivo):
                raise PermissionError(f"Sin permisos de lectura: {ruta_archivo}")
            
            # Ejecutar análisis según los tipos solicitados
            for tipo_analisis in tipos_analisis:
                if tipo_analisis == TipoAnalisisEspecializado.STRINGS:
                    resultados['strings'] = self.analizador_cadenas.analizar_archivo(ruta_archivo)
                # Aquí se agregarían otros analizadores cuando estén implementados
            
            # Registrar en SIEM
            self.siem.registrar_evento(
                TipoEvento.ANALISIS_COMPLETADO,
                f"Análisis especializado completado: {os.path.basename(ruta_archivo)}",
                {
                    'archivo': ruta_archivo,
                    'tipos_analisis': [t.value for t in tipos_analisis],
                    'resultados_count': len(resultados)
                },
                "MEDIO"
            )
            
            # Actualizar estadísticas
            self.estadisticas['total_analisis'] += 1
            self.estadisticas['analisis_completados'] += 1
            
            self.logger.info(f"Análisis completo finalizado: {ruta_archivo}")
            
        except Exception as e:
            self.logger.error(f"Error en análisis completo: {e}")
            self.estadisticas['analisis_con_errores'] += 1
            raise
        
        return resultados
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas del sistema de análisis."""
        return {
            'estadisticas_generales': self.estadisticas.copy(),
            'analisis_activos': len(self.analisis_activos),
            'cache_resultados': len(self.resultados_cache),
            'analizadores_disponibles': {
                'cadenas': True,
                'dinamico': False,  # No implementado aún
                'registros': False,  # No implementado aún
                'hexadecimal': False  # No implementado aún
            },
            'configuracion': {
                'analisis_simultaneos_maximos': self.analisis_simultaneos_maximos,
                'timeout_analisis': self.timeout_analisis
            }
        }


# Alias para compatibilidad
AnalizadoresEspecializados = GestorAnalizadoresEspecializados
