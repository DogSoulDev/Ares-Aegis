#!/usr/bin/env python3
"""
Descontaminación Inteligente - Ares Aegis
Módulo para limpieza automática y desinfección de archivos

Este módulo implementa técnicas de descontaminación automática,
limpieza de archivos infectados y restauración de datos cuando es posible.

Autor: DogSoulDev
Versión: 2.0.0 - "Los Purificadores de Asclepio"
"""

import os
import re
import shutil
import hashlib
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, NamedTuple, Set, Tuple
from dataclasses import dataclass
from ..utilidades.ayuda_logging import configurar_logger_modulo


@dataclass
class ArchivoContaminado:
    """Representa un archivo contaminado detectado."""
    ruta_original: str
    tipo_contaminacion: str
    nivel_severidad: str
    hash_original: str
    tamaño_original: int
    timestamp_deteccion: datetime
    metadatos: Dict[str, Any]


@dataclass
class ResultadoDescontaminacion:
    """Resultado de un proceso de descontaminación."""
    archivo_original: str
    archivo_limpio: Optional[str]
    exito: bool
    tipo_limpieza: str
    detalles_proceso: str
    tiempo_proceso: float
    hash_original: str
    hash_limpio: Optional[str]
    cambios_realizados: List[str]
    metadatos: Dict[str, Any]


@dataclass
class ReglaLimpieza:
    """Regla de limpieza para un tipo específico de contaminación."""
    nombre: str
    descripcion: str
    patron_deteccion: str
    patron_reemplazo: str
    tipo_archivo: List[str]
    es_regex: bool
    nivel_agresividad: str  # conservador, moderado, agresivo
    requiere_confirmacion: bool


