import os
import json
import shutil
import hashlib
import time
import threading
import zipfile
import tarfile
import subprocess
import tempfile
import mimetypes
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Union, Tuple
from collections import defaultdict, deque
from dataclasses import dataclass, field

from .modelo_siem import SIEM, TipoEvento
from ..utils.utils_validaciones import validar_ruta_archivo, validar_permisos_lectura
from ..utils.utils_ayuda_rutas import crear_ruta_segura, obtener_rutas_sistema
from ..utils.utils_ayuda_logging import configurar_logger_modulo

# Importar utilidades de cuarentena
from ..utils.utils_cuarentena import (
    EstadoCuarentena, TipoAmenazaCuarentena, NivelRiesgoCuarentena, AccionCuarentena,
    MetadatosCuarentena, UtilsCuarentena, AnalizadorForenseUtils, 
    GestorBackupCuarentena, ValidadorCuarentena
)


class AnalizadorForenseCuarentena:
    """Analizador forense simplificado que usa utilidades"""
    
    def __init__(self):
        """Inicializa el analizador forense."""
        self.logger = configurar_logger_modulo("analizador_forense_cuarentena")
        self.herramientas_disponibles = AnalizadorForenseUtils.verificar_herramientas_disponibles()
        self.patrones_malware = AnalizadorForenseUtils.cargar_patrones_malware()
        self.firmas_conocidas = {}  # Para almacenar firmas conocidas de malware
        self.logger.info("Analizador forense de cuarentena inicializado")
    
    def analizar_archivo(self, ruta_archivo: str, metadatos: MetadatosCuarentena) -> Dict[str, Any]:
        """Realiza análisis forense completo de un archivo usando utilidades."""
        inicio_tiempo = time.time()
        resultado = {
            'archivo': ruta_archivo,
            'timestamp': datetime.now().isoformat(),
            'herramientas_usadas': [],
            'resultados': {},
            'nivel_amenaza': 'bajo',
            'recomendaciones': []
        }
        
        # Análisis básico con 'file'
        if self.herramientas_disponibles.get('file'):
            resultado_file = AnalizadorForenseUtils.ejecutar_file(ruta_archivo)
            if resultado_file.get('exitoso'):
                resultado['resultados']['file'] = resultado_file
                resultado['herramientas_usadas'].append('file')
        
        # Análisis de strings
        if self.herramientas_disponibles.get('strings'):
            resultado_strings = AnalizadorForenseUtils.ejecutar_strings(ruta_archivo)
            if resultado_strings.get('exitoso'):
                resultado['resultados']['strings'] = resultado_strings
                resultado['herramientas_usadas'].append('strings')
        
        # Análisis hexadecimal
        if self.herramientas_disponibles.get('hexdump'):
            resultado_hex = AnalizadorForenseUtils.analizar_con_hexdump(ruta_archivo)
            if resultado_hex.get('exitoso'):
                resultado['resultados']['hexdump'] = resultado_hex
                resultado['herramientas_usadas'].append('hexdump')
        
        # Búsqueda de patrones sospechosos
        analisis_patrones = AnalizadorForenseUtils.buscar_patrones_en_archivo(ruta_archivo, self.patrones_malware)
        resultado['resultados']['patrones'] = analisis_patrones
        resultado['nivel_amenaza'] = analisis_patrones.get('nivel_sospecha', 'bajo')
        
        # Generar recomendaciones
        resultado['recomendaciones'] = self._generar_recomendaciones(analisis_patrones, metadatos)
        resultado['tiempo_analisis'] = time.time() - inicio_tiempo
        
        return resultado
    
    def _generar_recomendaciones(self, analisis_patrones: Dict[str, Any], metadatos: MetadatosCuarentena) -> List[str]:
        """Genera recomendaciones basadas en el análisis."""
        recomendaciones = []
        nivel_sospecha = analisis_patrones.get('nivel_sospecha', 'bajo')
        
        if nivel_sospecha == 'critico':
            recomendaciones.extend([
                "🚨 ALTO RIESGO: Mantener en cuarentena permanente",
                "🔍 Realizar análisis manual inmediato",
                "🚫 NO restaurar bajo ninguna circunstancia",
                "📊 Enviar muestra a laboratorio de análisis"
            ])
        elif nivel_sospecha == 'alto':
            recomendaciones.extend([
                "⚠️ RIESGO ELEVADO: Análisis adicional requerido",
                "🔒 Mantener aislado hasta confirmación",
                "🧪 Ejecutar en entorno sandboxed",
                "👨‍💻 Revisión manual recomendada"
            ])
        elif nivel_sospecha == 'medio':
            recomendaciones.extend([
                "🔍 Análisis adicional recomendado",
                "⏳ Monitoreo extendido sugerido",
                "🛡️ Verificar con antivirus actualizado"
            ])
        else:
            recomendaciones.extend([
                "✅ Archivo aparenta ser seguro",
                "🔄 Verificación rutinaria completada",
                "📝 Considerar para restauración"
            ])
        
        return recomendaciones


