#!/usr/bin/env python3
"""
Analizador de Cadenas
Módulo para extracción y análisis de strings en archivos binarios y ejecutables.

Autor: DogSoulDev
Versión: 2.0.0
"""

import re
import os
import codecs
from typing import Dict, List, Set, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
import binascii


class CadenaEncontrada:
    """Representa una cadena encontrada en un archivo."""
    
    def __init__(self, contenido: str, offset: int, encoding: str, longitud: int):
        """
        Inicializa una cadena encontrada.
        
        Args:
            contenido: El texto de la cadena
            offset: Posición en el archivo donde se encontró
            encoding: Codificación detectada
            longitud: Longitud de la cadena
        """
        self.contenido = contenido
        self.offset = offset
        self.encoding = encoding
        self.longitud = longitud
        self.tipo_cadena = self._clasificar_cadena()
        self.es_sospechosa = self._evaluar_sospecha()
    
    def _clasificar_cadena(self) -> str:
        """Clasifica el tipo de cadena encontrada."""
        contenido_lower = self.contenido.lower()
        
        # URLs y dominios
        if re.match(r'https?://', contenido_lower) or re.match(r'ftp://', contenido_lower):
            return 'URL'
        
        # Direcciones de email
        if re.match(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', self.contenido):
            return 'EMAIL'
        
        # Direcciones IP
        if re.match(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', self.contenido):
            return 'IP_ADDRESS'
        
        # Rutas de archivo
        if ('/' in self.contenido or '\\' in self.contenido) and len(self.contenido) > 3:
            if self.contenido.startswith(('/usr/', '/etc/', '/var/', '/tmp/', 'C:\\', 'D:\\')):
                return 'FILE_PATH'
        
        # Comandos de sistema
        comandos_sospechosos = [
            'cmd.exe', 'powershell', 'bash', 'sh', 'wget', 'curl', 
            'nc', 'netcat', 'telnet', 'ssh', 'ftp'
        ]
        if any(cmd in contenido_lower for cmd in comandos_sospechosos):
            return 'SYSTEM_COMMAND'
        
        # Funciones de API de Windows
        apis_windows = [
            'createfile', 'writefile', 'readfile', 'createprocess',
            'virtualalloc', 'getprocaddress', 'loadlibrary'
        ]
        if any(api in contenido_lower for api in apis_windows):
            return 'WINDOWS_API'
        
        # Claves de registro
        if contenido_lower.startswith(('hkey_', 'hklm\\', 'hkcu\\', 'software\\')):
            return 'REGISTRY_KEY'
        
        # Texto normal
        if self.contenido.isprintable() and ' ' in self.contenido:
            return 'TEXT'
        
        # Cadena hexadecimal
        if re.match(r'^[0-9a-fA-F]+$', self.contenido) and len(self.contenido) % 2 == 0:
            return 'HEX_STRING'
        
        # Base64
        if re.match(r'^[A-Za-z0-9+/]*={0,2}$', self.contenido) and len(self.contenido) % 4 == 0:
            return 'BASE64'
        
        return 'UNKNOWN'
    
    def _evaluar_sospecha(self) -> bool:
        """Evalúa si la cadena es potencialmente sospechosa."""
        contenido_lower = self.contenido.lower()
        
        # Palabras clave sospechosas
        palabras_sospechosas = [
            'password', 'passwd', 'secret', 'key', 'token', 'backdoor',
            'rootkit', 'keylogger', 'trojan', 'virus', 'malware',
            'exploit', 'payload', 'shellcode', 'reverse', 'shell',
            'cmd', 'exec', 'eval', 'system', 'popen'
        ]
        
        # URLs sospechosas
        dominios_sospechosos = [
            '.tk', '.ml', '.ga', '.cf', 'bit.ly', 'tinyurl',
            'pastebin', 'hastebin', 'ghostbin'
        ]
        
        # IPs privadas o localhost
        ips_sospechosas = ['127.0.0.1', '192.168.', '10.', '172.']
        
        # Verificar palabras clave
        if any(palabra in contenido_lower for palabra in palabras_sospechosas):
            return True
        
        # Verificar dominios sospechosos
        if any(dominio in contenido_lower for dominio in dominios_sospechosos):
            return True
        
        # Verificar IPs sospechosas
        if any(ip in self.contenido for ip in ips_sospechosas):
            return True
        
        # Cadenas muy largas pueden ser sospechosas
        if len(self.contenido) > 200:
            return True
        
        # Cadenas con caracteres de escape
        if '\\x' in self.contenido or '\\u' in self.contenido:
            return True
        
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la cadena a diccionario."""
        return {
            'contenido': self.contenido,
            'offset': self.offset,
            'encoding': self.encoding,
            'longitud': self.longitud,
            'tipo_cadena': self.tipo_cadena,
            'es_sospechosa': self.es_sospechosa
        }


class ExtractorCadenas:
    """Extractor de cadenas de archivos binarios."""
    
    def __init__(self, longitud_minima: int = 4, longitud_maxima: int = 1000):
        """
        Inicializa el extractor de cadenas.
        
        Args:
            longitud_minima: Longitud mínima de cadenas a extraer
            longitud_maxima: Longitud máxima de cadenas a extraer
        """
        self.longitud_minima = longitud_minima
        self.longitud_maxima = longitud_maxima
        self.encodings = ['ascii', 'utf-8', 'utf-16le', 'utf-16be', 'latin1']
        
    def extraer_cadenas_ascii(self, datos: bytes) -> List[CadenaEncontrada]:
        """
        Extrae cadenas ASCII de datos binarios.
        
        Args:
            datos: Datos binarios a analizar
            
        Returns:
            Lista de cadenas encontradas
        """
        cadenas = []
        patron_ascii = re.compile(rb'[ -~]{%d,%d}' % (self.longitud_minima, self.longitud_maxima))
        
        for match in patron_ascii.finditer(datos):
            try:
                contenido = match.group().decode('ascii')
                offset = match.start()
                longitud = len(contenido)
                
                cadena = CadenaEncontrada(contenido, offset, 'ascii', longitud)
                cadenas.append(cadena)
                
            except UnicodeDecodeError:
                continue
        
        return cadenas
    
    def extraer_cadenas_unicode(self, datos: bytes) -> List[CadenaEncontrada]:
        """
        Extrae cadenas Unicode de datos binarios.
        
        Args:
            datos: Datos binarios a analizar
            
        Returns:
            Lista de cadenas Unicode encontradas
        """
        cadenas = []
        
        # UTF-16 Little Endian
        try:
            for i in range(0, len(datos) - 1, 2):
                if datos[i + 1] == 0:  # Carácter seguido de byte nulo
                    inicio = i
                    fin = i
                    
                    # Buscar el final de la cadena
                    while fin < len(datos) - 1 and datos[fin + 1] == 0 and datos[fin] != 0:
                        fin += 2
                    
                    if fin - inicio >= self.longitud_minima * 2:
                        try:
                            contenido = datos[inicio:fin + 1:2].decode('ascii')
                            if len(contenido) >= self.longitud_minima:
                                cadena = CadenaEncontrada(contenido, inicio, 'utf-16le', len(contenido))
                                cadenas.append(cadena)
                        except UnicodeDecodeError:
                            continue
        except Exception:
            pass
        
        return cadenas
    
    def extraer_cadenas_encoding(self, datos: bytes, encoding: str) -> List[CadenaEncontrada]:
        """
        Extrae cadenas usando una codificación específica.
        
        Args:
            datos: Datos binarios a analizar
            encoding: Codificación a usar
            
        Returns:
            Lista de cadenas encontradas
        """
        cadenas = []
        
        try:
            texto_completo = datos.decode(encoding, errors='ignore')
            
            # Buscar secuencias de caracteres imprimibles
            patron = re.compile(r'[^\x00-\x1f\x7f-\x9f]{%d,%d}' % (self.longitud_minima, self.longitud_maxima))
            
            for match in patron.finditer(texto_completo):
                contenido = match.group()
                offset = match.start()
                longitud = len(contenido)
                
                # Filtrar cadenas que son solo espacios o caracteres repetidos
                if len(set(contenido.strip())) > 1:
                    cadena = CadenaEncontrada(contenido.strip(), offset, encoding, longitud)
                    cadenas.append(cadena)
                    
        except (UnicodeDecodeError, LookupError):
            pass
        
        return cadenas
    
    def extraer_todas_las_cadenas(self, datos: bytes) -> List[CadenaEncontrada]:
        """
        Extrae todas las cadenas usando múltiples métodos.
        
        Args:
            datos: Datos binarios a analizar
            
        Returns:
            Lista consolidada de cadenas únicas
        """
        todas_cadenas = []
        cadenas_vistas = set()
        
        # Extraer cadenas ASCII
        cadenas_ascii = self.extraer_cadenas_ascii(datos)
        for cadena in cadenas_ascii:
            if cadena.contenido not in cadenas_vistas:
                todas_cadenas.append(cadena)
                cadenas_vistas.add(cadena.contenido)
        
        # Extraer cadenas Unicode
        cadenas_unicode = self.extraer_cadenas_unicode(datos)
        for cadena in cadenas_unicode:
            if cadena.contenido not in cadenas_vistas:
                todas_cadenas.append(cadena)
                cadenas_vistas.add(cadena.contenido)
        
        # Probar otras codificaciones
        for encoding in ['utf-8', 'latin1']:
            cadenas_encoding = self.extraer_cadenas_encoding(datos, encoding)
            for cadena in cadenas_encoding:
                if cadena.contenido not in cadenas_vistas:
                    todas_cadenas.append(cadena)
                    cadenas_vistas.add(cadena.contenido)
        
        return todas_cadenas


class AnalizadorCadenas:
    """Analizador completo de cadenas en archivos."""
    
    def __init__(self, siem=None):
        """
        Inicializa el analizador de cadenas.
        
        Args:
            siem: Sistema SIEM para logging (opcional)
        """
        self.siem = siem
        self.extractor = ExtractorCadenas()
    
    def analizar_archivo(self, ruta_archivo: str, max_tamaño: int = 50 * 1024 * 1024) -> Dict[str, Any]:
        """
        Analiza las cadenas de un archivo.
        
        Args:
            ruta_archivo: Ruta al archivo a analizar
            max_tamaño: Tamaño máximo de archivo a procesar (50MB por defecto)
            
        Returns:
            Dict con análisis de cadenas
        """
        if self.siem:
            self.siem.log_evento('INFO', 'analizador_cadenas', 
                               f'Iniciando análisis de cadenas de {ruta_archivo}')
        
        archivo_path = Path(ruta_archivo)
        
        if not archivo_path.exists():
            return {
                'error': 'Archivo no encontrado',
                'timestamp_analisis': datetime.now().isoformat()
            }
        
        tamaño_archivo = archivo_path.stat().st_size
        if tamaño_archivo > max_tamaño:
            if self.siem:
                self.siem.log_evento('WARNING', 'analizador_cadenas', 
                                   f'Archivo demasiado grande: {tamaño_archivo} bytes')
            return {
                'error': f'Archivo demasiado grande: {tamaño_archivo} bytes (máximo: {max_tamaño})',
                'timestamp_analisis': datetime.now().isoformat()
            }
        
        try:
            with open(archivo_path, 'rb') as archivo:
                datos = archivo.read()
            
            # Extraer cadenas
            cadenas_encontradas = self.extractor.extraer_todas_las_cadenas(datos)
            
            # Analizar estadísticas
            estadisticas = self._calcular_estadisticas(cadenas_encontradas)
            
            # Filtrar cadenas sospechosas
            cadenas_sospechosas = [c for c in cadenas_encontradas if c.es_sospechosa]
            
            # Categorizar cadenas
            categorias = self._categorizar_cadenas(cadenas_encontradas)
            
            resultado = {
                'timestamp_analisis': datetime.now().isoformat(),
                'archivo': str(archivo_path),
                'tamaño_archivo': tamaño_archivo,
                'total_cadenas': len(cadenas_encontradas),
                'cadenas_sospechosas': len(cadenas_sospechosas),
                'estadisticas': estadisticas,
                'categorias': categorias,
                'cadenas': [c.to_dict() for c in cadenas_encontradas],
                'cadenas_sospechosas_detalle': [c.to_dict() for c in cadenas_sospechosas]
            }
            
            if self.siem:
                self.siem.log_evento('INFO', 'analizador_cadenas', 
                                   f'Análisis completado: {len(cadenas_encontradas)} cadenas encontradas')
            
            return resultado
            
        except Exception as e:
            error_msg = f'Error analizando archivo: {str(e)}'
            if self.siem:
                self.siem.log_evento('ERROR', 'analizador_cadenas', error_msg)
            
            return {
                'error': error_msg,
                'timestamp_analisis': datetime.now().isoformat()
            }
    
    def _calcular_estadisticas(self, cadenas: List[CadenaEncontrada]) -> Dict[str, Any]:
        """Calcula estadísticas de las cadenas encontradas."""
        if not cadenas:
            return {}
        
        longitudes = [c.longitud for c in cadenas]
        encodings = [c.encoding for c in cadenas]
        tipos = [c.tipo_cadena for c in cadenas]
        
        return {
            'longitud_promedio': sum(longitudes) / len(longitudes),
            'longitud_minima': min(longitudes),
            'longitud_maxima': max(longitudes),
            'encodings_encontrados': list(set(encodings)),
            'tipos_encontrados': list(set(tipos)),
            'porcentaje_sospechosas': (sum(1 for c in cadenas if c.es_sospechosa) / len(cadenas)) * 100
        }
    
    def _categorizar_cadenas(self, cadenas: List[CadenaEncontrada]) -> Dict[str, int]:
        """Categoriza las cadenas por tipo."""
        categorias = {}
        
        for cadena in cadenas:
            tipo = cadena.tipo_cadena
            categorias[tipo] = categorias.get(tipo, 0) + 1
        
        return categorias
    
    def buscar_patrones_especificos(self, ruta_archivo: str, patrones: List[str]) -> List[Dict[str, Any]]:
        """
        Busca patrones específicos en las cadenas del archivo.
        
        Args:
            ruta_archivo: Ruta al archivo a analizar
            patrones: Lista de patrones regex a buscar
            
        Returns:
            Lista de coincidencias encontradas
        """
        if self.siem:
            self.siem.log_evento('INFO', 'analizador_cadenas', 
                               f'Buscando patrones específicos en {ruta_archivo}')
        
        analisis = self.analizar_archivo(ruta_archivo)
        
        if 'error' in analisis:
            return []
        
        coincidencias = []
        cadenas = analisis['cadenas']
        
        for patron in patrones:
            try:
                regex = re.compile(patron, re.IGNORECASE)
                
                for cadena_dict in cadenas:
                    contenido = cadena_dict['contenido']
                    
                    if regex.search(contenido):
                        coincidencias.append({
                            'patron': patron,
                            'cadena': cadena_dict,
                            'coincidencia_completa': regex.findall(contenido)
                        })
                        
            except re.error as e:
                if self.siem:
                    self.siem.log_evento('WARNING', 'analizador_cadenas', 
                                       f'Patrón regex inválido {patron}: {e}')
        
        return coincidencias
    
    def extraer_urls(self, ruta_archivo: str) -> List[str]:
        """
        Extrae todas las URLs encontradas en el archivo.
        
        Args:
            ruta_archivo: Ruta al archivo a analizar
            
        Returns:
            Lista de URLs encontradas
        """
        analisis = self.analizar_archivo(ruta_archivo)
        
        if 'error' in analisis:
            return []
        
        urls = []
        for cadena_dict in analisis['cadenas']:
            if cadena_dict['tipo_cadena'] == 'URL':
                urls.append(cadena_dict['contenido'])
        
        return list(set(urls))  # Eliminar duplicados
    
    def extraer_ips(self, ruta_archivo: str) -> List[str]:
        """
        Extrae todas las direcciones IP encontradas en el archivo.
        
        Args:
            ruta_archivo: Ruta al archivo a analizar
            
        Returns:
            Lista de IPs encontradas
        """
        analisis = self.analizar_archivo(ruta_archivo)
        
        if 'error' in analisis:
            return []
        
        ips = []
        for cadena_dict in analisis['cadenas']:
            if cadena_dict['tipo_cadena'] == 'IP_ADDRESS':
                ips.append(cadena_dict['contenido'])
        
        return list(set(ips))  # Eliminar duplicados
    
    def generar_reporte_markdown(self, analisis: Dict[str, Any]) -> str:
        """
        Genera un reporte en formato Markdown del análisis.
        
        Args:
            analisis: Resultado del análisis de cadenas
            
        Returns:
            String con el reporte en formato Markdown
        """
        if 'error' in analisis:
            return f"# Error en Análisis de Cadenas\n\n**Error:** {analisis['error']}\n"
        
        archivo = Path(analisis['archivo']).name
        estadisticas = analisis['estadisticas']
        categorias = analisis['categorias']
        
        reporte = f"""# Análisis de Cadenas: {archivo}

## Resumen
- **Archivo:** `{analisis['archivo']}`
- **Tamaño:** {analisis['tamaño_archivo']:,} bytes
- **Total de cadenas:** {analisis['total_cadenas']}
- **Cadenas sospechosas:** {analisis['cadenas_sospechosas']}
- **Porcentaje sospechoso:** {estadisticas.get('porcentaje_sospechosas', 0):.1f}%

## Estadísticas
- **Longitud promedio:** {estadisticas.get('longitud_promedio', 0):.1f} caracteres
- **Longitud mínima:** {estadisticas.get('longitud_minima', 0)}
- **Longitud máxima:** {estadisticas.get('longitud_maxima', 0)}
- **Codificaciones encontradas:** {', '.join(estadisticas.get('encodings_encontrados', []))}

## Categorías de Cadenas
"""
        
        for categoria, cantidad in categorias.items():
            reporte += f"- **{categoria}:** {cantidad}\n"
        
        if analisis['cadenas_sospechosas'] > 0:
            reporte += "\n## Cadenas Sospechosas\n\n"
            for cadena in analisis['cadenas_sospechosas_detalle'][:10]:  # Mostrar solo las primeras 10
                reporte += f"- **Tipo:** {cadena['tipo_cadena']}\n"
                reporte += f"  **Contenido:** `{cadena['contenido'][:100]}{'...' if len(cadena['contenido']) > 100 else ''}`\n"
                reporte += f"  **Offset:** {cadena['offset']}\n\n"
        
        reporte += f"\n---\n*Análisis realizado el {analisis['timestamp_analisis']} por Ares Aegis*\n"
        
        return reporte
