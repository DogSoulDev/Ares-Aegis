#!/usr/bin/env python3
"""
Escaneador - Ares Aegis
Módulo para escaneo de archivos basado en firmas y heurísticas

Autor: DogSoulDev
Versión: 2.0.0
"""

import os
import hashlib
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime


class ResultadoEscaneo:
    """Representa el resultado de un escaneo."""
    
    def __init__(self, ruta: str, es_amenaza: bool = False, 
                 tipo_amenaza: str = "", detalles: str = ""):
        self.ruta = ruta
        self.es_amenaza = es_amenaza
        self.tipo_amenaza = tipo_amenaza
        self.detalles = detalles
        self.fecha_escaneo = datetime.now()
        self.hash_sha256 = self._calcular_hash()
    
    def _calcular_hash(self) -> str:
        try:
            with open(self.ruta, 'rb') as archivo:
                return hashlib.sha256(archivo.read()).hexdigest()
        except:
            return ""
    
    def es_limpio(self) -> bool:
        """Verifica si el archivo está limpio."""
        return not self.es_amenaza
    
    @property
    def limpio(self) -> bool:
        """Propiedad de compatibilidad."""
        return not self.es_amenaza
    
    @property
    def amenazas(self) -> List[str]:
        """Propiedad de compatibilidad para amenazas."""
        if self.es_amenaza and self.tipo_amenaza:
            return [self.tipo_amenaza]
        return []
    
    def to_markdown(self) -> str:
        """Convierte el resultado a formato Markdown."""
        md = f"# Resultado del Escaneo - {self.ruta}\n\n"
        md += f"**Fecha:** {self.fecha_escaneo.strftime('%Y-%m-%d %H:%M:%S')}\n"
        md += f"**Estado:** {'✅ LIMPIO' if not self.es_amenaza else '⚠️ INFECTADO'}\n\n"
        
        if self.es_amenaza:
            md += "## Amenazas Detectadas\n\n"
            md += f"- **Tipo:** {self.tipo_amenaza}\n"
            if self.detalles:
                md += f"- **Detalles:** {self.detalles}\n"
            md += "\n"
        
        if self.hash_sha256:
            md += "## Hash del Archivo\n\n"
            md += f"- **SHA256:** `{self.hash_sha256}`\n\n"
        
        return md
    
    def a_dict(self) -> Dict[str, Any]:
        return {
            'ruta': self.ruta,
            'es_amenaza': self.es_amenaza,
            'tipo_amenaza': self.tipo_amenaza,
            'detalles': self.detalles,
            'fecha_escaneo': self.fecha_escaneo.isoformat(),
            'hash_sha256': self.hash_sha256
        }