class GestorCuarentenaAvanzado:
    def obtener_lista_cuarentena(self):
        """Devuelve una lista de metadatos de archivos en cuarentena (activos)."""
        return [m for m in self.base_datos.values() if getattr(m, 'estado', None) and getattr(m.estado, 'value', None) == 'ACTIVO']

    def restaurar_archivo(self, hash_sha256: str) -> bool:
        """Restaura un archivo de la cuarentena a su ubicación original usando el hash."""
        for metadatos in self.base_datos.values():
            if getattr(metadatos, 'hash_sha256', None) == hash_sha256 and getattr(metadatos, 'estado', None) and getattr(metadatos.estado, 'value', None) == 'ACTIVO':
                try:
                    ruta_backup = getattr(metadatos, 'ruta_backup', None)
                    ruta_original = getattr(metadatos, 'ruta_original', None)
                    if ruta_backup and ruta_original and os.path.exists(ruta_backup):
                        import shutil
                        shutil.copy2(ruta_backup, ruta_original)
                        metadatos.estado = type(metadatos.estado)("RESTAURADO")
                        self._guardar_base_datos()
                        self.archivos_restaurados += 1
                        self.logger.info(f"Archivo restaurado: {ruta_original}")
                        return True
                except Exception as e:
                    self.logger.error(f"Error restaurando archivo: {e}")
                    return False
        return False

    def eliminar_archivo(self, hash_sha256: str) -> bool:
        """Elimina un archivo de la cuarentena y su backup usando el hash."""
        for metadatos in self.base_datos.values():
            if getattr(metadatos, 'hash_sha256', None) == hash_sha256 and getattr(metadatos, 'estado', None) and getattr(metadatos.estado, 'value', None) == 'ACTIVO':
                try:
                    ruta_cuarentena = getattr(metadatos, 'ruta_cuarentena', None)
                    ruta_backup = getattr(metadatos, 'ruta_backup', None)
                    if ruta_cuarentena and os.path.exists(ruta_cuarentena):
                        os.remove(ruta_cuarentena)
                    if ruta_backup and os.path.exists(ruta_backup):
                        os.remove(ruta_backup)
                    metadatos.estado = type(metadatos.estado)("ELIMINADO")
                    self._guardar_base_datos()
                    self.logger.info(f"Archivo eliminado: {hash_sha256}")
                    return True
                except Exception as e:
                    self.logger.error(f"Error eliminando archivo: {e}")
                    return False
        return False
    """Sistema avanzado de gestión de cuarentena."""
    
    def __init__(self, siem: SIEM):
        """
        Inicializa el gestor de cuarentena avanzado.
        
        Args:
            siem: Instancia del SIEM para registro de eventos
        """
        self.siem = siem
        self.logger = configurar_logger_modulo("gestor_cuarentena")
        
        # Componentes del sistema
        self.analizador_forense = AnalizadorForenseCuarentena()
        
        # Configuración de directorios
        self.directorio_cuarentena = self._configurar_directorio_cuarentena()
        self.directorio_activos = os.path.join(self.directorio_cuarentena, "activos")
        self.directorio_backups = os.path.join(self.directorio_cuarentena, "backups")
        self.directorio_logs = os.path.join(self.directorio_cuarentena, "logs")
        self.directorio_temp = os.path.join(self.directorio_cuarentena, "temp")
        
        # Base de datos de cuarentena
        self.base_datos: Dict[str, MetadatosCuarentena] = {}
        self.archivo_base_datos = os.path.join(self.directorio_cuarentena, "cuarentena_db.json")
        
        # Configuración
        self.tamaño_maximo_archivo = 500 * 1024 * 1024  # 500MB
        self.dias_retencion = 90  # Días antes de eliminar automáticamente
        self.analisis_automatico = True
        self.compresion_habilitada = True
        
        # Estado del sistema
        self.archivos_procesados = 0
        self.amenazas_detectadas = 0
        self.falsos_positivos = 0
        self.archivos_restaurados = 0
        
        # Inicializar sistema
        self._crear_estructura_directorios()
        self._cargar_base_datos()
        
        self.logger.info("Gestor de Cuarentena Avanzado inicializado correctamente")
        self.siem.registrar_evento(
            TipoEvento.SISTEMA_INICIADO,
            "Sistema de Cuarentena Avanzado inicializado correctamente",
            {
                'directorio_cuarentena': self.directorio_cuarentena,
                'archivos_en_cuarentena': len(self.base_datos),
                'analisis_automatico': self.analisis_automatico
            },
            "MEDIO"
        )
    
    def _configurar_directorio_cuarentena(self) -> str:
        """Configura y retorna el directorio de cuarentena unificado (solo cuarentena_avanzada)."""
        try:
            rutas_sistema = obtener_rutas_sistema()
            directorio = os.path.join(rutas_sistema['directorio_datos'], "cuarentena_avanzada")
        except Exception:
            directorio = str(Path.cwd() / "cuarentena_avanzada")
        # Eliminar carpeta antigua si existe (limpieza)
        carpeta_antigua = Path.cwd() / "cuarentena"
        if carpeta_antigua.exists() and carpeta_antigua.is_dir():
            try:
                import shutil
                shutil.rmtree(carpeta_antigua)
            except Exception:
                pass
        return directorio
    
    def _crear_estructura_directorios(self):
        """Crea la estructura de directorios necesaria."""
        directorios = [
            self.directorio_cuarentena,
            self.directorio_activos,
            self.directorio_backups,
            self.directorio_logs,
            self.directorio_temp
        ]
        
        for directorio in directorios:
            try:
                # Crear directorio usando os.makedirs en lugar de crear_ruta_segura
                os.makedirs(directorio, mode=0o700, exist_ok=True)
                # Establecer permisos restrictivos
                os.chmod(directorio, 0o700)
            except Exception as e:
                self.logger.error(f"Error creando directorio {directorio}: {e}")
    
    def _cargar_base_datos(self):
        """Carga la base de datos de cuarentena."""
        try:
            if os.path.exists(self.archivo_base_datos):
                with open(self.archivo_base_datos, 'r', encoding='utf-8') as archivo:
                    datos = json.load(archivo)
                    
                    for archivo_id, datos_metadatos in datos.items():
                        # Crear metadatos con los parámetros correctos
                        metadatos = MetadatosCuarentena(
                            ruta_original=datos_metadatos.get('ruta_original', ''),
                            ruta_cuarentena=datos_metadatos.get('ruta_cuarentena', ''),
                            fecha_cuarentena=datetime.now(),
                            estado=EstadoCuarentena.PENDIENTE,
                            tipo_amenaza=TipoAmenazaCuarentena.DESCONOCIDO,
                            nivel_riesgo=NivelRiesgoCuarentena.BAJO,
                            hash_md5=datos_metadatos.get('hash_md5', ''),
                            hash_sha256=datos_metadatos.get('hash_sha256', ''),
                            tamaño_bytes=datos_metadatos.get('tamaño_bytes', 0),
                            permisos_originales=datos_metadatos.get('permisos_originales', ''),
                            propietario_original=datos_metadatos.get('propietario_original', ''),
                            grupo_original=datos_metadatos.get('grupo_original', ''),
                            mime_type=datos_metadatos.get('mime_type', datos_metadatos.get('tipo_mime', '')),
                            motivo_cuarentena=datos_metadatos.get('motivo_cuarentena', datos_metadatos.get('razon_cuarentena', ''))
                        )
                        
                        # Actualizar fechas si están en formato string
                        if 'fecha_cuarentena' in datos_metadatos:
                            fecha_str = datos_metadatos['fecha_cuarentena']
                            if isinstance(fecha_str, str):
                                metadatos.fecha_cuarentena = datetime.fromisoformat(fecha_str)
                        
                        # Actualizar última fecha de análisis
                        if 'fecha_ultimo_analisis' in datos_metadatos and datos_metadatos['fecha_ultimo_analisis']:
                            fecha_str = datos_metadatos['fecha_ultimo_analisis']
                            if isinstance(fecha_str, str):
                                metadatos.fecha_ultimo_analisis = datetime.fromisoformat(fecha_str)
                        
                        # Convertir enums desde strings
                        if 'estado' in datos_metadatos and isinstance(datos_metadatos['estado'], str):
                            metadatos.estado = EstadoCuarentena(datos_metadatos['estado'])
                        
                        if 'nivel_riesgo' in datos_metadatos and isinstance(datos_metadatos['nivel_riesgo'], str):
                            metadatos.nivel_riesgo = NivelRiesgoCuarentena(datos_metadatos['nivel_riesgo'])
                        
                        if 'tipo_amenaza' in datos_metadatos and datos_metadatos['tipo_amenaza']:
                            metadatos.tipo_amenaza = TipoAmenazaCuarentena(datos_metadatos['tipo_amenaza'])
                            metadatos.tipo_amenaza = TipoAmenazaCuarentena(metadatos.tipo_amenaza)
                        
                        self.base_datos[archivo_id] = metadatos
                
                self.logger.info(f"Base de datos de cuarentena cargada: {len(self.base_datos)} archivos")
        
        except Exception as e:
            self.logger.warning(f"Error cargando base de datos de cuarentena: {e}")
    
    def _guardar_base_datos(self):
        """Guarda la base de datos de cuarentena."""
        try:
            datos = {}
            for archivo_id, metadatos in self.base_datos.items():
                datos[archivo_id] = metadatos.to_dict()
            
            with open(self.archivo_base_datos, 'w', encoding='utf-8') as archivo:
                json.dump(datos, archivo, ensure_ascii=False, indent=2)
            
            self.logger.debug("Base de datos de cuarentena guardada")
        
        except Exception as e:
            self.logger.error(f"Error guardando base de datos de cuarentena: {e}")
    
    def poner_en_cuarentena(self, ruta_archivo: str, origen_deteccion: str, 
                           razon: str, tipo_amenaza: Optional[TipoAmenazaCuarentena] = None,
                           nivel_riesgo: NivelRiesgoCuarentena = NivelRiesgoCuarentena.MEDIO) -> Optional[str]:
        """
        Pone un archivo en cuarentena.
        
        Args:
            ruta_archivo: Ruta del archivo a poner en cuarentena
            origen_deteccion: Módulo que detectó la amenaza
            razon: Razón para poner en cuarentena
            tipo_amenaza: Tipo de amenaza detectada
            nivel_riesgo: Nivel de riesgo del archivo
            
        Returns:
            Optional[str]: ID del archivo en cuarentena o None si falló
        """
        try:
            self.logger.info(f"Iniciando proceso de cuarentena para: {ruta_archivo}")
            
            # Validaciones
            if not os.path.exists(ruta_archivo):
                self.logger.error(f"El archivo no existe: {ruta_archivo}")
                return None
            
            if not validar_permisos_lectura(ruta_archivo):
                self.logger.error(f"Permisos de lectura insuficientes para: {ruta_archivo}")
                return None
            
            # Verificar tamaño
            tamaño_archivo = os.path.getsize(ruta_archivo)
            if tamaño_archivo > self.tamaño_maximo_archivo:
                self.logger.warning(f"El archivo excede el tamaño máximo permitido para cuarentena: {tamaño_archivo} bytes")
                return None
            
            # Generar metadatos
            metadatos = self._generar_metadatos_archivo(ruta_archivo, origen_deteccion, razon, tipo_amenaza, nivel_riesgo)
            
            # Crear ruta en cuarentena
            # Crear nombre único para cuarentena usando hash
            nombre_archivo = os.path.basename(metadatos.ruta_original)
            nombre_cuarentena = f"{metadatos.hash_sha256[:16]}_{nombre_archivo}"
            ruta_cuarentena = os.path.join(self.directorio_activos, nombre_cuarentena)
            
            # Crear backup antes de mover
            if self._crear_backup_archivo(ruta_archivo, metadatos):
                # Registrar backup en notas forenses
                metadatos.notas_forenses.append(f"[{datetime.now().isoformat()}] Backup creado exitosamente")
            
            # Mover archivo a cuarentena
            if self.compresion_habilitada:
                ruta_cuarentena += ".zip"
                self._comprimir_archivo(ruta_archivo, ruta_cuarentena)
            else:
                shutil.move(ruta_archivo, ruta_cuarentena)
            
            metadatos.ruta_cuarentena = ruta_cuarentena
            # Registrar movimiento en notas forenses
            metadatos.notas_forenses.append(f"[{datetime.now().isoformat()}] Movido desde {ruta_archivo}")
            
            # Establecer permisos restrictivos
            os.chmod(ruta_cuarentena, 0o600)
            
            # Guardar en base de datos usando hash como clave
            archivo_id = metadatos.hash_sha256[:16]
            self.base_datos[archivo_id] = metadatos
            self._guardar_base_datos()
            
            # Registrar evento
            nombre_archivo = os.path.basename(metadatos.ruta_original)
            self.siem.registrar_evento(
                TipoEvento.AMENAZA_DETECTADA,
                f"Archivo puesto en cuarentena: {nombre_archivo}",
                {
                    'ruta_original': metadatos.ruta_original,
                    'archivo_id': archivo_id,
                    'ruta_original': ruta_archivo,
                    'origen_deteccion': origen_deteccion,
                    'razon': razon,
                    'tipo_amenaza': tipo_amenaza.value if tipo_amenaza else None,
                    'nivel_riesgo': nivel_riesgo.value,
                    'hash_sha256': metadatos.hash_sha256
                },
                "ALTO" if nivel_riesgo in [NivelRiesgoCuarentena.CRITICO, NivelRiesgoCuarentena.ALTO] else "MEDIO"
            )
            
            # Iniciar análisis automático si está habilitado
            if self.analisis_automatico:
                threading.Thread(
                    target=self._analizar_archivo_automatico,
                    args=(archivo_id,),
                    daemon=True
                ).start()
            
            self.archivos_procesados += 1
            self.logger.info(f"Archivo puesto en cuarentena correctamente: {archivo_id}")
            
            return archivo_id
        
        except Exception as e:
            self.logger.error(f"Error al poner archivo en cuarentena: {e}")
            return None
    
    def _generar_metadatos_archivo(self, ruta_archivo: str, origen_deteccion: str, razon: str,
                                  tipo_amenaza: Optional[TipoAmenazaCuarentena],
                                  nivel_riesgo: NivelRiesgoCuarentena) -> MetadatosCuarentena:
        """Genera metadatos completos para un archivo."""
        ruta_path = Path(ruta_archivo)
        # Obtener tipo MIME
        try:
            # Usar mimetypes estándar de Python
            tipo_mime, encoding = mimetypes.guess_type(ruta_archivo)
            if not tipo_mime:
                tipo_mime = "application/octet-stream"
        except Exception:
            tipo_mime = "application/octet-stream"
            encoding = None
        
        # Obtener información del archivo
        stat_info = os.stat(ruta_archivo)
        hashes = self._calcular_hashes_archivo(ruta_archivo)
        
        # Obtener información de propietario
        try:
            import pwd, grp  # type: ignore
            propietario = pwd.getpwuid(stat_info.st_uid).pw_name  # type: ignore
            grupo = grp.getgrgid(stat_info.st_gid).gr_name  # type: ignore
        except Exception:
            propietario = str(stat_info.st_uid)
            grupo = str(stat_info.st_gid)
        
        return MetadatosCuarentena(
            ruta_original=ruta_archivo,
            ruta_cuarentena="",  # Se establecerá después
            fecha_cuarentena=datetime.now(),
            estado=EstadoCuarentena.PENDIENTE,
            tipo_amenaza=tipo_amenaza or TipoAmenazaCuarentena.DESCONOCIDO,
            nivel_riesgo=nivel_riesgo,
            hash_md5=hashes['md5'],
            hash_sha256=hashes['sha256'],
            tamaño_bytes=stat_info.st_size,
            permisos_originales=oct(stat_info.st_mode)[-3:],
            propietario_original=propietario,
            grupo_original=grupo,
            mime_type=tipo_mime or "application/octet-stream",
            motivo_cuarentena=razon,
        )
    
    def _calcular_hashes_archivo(self, ruta_archivo: str) -> Dict[str, str]:
        """Calcula múltiples hashes del archivo."""
        hashes = {'md5': '', 'sha1': '', 'sha256': '', 'sha512': ''}
        
        try:
            with open(ruta_archivo, 'rb') as archivo:
                contenido = archivo.read()
                
                hashes['md5'] = hashlib.md5(contenido).hexdigest()
                hashes['sha1'] = hashlib.sha1(contenido).hexdigest()
                hashes['sha256'] = hashlib.sha256(contenido).hexdigest()
                hashes['sha512'] = hashlib.sha512(contenido).hexdigest()
        
        except Exception as e:
            self.logger.warning(f"Error calculando hashes: {e}")
        
        return hashes
    
    def _crear_backup_archivo(self, ruta_archivo: str, metadatos: MetadatosCuarentena) -> bool:
        """Crea un backup del archivo antes de moverlo a cuarentena."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nombre_archivo = os.path.basename(metadatos.ruta_original)
            extension = os.path.splitext(nombre_archivo)[1]
            nombre_backup = f"{nombre_archivo}_{timestamp}_backup{extension}"
            ruta_backup = os.path.join(self.directorio_backups, nombre_backup)
            
            shutil.copy2(ruta_archivo, ruta_backup)
            os.chmod(ruta_backup, 0o600)
            
            self.logger.debug(f"Backup creado: {ruta_backup}")
            return True
        
        except Exception as e:
            self.logger.warning(f"Error creando backup: {e}")
            return False
    
    def _comprimir_archivo(self, ruta_origen: str, ruta_destino: str):
        """Comprime un archivo usando ZIP."""
        try:
            with zipfile.ZipFile(ruta_destino, 'w', zipfile.ZIP_DEFLATED) as archivo_zip:
                archivo_zip.write(ruta_origen, os.path.basename(ruta_origen))
            
            # Eliminar archivo original
            os.remove(ruta_origen)
            
            self.logger.debug(f"Archivo comprimido: {ruta_destino}")
        
        except Exception as e:
            self.logger.error(f"Error comprimiendo archivo: {e}")
            # Fallback: mover sin comprimir
            shutil.move(ruta_origen, ruta_destino.replace('.zip', ''))
    
    def _analizar_archivo_automatico(self, archivo_id: str):
        """Analiza automáticamente un archivo en cuarentena."""
        try:
            if archivo_id not in self.base_datos:
                return
            
            metadatos = self.base_datos[archivo_id]
            metadatos.estado = EstadoCuarentena.EN_ANALISIS
            self._guardar_base_datos()
            
            # Descomprimir si es necesario
            ruta_analisis = self._preparar_archivo_para_analisis(metadatos)
            
            # Ejecutar análisis forense
            resultado_analisis = self.analizador_forense.analizar_archivo(ruta_analisis, metadatos)
            
            # Actualizar metadatos con resultados
            metadatos.resultado_analisis = json.dumps(resultado_analisis)  # Convertir a string
            metadatos.fecha_ultimo_analisis = datetime.now()
            # Registrar acción en notas forenses
            metadatos.notas_forenses.append(f"[{datetime.now().isoformat()}] Análisis completado - Nivel: {resultado_analisis['nivel_amenaza']}")
            
            # Actualizar estado basado en análisis
            nivel_amenaza = resultado_analisis.get('nivel_amenaza', 'BAJO')
            if nivel_amenaza in ['CRITICO', 'ALTO']:
                metadatos.estado = EstadoCuarentena.MALICIOSO
                metadatos.tipo_amenaza = TipoAmenazaCuarentena.SOSPECHOSO
                self.amenazas_detectadas += 1
            elif nivel_amenaza == 'MEDIO':
                metadatos.estado = EstadoCuarentena.SOSPECHOSO
                # Registrar necesidad de atención manual
                metadatos.notas_forenses.append(f"[{datetime.now().isoformat()}] Requiere atención manual")
            else:
                metadatos.estado = EstadoCuarentena.SEGURO
            
            # Limpiar archivo temporal
            if ruta_analisis != metadatos.ruta_cuarentena:
                try:
                    os.remove(ruta_analisis)
                except Exception:
                    pass
            
            self._guardar_base_datos()
            
            # Registrar resultado
            nombre_archivo = os.path.basename(metadatos.ruta_original)
            self.siem.registrar_evento(
                TipoEvento.ANALISIS_COMPLETADO,
                f"Análisis automático completado: {nombre_archivo}",
                {
                    'archivo_id': archivo_id,
                    'nivel_amenaza': nivel_amenaza,
                    'estado_final': metadatos.estado.value,
                    'tiempo_analisis': resultado_analisis.get('tiempo_analisis', 0)
                },
                "ALTO" if nivel_amenaza in ['CRITICO', 'ALTO'] else "MEDIO"
            )
            
            self.logger.info(f"Análisis automático completado: {archivo_id} - {nivel_amenaza}")
        
        except Exception as e:
            self.logger.error(f"Error en análisis automático: {e}")
            if archivo_id in self.base_datos:
                self.base_datos[archivo_id].estado = EstadoCuarentena.ERROR
                self._guardar_base_datos()
    
    def _preparar_archivo_para_analisis(self, metadatos: MetadatosCuarentena) -> str:
        """Prepara un archivo para análisis (descomprime si es necesario)."""
        if metadatos.ruta_cuarentena.endswith('.zip'):
            # Descomprimir temporalmente
            # Crear directorio temporal para análisis usando hash como identificador
            archivo_id = metadatos.hash_sha256[:16]
            ruta_temp = os.path.join(self.directorio_temp, f"analisis_{archivo_id}")
            
            try:
                with zipfile.ZipFile(metadatos.ruta_cuarentena, 'r') as archivo_zip:
                    archivo_zip.extractall(ruta_temp)
                
                # Buscar el archivo extraído
                archivos_extraidos = os.listdir(ruta_temp)
                if archivos_extraidos:
                    return os.path.join(ruta_temp, archivos_extraidos[0])
            
            except Exception as e:
                self.logger.warning(f"Error descomprimiendo para análisis: {e}")
        
        return metadatos.ruta_cuarentena
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas del sistema de cuarentena."""
        total_archivos = len(self.base_datos)
        archivos_por_estado = defaultdict(int)
        archivos_por_riesgo = defaultdict(int)
        archivos_por_tipo_amenaza = defaultdict(int)
        
        for metadatos in self.base_datos.values():
            archivos_por_estado[metadatos.estado.value] += 1
            archivos_por_riesgo[metadatos.nivel_riesgo.value] += 1
            if metadatos.tipo_amenaza:
                archivos_por_tipo_amenaza[metadatos.tipo_amenaza.value] += 1
        
        return {
            'total_archivos_cuarentena': total_archivos,
            'archivos_procesados': self.archivos_procesados,
            'amenazas_detectadas': self.amenazas_detectadas,
            'falsos_positivos': self.falsos_positivos,
            'archivos_restaurados': self.archivos_restaurados,
            'archivos_por_estado': dict(archivos_por_estado),
            'archivos_por_riesgo': dict(archivos_por_riesgo),
            'archivos_por_tipo_amenaza': dict(archivos_por_tipo_amenaza),
            'directorio_cuarentena': self.directorio_cuarentena,
            'analisis_automatico': self.analisis_automatico,
            'herramientas_forenses': len([k for k, v in self.analizador_forense.herramientas_disponibles.items() if v])
        }


# Alias para compatibilidad
GestorCuarentena = GestorCuarentenaAvanzado

