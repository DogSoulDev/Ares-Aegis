#!/usr/bin/env python3
"""
Visor Hexadecimal - Ares Aegis
Módulo para visualización y análisis hexadecimal de archivos

Este módulo proporciona funcionalidades de visor hexadecimal para análisis
de archivos binarios, detección de patrones y análisis forense básico.

Autor: DogSoulDev
Versión: 2.0.0 - "Los Decifradores de Thot"
"""

import os
import mmap
import struct
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, NamedTuple, Tuple, Union
from dataclasses import dataclass
from ..utilidades.ayuda_logging import configurar_logger_modulo


@dataclass
class EntradaHex:
    """Representa una entrada en el visor hexadecimal."""
    offset: int
    bytes_hex: str
    bytes_ascii: str
    longitud: int


@dataclass
class PatronDetectado:
    """Representa un patrón detectado en el archivo."""
    tipo: str
    descripcion: str
    offset: int
    longitud: int
    patron: bytes
    confianza: float
    metadatos: Dict[str, Any]


@dataclass
class AnalisisArchivo:
    """Resultado del análisis de un archivo."""
    ruta_archivo: str
    tamaño_archivo: int
    tipo_archivo: str
    timestamp_analisis: datetime
    patrones_detectados: List[PatronDetectado]
    entropia: float
    firmas_encontradas: List[str]
    metadatos: Dict[str, Any]