class DescontaminacionInteligente:
    """Sistema principal de descontaminación automática."""
    
    def __init__(self, siem=None, cuarentena=None):
        """
        Inicializa el sistema de descontaminación.
        
        Args:
            siem: Instancia del SIEM para registro de eventos
            cuarentena: Instancia del sistema de cuarentena
        """
        self.logger = configurar_logger_modulo("descontaminacion_inteligente")
        self.siem = siem
        self.cuarentena = cuarentena
        
        # Configuración
        self.directorio_trabajo = Path("/tmp/ares_aegis_limpieza")
        self.directorio_backups = Path("/home/dogsoul/Ares-Aegis/cuarentena/backups")
        self.max_tamaño_archivo = 50 * 1024 * 1024  # 50MB
        
        # Crear directorios necesarios
        self.directorio_trabajo.mkdir(exist_ok=True)
        self.directorio_backups.mkdir(parents=True, exist_ok=True)
        
        # Estado del sistema
        self.archivos_procesados: List[ArchivoContaminado] = []
        self.resultados_limpieza: List[ResultadoDescontaminacion] = []
        self.estadisticas = {
            'archivos_analizados': 0,
            'archivos_limpiados': 0,
            'limpieza_exitosa': 0,
            'limpieza_fallida': 0,
            'bytes_limpiados': 0
        }
        
        # Reglas de limpieza predefinidas
        self.reglas_limpieza = self._inicializar_reglas_limpieza()
        
        # Tipos de archivo soportados para limpieza
        self.tipos_soportados = {
            '.txt', '.log', '.conf', '.cfg', '.ini', '.xml', '.html', '.htm',
            '.css', '.js', '.php', '.py', '.pl', '.sh', '.bat', '.cmd',
            '.sql', '.csv', '.json', '.yaml', '.yml', '.md'
        }
        
        # Extensiones de archivo peligrosas que requieren cuidado especial
        self.extensiones_peligrosas = {
            '.exe', '.dll', '.so', '.dylib', '.com', '.scr', '.pif',
            '.jar', '.class', '.dex', '.apk', '.ipa'
        }
        
        self.logger.info("Los Purificadores de Asclepio despiertan para sanar los archivos corrompidos")
    
    def _inicializar_reglas_limpieza(self) -> List[ReglaLimpieza]:
        """Inicializa las reglas de limpieza predefinidas."""
        reglas = [
            # Limpieza de código PHP malicioso
            ReglaLimpieza(
                nombre="PHP - eval() malicioso",
                descripcion="Elimina llamadas eval() sospechosas en PHP",
                patron_deteccion=r'eval\s*\(\s*base64_decode\s*\([^)]+\)\s*\)',
                patron_reemplazo="// [REMOVED MALICIOUS CODE]",
                tipo_archivo=['.php'],
                es_regex=True,
                nivel_agresividad="agresivo",
                requiere_confirmacion=False
            ),
            
            ReglaLimpieza(
                nombre="PHP - shell_exec malicioso",
                descripcion="Elimina llamadas shell_exec sospechosas",
                patron_deteccion=r'shell_exec\s*\([^)]*(?:wget|curl|chmod|rm)[^)]*\)',
                patron_reemplazo="// [REMOVED SHELL EXECUTION]",
                tipo_archivo=['.php'],
                es_regex=True,
                nivel_agresividad="agresivo",
                requiere_confirmacion=False
            ),
            
            # Limpieza de JavaScript malicioso
            ReglaLimpieza(
                nombre="JavaScript - eval() ofuscado",
                descripcion="Elimina código JavaScript eval() ofuscado",
                patron_deteccion=r'eval\s*\(\s*unescape\s*\([^)]+\)\s*\)',
                patron_reemplazo="// [REMOVED OBFUSCATED CODE]",
                tipo_archivo=['.js', '.html', '.htm'],
                es_regex=True,
                nivel_agresividad="moderado",
                requiere_confirmacion=False
            ),
            
            # Limpieza de scripts de shell maliciosos
            ReglaLimpieza(
                nombre="Shell - descarga y ejecución",
                descripcion="Elimina comandos de descarga y ejecución automática",
                patron_deteccion=r'(wget|curl)\s+[^\s]+\s*\|\s*(sh|bash|python)',
                patron_reemplazo="# [REMOVED DOWNLOAD AND EXECUTE]",
                tipo_archivo=['.sh', '.bash'],
                es_regex=True,
                nivel_agresividad="agresivo",
                requiere_confirmacion=False
            ),
            
            # Limpieza de comandos SQL maliciosos
            ReglaLimpieza(
                nombre="SQL - inyección UNION",
                descripcion="Elimina patrones de inyección SQL UNION",
                patron_deteccion=r'UNION\s+SELECT.*--',
                patron_reemplazo="-- [REMOVED SQL INJECTION]",
                tipo_archivo=['.sql', '.php', '.asp'],
                es_regex=True,
                nivel_agresividad="moderado",
                requiere_confirmacion=True
            ),
            
            # Limpieza de URLs maliciosas
            ReglaLimpieza(
                nombre="URLs sospechosas",
                descripcion="Elimina URLs con dominios sospechosos",
                patron_deteccion=r'https?://[^/]*\.(?:tk|ml|ga|cf)/[^\s"\'<>]*',
                patron_reemplazo="[REMOVED SUSPICIOUS URL]",
                tipo_archivo=['.html', '.php', '.js', '.txt'],
                es_regex=True,
                nivel_agresividad="conservador",
                requiere_confirmacion=True
            ),
            
            # Limpieza de código base64 sospechoso
            ReglaLimpieza(
                nombre="Base64 sospechoso",
                descripcion="Elimina cadenas base64 largas y sospechosas",
                patron_deteccion=r'[A-Za-z0-9+/]{200,}={0,2}',
                patron_reemplazo="[REMOVED SUSPICIOUS BASE64]",
                tipo_archivo=['.php', '.html', '.js'],
                es_regex=True,
                nivel_agresividad="conservador",
                requiere_confirmacion=True
            ),
            
            # Limpieza de iframes maliciosos
            ReglaLimpieza(
                nombre="iframes maliciosos",
                descripcion="Elimina iframes con características sospechosas",
                patron_deteccion=r'<iframe[^>]*(?:width=["\']?0["\']?|height=["\']?0["\']?|display:\s*none)[^>]*>.*?</iframe>',
                patron_reemplazo="<!-- [REMOVED MALICIOUS IFRAME] -->",
                tipo_archivo=['.html', '.htm', '.php'],
                es_regex=True,
                nivel_agresividad="moderado",
                requiere_confirmacion=False
            ),
            
            # Limpieza de scripts de minería
            ReglaLimpieza(
                nombre="Scripts de minería",
                descripcion="Elimina referencias a scripts de minería de criptomonedas",
                patron_deteccion=r'(coinhive|crypto-loot|jsecoin|mineralt)\.com[^\s"\'<>]*',
                patron_reemplazo="[REMOVED MINING SCRIPT]",
                tipo_archivo=['.html', '.js', '.php'],
                es_regex=True,
                nivel_agresividad="agresivo",
                requiere_confirmacion=False
            ),
            
            # Limpieza de backdoors comunes
            ReglaLimpieza(
                nombre="Backdoors PHP",
                descripcion="Elimina backdoors PHP comunes",
                patron_deteccion=r'\$_(?:GET|POST|REQUEST)\s*\[\s*["\'][^"\']*["\']?\s*\]\s*\(\s*\$_(?:GET|POST|REQUEST)',
                patron_reemplazo="// [REMOVED PHP BACKDOOR]",
                tipo_archivo=['.php'],
                es_regex=True,
                nivel_agresividad="agresivo",
                requiere_confirmacion=False
            )
        ]
        
        return reglas
    
    def analizar_archivo(self, ruta_archivo: str) -> Optional[ArchivoContaminado]:
        """
        Analiza un archivo en busca de contaminación.
        
        Args:
            ruta_archivo: Ruta del archivo a analizar
            
        Returns:
            Información de contaminación si se detecta, None si está limpio
        """
        try:
            ruta = Path(ruta_archivo)
            
            if not ruta.exists() or not ruta.is_file():
                self.logger.error(f"Archivo no válido: {ruta_archivo}")
                return None
            
            # Verificar tamaño
            tamaño = ruta.stat().st_size
            if tamaño > self.max_tamaño_archivo:
                self.logger.warning(f"Archivo demasiado grande para análisis: {tamaño} bytes")
                return None
            
            # Verificar tipo de archivo
            extension = ruta.suffix.lower()
            if extension in self.extensiones_peligrosas:
                self.logger.warning(f"Tipo de archivo peligroso detectado: {extension}")
                return ArchivoContaminado(
                    ruta_original=str(ruta),
                    tipo_contaminacion="archivo_ejecutable_sospechoso",
                    nivel_severidad="ALTO",
                    hash_original=self._calcular_hash(str(ruta)),
                    tamaño_original=tamaño,
                    timestamp_deteccion=datetime.now(),
                    metadatos={"razon": "Tipo de archivo ejecutable", "extension": extension}
                )
            
            # Analizar contenido si es un tipo soportado
            if extension not in self.tipos_soportados:
                return None
            
            # Leer y analizar contenido
            contaminacion_detectada = self._detectar_contaminacion(str(ruta))
            
            if contaminacion_detectada:
                return ArchivoContaminado(
                    ruta_original=str(ruta),
                    tipo_contaminacion=contaminacion_detectada['tipo'],
                    nivel_severidad=contaminacion_detectada['severidad'],
                    hash_original=self._calcular_hash(str(ruta)),
                    tamaño_original=tamaño,
                    timestamp_deteccion=datetime.now(),
                    metadatos=contaminacion_detectada['metadatos']
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error analizando archivo {ruta_archivo}: {e}")
            return None
    
    def _detectar_contaminacion(self, ruta_archivo: str) -> Optional[Dict[str, Any]]:
        """Detecta patrones de contaminación en un archivo."""
        try:
            with open(ruta_archivo, 'r', encoding='utf-8', errors='ignore') as archivo:
                contenido = archivo.read()
            
            patrones_encontrados = []
            nivel_severidad = "BAJO"
            
            # Aplicar reglas de detección
            for regla in self.reglas_limpieza:
                extension = Path(ruta_archivo).suffix.lower()
                if extension not in regla.tipo_archivo:
                    continue
                
                if regla.es_regex:
                    matches = re.findall(regla.patron_deteccion, contenido, re.IGNORECASE | re.MULTILINE)
                else:
                    matches = [m for m in [regla.patron_deteccion] if regla.patron_deteccion.lower() in contenido.lower()]
                
                if matches:
                    patrones_encontrados.append({
                        'regla': regla.nombre,
                        'matches': len(matches),
                        'agresividad': regla.nivel_agresividad
                    })
                    
                    # Determinar severidad basada en la agresividad de las reglas
                    if regla.nivel_agresividad == "agresivo":
                        nivel_severidad = "ALTO"
                    elif regla.nivel_agresividad == "moderado" and nivel_severidad == "BAJO":
                        nivel_severidad = "MEDIO"
            
            if patrones_encontrados:
                return {
                    'tipo': 'codigo_malicioso',
                    'severidad': nivel_severidad,
                    'metadatos': {
                        'patrones_detectados': patrones_encontrados,
                        'total_matches': sum(p['matches'] for p in patrones_encontrados)
                    }
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error detectando contaminación: {e}")
            return None
    
    def limpiar_archivo(self, archivo_contaminado: ArchivoContaminado, 
                       crear_backup: bool = True) -> ResultadoDescontaminacion:
        """
        Limpia un archivo contaminado.
        
        Args:
            archivo_contaminado: Información del archivo contaminado
            crear_backup: Si crear backup antes de limpiar
            
        Returns:
            Resultado del proceso de limpieza
        """
        inicio_tiempo = datetime.now()
        
        try:
            ruta_original = Path(archivo_contaminado.ruta_original)
            
            # Crear backup si se solicita
            ruta_backup = None
            if crear_backup:
                ruta_backup = self._crear_backup(str(ruta_original))
            
            # Crear archivo de trabajo temporal
            with tempfile.NamedTemporaryFile(mode='w+', suffix=ruta_original.suffix, 
                                           dir=self.directorio_trabajo, delete=False) as temp_file:
                ruta_temporal = temp_file.name
            
            # Copiar archivo original al temporal
            shutil.copy2(str(ruta_original), ruta_temporal)
            
            # Aplicar limpieza
            cambios_realizados = []
            contenido_limpio = self._aplicar_limpieza(ruta_temporal, cambios_realizados)
            
            if contenido_limpio is None:
                # Error en la limpieza
                os.unlink(ruta_temporal)
                return self._crear_resultado_fallido(archivo_contaminado, inicio_tiempo, 
                                                   "Error aplicando reglas de limpieza")
            
            # Escribir contenido limpio
            with open(ruta_temporal, 'w', encoding='utf-8') as archivo:
                archivo.write(contenido_limpio)
            
            # Verificar que la limpieza fue exitosa
            if self._verificar_limpieza(ruta_temporal):
                # Reemplazar archivo original
                shutil.move(ruta_temporal, str(ruta_original))
                
                # Calcular tiempo de proceso
                tiempo_proceso = (datetime.now() - inicio_tiempo).total_seconds()
                
                resultado = ResultadoDescontaminacion(
                    archivo_original=str(ruta_original),
                    archivo_limpio=str(ruta_original),
                    exito=True,
                    tipo_limpieza="automatica",
                    detalles_proceso=f"Limpieza exitosa: {len(cambios_realizados)} cambios",
                    tiempo_proceso=tiempo_proceso,
                    hash_original=archivo_contaminado.hash_original,
                    hash_limpio=self._calcular_hash(str(ruta_original)),
                    cambios_realizados=cambios_realizados,
                    metadatos={
                        'backup_creado': ruta_backup is not None,
                        'backup_ruta': str(ruta_backup) if ruta_backup else None,
                        'reglas_aplicadas': len(cambios_realizados)
                    }
                )
                
                # Actualizar estadísticas
                self.estadisticas['archivos_limpiados'] += 1
                self.estadisticas['limpieza_exitosa'] += 1
                self.estadisticas['bytes_limpiados'] += archivo_contaminado.tamaño_original
                
                # Registrar en SIEM
                if self.siem:
                    from .siem import TipoEvento
                    self.siem.registrar_evento(
                        TipoEvento.ARCHIVO_RESTAURADO,
                        f"Los Purificadores han sanado el archivo: {ruta_original.name}",
                        {
                            "archivo": str(ruta_original),
                            "cambios_realizados": len(cambios_realizados),
                            "tiempo_proceso": tiempo_proceso,
                            "hash_original": archivo_contaminado.hash_original,
                            "hash_limpio": resultado.hash_limpio
                        },
                        "MEDIO"
                    )
                
                self.logger.info(f"Archivo limpiado exitosamente: {ruta_original.name}")
                return resultado
            
            else:
                # Limpieza no verificada
                os.unlink(ruta_temporal)
                return self._crear_resultado_fallido(archivo_contaminado, inicio_tiempo,
                                                   "Verificación de limpieza falló")
        
        except Exception as e:
            self.logger.error(f"Error limpiando archivo: {e}")
            return self._crear_resultado_fallido(archivo_contaminado, inicio_tiempo, str(e))
    
    def _crear_backup(self, ruta_archivo: str) -> Optional[str]:
        """Crea un backup del archivo original."""
        try:
            ruta_original = Path(ruta_archivo)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_backup = f"{ruta_original.stem}_{timestamp}_backup{ruta_original.suffix}"
            ruta_backup = self.directorio_backups / nombre_backup
            
            shutil.copy2(str(ruta_original), str(ruta_backup))
            self.logger.info(f"Backup creado: {ruta_backup}")
            
            return str(ruta_backup)
            
        except Exception as e:
            self.logger.error(f"Error creando backup: {e}")
            return None
    
    def _aplicar_limpieza(self, ruta_temporal: str, cambios_realizados: List[str]) -> Optional[str]:
        """Aplica las reglas de limpieza al archivo temporal."""
        try:
            with open(ruta_temporal, 'r', encoding='utf-8', errors='ignore') as archivo:
                contenido = archivo.read()
            
            contenido_original = contenido
            extension = Path(ruta_temporal).suffix.lower()
            
            # Aplicar reglas de limpieza
            for regla in self.reglas_limpieza:
                if extension not in regla.tipo_archivo:
                    continue
                
                if regla.es_regex:
                    # Contar coincidencias antes
                    matches_antes = len(re.findall(regla.patron_deteccion, contenido, re.IGNORECASE | re.MULTILINE))
                    
                    if matches_antes > 0:
                        # Aplicar reemplazo
                        contenido_nuevo = re.sub(regla.patron_deteccion, regla.patron_reemplazo, 
                                               contenido, flags=re.IGNORECASE | re.MULTILINE)
                        
                        # Contar coincidencias después
                        matches_despues = len(re.findall(regla.patron_deteccion, contenido_nuevo, re.IGNORECASE | re.MULTILINE))
                        
                        if matches_despues < matches_antes:
                            contenido = contenido_nuevo
                            cambios_realizados.append(f"{regla.nombre}: {matches_antes - matches_despues} instancias removidas")
                
                else:
                    # Búsqueda literal
                    if regla.patron_deteccion.lower() in contenido.lower():
                        contenido_nuevo = contenido.replace(regla.patron_deteccion, regla.patron_reemplazo)
                        if contenido_nuevo != contenido:
                            contenido = contenido_nuevo
                            cambios_realizados.append(f"{regla.nombre}: patrón literal removido")
            
            # Verificar que hubo cambios
            if contenido != contenido_original:
                return contenido
            else:
                return contenido_original  # Sin cambios necesarios
                
        except Exception as e:
            self.logger.error(f"Error aplicando limpieza: {e}")
            return None
    
    def _verificar_limpieza(self, ruta_archivo: str) -> bool:
        """Verifica que la limpieza fue exitosa re-analizando el archivo."""
        try:
            contaminacion = self._detectar_contaminacion(ruta_archivo)
            return contaminacion is None
            
        except Exception as e:
            self.logger.error(f"Error verificando limpieza: {e}")
            return False
    
    def _calcular_hash(self, ruta_archivo: str) -> str:
        """Calcula el hash SHA256 de un archivo."""
        try:
            hash_sha256 = hashlib.sha256()
            with open(ruta_archivo, 'rb') as archivo:
                for chunk in iter(lambda: archivo.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
            
        except Exception as e:
            self.logger.error(f"Error calculando hash: {e}")
            return ""
    
    def _crear_resultado_fallido(self, archivo_contaminado: ArchivoContaminado, 
                               inicio_tiempo: datetime, razon: str) -> ResultadoDescontaminacion:
        """Crea un resultado de limpieza fallida."""
        tiempo_proceso = (datetime.now() - inicio_tiempo).total_seconds()
        
        self.estadisticas['limpieza_fallida'] += 1
        
        return ResultadoDescontaminacion(
            archivo_original=archivo_contaminado.ruta_original,
            archivo_limpio=None,
            exito=False,
            tipo_limpieza="fallida",
            detalles_proceso=f"Fallo en limpieza: {razon}",
            tiempo_proceso=tiempo_proceso,
            hash_original=archivo_contaminado.hash_original,
            hash_limpio=None,
            cambios_realizados=[],
            metadatos={"razon_fallo": razon}
        )
    
    def limpiar_directorio(self, ruta_directorio: str, recursivo: bool = True) -> List[ResultadoDescontaminacion]:
        """
        Limpia todos los archivos contaminados en un directorio.
        
        Args:
            ruta_directorio: Ruta del directorio a limpiar
            recursivo: Si procesar subdirectorios
            
        Returns:
            Lista de resultados de limpieza
        """
        resultados = []
        
        try:
            directorio = Path(ruta_directorio)
            
            if not directorio.exists() or not directorio.is_dir():
                self.logger.error(f"Directorio no válido: {ruta_directorio}")
                return resultados
            
            # Obtener archivos a procesar
            if recursivo:
                archivos = list(directorio.rglob('*'))
            else:
                archivos = list(directorio.iterdir())
            
            archivos_procesables = [f for f in archivos if f.is_file() and f.suffix.lower() in self.tipos_soportados]
            
            self.logger.info(f"Los Purificadores inician limpieza de {len(archivos_procesables)} archivos")
            
            for archivo in archivos_procesables:
                try:
                    # Analizar archivo
                    contaminacion = self.analizar_archivo(str(archivo))
                    self.estadisticas['archivos_analizados'] += 1
                    
                    if contaminacion:
                        # Limpiar archivo contaminado
                        resultado = self.limpiar_archivo(contaminacion)
                        resultados.append(resultado)
                        self.resultados_limpieza.append(resultado)
                        
                        if resultado.exito:
                            self.logger.info(f"Archivo sanado: {archivo.name}")
                        else:
                            self.logger.warning(f"Fallo limpiando: {archivo.name}")
                    
                except Exception as e:
                    self.logger.error(f"Error procesando {archivo}: {e}")
            
            # Registrar resumen en SIEM
            if self.siem and resultados:
                from .siem import TipoEvento
                exitosos = sum(1 for r in resultados if r.exito)
                self.siem.registrar_evento(
                    TipoEvento.INFORMACION,
                    f"Los Purificadores completan limpieza: {exitosos}/{len(resultados)} archivos sanados",
                    {
                        "directorio": str(directorio),
                        "archivos_procesados": len(archivos_procesables),
                        "archivos_contaminados": len(resultados),
                        "limpieza_exitosa": exitosos
                    },
                    "MEDIO" if exitosos > 0 else "BAJO"
                )
            
            self.logger.info(f"Limpieza de directorio completada: {len(resultados)} archivos procesados")
            
        except Exception as e:
            self.logger.error(f"Error limpiando directorio: {e}")
        
        return resultados
    
    def restaurar_desde_backup(self, ruta_backup: str, ruta_destino: str) -> bool:
        """
        Restaura un archivo desde backup.
        
        Args:
            ruta_backup: Ruta del archivo de backup
            ruta_destino: Ruta donde restaurar el archivo
            
        Returns:
            True si la restauración fue exitosa
        """
        try:
            backup = Path(ruta_backup)
            destino = Path(ruta_destino)
            
            if not backup.exists():
                self.logger.error(f"Backup no encontrado: {ruta_backup}")
                return False
            
            # Crear backup del archivo actual si existe
            if destino.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_actual = destino.parent / f"{destino.stem}_{timestamp}_pre_restore{destino.suffix}"
                shutil.copy2(str(destino), str(backup_actual))
                self.logger.info(f"Backup del archivo actual creado: {backup_actual}")
            
            # Restaurar desde backup
            shutil.copy2(str(backup), str(destino))
            
            # Registrar en SIEM
            if self.siem:
                from .siem import TipoEvento
                self.siem.registrar_evento(
                    TipoEvento.ARCHIVO_RESTAURADO,
                    f"Los Purificadores han restaurado desde backup: {destino.name}",
                    {
                        "archivo_destino": str(destino),
                        "archivo_backup": str(backup),
                        "timestamp_restauracion": datetime.now().isoformat()
                    },
                    "MEDIO"
                )
            
            self.logger.info(f"Archivo restaurado exitosamente desde backup: {destino.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error restaurando desde backup: {e}")
            return False
    
    def agregar_regla_personalizada(self, regla: ReglaLimpieza) -> bool:
        """
        Agrega una regla de limpieza personalizada.
        
        Args:
            regla: Nueva regla de limpieza
            
        Returns:
            True si se agregó correctamente
        """
        try:
            # Validar regla
            if regla.es_regex:
                re.compile(regla.patron_deteccion)  # Verificar que es regex válido
            
            self.reglas_limpieza.append(regla)
            self.logger.info(f"Regla personalizada agregada: {regla.nombre}")
            return True
            
        except re.error as e:
            self.logger.error(f"Regex inválido en regla {regla.nombre}: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error agregando regla personalizada: {e}")
            return False
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas del sistema de descontaminación."""
        return {
            'archivos_analizados': self.estadisticas['archivos_analizados'],
            'archivos_limpiados': self.estadisticas['archivos_limpiados'],
            'limpieza_exitosa': self.estadisticas['limpieza_exitosa'],
            'limpieza_fallida': self.estadisticas['limpieza_fallida'],
            'bytes_limpiados': self.estadisticas['bytes_limpiados'],
            'reglas_activas': len(self.reglas_limpieza),
            'tipos_soportados': len(self.tipos_soportados),
            'directorio_trabajo': str(self.directorio_trabajo),
            'directorio_backups': str(self.directorio_backups),
            'tasa_exito': (self.estadisticas['limpieza_exitosa'] / 
                          max(1, self.estadisticas['limpieza_exitosa'] + self.estadisticas['limpieza_fallida'])) * 100
        }
    
    def generar_reporte_limpieza(self) -> str:
        """Genera un reporte detallado de limpieza en formato Markdown."""
        stats = self.obtener_estadisticas()
        
        md = "# 🧹 Informe de los Purificadores de Asclepio\n\n"
        md += f"**Archivos Analizados:** {stats['archivos_analizados']:,}\n"
        md += f"**Archivos Contaminados:** {stats['archivos_limpiados']:,}\n"
        md += f"**Limpieza Exitosa:** {stats['limpieza_exitosa']:,}\n"
        md += f"**Limpieza Fallida:** {stats['limpieza_fallida']:,}\n"
        md += f"**Bytes Purificados:** {stats['bytes_limpiados']:,}\n"
        md += f"**Tasa de Éxito:** {stats['tasa_exito']:.1f}%\n"
        md += f"**Reglas Activas:** {stats['reglas_activas']}\n"
        md += f"**Fecha del Reporte:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # Resultados recientes
        resultados_recientes = sorted(
            self.resultados_limpieza,
            key=lambda r: r.tiempo_proceso,
            reverse=True
        )[:10]
        
        if resultados_recientes:
            md += "## 🔄 Procesos de Limpieza Recientes\n\n"
            md += "| Archivo | Estado | Cambios | Tiempo (s) |\n"
            md += "|---------|--------|---------|------------|\n"
            
            for resultado in resultados_recientes:
                archivo_nombre = Path(resultado.archivo_original).name
                estado_emoji = "✅" if resultado.exito else "❌"
                estado_texto = "Exitoso" if resultado.exito else "Fallido"
                cambios_count = len(resultado.cambios_realizados)
                
                md += f"| {archivo_nombre} | {estado_emoji} {estado_texto} | {cambios_count} | {resultado.tiempo_proceso:.2f} |\n"
            md += "\n"
        
        # Reglas más efectivas
        conteo_reglas = {}
        for resultado in self.resultados_limpieza:
            for cambio in resultado.cambios_realizados:
                regla_nombre = cambio.split(':')[0]
                conteo_reglas[regla_nombre] = conteo_reglas.get(regla_nombre, 0) + 1
        
        if conteo_reglas:
            md += "## 📊 Reglas Más Efectivas\n\n"
            md += "| Regla | Aplicaciones |\n"
            md += "|-------|-------------|\n"
            
            for regla, count in sorted(conteo_reglas.items(), key=lambda x: x[1], reverse=True)[:10]:
                md += f"| {regla} | {count} |\n"
            md += "\n"
        
        # Tipos de archivo procesados
        tipos_procesados = {}
        for resultado in self.resultados_limpieza:
            extension = Path(resultado.archivo_original).suffix.lower()
            tipos_procesados[extension] = tipos_procesados.get(extension, 0) + 1
        
        if tipos_procesados:
            md += "## 📁 Tipos de Archivo Procesados\n\n"
            md += "| Extensión | Cantidad |\n"
            md += "|-----------|----------|\n"
            
            for ext, count in sorted(tipos_procesados.items(), key=lambda x: x[1], reverse=True):
                md += f"| {ext or 'sin extensión'} | {count} |\n"
            md += "\n"
        
        # Configuración actual
        md += "## ⚙️ Configuración Actual\n\n"
        md += f"**Directorio de Trabajo:** `{stats['directorio_trabajo']}`\n"
        md += f"**Directorio de Backups:** `{stats['directorio_backups']}`\n"
        md += f"**Tipos Soportados:** {stats['tipos_soportados']} extensiones\n"
        md += f"**Tamaño Máximo:** {self.max_tamaño_archivo // (1024*1024)} MB\n\n"
        
        # Recomendaciones
        md += "## 💡 Recomendaciones\n\n"
        
        if stats['tasa_exito'] < 80:
            md += "- ⚠️ Tasa de éxito baja - revisar reglas de limpieza\n"
        
        if stats['limpieza_fallida'] > 0:
            md += "- 🔍 Analizar archivos con limpieza fallida para mejorar reglas\n"
        
        if stats['archivos_analizados'] > 1000:
            md += "- 📈 Considerar optimización para grandes volúmenes de archivos\n"
        
        md += "- 🔄 Realizar limpieza preventiva regularmente\n"
        md += "- 💾 Mantener backups de archivos críticos\n"
        md += "- 📊 Monitorear estadísticas de contaminación\n\n"
        
        md += "---\n"
        md += "*Reporte generado por los Purificadores de Asclepio de Ares Aegis*\n"
        
        return md
    
    def limpiar_temporales(self):
        """Limpia archivos temporales del directorio de trabajo."""
        try:
            archivos_eliminados = 0
            
            for archivo in self.directorio_trabajo.iterdir():
                if archivo.is_file():
                    archivo.unlink()
                    archivos_eliminados += 1
            
            self.logger.info(f"Limpieza de temporales: {archivos_eliminados} archivos eliminados")
            
        except Exception as e:
            self.logger.error(f"Error limpiando archivos temporales: {e}")
    
    def exportar_resultados_json(self) -> Dict[str, Any]:
        """Exporta los resultados de limpieza en formato JSON."""
        return {
            'timestamp': datetime.now().isoformat(),
            'estadisticas': self.obtener_estadisticas(),
            'resultados_limpieza': [
                {
                    'archivo_original': r.archivo_original,
                    'archivo_limpio': r.archivo_limpio,
                    'exito': r.exito,
                    'tipo_limpieza': r.tipo_limpieza,
                    'detalles_proceso': r.detalles_proceso,
                    'tiempo_proceso': r.tiempo_proceso,
                    'hash_original': r.hash_original,
                    'hash_limpio': r.hash_limpio,
                    'cambios_realizados': r.cambios_realizados,
                    'metadatos': r.metadatos
                }
                for r in self.resultados_limpieza
            ],
            'reglas_activas': [
                {
                    'nombre': regla.nombre,
                    'descripcion': regla.descripcion,
                    'tipo_archivo': regla.tipo_archivo,
                    'nivel_agresividad': regla.nivel_agresividad,
                    'requiere_confirmacion': regla.requiere_confirmacion
                }
                for regla in self.reglas_limpieza
            ]
        }
