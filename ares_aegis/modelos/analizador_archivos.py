#!/usr/bin/env python3
"""
Copyright (c) 2025 DogSoulDev (https://github.com/DogSoulDev)
Todos los derechos reservados. Este código es propietario y confidencial.

Analizador de Archivos
"""

import os
import hashlib
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from ..utilidades.ayuda_logging import configurar_logger_modulo
from ..utilidades.validaciones import validar_ruta_archivo


class AnalizadorHashes:
    """El Forjador de Huellas Digitales - Crea sellos únicos para cada pergamino."""
    
    def __init__(self):
        """Inicializa el forjador de huellas digitales celestiales."""
        self.logger = configurar_logger_modulo("analizador_hashes")
        self.algoritmos_soportados = ['md5', 'sha1', 'sha256', 'sha512']
        
        self.logger.info("El forjador de huellas digitales ha despertado en el yunque divino")
    
    def calcular_hash(self, ruta_archivo: str, algoritmo: str = 'sha256') -> Optional[str]:
        """
        Forja la huella digital única de un pergamino usando el fuego sagrado.
        
        Args:
            ruta_archivo: Sendero al pergamino a marcar
            algoritmo: Tipo de fuego sagrado a usar (md5, sha1, sha256, sha512)
            
        Returns:
            Huella digital única o None si falla el ritual
        """
        if algoritmo not in self.algoritmos_soportados:
            self.logger.error(f"El fuego sagrado '{algoritmo}' no es conocido en este templo")
            return None
        
        if not validar_ruta_archivo(ruta_archivo):
            self.logger.error(f"El sendero no conduce a pergamino alguno: {ruta_archivo}")
            return None
        
        try:
            # Invocar el fuego sagrado del algoritmo elegido
            hash_obj = hashlib.new(algoritmo)
            
            with open(ruta_archivo, 'rb') as archivo:
                # Leer el pergamino en fragmentos para no agotar la memoria divina
                for fragmento in iter(lambda: archivo.read(8192), b""):
                    hash_obj.update(fragmento)
            
            huella_digital = hash_obj.hexdigest()
            self.logger.debug(f"Huella digital forjada con {algoritmo}: {huella_digital}")
            
            return huella_digital
        
        except Exception as e:
            self.logger.error(f"Error forjando huella digital: {e}")
            return None
    
    def calcular_multiples_hashes(self, ruta_archivo: str) -> Dict[str, Optional[str]]:
        """
        Forja múltiples huellas digitales usando diferentes fuegos sagrados.
        
        Args:
            ruta_archivo: Sendero al pergamino a marcar
            
        Returns:
            Dict con todas las huellas digitales forjadas
        """
        huellas = {}
        
        for algoritmo in self.algoritmos_soportados:
            huellas[algoritmo] = self.calcular_hash(ruta_archivo, algoritmo)
        
        return huellas
    
    def comparar_hashes(self, hash1: str, hash2: str) -> bool:
        """
        Compara dos huellas digitales para determinar si pertenecen al mismo pergamino.
        
        Args:
            hash1: Primera huella digital
            hash2: Segunda huella digital
            
        Returns:
            True si las huellas son idénticas
        """
        return hash1.lower() == hash2.lower()


