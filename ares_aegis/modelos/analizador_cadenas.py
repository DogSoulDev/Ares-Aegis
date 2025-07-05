#!/usr/bin/env python3
"""
Copyright (c) 2025 DogSoulDev (https://github.com/DogSoulDev)
Todos los derechos reservados. Este código es propietario y confidencial.

Analizador de Cadenas
"""

import re
import os
from typing import Dict, List, Optional, Any, Set
from ..utilidades.ayuda_logging import configurar_logger_modulo
from ..utilidades.validaciones import validar_ruta_archivo


class ExtractorCadenas:
    
    def __init__(self):
        """Inicializa el descifrador de runas ancestrales."""
        self.logger = configurar_logger_modulo("extractor_cadenas")
        
        # Patrones de runas sospechosas conocidas
        self.patrones_sospechosos = {
            'urls': r'https?://[^\s<>"]+',
            'ips': r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
            'emails': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'rutas_archivos': r'[A-Za-z]:\\[^<>:"|?*\n\r]+|/[^\s<>:"|?*\n\r]+',
            'comandos_shell': r'(?:cmd|bash|sh|powershell|system|exec)\s*\(',
            'registry_keys': r'HKEY_[A-Z_]+\\[^\n\r]+',
            'base64': r'[A-Za-z0-9+/]{20,}={0,2}',
            'hex_strings': r'\\x[0-9a-fA-F]{2}',
            'crypto_keys': r'-----BEGIN [A-Z ]+-----[\s\S]*?-----END [A-Z ]+-----'
        }
        
        self.logger.info("El descifrador de runas ha despertado en el templo de la sabiduría")
    
    def extraer_cadenas_ascii(self, ruta_archivo: str, longitud_minima: int = 4) -> List[str]:
        """
        Extrae todas las cadenas ASCII legibles del pergamino.
        
        Args:
            ruta_archivo: Sendero al pergamino a examinar
            longitud_minima: Longitud mínima de cadenas a extraer
            
        Returns:
            Lista de cadenas ASCII encontradas
        """
        if not validar_ruta_archivo(ruta_archivo):
            self.logger.error(f"El sendero no conduce a pergamino válido: {ruta_archivo}")
            return []
        
        cadenas_encontradas = []
        
        try:
            with open(ruta_archivo, 'rb') as archivo:
                contenido = archivo.read()
            
            # Patrón para encontrar secuencias de caracteres ASCII imprimibles
            patron_ascii = re.compile(rb'[\x20-\x7E]{' + str(longitud_minima).encode() + rb',}')
            
            coincidencias = patron_ascii.findall(contenido)
            
            for coincidencia in coincidencias:
                try:
                    cadena = coincidencia.decode('ascii')
                    cadenas_encontradas.append(cadena)
                except UnicodeDecodeError:
                    continue
            
            self.logger.info(f"Extraídas {len(cadenas_encontradas)} cadenas ASCII del pergamino")
            return cadenas_encontradas
        
        except Exception as e:
            self.logger.error(f"Error extrayendo cadenas ASCII: {e}")
            return []
    
    def extraer_cadenas_unicode(self, ruta_archivo: str, longitud_minima: int = 4) -> List[str]:
        """
        Extrae cadenas Unicode (UTF-8/UTF-16) del pergamino.
        
        Args:
            ruta_archivo: Sendero al pergamino a examinar
            longitud_minima: Longitud mínima de cadenas a extraer
            
        Returns:
            Lista de cadenas Unicode encontradas
        """
        if not validar_ruta_archivo(ruta_archivo):
            return []
        
        cadenas_unicode = []
        
        try:
            with open(ruta_archivo, 'rb') as archivo:
                contenido = archivo.read()
            
            # Intentar decodificar como UTF-8
            try:
                texto_utf8 = contenido.decode('utf-8', errors='ignore')
                cadenas_utf8 = re.findall(r'[\x20-\x7E\u00A0-\uFFFF]{' + str(longitud_minima) + ',}', texto_utf8)
                cadenas_unicode.extend(cadenas_utf8)
            except:
                pass
            
            # Intentar decodificar como UTF-16
            try:
                texto_utf16 = contenido.decode('utf-16', errors='ignore')
                cadenas_utf16 = re.findall(r'[\x20-\x7E\u00A0-\uFFFF]{' + str(longitud_minima) + ',}', texto_utf16)
                cadenas_unicode.extend(cadenas_utf16)
            except:
                pass
            
            # Eliminar duplicados manteniendo el orden
            cadenas_unicas = []
            vistas = set()
            
            for cadena in cadenas_unicode:
                if cadena not in vistas:
                    cadenas_unicas.append(cadena)
                    vistas.add(cadena)
            
            self.logger.info(f"Extraídas {len(cadenas_unicas)} cadenas Unicode del pergamino")
            return cadenas_unicas
        
        except Exception as e:
            self.logger.error(f"Error extrayendo cadenas Unicode: {e}")
            return []
    
    def buscar_patrones_sospechosos(self, cadenas: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Busca patrones sospechosos en las cadenas extraídas.
        
        Args:
            cadenas: Lista de cadenas a analizar
            
        Returns:
            Dict con patrones encontrados organizados por tipo
        """
        patrones_encontrados = {}
        
        for tipo_patron, patron in self.patrones_sospechosos.items():
            coincidencias = []
            
            for cadena in cadenas:
                matches = re.finditer(patron, cadena, re.IGNORECASE)
                
                for match in matches:
                    coincidencias.append({
                        'cadena_completa': cadena,
                        'coincidencia': match.group(),
                        'posicion_inicio': match.start(),
                        'posicion_fin': match.end()
                    })
            
            if coincidencias:
                patrones_encontrados[tipo_patron] = coincidencias
        
        return patrones_encontrados
    
    def analizar_entropia(self, cadenas: List[str]) -> Dict[str, Any]:
        """
        Analiza la entropía de las cadenas para detectar posible contenido codificado.
        
        Args:
            cadenas: Lista de cadenas a analizar
            
        Returns:
            Dict con análisis de entropía
        """
        import math
        from collections import Counter
        
        if not cadenas:
            return {
                'cadena_alta_entropia': [],
                'entropia_promedio': 0.0,
                'cadenas_analizadas': 0
            }
        
        cadenas_alta_entropia = []
        entropias = []
        
        for cadena in cadenas:
            if len(cadena) < 10:  # Ignorar cadenas muy cortas
                continue
            
            # Calcular entropía
            contador = Counter(cadena)
            longitud = len(cadena)
            entropia = -sum(
                (count / longitud) * math.log2(count / longitud)
                for count in contador.values()
            )
            
            entropias.append(entropia)
            
            # Considerar alta entropía si es mayor a 4.5
            if entropia > 4.5:
                cadenas_alta_entropia.append({
                    'cadena': cadena[:100] + "..." if len(cadena) > 100 else cadena,
                    'entropia': round(entropia, 3),
                    'longitud': len(cadena),
                    'razon_sospecha': 'Posible contenido codificado o encriptado'
                })
        
        entropia_promedio = sum(entropias) / len(entropias) if entropias else 0.0
        
        return {
            'cadenas_alta_entropia': cadenas_alta_entropia,
            'entropia_promedio': round(entropia_promedio, 3),
            'cadenas_analizadas': len(entropias),
            'umbral_sospecha': 4.5
        }


class AnalizadorCadenas:
    """El Gran Intérprete de Runas - Combina todos los análisis de cadenas."""
    
    def __init__(self, siem=None):
        """Inicializa el gran intérprete de runas ancestrales."""
        self.logger = configurar_logger_modulo("analizador_cadenas")
        self.siem = siem
        self.extractor = ExtractorCadenas()
        
        # Palabras clave que sugieren malware o comportamiento sospechoso
        self.palabras_clave_malware = {
            'red': ['socket', 'connect', 'bind', 'listen', 'download', 'upload', 'ftp', 'http'],
            'sistema': ['system', 'exec', 'shell', 'cmd', 'powershell', 'bash', 'registry'],
            'archivos': ['delete', 'remove', 'unlink', 'rmdir', 'copy', 'move', 'temp'],
            'proceso': ['process', 'thread', 'mutex', 'kill', 'terminate', 'suspend'],
            'crypto': ['encrypt', 'decrypt', 'cipher', 'key', 'hash', 'crypto'],
            'persistencia': ['startup', 'autorun', 'schedule', 'service', 'daemon'],
            'evasion': ['debug', 'antivirus', 'av', 'sandbox', 'virtual', 'vm']
        }
        
        self.logger.info("El gran intérprete de runas ha abierto su biblioteca sagrada")
    
    def analisis_completo_cadenas(self, ruta_archivo: str) -> Dict[str, Any]:
        """
        Realiza un análisis completo de cadenas del pergamino.
        
        Args:
            ruta_archivo: Sendero al pergamino a examinar
            
        Returns:
            Dict con todos los análisis de cadenas
        """
        self.logger.info(f"Iniciando análisis completo de runas en: {ruta_archivo}")
        
        resultado: Dict[str, Any] = {
            'archivo': ruta_archivo,
            'estado': 'iniciado',
            'timestamp': self._obtener_timestamp()
        }
        
        try:
            # Extraer cadenas ASCII
            cadenas_ascii = self.extractor.extraer_cadenas_ascii(ruta_archivo)
            resultado['cadenas_ascii'] = {
                'total': len(cadenas_ascii),
                'cadenas': cadenas_ascii[:100]  # Limitar para no saturar
            }
            
            # Extraer cadenas Unicode
            cadenas_unicode = self.extractor.extraer_cadenas_unicode(ruta_archivo)
            resultado['cadenas_unicode'] = {
                'total': len(cadenas_unicode),
                'cadenas': cadenas_unicode[:50]  # Limitar para no saturar
            }
            
            # Combinar todas las cadenas para análisis
            todas_cadenas = list(set(cadenas_ascii + cadenas_unicode))
            
            # Buscar patrones sospechosos
            patrones = self.extractor.buscar_patrones_sospechosos(todas_cadenas)
            resultado['patrones_sospechosos'] = patrones
            
            # Análisis de entropía
            entropia = self.extractor.analizar_entropia(todas_cadenas)
            resultado['analisis_entropia'] = entropia
            
            # Buscar palabras clave de malware
            palabras_malware = self._buscar_palabras_clave_malware(todas_cadenas)
            resultado['palabras_clave_malware'] = palabras_malware
            
            # Generar evaluación de riesgo
            evaluacion = self._evaluar_riesgo_cadenas(patrones, entropia, palabras_malware)
            resultado['evaluacion_riesgo'] = evaluacion
            
            resultado['estado'] = 'completado'
            resultado['mensaje'] = 'Las runas del pergamino han sido completamente descifradas'
            
        except Exception as e:
            resultado['estado'] = 'error'
            resultado['mensaje'] = f'Una tormenta ha interrumpido el descifrado de runas: {e}'
            self.logger.error(f"Error en análisis de cadenas: {e}")
        
        return resultado
    
    def _buscar_palabras_clave_malware(self, cadenas: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """Busca palabras clave asociadas con malware en las cadenas."""
        palabras_encontradas = {}
        
        for categoria, palabras in self.palabras_clave_malware.items():
            coincidencias = []
            
            for cadena in cadenas:
                cadena_lower = cadena.lower()
                
                for palabra in palabras:
                    if palabra in cadena_lower:
                        coincidencias.append({
                            'palabra_clave': palabra,
                            'cadena_completa': cadena,
                            'categoria': categoria,
                            'contexto': self._extraer_contexto(cadena, palabra)
                        })
            
            if coincidencias:
                palabras_encontradas[categoria] = coincidencias
        
        return palabras_encontradas
    
    def _extraer_contexto(self, cadena: str, palabra: str, ventana: int = 20) -> str:
        """Extrae el contexto alrededor de una palabra clave."""
        pos = cadena.lower().find(palabra.lower())
        if pos == -1:
            return cadena[:50] + "..." if len(cadena) > 50 else cadena
        
        inicio = max(0, pos - ventana)
        fin = min(len(cadena), pos + len(palabra) + ventana)
        
        contexto = cadena[inicio:fin]
        if inicio > 0:
            contexto = "..." + contexto
        if fin < len(cadena):
            contexto = contexto + "..."
        
        return contexto
    
    def _evaluar_riesgo_cadenas(self, patrones: Dict, entropia: Dict, palabras_malware: Dict) -> Dict[str, Any]:
        """Evalúa el riesgo basado en el análisis de cadenas."""
        puntuacion_riesgo = 0
        factores_riesgo = []
        
        # Evaluar patrones sospechosos
        for tipo_patron, coincidencias in patrones.items():
            num_coincidencias = len(coincidencias)
            if num_coincidencias > 0:
                puntos = {
                    'urls': 2,
                    'ips': 3,
                    'comandos_shell': 5,
                    'registry_keys': 4,
                    'base64': 3,
                    'crypto_keys': 4
                }.get(tipo_patron, 1)
                
                puntuacion_riesgo += min(puntos * num_coincidencias, 10)
                factores_riesgo.append(f"{num_coincidencias} patrones {tipo_patron} detectados")
        
        # Evaluar entropía alta
        cadenas_alta_entropia = entropia.get('cadenas_alta_entropia', [])
        if cadenas_alta_entropia:
            puntuacion_riesgo += min(len(cadenas_alta_entropia) * 2, 8)
            factores_riesgo.append(f"{len(cadenas_alta_entropia)} cadenas con alta entropía (posible codificación)")
        
        # Evaluar palabras clave de malware
        for categoria, coincidencias in palabras_malware.items():
            if coincidencias:
                puntos = {
                    'red': 3,
                    'sistema': 4,
                    'proceso': 3,
                    'crypto': 2,
                    'persistencia': 5,
                    'evasion': 4
                }.get(categoria, 2)
                
                puntuacion_riesgo += min(puntos, 6)
                factores_riesgo.append(f"Palabras clave de {categoria}: {len(coincidencias)} encontradas")
        
        # Determinar nivel de riesgo
        if puntuacion_riesgo >= 15:
            nivel = "CRITICO"
            mensaje = "¡Las runas revelan intenciones malévolas! ¡El Égida debe actuar!"
        elif puntuacion_riesgo >= 10:
            nivel = "ALTO"
            mensaje = "Las runas portan signos inquietantes que alertan a los centinelas divinos"
        elif puntuacion_riesgo >= 5:
            nivel = "MEDIO"
            mensaje = "Algunas runas despiertan la vigilancia del ojo de Ares"
        else:
            nivel = "BAJO"
            mensaje = "Las runas parecen inofensivas bajo el juicio divino"
        
        return {
            'nivel': nivel,
            'puntuacion': puntuacion_riesgo,
            'factores_riesgo': factores_riesgo,
            'mensaje': mensaje,
            'recomendacion': self._generar_recomendacion_cadenas(nivel)
        }
    
    def _generar_recomendacion_cadenas(self, nivel: str) -> str:
        """Genera recomendación basada en el análisis de cadenas."""
        recomendaciones = {
            "BAJO": "Las runas no revelan amenazas - el pergamino puede ser usado con confianza",
            "MEDIO": "Examina las runas con cautela - algunos patrones requieren atención",
            "ALTO": "Las runas sugieren comportamiento sospechoso - mantén el Égida preparado",
            "CRITICO": "¡Las runas revelan intenciones malévolas! Destierro inmediato recomendado"
        }
        
        return recomendaciones.get(nivel, "La sabiduría de los antiguos es incierta")
    
    def _obtener_timestamp(self) -> str:
        """Obtiene timestamp actual en formato ISO."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def generar_reporte_cadenas_markdown(self, analisis: Dict[str, Any]) -> str:
        """
        Genera un reporte detallado del análisis de cadenas en formato Markdown.
        
        Args:
            analisis: Resultado del análisis de cadenas
            
        Returns:
            Reporte en formato Markdown
        """
        md = f"# 📜 Reporte del Descifrado de Runas\n\n"
        md += f"**Pergamino Analizado:** `{analisis['archivo']}`\n"
        md += f"**Fecha del Descifrado:** {analisis['timestamp']}\n"
        md += f"**Estado:** {analisis['estado']}\n\n"
        
        if analisis['estado'] != 'completado':
            md += f"**Mensaje:** {analisis.get('mensaje', 'Descifrado incompleto')}\n"
            return md
        
        # Resumen de cadenas extraídas
        cadenas_ascii = analisis.get('cadenas_ascii', {})
        cadenas_unicode = analisis.get('cadenas_unicode', {})
        
        md += "## 📊 Runas Extraídas\n\n"
        md += f"- **Cadenas ASCII:** {cadenas_ascii.get('total', 0)}\n"
        md += f"- **Cadenas Unicode:** {cadenas_unicode.get('total', 0)}\n\n"
        
        # Patrones sospechosos
        patrones = analisis.get('patrones_sospechosos', {})
        if patrones:
            md += "## ⚠️ Patrones Sospechosos Detectados\n\n"
            for tipo, coincidencias in patrones.items():
                md += f"### {tipo.replace('_', ' ').title()}\n\n"
                for i, coincidencia in enumerate(coincidencias[:5]):  # Limitar a 5
                    md += f"- **Coincidencia {i+1}:** `{coincidencia['coincidencia']}`\n"
                if len(coincidencias) > 5:
                    md += f"- *... y {len(coincidencias) - 5} más*\n"
                md += "\n"
        
        # Análisis de entropía
        entropia = analisis.get('analisis_entropia', {})
        if entropia:
            md += "## 🔢 Análisis de Entropía\n\n"
            md += f"- **Entropía Promedio:** {entropia.get('entropia_promedio', 0)}\n"
            md += f"- **Cadenas Analizadas:** {entropia.get('cadenas_analizadas', 0)}\n"
            
            cadenas_alta = entropia.get('cadenas_alta_entropia', [])
            if cadenas_alta:
                md += f"- **Cadenas de Alta Entropía:** {len(cadenas_alta)}\n\n"
                md += "**Cadenas Sospechosas por Alta Entropía:**\n"
                for cadena_info in cadenas_alta[:3]:  # Mostrar solo las primeras 3
                    md += f"- Entropía: {cadena_info['entropia']} - `{cadena_info['cadena']}`\n"
                md += "\n"
        
        # Palabras clave de malware
        palabras_malware = analisis.get('palabras_clave_malware', {})
        if palabras_malware:
            md += "## 🚨 Palabras Clave de Malware\n\n"
            for categoria, coincidencias in palabras_malware.items():
                md += f"### {categoria.replace('_', ' ').title()}\n\n"
                palabras_unicas = set(c['palabra_clave'] for c in coincidencias)
                md += f"- **Palabras encontradas:** {', '.join(palabras_unicas)}\n"
                md += f"- **Total de coincidencias:** {len(coincidencias)}\n\n"
        
        # Evaluación de riesgo
        evaluacion = analisis.get('evaluacion_riesgo', {})
        if evaluacion:
            md += "## ⚔️ Juicio del Égida sobre las Runas\n\n"
            md += f"**Nivel de Riesgo:** {evaluacion.get('nivel', 'DESCONOCIDO')}\n"
            md += f"**Puntuación:** {evaluacion.get('puntuacion', 0)}\n"
            md += f"**Mensaje:** {evaluacion.get('mensaje', 'Sin juicio')}\n"
            md += f"**Recomendación:** {evaluacion.get('recomendacion', 'Sin recomendación')}\n\n"
            
            factores = evaluacion.get('factores_riesgo', [])
            if factores:
                md += "**Factores de Riesgo:**\n"
                for factor in factores:
                    md += f"- {factor}\n"
                md += "\n"
        
        md += "---\n\n"
        md += "*Descifrado completado por el Gran Intérprete de Runas del Égida*\n"
        
        return md