class Escaneador:
    
    def __init__(self, siem=None):
        self.siem = siem
        self.firmas_texto = []
        self.firmas_hash = []
        self.firmas_regex = []
        self.cargar_firmas()
    
    def cargar_firmas(self):
        archivo_firmas = Path("configuracion/firmas.txt")
        
        if not archivo_firmas.exists():
            self._crear_archivo_firmas_por_defecto(archivo_firmas)
        
        try:
            with open(archivo_firmas, 'r', encoding='utf-8') as archivo:
                for linea in archivo:
                    linea = linea.strip()
                    if linea and not linea.startswith('#'):
                        self._procesar_firma(linea)
            
            if self.siem:
                self.siem.log_evento('INFO', 'escaneador', 
                                         f'Firmas cargadas: {len(self.firmas_texto)} texto, '
                                         f'{len(self.firmas_hash)} hash, {len(self.firmas_regex)} regex')
        except Exception as e:
            if self.siem:
                self.siem.log_evento('ERROR', 'escaneador', 
                                         f'Error cargando firmas: {e}')
    
    def _crear_archivo_firmas_por_defecto(self, archivo_firmas: Path):
        archivo_firmas.parent.mkdir(exist_ok=True)
        
        firmas_por_defecto = """# Firmas de Ares Aegis
# Formato: una firma por línea
# HASH:valor_hash - para hashes maliciosos
# REGEX:patrón - para expresiones regulares
# Texto simple - para búsqueda de cadenas

# Firmas de texto comunes
eval(base64_decode
system($_GET
<script>alert
powershell -encodedcommand
cmd.exe /c
/bin/sh -c

# Hashes maliciosos conocidos (ejemplos)
HASH:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
HASH:da39a3ee5e6b4b0d3255bfef95601890afd80709

# Expresiones regulares
REGEX:eval\\s*\\(\\s*base64_decode
REGEX:<script[^>]*>.*alert.*</script>
REGEX:powershell\\s+-[eE]ncodedcommand
"""
        
        with open(archivo_firmas, 'w', encoding='utf-8') as archivo:
            archivo.write(firmas_por_defecto)
    
    def _procesar_firma(self, linea: str):
        if linea.startswith('HASH:'):
            self.firmas_hash.append(linea[5:].strip().lower())
        elif linea.startswith('REGEX:'):
            try:
                patron = re.compile(linea[6:].strip(), re.IGNORECASE)
                self.firmas_regex.append(patron)
            except re.error:
                if self.siem:
                    self.siem.log_evento('WARNING', 'escaneador', 
                                             f'Regex inválida: {linea}')
        else:
            self.firmas_texto.append(linea.lower())
    
    def escanear_archivo(self, ruta_archivo: str) -> ResultadoEscaneo:
        path_archivo = Path(ruta_archivo)
        
        if not path_archivo.exists():
            resultado = ResultadoEscaneo(ruta_archivo, True, 
                                       "ARCHIVO_NO_ENCONTRADO", 
                                       "El archivo no existe")
            if self.siem:
                self.siem.log_evento('WARNING', 'escaneador', 
                                         f'Archivo no encontrado: {ruta_archivo}')
            return resultado
        
        if not path_archivo.is_file():
            resultado = ResultadoEscaneo(ruta_archivo, False, 
                                       "", "No es un archivo regular")
            return resultado
        
        # Verificar hash
        hash_resultado = self._verificar_hash(path_archivo)
        if hash_resultado.es_amenaza:
            return hash_resultado
        
        # Verificar contenido
        contenido_resultado = self._verificar_contenido(path_archivo)
        if contenido_resultado.es_amenaza:
            return contenido_resultado
        
        # Análisis heurístico
        heuristico_resultado = self._analisis_heuristico(path_archivo)
        if heuristico_resultado.es_amenaza:
            return heuristico_resultado
        
        resultado = ResultadoEscaneo(ruta_archivo, False, "", "Archivo limpio")
        
        if self.siem:
            self.siem.log_evento('INFO', 'escaneador', 
                                     f'Archivo escaneado limpio: {ruta_archivo}')
        
        return resultado
    
    def _verificar_hash(self, ruta_archivo: Path) -> ResultadoEscaneo:
        try:
            with open(ruta_archivo, 'rb') as archivo:
                contenido = archivo.read()
                hash_sha256 = hashlib.sha256(contenido).hexdigest().lower()
                hash_md5 = hashlib.md5(contenido).hexdigest().lower()
                hash_sha1 = hashlib.sha1(contenido).hexdigest().lower()
            
            for hash_malicioso in self.firmas_hash:
                if hash_sha256 == hash_malicioso or hash_md5 == hash_malicioso or hash_sha1 == hash_malicioso:
                    resultado = ResultadoEscaneo(str(ruta_archivo), True, 
                                               "HASH_MALICIOSO", 
                                               f"Hash coincide con base de datos: {hash_malicioso}")
                    if self.siem:
                        self.siem.log_evento('CRITICAL', 'escaneador', 
                                                 f'Hash malicioso detectado: {ruta_archivo}')
                    return resultado
            
            return ResultadoEscaneo(str(ruta_archivo), False)
            
        except Exception as e:
            return ResultadoEscaneo(str(ruta_archivo), False, "", 
                                  f"Error calculando hash: {e}")
    
    def _verificar_contenido(self, ruta_archivo: Path) -> ResultadoEscaneo:
        try:
            contenido_texto = ""
            try:
                with open(ruta_archivo, 'r', encoding='utf-8', errors='ignore') as archivo:
                    contenido_texto = archivo.read().lower()
            except:
                with open(ruta_archivo, 'rb') as archivo:
                    contenido_binario = archivo.read()
                    strings = re.findall(b'[ -~]{4,}', contenido_binario)
                    contenido_texto = '\n'.join(s.decode('ascii', errors='ignore') for s in strings).lower()
            
            # Verificar firmas de texto
            for firma in self.firmas_texto:
                if firma in contenido_texto:
                    resultado = ResultadoEscaneo(str(ruta_archivo), True, 
                                               "FIRMA_TEXTO", 
                                               f"Firma detectada: {firma}")
                    if self.siem:
                        self.siem.log_evento('HIGH', 'escaneador', 
                                                 f'Firma de texto detectada en {ruta_archivo}: {firma}')
                    return resultado
            
            # Verificar expresiones regulares
            for patron_regex in self.firmas_regex:
                if patron_regex.search(contenido_texto):
                    resultado = ResultadoEscaneo(str(ruta_archivo), True, 
                                               "FIRMA_REGEX", 
                                               f"Patrón regex detectado: {patron_regex.pattern}")
                    if self.siem:
                        self.siem.log_evento('HIGH', 'escaneador', 
                                                 f'Patrón regex detectado en {ruta_archivo}: {patron_regex.pattern}')
                    return resultado
            
            return ResultadoEscaneo(str(ruta_archivo), False)
            
        except Exception as e:
            return ResultadoEscaneo(str(ruta_archivo), False, "", 
                                  f"Error verificando contenido: {e}")
    
    def _analisis_heuristico(self, ruta_archivo: Path) -> ResultadoEscaneo:
        try:
            puntuacion_sospecha = 0
            razones = []
            
            # Verificar extensión sospechosa
            extensiones_sospechosas = ['.exe', '.bat', '.cmd', '.scr', '.pif', '.com']
            if ruta_archivo.suffix.lower() in extensiones_sospechosas:
                puntuacion_sospecha += 2
                razones.append(f"Extensión sospechosa: {ruta_archivo.suffix}")
            
            # Verificar tamaño del archivo
            tamano = ruta_archivo.stat().st_size
            if tamano < 100:
                puntuacion_sospecha += 1
                razones.append("Archivo muy pequeño")
            elif tamano > 50 * 1024 * 1024:
                puntuacion_sospecha += 1
                razones.append("Archivo muy grande")
            
            # Verificar permisos de ejecución
            if os.access(ruta_archivo, os.X_OK):
                puntuacion_sospecha += 1
                razones.append("Archivo ejecutable")
            
            # Verificar ubicación sospechosa
            ubicaciones_sospechosas = ['/tmp/', '/var/tmp/', '/dev/shm/']
            ruta_str = str(ruta_archivo)
            for ubicacion in ubicaciones_sospechosas:
                if ubicacion in ruta_str:
                    puntuacion_sospecha += 2
                    razones.append(f"Ubicación sospechosa: {ubicacion}")
                    break
            
            if puntuacion_sospecha >= 4:
                resultado = ResultadoEscaneo(str(ruta_archivo), True, 
                                           "HEURISTICO_SOSPECHOSO", 
                                           f"Puntuación: {puntuacion_sospecha}, Razones: {', '.join(razones)}")
                if self.siem:
                    self.siem.log_evento('MEDIUM', 'escaneador', 
                                             f'Archivo heurísticamente sospechoso: {ruta_archivo}')
                return resultado
            
            return ResultadoEscaneo(str(ruta_archivo), False)
            
        except Exception as e:
            return ResultadoEscaneo(str(ruta_archivo), False, "", 
                                  f"Error en análisis heurístico: {e}")
    
    def escanear_directorio(self, ruta_directorio: str, recursivo: bool = True) -> List[ResultadoEscaneo]:
        path_directorio = Path(ruta_directorio)
        resultados = []
        
        if not path_directorio.exists():
            resultado = ResultadoEscaneo(ruta_directorio, True, 
                                       "DIRECTORIO_NO_ENCONTRADO", 
                                       "El directorio no existe")
            if self.siem:
                self.siem.log_evento('WARNING', 'escaneador', 
                                         f'Directorio no encontrado: {ruta_directorio}')
            return [resultado]
        
        if not path_directorio.is_dir():
            resultado = ResultadoEscaneo(ruta_directorio, False, 
                                       "", "No es un directorio")
            return [resultado]
        
        try:
            patron = "**/*" if recursivo else "*"
            archivos = list(path_directorio.glob(patron))
            
            total_archivos = len([f for f in archivos if f.is_file()])
            archivos_procesados = 0
            
            if self.siem:
                self.siem.log_evento('INFO', 'escaneador', 
                                         f'Iniciando escaneo de directorio: {ruta_directorio} ({total_archivos} archivos)')
            
            for archivo in archivos:
                if archivo.is_file():
                    resultado = self.escanear_archivo(str(archivo))
                    resultados.append(resultado)
                    archivos_procesados += 1
                    
                    if archivos_procesados % 100 == 0 and self.siem:
                        self.siem.log_evento('INFO', 'escaneador', 
                                                 f'Progreso: {archivos_procesados}/{total_archivos} archivos')
            
            amenazas_encontradas = len([r for r in resultados if r.es_amenaza])
            
            if self.siem:
                self.siem.log_evento('INFO', 'escaneador', 
                                         f'Escaneo completado: {archivos_procesados} archivos, {amenazas_encontradas} amenazas')
            
        except Exception as e:
            resultado = ResultadoEscaneo(ruta_directorio, False, "", 
                                       f"Error escaneando directorio: {e}")
            resultados.append(resultado)
            
            if self.siem:
                self.siem.log_evento('ERROR', 'escaneador', 
                                         f'Error escaneando directorio {ruta_directorio}: {e}')
        
        return resultados
    
    def generar_reporte_directorio(self, resultados: List[ResultadoEscaneo]) -> Dict[str, Any]:
        """Genera un reporte resumen del escaneo de directorio."""
        total_archivos = len(resultados)
        amenazas_encontradas = len([r for r in resultados if r.es_amenaza])
        archivos_infectados = [r for r in resultados if r.es_amenaza]
        
        return {
            'total_archivos': total_archivos,
            'amenazas_encontradas': amenazas_encontradas,
            'archivos_limpios': total_archivos - amenazas_encontradas,
            'archivos_infectados': [
                {
                    'ruta': r.ruta,
                    'amenazas': [r.tipo_amenaza] if r.tipo_amenaza else [],
                    'detalles': r.detalles
                } for r in archivos_infectados
            ]
        }
    
    def generar_reporte_markdown_directorio(self, reporte_data: Dict[str, Any]) -> str:
        """Genera reporte en formato Markdown."""
        md = "# Reporte de Escaneo de Directorio - Ares Aegis\n\n"
        md += f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        md += "## Resumen del Escaneo\n\n"
        md += f"- **Total de archivos:** {reporte_data['total_archivos']}\n"
        md += f"- **Archivos limpios:** {reporte_data['archivos_limpios']}\n"
        md += f"- **Amenazas encontradas:** {reporte_data['amenazas_encontradas']}\n\n"
        
        if reporte_data['archivos_infectados']:
            md += "## Archivos Infectados\n\n"
            for archivo in reporte_data['archivos_infectados']:
                md += f"### {archivo['ruta']}\n\n"
                if archivo['amenazas']:
                    md += f"- **Amenazas:** {', '.join(archivo['amenazas'])}\n"
                if archivo['detalles']:
                    md += f"- **Detalles:** {archivo['detalles']}\n"
                md += "\n"
        
        return md
    
    def actualizar_firmas(self, nuevas_firmas: List[str]):
        archivo_firmas = Path("configuracion/firmas.txt")
        
        try:
            with open(archivo_firmas, 'a', encoding='utf-8') as archivo:
                archivo.write('\n# Firmas añadidas automáticamente\n')
                for firma in nuevas_firmas:
                    archivo.write(f"{firma}\n")
            
            self.cargar_firmas()
            
            if self.siem:
                self.siem.log_evento('INFO', 'escaneador', 
                                         f'Firmas actualizadas: {len(nuevas_firmas)} nuevas firmas')
            
        except Exception as e:
            if self.siem:
                self.siem.log_evento('ERROR', 'escaneador', 
                                         f'Error actualizando firmas: {e}')
    
    def generar_reporte_markdown(self, resultados: List[ResultadoEscaneo]) -> str:
        reporte = "# Reporte de Escaneo - Ares Aegis\n\n"
        reporte += f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        total_archivos = len(resultados)
        amenazas = [r for r in resultados if r.es_amenaza]
        archivos_limpios = total_archivos - len(amenazas)
        
        reporte += "## Resumen\n\n"
        reporte += f"- **Total de archivos:** {total_archivos}\n"
        reporte += f"- **Archivos limpios:** {archivos_limpios}\n"
        reporte += f"- **Amenazas detectadas:** {len(amenazas)}\n\n"
        
        if amenazas:
            reporte += "## Amenazas Detectadas\n\n"
            for amenaza in amenazas:
                reporte += f"### {amenaza.tipo_amenaza}\n\n"
                reporte += f"- **Archivo:** `{amenaza.ruta}`\n"
                reporte += f"- **Detalles:** {amenaza.detalles}\n"
                reporte += f"- **Hash SHA256:** `{amenaza.hash_sha256}`\n"
                reporte += f"- **Fecha:** {amenaza.fecha_escaneo.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        return reporte