class VisorHex:
    """Visor hexadecimal principal para análisis de archivos."""
    
    def __init__(self, siem=None):
        """
        Inicializa el visor hexadecimal.
        
        Args:
            siem: Instancia del SIEM para registro de eventos
        """
        self.logger = configurar_logger_modulo("visor_hexadecimal")
        self.siem = siem
        
        # Configuración del visor
        self.bytes_por_linea = 16
        self.max_tamaño_archivo = 100 * 1024 * 1024  # 100MB
        self.buffer_lectura = 4096
        
        # Patrones de archivos conocidos (firmas mágicas)
        self.firmas_magicas = {
            b'\x89PNG\r\n\x1a\n': 'PNG Image',
            b'\xff\xd8\xff': 'JPEG Image',
            b'GIF87a': 'GIF Image (87a)',
            b'GIF89a': 'GIF Image (89a)',
            b'BM': 'Windows Bitmap',
            b'RIFF': 'RIFF Container (WAV, AVI, etc.)',
            b'\x50\x4b\x03\x04': 'ZIP Archive',
            b'\x50\x4b\x05\x06': 'ZIP Archive (empty)',
            b'\x50\x4b\x07\x08': 'ZIP Archive (spanned)',
            b'\x7f\x45\x4c\x46': 'ELF Executable',
            b'MZ': 'DOS/Windows Executable',
            b'\xca\xfe\xba\xbe': 'Java Class File',
            b'\xfe\xed\xfa\xce': 'Mach-O Binary (32-bit)',
            b'\xfe\xed\xfa\xcf': 'Mach-O Binary (64-bit)',
            b'\xcf\xfa\xed\xfe': 'Mach-O Binary (reverse 32-bit)',
            b'\xcf\xfa\xed\xfe': 'Mach-O Binary (reverse 64-bit)',
            b'%PDF': 'PDF Document',
            b'PK': 'ZIP-based format',
            b'\x1f\x8b': 'GZIP Compressed',
            b'BZh': 'BZIP2 Compressed',
            b'\xfd7zXZ\x00': 'XZ Compressed',
            b'\x00\x00\x01\x00': 'Windows Icon',
            b'\x00\x00\x02\x00': 'Windows Cursor',
            b'fLaC': 'FLAC Audio',
            b'ID3': 'MP3 Audio (ID3)',
            b'\xff\xfb': 'MP3 Audio',
            b'OggS': 'OGG Container',
            b'\x1a\x45\xdf\xa3': 'Matroska Video',
            b'ftypmp4': 'MP4 Video',
            b'ftypisom': 'MP4 Video (ISO)',
            b'\x00\x00\x00\x20ftypM4A': 'M4A Audio',
        }
        
        # Patrones sospechosos
        self.patrones_sospechosos = {
            b'eval(': 'Posible código PHP/JavaScript malicioso',
            b'base64_decode': 'Posible decodificación base64 sospechosa',
            b'shell_exec': 'Ejecución de shell en PHP',
            b'system(': 'Llamada al sistema',
            b'exec(': 'Ejecución de comando',
            b'passthru': 'Ejecución passthru en PHP',
            b'cmd.exe': 'Referencia a cmd.exe',
            b'powershell': 'Referencia a PowerShell',
            b'/bin/sh': 'Referencia a shell Unix',
            b'/bin/bash': 'Referencia a bash',
            b'wget ': 'Comando de descarga wget',
            b'curl ': 'Comando de descarga curl',
            b'chmod +x': 'Cambio de permisos de ejecución',
            b'rm -rf': 'Comando de eliminación recursiva',
            b'dd if=': 'Comando dd (potencialmente peligroso)',
            b'nc -': 'Netcat (potencial backdoor)',
            b'telnet': 'Conexión telnet',
            b'ftp://': 'URL FTP',
            b'http://': 'URL HTTP',
            b'https://': 'URL HTTPS',
            b'tcp://': 'Conexión TCP directa',
            b'0x': 'Valor hexadecimal',
            b'\\x': 'Escape hexadecimal',
            b'%u': 'Unicode escape',
            b'javascript:': 'JavaScript URL',
            b'data:': 'Data URL',
            b'vbscript:': 'VBScript URL',
        }
        
        # Cadenas de texto comunes en malware
        self.cadenas_malware = {
            b'keylogger': 'Posible keylogger',
            b'backdoor': 'Posible backdoor',
            b'rootkit': 'Posible rootkit',
            b'trojan': 'Posible trojan',
            b'virus': 'Posible virus',
            b'worm': 'Posible gusano',
            b'ransomware': 'Posible ransomware',
            b'cryptolock': 'Posible ransomware',
            b'payload': 'Posible payload malicioso',
            b'shellcode': 'Posible shellcode',
            b'exploit': 'Posible exploit',
            b'metasploit': 'Referencia a Metasploit',
            b'meterpreter': 'Posible Meterpreter',
            b'cobalt': 'Posible Cobalt Strike',
            b'empire': 'Posible PowerShell Empire',
        }
        
        self.logger.info("Los Decifradores de Thot despiertan para revelar los secretos binarios")
    
    def abrir_archivo(self, ruta_archivo: str) -> bool:
        """
        Abre un archivo para análisis hexadecimal.
        
        Args:
            ruta_archivo: Ruta al archivo a abrir
            
        Returns:
            True si el archivo se abrió correctamente
        """
        try:
            ruta = Path(ruta_archivo)
            
            if not ruta.exists():
                self.logger.error(f"Archivo no encontrado: {ruta_archivo}")
                return False
            
            if not ruta.is_file():
                self.logger.error(f"No es un archivo regular: {ruta_archivo}")
                return False
            
            tamaño = ruta.stat().st_size
            
            if tamaño > self.max_tamaño_archivo:
                self.logger.warning(f"Archivo demasiado grande: {tamaño} bytes")
                respuesta = input(f"¿Continuar con archivo de {tamaño/1024/1024:.1f}MB? (s/n): ")
                if respuesta.lower() != 's':
                    return False
            
            self.archivo_actual = str(ruta.absolute())
            self.tamaño_archivo = tamaño
            
            self.logger.info(f"Los Decifradores han abierto el pergamino: {ruta_archivo} ({tamaño} bytes)")
            
            if self.siem:
                from .siem import TipoEvento
                self.siem.registrar_evento(
                    TipoEvento.INFORMACION,
                    f"Los Decifradores examinan el pergamino binario: {ruta.name}",
                    {
                        "archivo": str(ruta),
                        "tamaño": tamaño,
                        "componente": "visor_hexadecimal"
                    },
                    "BAJO"
                )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error abriendo archivo {ruta_archivo}: {e}")
            return False
    
    def leer_hex(self, offset: int = 0, longitud: int = 256) -> List[EntradaHex]:
        """
        Lee y convierte datos a formato hexadecimal.
        
        Args:
            offset: Offset de inicio en bytes
            longitud: Número de bytes a leer
            
        Returns:
            Lista de entradas hexadecimales
        """
        if not hasattr(self, 'archivo_actual'):
            self.logger.error("No hay archivo abierto")
            return []
        
        entradas = []
        
        try:
            with open(self.archivo_actual, 'rb') as archivo:
                archivo.seek(offset)
                datos = archivo.read(longitud)
                
                for i in range(0, len(datos), self.bytes_por_linea):
                    chunk = datos[i:i + self.bytes_por_linea]
                    offset_linea = offset + i
                    
                    # Convertir a hexadecimal
                    hex_str = ' '.join(f'{b:02x}' for b in chunk)
                    hex_str = hex_str.ljust(self.bytes_por_linea * 3 - 1)  # Padding
                    
                    # Convertir a ASCII (reemplazar no imprimibles)
                    ascii_str = ''
                    for b in chunk:
                        if 32 <= b <= 126:
                            ascii_str += chr(b)
                        else:
                            ascii_str += '.'
                    
                    entrada = EntradaHex(
                        offset=offset_linea,
                        bytes_hex=hex_str,
                        bytes_ascii=ascii_str,
                        longitud=len(chunk)
                    )
                    entradas.append(entrada)
            
            return entradas
            
        except Exception as e:
            self.logger.error(f"Error leyendo datos hexadecimales: {e}")
            return []
    
    def mostrar_hex(self, offset: int = 0, longitud: int = 256) -> str:
        """
        Genera una representación visual del contenido hexadecimal.
        
        Args:
            offset: Offset de inicio
            longitud: Número de bytes a mostrar
            
        Returns:
            Representación hexadecimal formateada
        """
        entradas = self.leer_hex(offset, longitud)
        
        if not entradas:
            return "No hay datos para mostrar"
        
        resultado = []
        resultado.append("Offset    | Hex                                              | ASCII")
        resultado.append("----------|--------------------------------------------------|------------------")
        
        for entrada in entradas:
            linea = f"{entrada.offset:08x}  | {entrada.bytes_hex} | {entrada.bytes_ascii}"
            resultado.append(linea)
        
        return '\n'.join(resultado)
    
    def buscar_patron(self, patron: Union[str, bytes], offset_inicio: int = 0) -> List[Tuple[int, bytes]]:
        """
        Busca un patrón específico en el archivo.
        
        Args:
            patron: Patrón a buscar (string o bytes)
            offset_inicio: Offset donde comenzar la búsqueda
            
        Returns:
            Lista de tuplas (offset, datos_encontrados)
        """
        if not hasattr(self, 'archivo_actual'):
            self.logger.error("No hay archivo abierto")
            return []
        
        # Convertir string a bytes si es necesario
        if isinstance(patron, str):
            patron_bytes = patron.encode('utf-8', errors='ignore')
        else:
            patron_bytes = patron
        
        coincidencias = []
        
        try:
            with open(self.archivo_actual, 'rb') as archivo:
                archivo.seek(offset_inicio)
                
                # Leer archivo en chunks para manejar archivos grandes
                buffer_overlap = len(patron_bytes) - 1
                chunk_size = self.buffer_lectura
                buffer_anterior = b''
                offset_actual = offset_inicio
                
                while True:
                    chunk = archivo.read(chunk_size)
                    if not chunk:
                        break
                    
                    # Combinar con buffer anterior para evitar perder coincidencias en límites
                    datos_busqueda = buffer_anterior + chunk
                    
                    # Buscar patrón en los datos
                    pos = 0
                    while True:
                        pos = datos_busqueda.find(patron_bytes, pos)
                        if pos == -1:
                            break
                        
                        offset_coincidencia = offset_actual - len(buffer_anterior) + pos
                        contexto = datos_busqueda[max(0, pos-16):pos+len(patron_bytes)+16]
                        coincidencias.append((offset_coincidencia, contexto))
                        
                        pos += 1
                    
                    # Preparar para siguiente iteración
                    buffer_anterior = chunk[-buffer_overlap:] if len(chunk) >= buffer_overlap else chunk
                    offset_actual += len(chunk)
            
            self.logger.info(f"Patrón encontrado {len(coincidencias)} veces")
            return coincidencias
            
        except Exception as e:
            self.logger.error(f"Error buscando patrón: {e}")
            return []
    
    def detectar_firmas(self) -> List[str]:
        """
        Detecta firmas de archivos conocidos.
        
        Returns:
            Lista de tipos de archivo detectados
        """
        if not hasattr(self, 'archivo_actual'):
            return []
        
        firmas_detectadas = []
        
        try:
            with open(self.archivo_actual, 'rb') as archivo:
                # Leer los primeros bytes para detección
                inicio = archivo.read(512)
                
                # Verificar firmas mágicas
                for firma, descripcion in self.firmas_magicas.items():
                    if inicio.startswith(firma):
                        firmas_detectadas.append(descripcion)
                    elif firma in inicio[:64]:  # Buscar en los primeros 64 bytes
                        firmas_detectadas.append(f"{descripcion} (no al inicio)")
                
                # Verificar otras posiciones comunes
                archivo.seek(0x3c)  # Offset PE en archivos Windows
                pe_offset_data = archivo.read(4)
                if len(pe_offset_data) == 4:
                    pe_offset = struct.unpack('<I', pe_offset_data)[0]
                    if pe_offset < self.tamaño_archivo - 4:
                        archivo.seek(pe_offset)
                        pe_sig = archivo.read(4)
                        if pe_sig == b'PE\x00\x00':
                            firmas_detectadas.append('Windows PE Executable')
            
        except Exception as e:
            self.logger.error(f"Error detectando firmas: {e}")
        
        return firmas_detectadas
    
    def analizar_archivo_completo(self) -> Optional[AnalisisArchivo]:
        """
        Realiza un análisis completo del archivo abierto.
        
        Returns:
            Análisis completo del archivo
        """
        if not hasattr(self, 'archivo_actual'):
            self.logger.error("No hay archivo abierto")
            return None
        
        self.logger.info("Los Decifradores inician el análisis completo del pergamino")
        
        try:
            patrones_detectados = []
            
            # Detectar firmas de archivo
            firmas = self.detectar_firmas()
            
            # Buscar patrones sospechosos
            for patron, descripcion in self.patrones_sospechosos.items():
                coincidencias = self.buscar_patron(patron)
                for offset, contexto in coincidencias:
                    patron_obj = PatronDetectado(
                        tipo="sospechoso",
                        descripcion=descripcion,
                        offset=offset,
                        longitud=len(patron),
                        patron=patron,
                        confianza=0.7,
                        metadatos={"contexto": contexto.hex()}
                    )
                    patrones_detectados.append(patron_obj)
            
            # Buscar cadenas de malware
            for cadena, descripcion in self.cadenas_malware.items():
                coincidencias = self.buscar_patron(cadena)
                for offset, contexto in coincidencias:
                    patron_obj = PatronDetectado(
                        tipo="malware",
                        descripcion=descripcion,
                        offset=offset,
                        longitud=len(cadena),
                        patron=cadena,
                        confianza=0.9,
                        metadatos={"contexto": contexto.hex()}
                    )
                    patrones_detectados.append(patron_obj)
            
            # Calcular entropía
            entropia = self.calcular_entropia()
            
            # Determinar tipo de archivo
            tipo_archivo = self._determinar_tipo_archivo(firmas)
            
            analisis = AnalisisArchivo(
                ruta_archivo=self.archivo_actual,
                tamaño_archivo=self.tamaño_archivo,
                tipo_archivo=tipo_archivo,
                timestamp_analisis=datetime.now(),
                patrones_detectados=patrones_detectados,
                entropia=entropia,
                firmas_encontradas=firmas,
                metadatos={
                    "patrones_sospechosos": len([p for p in patrones_detectados if p.tipo == "sospechoso"]),
                    "patrones_malware": len([p for p in patrones_detectados if p.tipo == "malware"]),
                    "entropia_nivel": self._clasificar_entropia(entropia)
                }
            )
            
            # Registrar en SIEM si hay patrones sospechosos
            if patrones_detectados and self.siem:
                from .siem import TipoEvento
                self.siem.registrar_evento(
                    TipoEvento.AMENAZA_DETECTADA,
                    f"Los Decifradores revelan {len(patrones_detectados)} patrones sospechosos",
                    {
                        "archivo": self.archivo_actual,
                        "patrones_detectados": len(patrones_detectados),
                        "entropia": entropia,
                        "tipo_archivo": tipo_archivo
                    },
                    "ALTO" if any(p.tipo == "malware" for p in patrones_detectados) else "MEDIO"
                )
            
            self.logger.info(f"Análisis completado: {len(patrones_detectados)} patrones, entropía {entropia:.2f}")
            
            return analisis
            
        except Exception as e:
            self.logger.error(f"Error en análisis completo: {e}")
            return None
    
    def calcular_entropia(self, tamaño_muestra: int = 8192) -> float:
        """
        Calcula la entropía del archivo para detectar posible cifrado/compresión.
        
        Args:
            tamaño_muestra: Tamaño de la muestra para calcular entropía
            
        Returns:
            Valor de entropía (0-8)
        """
        if not hasattr(self, 'archivo_actual'):
            return 0.0
        
        try:
            import math
            
            # Contar frecuencia de bytes
            contadores = [0] * 256
            total_bytes = 0
            
            with open(self.archivo_actual, 'rb') as archivo:
                # Leer muestras distribuidas a lo largo del archivo
                muestras = min(10, max(1, self.tamaño_archivo // tamaño_muestra))
                
                for i in range(muestras):
                    offset = i * (self.tamaño_archivo // muestras)
                    archivo.seek(offset)
                    datos = archivo.read(tamaño_muestra)
                    
                    for byte in datos:
                        contadores[byte] += 1
                        total_bytes += 1
            
            if total_bytes == 0:
                return 0.0
            
            # Calcular entropía de Shannon
            entropia = 0.0
            for count in contadores:
                if count > 0:
                    probabilidad = count / total_bytes
                    entropia -= probabilidad * math.log2(probabilidad)
            
            return entropia
            
        except Exception as e:
            self.logger.error(f"Error calculando entropía: {e}")
            return 0.0
    
    def _determinar_tipo_archivo(self, firmas: List[str]) -> str:
        """Determina el tipo de archivo basado en las firmas detectadas."""
        if not firmas:
            return "Desconocido"
        
        # Usar la primera firma como tipo principal
        return firmas[0]
    
    def _clasificar_entropia(self, entropia: float) -> str:
        """Clasifica el nivel de entropía."""
        if entropia < 1.0:
            return "Muy Baja"
        elif entropia < 3.0:
            return "Baja"
        elif entropia < 5.0:
            return "Media"
        elif entropia < 7.0:
            return "Alta"
        else:
            return "Muy Alta"
    
    def extraer_cadenas(self, longitud_minima: int = 4, longitud_maxima: int = 100) -> List[Tuple[int, str]]:
        """
        Extrae cadenas legibles del archivo.
        
        Args:
            longitud_minima: Longitud mínima de cadena
            longitud_maxima: Longitud máxima de cadena
            
        Returns:
            Lista de tuplas (offset, cadena)
        """
        if not hasattr(self, 'archivo_actual'):
            return []
        
        cadenas_encontradas = []
        
        try:
            with open(self.archivo_actual, 'rb') as archivo:
                buffer = b''
                cadena_actual = b''
                offset_cadena = 0
                offset_archivo = 0
                
                while True:
                    chunk = archivo.read(self.buffer_lectura)
                    if not chunk:
                        break
                    
                    for i, byte in enumerate(chunk):
                        # Verificar si es un carácter imprimible
                        if 32 <= byte <= 126:
                            if not cadena_actual:
                                offset_cadena = offset_archivo + i
                            cadena_actual += bytes([byte])
                        else:
                            # Fin de cadena
                            if len(cadena_actual) >= longitud_minima:
                                try:
                                    cadena_str = cadena_actual.decode('utf-8', errors='ignore')
                                    if len(cadena_str) <= longitud_maxima:
                                        cadenas_encontradas.append((offset_cadena, cadena_str))
                                except:
                                    pass
                            cadena_actual = b''
                    
                    offset_archivo += len(chunk)
                
                # Procesar última cadena si existe
                if len(cadena_actual) >= longitud_minima:
                    try:
                        cadena_str = cadena_actual.decode('utf-8', errors='ignore')
                        if len(cadena_str) <= longitud_maxima:
                            cadenas_encontradas.append((offset_cadena, cadena_str))
                    except:
                        pass
            
            self.logger.info(f"Extraídas {len(cadenas_encontradas)} cadenas legibles")
            return cadenas_encontradas
            
        except Exception as e:
            self.logger.error(f"Error extrayendo cadenas: {e}")
            return []
    
    def comparar_archivos(self, archivo1: str, archivo2: str) -> Dict[str, Any]:
        """
        Compara dos archivos binariamente.
        
        Args:
            archivo1: Ruta del primer archivo
            archivo2: Ruta del segundo archivo
            
        Returns:
            Diccionario con resultados de la comparación
        """
        try:
            ruta1 = Path(archivo1)
            ruta2 = Path(archivo2)
            
            if not ruta1.exists() or not ruta2.exists():
                return {"error": "Uno o ambos archivos no existen"}
            
            tamaño1 = ruta1.stat().st_size
            tamaño2 = ruta2.stat().st_size
            
            diferencias = []
            bytes_identicos = 0
            bytes_diferentes = 0
            
            with open(archivo1, 'rb') as f1, open(archivo2, 'rb') as f2:
                offset = 0
                while True:
                    chunk1 = f1.read(self.buffer_lectura)
                    chunk2 = f2.read(self.buffer_lectura)
                    
                    if not chunk1 and not chunk2:
                        break
                    
                    # Comparar byte a byte en este chunk
                    max_len = max(len(chunk1), len(chunk2))
                    for i in range(max_len):
                        byte1 = chunk1[i] if i < len(chunk1) else None
                        byte2 = chunk2[i] if i < len(chunk2) else None
                        
                        if byte1 == byte2:
                            bytes_identicos += 1
                        else:
                            bytes_diferentes += 1
                            if len(diferencias) < 100:  # Limitar diferencias mostradas
                                diferencias.append({
                                    'offset': offset + i,
                                    'byte1': byte1,
                                    'byte2': byte2
                                })
                    
                    offset += max_len
            
            total_bytes = bytes_identicos + bytes_diferentes
            similitud = (bytes_identicos / total_bytes * 100) if total_bytes > 0 else 0
            
            resultado = {
                'archivo1': archivo1,
                'archivo2': archivo2,
                'tamaño1': tamaño1,
                'tamaño2': tamaño2,
                'bytes_identicos': bytes_identicos,
                'bytes_diferentes': bytes_diferentes,
                'similitud_porcentaje': similitud,
                'diferencias': diferencias[:50],  # Mostrar solo primeras 50
                'total_diferencias': len(diferencias)
            }
            
            self.logger.info(f"Comparación completada: {similitud:.1f}% similitud")
            return resultado
            
        except Exception as e:
            self.logger.error(f"Error comparando archivos: {e}")
            return {"error": str(e)}
    
    def generar_reporte_analisis(self, analisis: AnalisisArchivo) -> str:
        """Genera un reporte detallado del análisis en formato Markdown."""
        md = "# 🔍 Revelaciones de los Decifradores de Thot\n\n"
        md += f"**Archivo Analizado:** `{Path(analisis.ruta_archivo).name}`\n"
        md += f"**Ruta Completa:** `{analisis.ruta_archivo}`\n"
        md += f"**Tamaño:** {analisis.tamaño_archivo:,} bytes ({analisis.tamaño_archivo/1024:.1f} KB)\n"
        md += f"**Tipo Detectado:** {analisis.tipo_archivo}\n"
        md += f"**Entropía:** {analisis.entropia:.2f} ({analisis.metadatos.get('entropia_nivel', 'N/A')})\n"
        md += f"**Fecha de Análisis:** {analisis.timestamp_analisis.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # Firmas detectadas
        if analisis.firmas_encontradas:
            md += "## 🏷️ Firmas Detectadas\n\n"
            for firma in analisis.firmas_encontradas:
                md += f"- {firma}\n"
            md += "\n"
        
        # Patrones detectados
        if analisis.patrones_detectados:
            md += "## 🚨 Patrones Detectados\n\n"
            
            # Agrupar por tipo
            patrones_por_tipo = {}
            for patron in analisis.patrones_detectados:
                tipo = patron.tipo
                if tipo not in patrones_por_tipo:
                    patrones_por_tipo[tipo] = []
                patrones_por_tipo[tipo].append(patron)
            
            for tipo, patrones in patrones_por_tipo.items():
                emoji = "💀" if tipo == "malware" else "⚠️"
                md += f"### {emoji} {tipo.title()}\n\n"
                md += "| Offset | Descripción | Confianza | Patrón |\n"
                md += "|--------|-------------|-----------|--------|\n"
                
                for patron in sorted(patrones, key=lambda p: p.offset)[:10]:  # Top 10
                    offset_hex = f"0x{patron.offset:08x}"
                    patron_hex = patron.patron.hex()[:20] + "..." if len(patron.patron.hex()) > 20 else patron.patron.hex()
                    md += f"| {offset_hex} | {patron.descripcion} | {patron.confianza:.1f} | `{patron_hex}` |\n"
                
                if len(patrones) > 10:
                    md += f"| ... | ... | ... | ... |\n"
                    md += f"| **Total:** {len(patrones)} patrones | | | |\n"
                
                md += "\n"
        
        # Análisis de entropía
        md += "## 📊 Análisis de Entropía\n\n"
        md += f"**Valor de Entropía:** {analisis.entropia:.3f}\n"
        md += f"**Clasificación:** {analisis.metadatos.get('entropia_nivel', 'N/A')}\n\n"
        
        entropia_nivel = analisis.metadatos.get('entropia_nivel', 'N/A')
        if entropia_nivel == "Muy Alta":
            md += "⚠️ **Alerta:** Entropía muy alta puede indicar archivo cifrado, comprimido o potencialmente malicioso.\n\n"
        elif entropia_nivel == "Alta":
            md += "⚠️ **Nota:** Entropía alta puede indicar archivo comprimido o binario complejo.\n\n"
        
        # Resumen de seguridad
        md += "## 🛡️ Evaluación de Seguridad\n\n"
        
        total_patrones = len(analisis.patrones_detectados)
        patrones_malware = analisis.metadatos.get('patrones_malware', 0)
        patrones_sospechosos = analisis.metadatos.get('patrones_sospechosos', 0)
        
        if patrones_malware > 0:
            md += f"🔴 **RIESGO ALTO:** Se detectaron {patrones_malware} patrones de malware conocido.\n"
        elif patrones_sospechosos > 5:
            md += f"🟠 **RIESGO MEDIO:** Se detectaron {patrones_sospechosos} patrones sospechosos.\n"
        elif patrones_sospechosos > 0:
            md += f"🟡 **RIESGO BAJO:** Se detectaron {patrones_sospechosos} patrones menores.\n"
        else:
            md += f"🟢 **RIESGO BAJO:** No se detectaron patrones maliciosos obvios.\n"
        
        if analisis.entropia > 7.0:
            md += f"⚠️ **Nota:** La alta entropía ({analisis.entropia:.2f}) requiere análisis adicional.\n"
        
        md += "\n"
        
        # Recomendaciones
        md += "## 💡 Recomendaciones\n\n"
        
        if patrones_malware > 0:
            md += "- 🚨 **INMEDIATO:** Aislar el archivo y realizar análisis completo de malware\n"
            md += "- 🔍 Verificar integridad del sistema que contenía este archivo\n"
            md += "- 📋 Documentar el incidente para análisis forense\n"
        elif patrones_sospechosos > 0:
            md += "- 🔍 Realizar análisis adicional con herramientas especializadas\n"
            md += "- 📊 Comparar con bases de datos de amenazas conocidas\n"
            md += "- 🛡️ Considerar ejecución en entorno aislado si es necesario\n"
        else:
            md += "- ✅ El archivo parece seguro basado en el análisis inicial\n"
            md += "- 🔄 Considerar análisis periódicos si es un archivo crítico\n"
        
        if analisis.entropia > 7.0:
            md += "- 🔐 Investigar si el archivo está cifrado o comprimido legítimamente\n"
        
        md += "\n---\n"
        md += "*Análisis realizado por los Decifradores de Thot de Ares Aegis*\n"
        
        return md
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas del visor hexadecimal."""
        return {
            'archivo_abierto': hasattr(self, 'archivo_actual'),
            'archivo_actual': getattr(self, 'archivo_actual', None),
            'tamaño_archivo': getattr(self, 'tamaño_archivo', 0),
            'firmas_conocidas': len(self.firmas_magicas),
            'patrones_sospechosos': len(self.patrones_sospechosos),
            'cadenas_malware': len(self.cadenas_malware),
            'bytes_por_linea': self.bytes_por_linea,
            'max_tamaño_archivo': self.max_tamaño_archivo,
            'buffer_lectura': self.buffer_lectura
        }
