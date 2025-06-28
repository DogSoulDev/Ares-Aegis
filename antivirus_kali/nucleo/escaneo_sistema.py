
"""
Módulo para el escaneo del sistema operativo, carpetas y programas instalados.
Permite comparar con la base de datos de referencia de Kali Linux.
Refactorizado para usar pathlib y mayor robustez.
"""
import hashlib
import subprocess
import psutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

from antivirus_kali.utilidades.logger import get_logger
from antivirus_kali.utilidades.auxiliares import formatear_tamaño, obtener_info_sistema
from antivirus_kali.utilidades.seguridad import ValidadorSeguridad

logger = get_logger(__name__)


class EscaneoSistema:
    """
    Clase principal para realizar escaneo completo del sistema.
    Incluye análisis de integridad, procesos, servicios y configuraciones.
    """
    
    def __init__(self, rutas_directorios: Optional[List[str]] = None):
        """
        Inicializa el escaneo del sistema.
        
        Args:
            rutas_directorios: Lista de rutas a analizar (por defecto, binarios principales)
        """
        self.rutas_directorios = rutas_directorios or [
            "/bin", "/usr/bin", "/sbin", "/usr/sbin", "/usr/local/bin"
        ]
        self.resultados_cache = {}
        self.inicio_escaneo = None

    def obtener_programas_instalados(self) -> Dict[str, Any]:
        """
        Obtiene lista de programas instalados según el gestor de paquetes.
        
        Returns:
            Diccionario con información de paquetes instalados
        """
        logger.info("Obteniendo lista de programas instalados")
        resultado = {
            'paquetes_dpkg': [],
            'paquetes_snap': [],
            'paquetes_flatpak': [],
            'total_paquetes': 0,
            'gestores_disponibles': []
        }
        
        try:
            # Paquetes dpkg (Debian/Ubuntu)
            try:
                salida = subprocess.check_output(
                    ['dpkg-query', '-W', '-f', '${Package}\t${Version}\t${Status}\n'], 
                    text=True, timeout=30
                )
                paquetes_dpkg = []
                for linea in salida.splitlines():
                    if '\t' in linea:
                        partes = linea.split('\t')
                        if len(partes) >= 3 and 'installed' in partes[2]:
                            paquetes_dpkg.append({
                                'nombre': partes[0],
                                'version': partes[1],
                                'gestor': 'dpkg'
                            })
                
                resultado['paquetes_dpkg'] = paquetes_dpkg
                resultado['gestores_disponibles'].append('dpkg')
                logger.info(f"Encontrados {len(paquetes_dpkg)} paquetes dpkg")
                
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                logger.warning("dpkg no disponible o error al ejecutar")
            
            # Paquetes Snap
            try:
                salida = subprocess.check_output(['snap', 'list'], text=True, timeout=30)
                paquetes_snap = []
                for linea in salida.splitlines()[1:]:  # Saltar encabezado
                    if linea.strip():
                        partes = linea.split()
                        if len(partes) >= 2:
                            paquetes_snap.append({
                                'nombre': partes[0],
                                'version': partes[1],
                                'gestor': 'snap'
                            })
                
                resultado['paquetes_snap'] = paquetes_snap
                resultado['gestores_disponibles'].append('snap')
                logger.info(f"Encontrados {len(paquetes_snap)} paquetes snap")
                
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                logger.debug("Snap no disponible")
            
            # Paquetes Flatpak
            try:
                salida = subprocess.check_output(['flatpak', 'list'], text=True, timeout=30)
                paquetes_flatpak = []
                for linea in salida.splitlines():
                    if linea.strip() and '\t' in linea:
                        partes = linea.split('\t')
                        if len(partes) >= 2:
                            paquetes_flatpak.append({
                                'nombre': partes[0],
                                'version': partes[1] if len(partes) > 1 else 'desconocida',
                                'gestor': 'flatpak'
                            })
                
                resultado['paquetes_flatpak'] = paquetes_flatpak
                resultado['gestores_disponibles'].append('flatpak')
                logger.info(f"Encontrados {len(paquetes_flatpak)} paquetes flatpak")
                
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                logger.debug("Flatpak no disponible")
            
            # Calcular total
            resultado['total_paquetes'] = (
                len(resultado['paquetes_dpkg']) + 
                len(resultado['paquetes_snap']) + 
                len(resultado['paquetes_flatpak'])
            )
            
        except Exception as e:
            logger.error(f"Error obteniendo programas instalados: {e}")
            resultado['error'] = str(e)
        
        return resultado

    def escanear_rootkits(self) -> Dict[str, Any]:
        """
        Ejecuta análisis de rootkits usando herramientas disponibles.
        
        Returns:
            Diccionario con resultados del análisis
        """
        logger.info("Iniciando escaneo de rootkits")
        resultado = {
            'herramientas_ejecutadas': [],
            'amenazas_detectadas': [],
            'advertencias': [],
            'estado': 'COMPLETADO'
        }
        
        # chkrootkit
        try:
            salida = subprocess.check_output(['chkrootkit'], text=True, timeout=120)
            resultado['herramientas_ejecutadas'].append('chkrootkit')
            
            # Analizar salida de chkrootkit
            lineas_sospechosas = []
            for linea in salida.splitlines():
                linea_lower = linea.lower()
                if any(keyword in linea_lower for keyword in ['infected', 'trojan', 'rootkit', 'suspicious']):
                    lineas_sospechosas.append(linea.strip())
            
            if lineas_sospechosas:
                resultado['amenazas_detectadas'].extend(lineas_sospechosas)
                logger.warning(f"chkrootkit detectó {len(lineas_sospechosas)} posibles amenazas")
            else:
                logger.info("chkrootkit no detectó amenazas")
                
        except subprocess.TimeoutExpired:
            resultado['advertencias'].append("chkrootkit timeout - escaneo incompleto")
            logger.warning("chkrootkit timeout")
        except FileNotFoundError:
            resultado['advertencias'].append("chkrootkit no instalado")
            logger.info("chkrootkit no disponible")
        except Exception as e:
            resultado['advertencias'].append(f"Error ejecutando chkrootkit: {e}")
            logger.error(f"Error en chkrootkit: {e}")
        
        # rkhunter
        try:
            salida = subprocess.check_output(
                ['rkhunter', '--check', '--sk', '--rwo'], 
                text=True, timeout=180
            )
            resultado['herramientas_ejecutadas'].append('rkhunter')
            
            # Analizar salida de rkhunter
            amenazas_rkhunter = []
            for linea in salida.splitlines():
                if 'Warning:' in linea or 'Infected:' in linea:
                    amenazas_rkhunter.append(linea.strip())
            
            if amenazas_rkhunter:
                resultado['amenazas_detectadas'].extend(amenazas_rkhunter)
                logger.warning(f"rkhunter detectó {len(amenazas_rkhunter)} posibles amenazas")
            else:
                logger.info("rkhunter no detectó amenazas")
                
        except subprocess.TimeoutExpired:
            resultado['advertencias'].append("rkhunter timeout - escaneo incompleto")
            logger.warning("rkhunter timeout")
        except FileNotFoundError:
            resultado['advertencias'].append("rkhunter no instalado")
            logger.info("rkhunter no disponible")
        except Exception as e:
            resultado['advertencias'].append(f"Error ejecutando rkhunter: {e}")
            logger.error(f"Error en rkhunter: {e}")
        
        # Si no hay herramientas disponibles
        if not resultado['herramientas_ejecutadas']:
            resultado['estado'] = 'SIN_HERRAMIENTAS'
            resultado['advertencias'].append("No hay herramientas anti-rootkit instaladas")
        
        return resultado

    def escanear_procesos_sospechosos(self) -> Dict[str, Any]:
        """
        Analiza procesos en ejecución en busca de actividad sospechosa.
        
        Returns:
            Diccionario con análisis de procesos
        """
        logger.info("Analizando procesos sospechosos")
        resultado = {
            'procesos_sospechosos': [],
            'procesos_alto_consumo': [],
            'procesos_red_activa': [],
            'total_procesos': 0,
            'estadisticas': {}
        }
        
        try:
            procesos = list(psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_percent']))
            resultado['total_procesos'] = len(procesos)
            
            # Palabras clave sospechosas
            keywords_sospechosos = [
                'keylogger', 'backdoor', 'trojan', 'malware', 'virus',
                'cryptominer', 'coinminer', 'botnet', 'ransomware'
            ]
            
            for proceso in procesos:
                try:
                    info = proceso.info
                    nombre = info.get('name', '').lower()
                    cmdline = ' '.join(info.get('cmdline', [])).lower()
                    
                    # Verificar nombres sospechosos
                    for keyword in keywords_sospechosos:
                        if keyword in nombre or keyword in cmdline:
                            resultado['procesos_sospechosos'].append({
                                'pid': info['pid'],
                                'nombre': info['name'],
                                'comando': ' '.join(info.get('cmdline', [])),
                                'motivo': f'Contiene palabra clave sospechosa: {keyword}'
                            })
                            break
                    
                    # Procesos con alto consumo de CPU
                    cpu_percent = info.get('cpu_percent', 0)
                    if cpu_percent > 80:
                        resultado['procesos_alto_consumo'].append({
                            'pid': info['pid'],
                            'nombre': info['name'],
                            'cpu_percent': cpu_percent,
                            'memory_percent': info.get('memory_percent', 0)
                        })
                    
                    # Procesos con conexiones de red activas
                    try:
                        conexiones = psutil.Process(info['pid']).connections()
                        if conexiones:
                            resultado['procesos_red_activa'].append({
                                'pid': info['pid'],
                                'nombre': info['name'],
                                'conexiones': len(conexiones)
                            })
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Estadísticas
            resultado['estadisticas'] = {
                'procesos_sospechosos': len(resultado['procesos_sospechosos']),
                'alto_consumo_cpu': len(resultado['procesos_alto_consumo']),
                'con_red_activa': len(resultado['procesos_red_activa'])
            }
            
        except Exception as e:
            logger.error(f"Error analizando procesos: {e}")
            resultado['error'] = str(e)
        
        return resultado

    def escanear_puertos_abiertos(self) -> Dict[str, Any]:
        """
        Escanea puertos abiertos y analiza su seguridad.
        
        Returns:
            Diccionario con información de puertos
        """
        logger.info("Escaneando puertos abiertos")
        resultado = {
            'puertos_tcp': [],
            'puertos_udp': [],
            'puertos_sospechosos': [],
            'estadisticas': {}
        }
        
        try:
            # Obtener conexiones usando psutil (más detallado que ss)
            conexiones = psutil.net_connections(kind='inet')
            
            for conn in conexiones:
                if conn.status == 'LISTEN' and conn.laddr:
                    puerto_info = {
                        'puerto': conn.laddr.port,
                        'ip': conn.laddr.ip,
                        'tipo': 'TCP' if conn.type == 1 else 'UDP',
                        'proceso': None
                    }
                    
                    # Obtener información del proceso
                    try:
                        if conn.pid:
                            proceso = psutil.Process(conn.pid)
                            puerto_info['proceso'] = {
                                'pid': conn.pid,
                                'nombre': proceso.name(),
                                'comando': ' '.join(proceso.cmdline())
                            }
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                    
                    # Clasificar por tipo
                    if conn.type == 1:  # TCP
                        resultado['puertos_tcp'].append(puerto_info)
                    else:  # UDP
                        resultado['puertos_udp'].append(puerto_info)
                    
                    # Verificar si es sospechoso
                    if conn.laddr.port in ValidadorSeguridad.PUERTOS_SOSPECHOSOS:
                        puerto_info['motivo'] = 'Puerto comúnmente usado por malware'
                        resultado['puertos_sospechosos'].append(puerto_info)
            
            # Estadísticas
            resultado['estadisticas'] = {
                'total_tcp': len(resultado['puertos_tcp']),
                'total_udp': len(resultado['puertos_udp']),
                'sospechosos': len(resultado['puertos_sospechosos'])
            }
            
        except Exception as e:
            logger.error(f"Error escaneando puertos: {e}")
            resultado['error'] = str(e)
        
        return resultado

    def escanear_servicios_activos(self) -> Dict[str, Any]:
        """
        Obtiene información de servicios activos del sistema.
        
        Returns:
            Diccionario con información de servicios
        """
        logger.info("Analizando servicios activos")
        resultado = {
            'servicios_activos': [],
            'servicios_fallidos': [],
            'servicios_sospechosos': [],
            'estadisticas': {}
        }
        
        try:
            # Usar systemctl para obtener servicios
            salida = subprocess.check_output(
                ['systemctl', 'list-units', '--type=service', '--all', '--no-pager'], 
                text=True, timeout=30
            )
            
            for linea in salida.splitlines():
                if '.service' in linea:
                    partes = linea.split()
                    if len(partes) >= 4:
                        servicio = {
                            'nombre': partes[0],
                            'cargado': partes[1],
                            'activo': partes[2],
                            'en_ejecucion': partes[3],
                            'descripcion': ' '.join(partes[4:]) if len(partes) > 4 else ''
                        }
                        
                        if servicio['activo'] == 'active':
                            resultado['servicios_activos'].append(servicio)
                        elif servicio['activo'] == 'failed':
                            resultado['servicios_fallidos'].append(servicio)
                        
                        # Verificar servicios sospechosos
                        nombre_lower = servicio['nombre'].lower()
                        if any(keyword in nombre_lower for keyword in ['crypto', 'miner', 'bot', 'hack']):
                            resultado['servicios_sospechosos'].append(servicio)
            
            # Estadísticas
            resultado['estadisticas'] = {
                'activos': len(resultado['servicios_activos']),
                'fallidos': len(resultado['servicios_fallidos']),
                'sospechosos': len(resultado['servicios_sospechosos'])
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo servicios: {e}")
            resultado['error'] = str(e)
        
        return resultado

    def escanear_integridad_binarios(self, base_hashes: Dict[str, str]) -> Dict[str, Any]:
        """
        Verifica la integridad de binarios críticos del sistema.
        
        Args:
            base_hashes: Diccionario con hashes de referencia
            
        Returns:
            Diccionario con resultados de verificación
        """
        logger.info("Verificando integridad de binarios del sistema")
        resultado = {
            'archivos_verificados': 0,
            'archivos_modificados': [],
            'archivos_faltantes': [],
            'archivos_integros': [],
            'estadisticas': {}
        }
        
        try:
            for archivo, hash_ref in base_hashes.items():
                resultado['archivos_verificados'] += 1
                
                hash_actual = self.calcular_hash_archivo(archivo)
                
                if hash_actual is None:
                    resultado['archivos_faltantes'].append({
                        'archivo': archivo,
                        'hash_esperado': hash_ref
                    })
                elif hash_actual != hash_ref:
                    resultado['archivos_modificados'].append({
                        'archivo': archivo,
                        'hash_esperado': hash_ref,
                        'hash_actual': hash_actual
                    })
                else:
                    resultado['archivos_integros'].append(archivo)
            
            # Estadísticas
            resultado['estadisticas'] = {
                'total_verificados': resultado['archivos_verificados'],
                'modificados': len(resultado['archivos_modificados']),
                'faltantes': len(resultado['archivos_faltantes']),
                'integros': len(resultado['archivos_integros']),
                'porcentaje_integridad': (len(resultado['archivos_integros']) / 
                                        max(resultado['archivos_verificados'], 1)) * 100
            }
            
        except Exception as e:
            logger.error(f"Error verificando integridad: {e}")
            resultado['error'] = str(e)
        
        return resultado

    def calcular_hash_archivo(self, ruta: str, algoritmo: str = 'sha256') -> Optional[str]:
        """
        Calcula el hash de un archivo usando pathlib para mayor robustez.
        
        Args:
            ruta: Ruta al archivo
            algoritmo: Algoritmo de hash a usar
            
        Returns:
            Hash del archivo o None si hay error
        """
        try:
            hash_func = hashlib.new(algoritmo)
            ruta_path = Path(ruta)
            
            if not ruta_path.exists():
                return None
                
            with ruta_path.open('rb') as f:
                for bloque in iter(lambda: f.read(4096), b''):
                    hash_func.update(bloque)
            
            return hash_func.hexdigest()
            
        except Exception as e:
            logger.error(f"Error calculando hash de {ruta}: {e}")
            return None

    def obtener_resumen_completo(self, base_hashes: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Obtiene un resumen completo del estado del sistema.
        
        Args:
            base_hashes: Hashes de referencia para verificación de integridad
            
        Returns:
            Diccionario con resumen completo
        """
        self.inicio_escaneo = datetime.now()
        logger.info("Iniciando escaneo completo del sistema")
        
        resumen = {
            'timestamp': self.inicio_escaneo.isoformat(),
            'info_sistema': obtener_info_sistema(),
            'programas_instalados': self.obtener_programas_instalados(),
            'rootkits': self.escanear_rootkits(),
            'procesos': self.escanear_procesos_sospechosos(),
            'puertos': self.escanear_puertos_abiertos(),
            'servicios': self.escanear_servicios_activos(),
            'seguridad': ValidadorSeguridad.generar_reporte_seguridad(),
            'resumen_ejecutivo': {}
        }
        
        # Agregar integridad si se proporcionan hashes
        if base_hashes:
            resumen['integridad'] = self.escanear_integridad_binarios(base_hashes)
        
        # Generar resumen ejecutivo
        total_amenazas = (
            len(resumen['rootkits'].get('amenazas_detectadas', [])) +
            len(resumen['procesos'].get('procesos_sospechosos', [])) +
            len(resumen['puertos'].get('puertos_sospechosos', [])) +
            len(resumen['servicios'].get('servicios_sospechosos', []))
        )
        
        nivel_riesgo = 'BAJO'
        if total_amenazas > 10:
            nivel_riesgo = 'CRITICO'
        elif total_amenazas > 5:
            nivel_riesgo = 'ALTO'
        elif total_amenazas > 0:
            nivel_riesgo = 'MEDIO'
        
        resumen['resumen_ejecutivo'] = {
            'total_amenazas_detectadas': total_amenazas,
            'nivel_riesgo': nivel_riesgo,
            'tiempo_escaneo': (datetime.now() - self.inicio_escaneo).total_seconds(),
            'recomendaciones': self._generar_recomendaciones(resumen)
        }
        
        logger.info(f"Escaneo completado: {total_amenazas} amenazas, nivel {nivel_riesgo}")
        
        return resumen

    def _generar_recomendaciones(self, resumen: Dict[str, Any]) -> List[str]:
        """
        Genera recomendaciones basadas en los resultados del escaneo.
        
        Args:
            resumen: Resultados del escaneo
            
        Returns:
            Lista de recomendaciones
        """
        recomendaciones = []
        
        # Recomendaciones basadas en rootkits
        if resumen['rootkits'].get('amenazas_detectadas'):
            recomendaciones.append("Ejecutar limpieza profunda del sistema con herramientas especializadas")
        
        # Recomendaciones basadas en procesos
        if resumen['procesos'].get('procesos_sospechosos'):
            recomendaciones.append("Investigar y terminar procesos sospechosos identificados")
        
        # Recomendaciones basadas en puertos
        if resumen['puertos'].get('puertos_sospechosos'):
            recomendaciones.append("Cerrar puertos sospechosos o verificar legitimidad de servicios")
        
        # Recomendaciones basadas en servicios
        if resumen['servicios'].get('servicios_fallidos'):
            recomendaciones.append("Revisar y corregir servicios fallidos del sistema")
        
        # Recomendaciones generales
        if not recomendaciones:
            recomendaciones.extend([
                "Sistema aparentemente seguro - mantener monitoreo regular",
                "Actualizar regularmente el sistema y definiciones de antivirus",
                "Realizar escaneos periódicos del sistema"
            ])
        
        return recomendaciones

    def exportar_informe(self, resumen: Dict[str, Any], 
                        ruta: str = "/tmp/informe_ares_aegis.pdf", 
                        usuario: str = "Administrador") -> str:
        """
        Exporta el resumen a un informe PDF.
        
        Args:
            resumen: Resumen del escaneo
            ruta: Ruta donde guardar el PDF
            usuario: Nombre del usuario
            
        Returns:
            Mensaje de resultado
        """
        try:
            from antivirus_kali.informes.generador_pdf import generar_informe_pdf
            
            ruta_pdf = ruta if ruta.endswith('.pdf') else ruta + '.pdf'
            resultado = generar_informe_pdf(resumen, ruta_pdf, usuario=usuario)
            
            logger.info(f"Informe PDF generado: {ruta_pdf}")
            return resultado
            
        except ImportError:
            error_msg = "Módulo de generación de PDF no disponible"
            logger.error(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"Error al exportar informe PDF: {e}"
            logger.error(error_msg)
            return error_msg