class AnalizadorMetadatos:
    """El Lector de Pergaminos Ancestrales - Desvela los secretos ocultos en los archivos."""
    
    def __init__(self):
        """Inicializa el lector de secretos ancestrales."""
        self.logger = configurar_logger_modulo("analizador_metadatos")
        
        self.logger.info("El lector de pergaminos ancestrales ha abierto sus ojos divinos")
    
    def obtener_metadatos_basicos(self, ruta_archivo: str) -> Dict[str, Any]:
        """
        Extrae los secretos básicos del pergamino usando la sabiduría del sistema.
        
        Args:
            ruta_archivo: Sendero al pergamino a examinar
            
        Returns:
            Dict con los metadatos básicos descubiertos
        """
        if not validar_ruta_archivo(ruta_archivo):
            return {
                'valido': False,
                'mensaje': 'El sendero no conduce a pergamino alguno en este reino',
                'ruta': ruta_archivo
            }
        
        try:
            ruta_path = Path(ruta_archivo)
            stats = ruta_path.stat()
            
            # Obtener información temporal
            tiempo_creacion = datetime.fromtimestamp(stats.st_ctime)
            tiempo_modificacion = datetime.fromtimestamp(stats.st_mtime)
            tiempo_acceso = datetime.fromtimestamp(stats.st_atime)
            
            metadatos = {
                'valido': True,
                'ruta_completa': str(ruta_path.absolute()),
                'nombre_archivo': ruta_path.name,
                'extension': ruta_path.suffix.lower(),
                'directorio_padre': str(ruta_path.parent),
                
                # Información del tamaño en el reino físico
                'tamano_bytes': stats.st_size,
                'tamano_legible': self._formatear_tamano(stats.st_size),
                
                # Los sellos temporales del pergamino
                'tiempo_creacion': tiempo_creacion.isoformat(),
                'tiempo_modificacion': tiempo_modificacion.isoformat(),
                'tiempo_ultimo_acceso': tiempo_acceso.isoformat(),
                
                # Los permisos otorgados por Zeus
                'permisos': oct(stats.st_mode)[-3:],
                'permisos_legibles': self._formatear_permisos(stats.st_mode),
                
                # Identificadores del reino del sistema
                'propietario_uid': stats.st_uid,
                'grupo_gid': stats.st_gid,
                'inodo': stats.st_ino,
                
                # El juicio sobre la naturaleza del pergamino
                'es_archivo': ruta_path.is_file(),
                'es_directorio': ruta_path.is_dir(),
                'es_enlace_simbolico': ruta_path.is_symlink(),
                'es_ejecutable': os.access(ruta_archivo, os.X_OK),
                'es_legible': os.access(ruta_archivo, os.R_OK),
                'es_escribible': os.access(ruta_archivo, os.W_OK)
            }
            
            # Agregar el tipo MIME si es posible
            tipo_mime = self._detectar_tipo_mime(ruta_archivo)
            if tipo_mime:
                metadatos['tipo_mime'] = tipo_mime
            
            return metadatos
        
        except Exception as e:
            self.logger.error(f"Error extrayendo metadatos: {e}")
            return {
                'valido': False,
                'mensaje': f'Una tormenta ha impedido leer los secretos del pergamino: {e}',
                'ruta': ruta_archivo
            }
    
    def _formatear_tamano(self, bytes_cantidad: int) -> str:
        """Convierte bytes a una forma legible por mortales."""
        if bytes_cantidad < 1024:
            return f"{bytes_cantidad} bytes"
        elif bytes_cantidad < 1024 * 1024:
            return f"{bytes_cantidad / 1024:.2f} KB"
        elif bytes_cantidad < 1024 * 1024 * 1024:
            return f"{bytes_cantidad / (1024 * 1024):.2f} MB"
        else:
            return f"{bytes_cantidad / (1024 * 1024 * 1024):.2f} GB"
    
    def _formatear_permisos(self, modo: int) -> str:
        """Traduce los permisos del sistema a lenguaje mortal."""
        permisos_str = ""
        
        # Permisos del propietario
        permisos_str += "r" if modo & 0o400 else "-"
        permisos_str += "w" if modo & 0o200 else "-"
        permisos_str += "x" if modo & 0o100 else "-"
        
        # Permisos del grupo
        permisos_str += "r" if modo & 0o040 else "-"
        permisos_str += "w" if modo & 0o020 else "-"
        permisos_str += "x" if modo & 0o010 else "-"
        
        # Permisos de otros
        permisos_str += "r" if modo & 0o004 else "-"
        permisos_str += "w" if modo & 0o002 else "-"
        permisos_str += "x" if modo & 0o001 else "-"
        
        return permisos_str
    
    def _detectar_tipo_mime(self, ruta_archivo: str) -> Optional[str]:
        """Intenta detectar el tipo MIME del pergamino usando la sabiduría del sistema."""
        try:
            # Usar el comando file si está disponible
            import subprocess
            resultado = subprocess.run(
                ['file', '--mime-type', '-b', ruta_archivo],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if resultado.returncode == 0:
                return resultado.stdout.strip()
        except Exception:
            pass
        
        # Método alternativo basado en extensiones
        extensiones_mime = {
            '.txt': 'text/plain',
            '.py': 'text/x-python',
            '.html': 'text/html',
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.json': 'application/json',
            '.pdf': 'application/pdf',
            '.zip': 'application/zip',
            '.tar': 'application/x-tar',
            '.gz': 'application/gzip',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.mp3': 'audio/mpeg',
            '.mp4': 'video/mp4',
            '.exe': 'application/x-executable',
            '.dll': 'application/x-msdownload'
        }
        
        extension = Path(ruta_archivo).suffix.lower()
        return extensiones_mime.get(extension, 'application/octet-stream')
    
    def analizar_cabeceras_archivo(self, ruta_archivo: str, num_bytes: int = 512) -> Dict[str, Any]:
        """
        Examina las primeras runas del pergamino para descubrir su verdadera naturaleza.
        
        Args:
            ruta_archivo: Sendero al pergamino
            num_bytes: Cantidad de runas a examinar
            
        Returns:
            Dict con análisis de las cabeceras
        """
        if not validar_ruta_archivo(ruta_archivo):
            return {
                'valido': False,
                'mensaje': 'El sendero no conduce a pergamino válido'
            }
        
        try:
            with open(ruta_archivo, 'rb') as archivo:
                cabecera = archivo.read(num_bytes)
            
            analisis = {
                'valido': True,
                'tamano_cabecera': len(cabecera),
                'cabecera_hex': cabecera.hex(),
                'cabecera_ascii': self._extraer_ascii_legible(cabecera),
                'firmas_detectadas': []
            }
            
            # Detectar firmas conocidas en las primeras runas
            firmas_magicas = {
                b'\x7fELF': 'Ejecutable ELF (Linux)',
                b'MZ': 'Ejecutable PE (Windows)',
                b'\x89PNG': 'Imagen PNG',
                b'\xff\xd8\xff': 'Imagen JPEG',
                b'GIF8': 'Imagen GIF',
                b'%PDF': 'Documento PDF',
                b'PK\x03\x04': 'Archivo ZIP',
                b'\x1f\x8b': 'Archivo Gzip',
                b'BZh': 'Archivo Bzip2',
                b'\x50\x4b\x03\x04': 'Archivo comprimido ZIP',
                b'\xd0\xcf\x11\xe0': 'Documento Microsoft Office',
                b'#!/': 'Script con shebang'
            }
            
            for firma, descripcion in firmas_magicas.items():
                if cabecera.startswith(firma):
                    analisis['firmas_detectadas'].append({
                        'firma': firma.hex(),
                        'descripcion': descripcion,
                        'posicion': 0
                    })
            
            # Buscar patrones sospechosos
            patrones_sospechosos = [
                (b'eval(', 'Posible código malicioso con eval'),
                (b'exec(', 'Posible código malicioso con exec'),
                (b'base64', 'Posible contenido codificado en base64'),
                (b'system(', 'Llamada al sistema detectada'),
                (b'shell_exec', 'Ejecución de shell detectada')
            ]
            
            patrones_encontrados = []
            for patron, descripcion in patrones_sospechosos:
                if patron in cabecera.lower():
                    patrones_encontrados.append({
                        'patron': patron.decode('ascii', errors='ignore'),
                        'descripcion': descripcion
                    })
            
            if patrones_encontrados:
                analisis['patrones_sospechosos'] = patrones_encontrados
            
            return analisis
        
        except Exception as e:
            self.logger.error(f"Error analizando cabeceras: {e}")
            return {
                'valido': False,
                'mensaje': f'Una tormenta ha impedido leer las primeras runas: {e}'
            }
    
    def _extraer_ascii_legible(self, datos: bytes) -> str:
        """Extrae caracteres ASCII legibles de los datos binarios."""
        ascii_chars = []
        for byte in datos:
            if 32 <= byte <= 126:  # Caracteres ASCII imprimibles
                ascii_chars.append(chr(byte))
            else:
                ascii_chars.append('.')
        return ''.join(ascii_chars)


class AnalizadorArchivos:
    """El Gran Examinador - Combina todos los análisis para revelar la verdad completa."""
    
    def __init__(self, siem=None):
        """Inicializa el gran examinador de pergaminos."""
        self.logger = configurar_logger_modulo("analizador_archivos")
        self.siem = siem
        self.analizador_hashes = AnalizadorHashes()
        self.analizador_metadatos = AnalizadorMetadatos()
        
        self.logger.info("El gran examinador de pergaminos ha abierto su ojo omnisciente")
    
    def analisis_completo(self, ruta_archivo: str) -> Dict[str, Any]:
        """
        Realiza un análisis completo y exhaustivo del pergamino.
        
        Args:
            ruta_archivo: Sendero al pergamino a examinar
            
        Returns:
            Dict con todos los análisis combinados
        """
        self.logger.info(f"Iniciando análisis completo del pergamino: {ruta_archivo}")
        
        inicio_tiempo = time.time()
        
        resultado: Dict[str, Any] = {
            'ruta_archivo': ruta_archivo,
            'timestamp_analisis': datetime.now().isoformat(),
            'estado_analisis': 'iniciado'
        }
        
        try:
            # Análisis de metadatos básicos
            metadatos = self.analizador_metadatos.obtener_metadatos_basicos(ruta_archivo)
            resultado['metadatos'] = metadatos
            
            if not metadatos.get('valido', False):
                resultado['estado_analisis'] = 'fallido'
                resultado['mensaje'] = 'El pergamino no pudo ser examinado por el ojo divino'
                return resultado
            
            # Análisis de huellas digitales
            hashes = self.analizador_hashes.calcular_multiples_hashes(ruta_archivo)
            resultado['hashes'] = hashes
            
            # Análisis de cabeceras
            cabeceras = self.analizador_metadatos.analizar_cabeceras_archivo(ruta_archivo)
            resultado['analisis_cabeceras'] = cabeceras
            
            # Evaluación de riesgo basada en los hallazgos
            evaluacion_riesgo = self._evaluar_riesgo(metadatos, cabeceras)
            resultado['evaluacion_riesgo'] = evaluacion_riesgo
            
            # Tiempo total del análisis
            tiempo_total = time.time() - inicio_tiempo
            resultado['tiempo_analisis_segundos'] = round(tiempo_total, 3)
            
            resultado['estado_analisis'] = 'completado'
            resultado['mensaje'] = 'El ojo omnisciente ha revelado todos los secretos del pergamino'
            
            self.logger.info(f"Análisis completado en {tiempo_total:.3f} segundos")
            
        except Exception as e:
            resultado['estado_analisis'] = 'error'
            resultado['mensaje'] = f'Una tormenta divina ha interrumpido el examen: {e}'
            self.logger.error(f"Error en análisis completo: {e}")
        
        return resultado
    
    def _evaluar_riesgo(self, metadatos: Dict[str, Any], cabeceras: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evalúa el nivel de riesgo del pergamino basándose en los hallazgos.
        
        Args:
            metadatos: Metadatos del archivo
            cabeceras: Análisis de cabeceras
            
        Returns:
            Dict con la evaluación de riesgo
        """
        puntuacion_riesgo = 0
        factores_riesgo = []
        nivel_riesgo = "BAJO"
        
        # Evaluar el tamaño del pergamino
        tamano = metadatos.get('tamano_bytes', 0)
        if tamano > 100 * 1024 * 1024:  # Más de 100MB
            puntuacion_riesgo += 2
            factores_riesgo.append("Pergamino de gran tamaño - posible contenido oculto")
        
        # Evaluar permisos sospechosos
        if metadatos.get('es_ejecutable', False):
            puntuacion_riesgo += 3
            factores_riesgo.append("Pergamino con poderes ejecutables")
        
        # Evaluar extensión vs tipo real
        extension = metadatos.get('extension', '').lower()
        firmas = cabeceras.get('firmas_detectadas', [])
        
        if extension in ['.exe', '.bat', '.cmd', '.scr', '.com']:
            puntuacion_riesgo += 4
            factores_riesgo.append("Extensión típica de archivos ejecutables peligrosos")
        
        # Evaluar patrones sospechosos en cabeceras
        patrones_sospechosos = cabeceras.get('patrones_sospechosos', [])
        if patrones_sospechosos:
            puntuacion_riesgo += len(patrones_sospechosos) * 2
            for patron in patrones_sospechosos:
                factores_riesgo.append(f"Patrón sospechoso: {patron['descripcion']}")
        
        # Evaluar ubicación del archivo
        ruta = metadatos.get('ruta_completa', '')
        ubicaciones_sospechosas = ['/tmp/', '/var/tmp/', '/dev/shm/', 'Downloads']
        
        for ubicacion in ubicaciones_sospechosas:
            if ubicacion in ruta:
                puntuacion_riesgo += 2
                factores_riesgo.append(f"Ubicado en directorio temporal/sospechoso: {ubicacion}")
                break
        
        # Determinar nivel de riesgo final
        if puntuacion_riesgo >= 8:
            nivel_riesgo = "CRITICO"
        elif puntuacion_riesgo >= 5:
            nivel_riesgo = "ALTO"
        elif puntuacion_riesgo >= 3:
            nivel_riesgo = "MEDIO"
        
        # Mensaje descriptivo según el nivel
        mensajes_riesgo = {
            "BAJO": "El pergamino parece inofensivo bajo el ojo de Ares",
            "MEDIO": "El pergamino despierta cierta desconfianza en la mirada divina",
            "ALTO": "El pergamino porta señales inquietantes que alertan al Égida",
            "CRITICO": "¡El pergamino irradia aura malévola! ¡La Égida clama venganza!"
        }
        
        return {
            'nivel': nivel_riesgo,
            'puntuacion': puntuacion_riesgo,
            'factores_riesgo': factores_riesgo,
            'mensaje': mensajes_riesgo[nivel_riesgo],
            'recomendacion': self._generar_recomendacion(nivel_riesgo)
        }
    
    def _generar_recomendacion(self, nivel_riesgo: str) -> str:
        """Genera una recomendación basada en el nivel de riesgo."""
        recomendaciones = {
            "BAJO": "El pergamino puede ser usado con confianza bajo la protección del Égida",
            "MEDIO": "Examina con cautela - que la sabiduría de Atenea guíe tu decisión",
            "ALTO": "Procede con extrema precaución - mantén el Égida alzado",
            "CRITICO": "¡Destierro inmediato a la cripta de Érebo! No permitas que corrompa tu reino"
        }
        
        return recomendaciones.get(nivel_riesgo, "La sabiduría de los dioses es incierta en este caso")
    
    def generar_reporte_markdown(self, analisis: Dict[str, Any]) -> str:
        """
        Genera un reporte detallado en formato Markdown del análisis.
        
        Args:
            analisis: Resultado del análisis completo
            
        Returns:
            Reporte en formato Markdown
        """
        md = f"# 📜 Reporte de Análisis del Pergamino Sagrado\n\n"
        md += f"**Archivo Analizado:** `{analisis['ruta_archivo']}`\n"
        md += f"**Fecha del Examen:** {analisis['timestamp_analisis']}\n"
        md += f"**Estado del Análisis:** {analisis['estado_analisis']}\n\n"
        
        if analisis['estado_analisis'] != 'completado':
            md += f"**Mensaje:** {analisis.get('mensaje', 'Examen incompleto')}\n"
            return md
        
        # Metadatos
        metadatos = analisis.get('metadatos', {})
        md += "## 📊 Secretos Revelados (Metadatos)\n\n"
        md += f"- **Nombre:** {metadatos.get('nombre_archivo', 'Desconocido')}\n"
        md += f"- **Tamaño:** {metadatos.get('tamano_legible', 'Desconocido')}\n"
        md += f"- **Tipo MIME:** {metadatos.get('tipo_mime', 'Desconocido')}\n"
        md += f"- **Permisos:** {metadatos.get('permisos_legibles', 'Desconocidos')}\n"
        md += f"- **Última Modificación:** {metadatos.get('tiempo_modificacion', 'Desconocida')}\n\n"
        
        # Huellas digitales
        hashes = analisis.get('hashes', {})
        md += "## 🔐 Huellas Digitales Forjadas\n\n"
        for algoritmo, hash_valor in hashes.items():
            if hash_valor:
                md += f"- **{algoritmo.upper()}:** `{hash_valor}`\n"
        md += "\n"
        
        # Evaluación de riesgo
        evaluacion = analisis.get('evaluacion_riesgo', {})
        md += "## ⚠️ Juicio del Égida\n\n"
        md += f"**Nivel de Riesgo:** {evaluacion.get('nivel', 'DESCONOCIDO')}\n"
        md += f"**Puntuación:** {evaluacion.get('puntuacion', 0)}\n"
        md += f"**Mensaje:** {evaluacion.get('mensaje', 'Sin juicio')}\n"
        md += f"**Recomendación:** {evaluacion.get('recomendacion', 'Sin recomendación')}\n\n"
        
        factores = evaluacion.get('factores_riesgo', [])
        if factores:
            md += "**Factores de Riesgo Detectados:**\n"
            for factor in factores:
                md += f"- {factor}\n"
            md += "\n"
        
        # Análisis de cabeceras
        cabeceras = analisis.get('analisis_cabeceras', {})
        if cabeceras.get('valido', False):
            md += "## 🔍 Análisis de las Primeras Runas\n\n"
            
            firmas = cabeceras.get('firmas_detectadas', [])
            if firmas:
                md += "**Firmas Mágicas Detectadas:**\n"
                for firma in firmas:
                    md += f"- {firma['descripcion']} (Firma: `{firma['firma']}`)\n"
                md += "\n"
            
            patrones = cabeceras.get('patrones_sospechosos', [])
            if patrones:
                md += "**Patrones Sospechosos Encontrados:**\n"
                for patron in patrones:
                    md += f"- ⚠️ {patron['descripcion']}\n"
                md += "\n"
        
        md += f"---\n\n"
        md += f"*Análisis completado por el Égida de Ares en {analisis.get('tiempo_analisis_segundos', 0)} segundos*\n"
        
        return md
