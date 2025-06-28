
"""
Motor de escaneo principal que integra todos los motores de detección.
Proporciona una interfaz unificada para análisis de malware.
"""

import asyncio
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed

from antivirus_kali.core.clamav_engine import MotorClamAV
from antivirus_kali.core.yara_engine import MotorYARA
from antivirus_kali.core.rootkit_engine import MotorRootkits
from antivirus_kali.core.hash_engine import MotorHashes
from antivirus_kali.utilidades.logger import get_logger
from antivirus_kali.utilidades.auxiliares import formatear_tamaño, obtener_hash_archivo

logger = get_logger(__name__)


class MotorEscaneo:
    """
    Motor de escaneo principal que coordina todos los motores de detección.
    Proporciona análisis completo con informes detallados.
    """
    
    def __init__(self, reglas_yara: Optional[str] = None, 
                 algoritmos_hash: Optional[List[str]] = None, 
                 herramienta_rootkits: str = 'rkhunter'):
        """
        Inicializa el motor de escaneo con configuraciones específicas.
        
        Args:
            reglas_yara: Ruta a las reglas YARA
            algoritmos_hash: Lista de algoritmos de hash a usar
            herramienta_rootkits: Herramienta para detección de rootkits
        """
        self.inicio_tiempo = None
        self.callback_progreso = None
        self.cancelado = False
        
        # Inicializar motores
        try:
            self.clamav = MotorClamAV()
            logger.info("Motor ClamAV inicializado")
        except Exception as e:
            logger.warning(f"No se pudo inicializar ClamAV: {e}")
            self.clamav = None
            
        try:
            self.yara = MotorYARA(reglas_yara) if reglas_yara else None
            if self.yara:
                logger.info("Motor YARA inicializado")
        except Exception as e:
            logger.warning(f"No se pudo inicializar YARA: {e}")
            self.yara = None
            
        try:
            self.rootkits = MotorRootkits(herramienta_rootkits)
            logger.info("Motor Rootkits inicializado")
        except Exception as e:
            logger.warning(f"No se pudo inicializar motor rootkits: {e}")
            self.rootkits = None
            
        try:
            self.hashes = MotorHashes(algoritmos_hash or ['sha256', 'md5'])
            logger.info("Motor Hashes inicializado")
        except Exception as e:
            logger.warning(f"No se pudo inicializar motor hashes: {e}")
            self.hashes = None

    def configurar_callback_progreso(self, callback: Callable[[str, int], None]):
        """Configura función de callback para reportar progreso"""
        self.callback_progreso = callback

    def cancelar_escaneo(self):
        """Cancela el escaneo en curso"""
        self.cancelado = True
        logger.info("Cancelación de escaneo solicitada")

    def _reportar_progreso(self, mensaje: str, porcentaje: int = 0):
        """Reporta progreso del escaneo"""
        if self.callback_progreso:
            self.callback_progreso(mensaje, porcentaje)

    def _obtener_archivos_objetivo(self, ruta_objetivo: str) -> List[Path]:
        """Obtiene lista de archivos a escanear"""
        ruta = Path(ruta_objetivo)
        archivos = []
        
        if ruta.is_file():
            archivos = [ruta]
        elif ruta.is_dir():
            # Buscar archivos comunes que pueden contener malware
            extensiones_objetivo = {
                '.exe', '.dll', '.bat', '.cmd', '.scr', '.pif',
                '.com', '.jar', '.class', '.py', '.js', '.vbs',
                '.ps1', '.sh', '.bin', '.so', '.deb', '.rpm'
            }
            
            try:
                for archivo in ruta.rglob("*"):
                    if self.cancelado:
                        break
                        
                    if archivo.is_file():
                        # Incluir archivos ejecutables y scripts
                        if archivo.suffix.lower() in extensiones_objetivo:
                            archivos.append(archivo)
                        # Incluir archivos grandes que podrían ser sospechosos
                        elif archivo.stat().st_size > 1024 * 1024:  # > 1MB
                            archivos.append(archivo)
                            
            except PermissionError as e:
                logger.warning(f"Sin permisos para acceder a {ruta}: {e}")
            except Exception as e:
                logger.error(f"Error listando archivos en {ruta}: {e}")
        
        return archivos[:1000]  # Limitar para evitar sobrecarga

    def escanear_archivo_individual(self, ruta_archivo: str) -> Dict[str, Any]:
        """
        Escanea un archivo individual con todos los motores disponibles.
        
        Args:
            ruta_archivo: Ruta al archivo a escanear
            
        Returns:
            Diccionario con resultados del escaneo
        """
        ruta = Path(ruta_archivo)
        if not ruta.exists():
            return {'error': 'Archivo no encontrado'}
        
        resultados = {
            'archivo': str(ruta),
            'tamaño': ruta.stat().st_size,
            'tamaño_formateado': formatear_tamaño(ruta.stat().st_size),
            'modificado': datetime.fromtimestamp(ruta.stat().st_mtime).isoformat(),
            'hash_sha256': obtener_hash_archivo(ruta, 'sha256'),
            'amenazas_detectadas': [],
            'motores_ejecutados': []
        }
        
        # Escaneo con ClamAV
        if self.clamav:
            try:
                resultado_clamav = self.clamav.escanear(str(ruta))
                resultados['motores_ejecutados'].append('ClamAV')
                total_infectados = resultado_clamav.get('total_infectados', 0)
                if isinstance(total_infectados, int) and total_infectados > 0:
                    detalles = resultado_clamav.get('detalles', [])
                    if isinstance(detalles, list):
                        for amenaza in detalles:
                            if isinstance(amenaza, dict):
                                resultados['amenazas_detectadas'].append({
                                    'motor': 'ClamAV',
                                    'tipo': 'Virus/Malware',
                                    'nombre': amenaza.get('virus', 'Desconocido'),
                                    'severidad': 'ALTA'
                                })
            except Exception as e:
                logger.error(f"Error en escaneo ClamAV: {e}")
        
        # Escaneo con YARA
        if self.yara:
            try:
                resultado_yara = self.yara.escanear(str(ruta))
                resultados['motores_ejecutados'].append('YARA')
                total_yara = resultado_yara.get('total', 0)
                if isinstance(total_yara, int) and total_yara > 0:
                    reglas = resultado_yara.get('reglas_activadas', [])
                    if isinstance(reglas, list):
                        for regla in reglas:
                            resultados['amenazas_detectadas'].append({
                                'motor': 'YARA',
                                'tipo': 'Patrón Sospechoso',
                                'nombre': str(regla),
                                'severidad': 'MEDIA'
                            })
            except Exception as e:
                logger.error(f"Error en escaneo YARA: {e}")
        
        # Escaneo de hashes
        if self.hashes:
            try:
                resultado_hashes = self.hashes.verificar_archivo(str(ruta))
                resultados['motores_ejecutados'].append('Hashes')
                if resultado_hashes.get('es_malicioso', False):
                    resultados['amenazas_detectadas'].append({
                        'motor': 'Base de Datos de Hashes',
                        'tipo': 'Hash Malicioso',
                        'nombre': resultado_hashes.get('tipo_malware', 'Malware Conocido'),
                        'severidad': 'ALTA'
                    })
            except Exception as e:
                logger.error(f"Error en verificación de hashes: {e}")
        
        return resultados

    def escanear_todo(self, ruta_objetivo: str) -> Dict[str, Any]:
        """
        Ejecuta todos los motores sobre el objetivo y devuelve un resumen estructurado.
        
        Args:
            ruta_objetivo: Ruta del directorio o archivo a escanear
            
        Returns:
            Diccionario con resultados completos del escaneo
        """
        self.inicio_tiempo = time.time()
        self.cancelado = False
        
        logger.info(f"Iniciando escaneo completo de: {ruta_objetivo}")
        self._reportar_progreso("Iniciando escaneo...", 0)
        
        resumen = {
            'ruta_objetivo': ruta_objetivo,
            'inicio': datetime.now().isoformat(),
            'estado': 'EN_PROGRESO',
            'archivos_escaneados': 0,
            'amenazas_totales': 0,
            'motores_utilizados': [],
            'resultados_detallados': {},
            'archivos_con_amenazas': [],
            'estadisticas': {}
        }
        
        try:
            # Obtener archivos a escanear
            self._reportar_progreso("Analizando estructura de archivos...", 10)
            archivos = self._obtener_archivos_objetivo(ruta_objetivo)
            
            if not archivos:
                resumen['estado'] = 'COMPLETADO'
                resumen['mensaje'] = 'No se encontraron archivos para escanear'
                return resumen
            
            logger.info(f"Se escanearán {len(archivos)} archivos")
            
            # Escaneo con ClamAV (si está disponible)
            if self.clamav and not self.cancelado:
                self._reportar_progreso("Ejecutando escaneo ClamAV...", 20)
                try:
                    resultado_clamav = self.clamav.escanear(ruta_objetivo)
                    resumen['resultados_detallados']['clamav'] = resultado_clamav
                    resumen['motores_utilizados'].append('ClamAV')
                    total_infectados = resultado_clamav.get('total_infectados', 0)
                    if isinstance(total_infectados, int) and total_infectados > 0:
                        resumen['amenazas_totales'] += total_infectados
                except Exception as e:
                    logger.error(f"Error en ClamAV: {e}")
                    resumen['resultados_detallados']['clamav'] = {'error': str(e)}
            
            # Escaneo con YARA (si está disponible)
            if self.yara and not self.cancelado:
                self._reportar_progreso("Ejecutando escaneo YARA...", 40)
                try:
                    resultado_yara = self.yara.escanear(ruta_objetivo)
                    resumen['resultados_detallados']['yara'] = resultado_yara
                    resumen['motores_utilizados'].append('YARA')
                    total_yara = resultado_yara.get('total', 0)
                    if isinstance(total_yara, int) and total_yara > 0:
                        resumen['amenazas_totales'] += total_yara
                except Exception as e:
                    logger.error(f"Error en YARA: {e}")
                    resumen['resultados_detallados']['yara'] = {'error': str(e)}
            
            # Escaneo de rootkits (si está disponible)
            if self.rootkits and not self.cancelado:
                self._reportar_progreso("Ejecutando escaneo de rootkits...", 60)
                try:
                    resultado_rootkits = self.rootkits.escanear()
                    resumen['resultados_detallados']['rootkits'] = resultado_rootkits
                    resumen['motores_utilizados'].append('Rootkits')
                    total_hallazgos = resultado_rootkits.get('total_hallazgos', 0)
                    if isinstance(total_hallazgos, int) and total_hallazgos > 0:
                        resumen['amenazas_totales'] += total_hallazgos
                except Exception as e:
                    logger.error(f"Error en escaneo rootkits: {e}")
                    resumen['resultados_detallados']['rootkits'] = {'error': str(e)}
            
            # Escaneo de hashes en archivos principales
            if self.hashes and not self.cancelado and len(archivos) <= 100:
                self._reportar_progreso("Verificando hashes maliciosos...", 80)
                try:
                    archivos_maliciosos = []
                    for archivo in archivos[:50]:  # Limitar para rendimiento
                        if self.cancelado:
                            break
                        resultado = self.hashes.verificar_archivo(str(archivo))
                        if resultado.get('es_malicioso', False):
                            archivos_maliciosos.append({
                                'archivo': str(archivo),
                                'hash': resultado.get('hash'),
                                'tipo': resultado.get('tipo_malware')
                            })
                    
                    resumen['resultados_detallados']['hashes'] = {
                        'archivos_verificados': min(50, len(archivos)),
                        'archivos_maliciosos': archivos_maliciosos,
                        'total_maliciosos': len(archivos_maliciosos)
                    }
                    resumen['motores_utilizados'].append('Hashes')
                    resumen['amenazas_totales'] += len(archivos_maliciosos)
                    
                except Exception as e:
                    logger.error(f"Error en verificación de hashes: {e}")
                    resumen['resultados_detallados']['hashes'] = {'error': str(e)}
            
            # Finalizar escaneo
            resumen['archivos_escaneados'] = len(archivos)
            resumen['tiempo_transcurrido'] = time.time() - self.inicio_tiempo
            resumen['fin'] = datetime.now().isoformat()
            resumen['estado'] = 'CANCELADO' if self.cancelado else 'COMPLETADO'
            
            # Estadísticas finales
            resumen['estadisticas'] = {
                'archivos_por_segundo': len(archivos) / max(resumen['tiempo_transcurrido'], 1),
                'motores_ejecutados': len(resumen['motores_utilizados']),
                'tasa_deteccion': (resumen['amenazas_totales'] / max(len(archivos), 1)) * 100
            }
            
            self._reportar_progreso("Escaneo completado", 100)
            
            logger.info(f"Escaneo completado: {resumen['amenazas_totales']} amenazas en {resumen['tiempo_transcurrido']:.2f}s")
            
        except Exception as e:
            logger.error(f"Error durante el escaneo: {e}")
            resumen['estado'] = 'ERROR'
            resumen['error'] = str(e)
            resumen['fin'] = datetime.now().isoformat()
        
        return resumen

    def resumen_profesional(self, ruta_objetivo: str) -> Dict[str, Any]:
        """
        Devuelve un resumen ejecutivo para mostrar en la interfaz.
        
        Args:
            ruta_objetivo: Ruta del objetivo a escanear
            
        Returns:
            Resumen ejecutivo del escaneo
        """
        resultados = self.escanear_todo(ruta_objetivo)
        
        # Calcular nivel de riesgo
        total_amenazas = resultados.get('amenazas_totales', 0)
        if total_amenazas == 0:
            nivel_riesgo = 'BAJO'
        elif total_amenazas <= 5:
            nivel_riesgo = 'MEDIO'
        elif total_amenazas <= 20:
            nivel_riesgo = 'ALTO'
        else:
            nivel_riesgo = 'CRÍTICO'
        
        # Recomendaciones basadas en resultados
        recomendaciones = []
        if total_amenazas > 0:
            recomendaciones.extend([
                'Aislar inmediatamente los archivos infectados',
                'Ejecutar un escaneo completo del sistema',
                'Actualizar las definiciones de antivirus'
            ])
        
        if resultados.get('resultados_detallados', {}).get('rootkits', {}).get('total_hallazgos', 0) > 0:
            recomendaciones.append('Ejecutar herramientas especializadas anti-rootkit')
        
        return {
            'total_amenazas': total_amenazas,
            'nivel_riesgo': nivel_riesgo,
            'archivos_escaneados': resultados.get('archivos_escaneados', 0),
            'tiempo_transcurrido': resultados.get('tiempo_transcurrido', 0),
            'motores_utilizados': resultados.get('motores_utilizados', []),
            'estado': resultados.get('estado', 'DESCONOCIDO'),
            'recomendaciones': recomendaciones,
            'detalles_completos': resultados
        }
