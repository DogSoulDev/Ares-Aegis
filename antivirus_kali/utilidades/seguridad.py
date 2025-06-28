"""
Utilidades de seguridad para Ares Aegis.
Funciones para validación, sanitización y análisis de seguridad.
"""

import os
import re
import subprocess
import psutil
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple
from urllib.parse import urlparse
import ipaddress

from antivirus_kali.utilidades.logger import get_logger

logger = get_logger(__name__)


class ValidadorSeguridad:
    """
    Clase para validaciones de seguridad y análisis de riesgos.
    """
    
    # Extensiones de archivos potencialmente peligrosas
    EXTENSIONES_PELIGROSAS = {
        '.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.vbe',
        '.js', '.jar', '.app', '.deb', '.rpm', '.dmg', '.pkg', '.msi',
        '.ps1', '.psm1', '.psd1', '.sh', '.bash', '.zsh', '.fish'
    }
    
    # Directorios del sistema que no deben modificarse
    DIRECTORIOS_SISTEMA = {
        '/bin', '/sbin', '/usr/bin', '/usr/sbin', '/boot', '/sys',
        '/proc', '/dev', '/etc/systemd', '/lib', '/usr/lib'
    }
    
    # Puertos comúnmente utilizados por malware
    PUERTOS_SOSPECHOSOS = {
        1337, 31337, 12345, 54321, 65534, 4444, 5555, 6666, 7777, 8888,
        9999, 6667, 6668, 6669, 8080, 3389, 1234, 2222, 3333
    }

    @staticmethod
    def es_archivo_peligroso(ruta_archivo: str) -> Tuple[bool, str]:
        """
        Verifica si un archivo tiene características peligrosas.
        
        Args:
            ruta_archivo: Ruta al archivo a verificar
            
        Returns:
            Tupla (es_peligroso, motivo)
        """
        try:
            ruta = Path(ruta_archivo)
            
            # Verificar si el archivo existe
            if not ruta.exists():
                return False, "Archivo no existe"
            
            # Verificar extensión
            if ruta.suffix.lower() in ValidadorSeguridad.EXTENSIONES_PELIGROSAS:
                return True, f"Extensión peligrosa: {ruta.suffix}"
            
            # Verificar permisos de ejecución
            if os.access(ruta, os.X_OK):
                return True, "Archivo ejecutable"
            
            # Verificar tamaño sospechoso (muy pequeño o muy grande)
            tamaño = ruta.stat().st_size
            if tamaño < 10:  # Menos de 10 bytes
                return True, "Archivo demasiado pequeño (sospechoso)"
            elif tamaño > 100 * 1024 * 1024:  # Más de 100MB
                return True, "Archivo demasiado grande (sospechoso)"
            
            # Verificar si está en directorio del sistema
            for dir_sistema in ValidadorSeguridad.DIRECTORIOS_SISTEMA:
                if str(ruta).startswith(dir_sistema):
                    return True, f"Archivo en directorio del sistema: {dir_sistema}"
            
            return False, "Archivo aparentemente seguro"
            
        except Exception as e:
            logger.error(f"Error verificando archivo {ruta_archivo}: {e}")
            return True, f"Error en verificación: {e}"

    @staticmethod
    def validar_url(url: str) -> Tuple[bool, str]:
        """
        Valida una URL y verifica si es segura.
        
        Args:
            url: URL a validar
            
        Returns:
            Tupla (es_valida, motivo)
        """
        try:
            # Verificar formato básico
            parsed = urlparse(url)
            
            if not parsed.scheme:
                return False, "URL sin esquema (http/https)"
            
            if parsed.scheme not in ['http', 'https']:
                return False, f"Esquema no permitido: {parsed.scheme}"
            
            if not parsed.netloc:
                return False, "URL sin dominio"
            
            # Verificar caracteres sospechosos
            caracteres_sospechosos = ['<', '>', '"', '\'', '&', '%00']
            for char in caracteres_sospechosos:
                if char in url:
                    return False, f"Carácter sospechoso detectado: {char}"
            
            # Verificar longitud
            if len(url) > 2000:
                return False, "URL demasiado larga"
            
            # Verificar dominios sospechosos (lista básica)
            dominios_sospechosos = [
                'bit.ly', 'tinyurl.com', 'goo.gl', 't.co',
                'ow.ly', 'short.link', 'rebrand.ly'
            ]
            
            for dominio in dominios_sospechosos:
                if dominio in parsed.netloc:
                    return False, f"Dominio acortador detectado: {dominio}"
            
            return True, "URL válida"
            
        except Exception as e:
            return False, f"Error validando URL: {e}"

    @staticmethod
    def analizar_conexiones_red() -> Dict[str, Any]:
        """
        Analiza las conexiones de red activas en busca de actividad sospechosa.
        
        Returns:
            Diccionario con análisis de conexiones
        """
        conexiones_sospechosas = []
        estadisticas = {
            'total_conexiones': 0,
            'conexiones_establecidas': 0,
            'conexiones_escuchando': 0,
            'puertos_sospechosos': 0,
            'conexiones_externas': 0
        }
        
        try:
            conexiones = psutil.net_connections(kind='inet')
            estadisticas['total_conexiones'] = len(conexiones)
            
            for conn in conexiones:
                # Estadísticas básicas
                if conn.status == 'ESTABLISHED':
                    estadisticas['conexiones_establecidas'] += 1
                elif conn.status == 'LISTEN':
                    estadisticas['conexiones_escuchando'] += 1
                
                # Verificar puertos sospechosos
                if conn.laddr and conn.laddr.port in ValidadorSeguridad.PUERTOS_SOSPECHOSOS:
                    estadisticas['puertos_sospechosos'] += 1
                    conexiones_sospechosas.append({
                        'tipo': 'Puerto sospechoso',
                        'puerto': conn.laddr.port,
                        'proceso': conn.pid,
                        'estado': conn.status
                    })
                
                # Verificar conexiones externas
                if conn.raddr and conn.raddr.ip not in ['127.0.0.1', '::1']:
                    estadisticas['conexiones_externas'] += 1
                    
                    # Verificar IPs sospechosas (rangos privados inesperados)
                    try:
                        ip = ipaddress.ip_address(conn.raddr.ip)
                        if not ip.is_private and not ip.is_loopback:
                            conexiones_sospechosas.append({
                                'tipo': 'Conexión externa',
                                'ip_remota': conn.raddr.ip,
                                'puerto_remoto': conn.raddr.port,
                                'puerto_local': conn.laddr.port if conn.laddr else None,
                                'proceso': conn.pid,
                                'estado': conn.status
                            })
                    except ValueError:
                        pass  # IP no válida
                        
        except Exception as e:
            logger.error(f"Error analizando conexiones de red: {e}")
        
        return {
            'estadisticas': estadisticas,
            'conexiones_sospechosas': conexiones_sospechosas,
            'nivel_riesgo': 'ALTO' if len(conexiones_sospechosas) > 5 else 
                          'MEDIO' if len(conexiones_sospechosas) > 0 else 'BAJO'
        }

    @staticmethod
    def verificar_integridad_sistema() -> Dict[str, Any]:
        """
        Verifica la integridad básica del sistema.
        
        Returns:
            Diccionario con resultados de verificación
        """
        resultados = {
            'archivos_sistema_modificados': [],
            'servicios_sospechosos': [],
            'usuarios_sospechosos': [],
            'nivel_riesgo': 'BAJO'
        }
        
        try:
            # Verificar archivos críticos del sistema
            archivos_criticos = [
                '/etc/passwd', '/etc/shadow', '/etc/hosts',
                '/etc/resolv.conf', '/etc/sudoers'
            ]
            
            for archivo in archivos_criticos:
                try:
                    ruta = Path(archivo)
                    if ruta.exists():
                        # Verificar permisos
                        permisos = oct(ruta.stat().st_mode)[-3:]
                        if archivo == '/etc/shadow' and permisos != '640':
                            resultados['archivos_sistema_modificados'].append({
                                'archivo': archivo,
                                'problema': f'Permisos incorrectos: {permisos}'
                            })
                        elif archivo == '/etc/passwd' and permisos not in ['644', '640']:
                            resultados['archivos_sistema_modificados'].append({
                                'archivo': archivo,
                                'problema': f'Permisos incorrectos: {permisos}'
                            })
                except Exception as e:
                    logger.warning(f"No se pudo verificar {archivo}: {e}")
            
            # Verificar usuarios con UID 0 (root)
            try:
                with open('/etc/passwd', 'r') as f:
                    for linea in f:
                        campos = linea.strip().split(':')
                        if len(campos) >= 3 and campos[2] == '0' and campos[0] != 'root':
                            resultados['usuarios_sospechosos'].append({
                                'usuario': campos[0],
                                'problema': 'Usuario con UID 0 (privilegios root)'
                            })
            except Exception as e:
                logger.warning(f"No se pudo verificar usuarios: {e}")
            
            # Determinar nivel de riesgo
            total_problemas = (len(resultados['archivos_sistema_modificados']) +
                             len(resultados['servicios_sospechosos']) +
                             len(resultados['usuarios_sospechosos']))
            
            if total_problemas > 5:
                resultados['nivel_riesgo'] = 'CRITICO'
            elif total_problemas > 2:
                resultados['nivel_riesgo'] = 'ALTO'
            elif total_problemas > 0:
                resultados['nivel_riesgo'] = 'MEDIO'
                
        except Exception as e:
            logger.error(f"Error verificando integridad del sistema: {e}")
            resultados['error'] = str(e)
            resultados['nivel_riesgo'] = 'DESCONOCIDO'
        
        return resultados

    @staticmethod
    def sanitizar_entrada(entrada: str, max_longitud: int = 1000) -> str:
        """
        Sanitiza una entrada de usuario para prevenir inyecciones.
        
        Args:
            entrada: Cadena a sanitizar
            max_longitud: Longitud máxima permitida
            
        Returns:
            Cadena sanitizada
        """
        if not isinstance(entrada, str):
            return ""
        
        # Limitar longitud
        entrada = entrada[:max_longitud]
        
        # Remover caracteres peligrosos
        caracteres_peligrosos = ['<', '>', '&', '"', "'", '\\', '/', '|', ';', '`']
        for char in caracteres_peligrosos:
            entrada = entrada.replace(char, '')
        
        # Remover secuencias de escape
        entrada = re.sub(r'\x1b\[[0-9;]*m', '', entrada)  # Códigos ANSI
        entrada = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', entrada)  # Caracteres de control
        
        return entrada.strip()

    @staticmethod
    def verificar_firma_digital(archivo: str) -> Dict[str, Any]:
        """
        Verifica si un archivo tiene firma digital válida (Linux básico).
        
        Args:
            archivo: Ruta al archivo
            
        Returns:
            Diccionario con información de la firma
        """
        resultado = {
            'tiene_firma': False,
            'firma_valida': False,
            'emisor': None,
            'algoritmo': None,
            'error': None
        }
        
        try:
            # Para archivos .deb
            if archivo.endswith('.deb'):
                cmd = ['dpkg-sig', '--verify', archivo]
                try:
                    process = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                    if process.returncode == 0:
                        resultado['tiene_firma'] = True
                        resultado['firma_valida'] = True
                        resultado['algoritmo'] = 'dpkg-sig'
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    resultado['error'] = 'dpkg-sig no disponible'
            
            # Para archivos .rpm
            elif archivo.endswith('.rpm'):
                cmd = ['rpm', '--checksig', archivo]
                try:
                    process = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                    if 'OK' in process.stdout:
                        resultado['tiene_firma'] = True
                        resultado['firma_valida'] = True
                        resultado['algoritmo'] = 'rpm'
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    resultado['error'] = 'rpm no disponible'
            
            else:
                resultado['error'] = 'Tipo de archivo no soportado para verificación de firma'
                
        except Exception as e:
            resultado['error'] = str(e)
        
        return resultado

    @staticmethod
    def generar_reporte_seguridad() -> Dict[str, Any]:
        """
        Genera un reporte completo de seguridad del sistema.
        
        Returns:
            Diccionario con reporte completo
        """
        logger.info("Generando reporte de seguridad del sistema")
        
        reporte = {
            'timestamp': psutil.boot_time(),
            'conexiones_red': ValidadorSeguridad.analizar_conexiones_red(),
            'integridad_sistema': ValidadorSeguridad.verificar_integridad_sistema(),
            'resumen': {
                'nivel_riesgo_general': 'BAJO',
                'problemas_criticos': 0,
                'recomendaciones': []
            }
        }
        
        # Calcular nivel de riesgo general
        niveles = [
            reporte['conexiones_red']['nivel_riesgo'],
            reporte['integridad_sistema']['nivel_riesgo']
        ]
        
        if 'CRITICO' in niveles:
            reporte['resumen']['nivel_riesgo_general'] = 'CRITICO'
        elif 'ALTO' in niveles:
            reporte['resumen']['nivel_riesgo_general'] = 'ALTO'
        elif 'MEDIO' in niveles:
            reporte['resumen']['nivel_riesgo_general'] = 'MEDIO'
        
        # Contar problemas críticos
        reporte['resumen']['problemas_criticos'] = (
            len(reporte['conexiones_red']['conexiones_sospechosas']) +
            len(reporte['integridad_sistema']['archivos_sistema_modificados']) +
            len(reporte['integridad_sistema']['usuarios_sospechosos'])
        )
        
        # Generar recomendaciones
        if reporte['conexiones_red']['estadisticas']['puertos_sospechosos'] > 0:
            reporte['resumen']['recomendaciones'].append(
                'Revisar puertos abiertos sospechosos'
            )
        
        if len(reporte['integridad_sistema']['usuarios_sospechosos']) > 0:
            reporte['resumen']['recomendaciones'].append(
                'Verificar usuarios con privilegios elevados'
            )
        
        if reporte['resumen']['problemas_criticos'] == 0:
            reporte['resumen']['recomendaciones'].append(
                'Sistema aparentemente seguro - mantener monitoreo regular'
            )
        
        logger.info(f"Reporte generado: {reporte['resumen']['problemas_criticos']} problemas detectados")
        
        return reporte
