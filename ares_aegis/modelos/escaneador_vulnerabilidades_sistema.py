#!/usr/bin/env python3
"""
Escaneador de Vulnerabilidades - Ares Aegis
Módulo para escaneo básico de vulnerabilidades del sistema

Los mensajes de este módulo siguen el estilo mitológico inspirado en Ares y la Égida.

Autor: DogSoulDev
Versión: 2.0.0 - El Vigía de las Grietas del Reino
"""

import os
import subprocess
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from ..utilidades.ayuda_logging import configurar_logger_modulo


class VigiaGrietasRealm:
    """El Vigía de las Grietas - Busca debilidades en los cimientos del reino digital."""
    
    def __init__(self):
        """Inicializa el vigía que observa las grietas en los muros del reino."""
        self.logger = configurar_logger_modulo("escaneador_vulnerabilidades")
        
        # Rutas críticas del reino que deben ser vigiladas
        self.rutas_criticas = [
            '/etc/passwd',
            '/etc/shadow',
            '/etc/sudoers',
            '/etc/ssh/sshd_config',
            '/etc/hosts',
            '/etc/crontab',
            '/var/log/',
            '/tmp/',
            '/home/',
            '/root/'
        ]
        
        # Servicios que deben ser vigilados por su naturaleza peligrosa
        self.servicios_criticos = [
            'ssh', 'sshd', 'apache2', 'nginx', 'mysql', 'postgresql', 
            'ftp', 'telnet', 'rsh', 'rlogin', 'finger'
        ]
        
        self.logger.info("El vigía de las grietas ha comenzado su vigilancia eterna sobre el reino")
    
    def verificar_permisos_archivos_criticos(self) -> Dict[str, Any]:
        """
        Examina los permisos de los pergaminos sagrados del reino.
        
        Returns:
            Dict con el estado de los permisos de archivos críticos
        """
        self.logger.info("Iniciando inspección de permisos en los pergaminos sagrados")
        
        vulnerabilidades = []
        archivos_seguros = []
        archivos_no_encontrados = []
        
        # Configuraciones seguras esperadas para cada archivo
        permisos_esperados = {
            '/etc/passwd': '644',
            '/etc/shadow': '640',
            '/etc/sudoers': '440',
            '/etc/ssh/sshd_config': '644',
            '/etc/hosts': '644',
            '/etc/crontab': '644'
        }
        
        for ruta in self.rutas_criticas:
            if os.path.isfile(ruta):
                try:
                    stat_info = os.stat(ruta)
                    permisos_actuales = oct(stat_info.st_mode)[-3:]
                    
                    archivo_info = {
                        'ruta': ruta,
                        'permisos_actuales': permisos_actuales,
                        'propietario_uid': stat_info.st_uid,
                        'grupo_gid': stat_info.st_gid
                    }
                    
                    # Verificar si los permisos son seguros
                    permisos_seguros = permisos_esperados.get(ruta)
                    
                    if permisos_seguros and permisos_actuales != permisos_seguros:
                        archivo_info['permisos_esperados'] = permisos_seguros
                        archivo_info['nivel_riesgo'] = self._evaluar_riesgo_permisos(ruta, permisos_actuales)
                        archivo_info['mensaje'] = f"Los permisos del pergamino sagrado '{ruta}' despiertan inquietud en el vigía"
                        vulnerabilidades.append(archivo_info)
                    
                    # Verificar permisos excesivamente permisivos
                    elif self._son_permisos_peligrosos(permisos_actuales):
                        archivo_info['nivel_riesgo'] = 'ALTO'
                        archivo_info['mensaje'] = f"¡El pergamino '{ruta}' está expuesto a miradas impías! Permisos demasiado permisivos"
                        vulnerabilidades.append(archivo_info)
                    
                    else:
                        archivo_info['mensaje'] = f"El pergamino '{ruta}' está protegido bajo el sello divino"
                        archivos_seguros.append(archivo_info)
                
                except Exception as e:
                    self.logger.error(f"Error examinando permisos de {ruta}: {e}")
                    vulnerabilidades.append({
                        'ruta': ruta,
                        'nivel_riesgo': 'MEDIO',
                        'mensaje': f"Una tormenta impide examinar los permisos del pergamino: {e}"
                    })
            
            elif os.path.isdir(ruta):
                # Verificar directorios críticos
                try:
                    stat_info = os.stat(ruta)
                    permisos_dir = oct(stat_info.st_mode)[-3:]
                    
                    if self._son_permisos_directorio_peligrosos(ruta, permisos_dir):
                        vulnerabilidades.append({
                            'ruta': ruta,
                            'permisos_actuales': permisos_dir,
                            'nivel_riesgo': 'ALTO',
                            'mensaje': f"El directorio sagrado '{ruta}' permite acceso a almas impías"
                        })
                
                except Exception as e:
                    self.logger.error(f"Error examinando directorio {ruta}: {e}")
            
            else:
                archivos_no_encontrados.append(ruta)
        
        return {
            'vulnerabilidades_detectadas': len(vulnerabilidades),
            'archivos_seguros': len(archivos_seguros),
            'archivos_no_encontrados': len(archivos_no_encontrados),
            'vulnerabilidades': vulnerabilidades,
            'archivos_seguros_lista': archivos_seguros,
            'mensaje_general': self._generar_mensaje_permisos(len(vulnerabilidades))
        }
    
    def _son_permisos_peligrosos(self, permisos: str) -> bool:
        """Evalúa si los permisos son peligrosamente permisivos."""
        # Verificar escritura para otros (worldwritable)
        if permisos[2] in ['2', '3', '6', '7']:
            return True
        
        # Verificar si archivos críticos tienen permisos de ejecución para otros
        if permisos[2] in ['1', '3', '5', '7']:
            return True
        
        return False
    
    def _son_permisos_directorio_peligrosos(self, ruta: str, permisos: str) -> bool:
        """Evalúa si los permisos de directorio son peligrosos."""
        # Directorios como /tmp/ pueden ser world-writable por diseño
        if ruta in ['/tmp/', '/var/tmp/']:
            return False
        
        # Otros directorios críticos no deberían ser world-writable
        if permisos[2] in ['2', '3', '6', '7']:
            return True
        
        return False
    
    def _evaluar_riesgo_permisos(self, ruta: str, permisos: str) -> str:
        """Evalúa el nivel de riesgo basado en el archivo y permisos."""
        archivos_criticos = ['/etc/shadow', '/etc/sudoers']
        
        if ruta in archivos_criticos:
            return 'CRITICO'
        elif self._son_permisos_peligrosos(permisos):
            return 'ALTO'
        else:
            return 'MEDIO'
    
    def verificar_servicios_expuestos(self) -> Dict[str, Any]:
        """
        Examina los servicios que escuchan en los puertos del reino.
        
        Returns:
            Dict con información sobre servicios expuestos
        """
        self.logger.info("Inspeccionando servicios que escuchan en las puertas del reino")
        
        servicios_detectados = []
        servicios_riesgosos = []
        
        try:
            # Usar netstat para obtener servicios escuchando
            resultado = subprocess.run(
                ['netstat', '-tuln'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if resultado.returncode == 0:
                lineas = resultado.stdout.split('\n')
                
                for linea in lineas:
                    if 'LISTEN' in linea or 'LISTENING' in linea:
                        partes = linea.split()
                        if len(partes) >= 4:
                            direccion_local = partes[3]
                            
                            # Extraer puerto
                            if ':' in direccion_local:
                                puerto = direccion_local.split(':')[-1]
                                
                                servicio_info = {
                                    'puerto': puerto,
                                    'direccion': direccion_local,
                                    'protocolo': partes[0] if partes else 'desconocido'
                                }
                                
                                # Identificar servicio por puerto
                                nombre_servicio = self._identificar_servicio_por_puerto(puerto)
                                if nombre_servicio:
                                    servicio_info['servicio'] = nombre_servicio
                                    
                                    # Evaluar riesgo del servicio
                                    riesgo = self._evaluar_riesgo_servicio(nombre_servicio, puerto)
                                    servicio_info['nivel_riesgo'] = riesgo
                                    servicio_info['mensaje'] = self._generar_mensaje_servicio(nombre_servicio, riesgo)
                                    
                                    if riesgo in ['ALTO', 'CRITICO']:
                                        servicios_riesgosos.append(servicio_info)
                                
                                servicios_detectados.append(servicio_info)
        
        except subprocess.TimeoutExpired:
            self.logger.warning("El oráculo netstat no respondió en tiempo divino")
            return {
                'servicios_detectados': 0,
                'servicios_riesgosos': 0,
                'mensaje': 'El oráculo de los puertos permanece en silencio - tiempo de consulta excedido'
            }
        
        except Exception as e:
            self.logger.error(f"Error verificando servicios: {e}")
            return {
                'servicios_detectados': 0,
                'servicios_riesgosos': 0,
                'mensaje': f'Una tormenta impide consultar a los guardianes de los puertos: {e}'
            }
        
        return {
            'servicios_detectados': len(servicios_detectados),
            'servicios_riesgosos': len(servicios_riesgosos),
            'servicios': servicios_detectados,
            'servicios_alto_riesgo': servicios_riesgosos,
            'mensaje_general': self._generar_mensaje_servicios(len(servicios_riesgosos))
        }
    
    def _identificar_servicio_por_puerto(self, puerto: str) -> Optional[str]:
        """Identifica el servicio basándose en el puerto."""
        puertos_conocidos = {
            '22': 'ssh',
            '23': 'telnet',
            '21': 'ftp',
            '80': 'http',
            '443': 'https',
            '25': 'smtp',
            '53': 'dns',
            '3306': 'mysql',
            '5432': 'postgresql',
            '6379': 'redis',
            '27017': 'mongodb',
            '139': 'netbios',
            '445': 'smb',
            '110': 'pop3',
            '143': 'imap',
            '993': 'imaps',
            '995': 'pop3s'
        }
        
        return puertos_conocidos.get(puerto)
    
    def _evaluar_riesgo_servicio(self, servicio: str, puerto: str) -> str:
        """Evalúa el riesgo de un servicio específico."""
        servicios_alto_riesgo = ['telnet', 'rsh', 'rlogin', 'finger', 'ftp']
        servicios_medio_riesgo = ['ssh', 'http', 'smtp', 'dns']
        
        if servicio in servicios_alto_riesgo:
            return 'CRITICO'
        elif servicio == 'ssh' and puerto != '22':
            return 'MEDIO'  # SSH en puerto no estándar puede ser bueno o malo
        elif servicio in servicios_medio_riesgo:
            return 'MEDIO'
        elif puerto in ['80', '443']:
            return 'BAJO'  # HTTP/HTTPS normalmente aceptables
        else:
            return 'MEDIO'  # Servicios desconocidos requieren investigación
    
    def _generar_mensaje_servicio(self, servicio: str, riesgo: str) -> str:
        """Genera mensaje descriptivo para un servicio."""
        mensajes = {
            'telnet': 'El demonio Telnet susurra secretos sin protección - ¡gran peligro!',
            'ftp': 'El puerto FTP está abierto - las credenciales pueden viajar desnudas',
            'ssh': 'El guardián SSH vigila la puerta - mantén sus llaves seguras',
            'http': 'El heraldo HTTP proclama contenido al reino',
            'https': 'El mensajero HTTPS porta el sello de la encriptación',
            'mysql': 'La base de datos MySQL late en el corazón del sistema',
            'postgresql': 'El oráculo PostgreSQL guarda secretos en sus tablas'
        }
        
        return mensajes.get(servicio, f'El servicio {servicio} escucha en las sombras del reino')
    
    def verificar_configuracion_ssh(self) -> Dict[str, Any]:
        """
        Examina la configuración del guardián SSH.
        
        Returns:
            Dict con análisis de la configuración SSH
        """
        ruta_config = '/etc/ssh/sshd_config'
        
        if not os.path.exists(ruta_config):
            return {
                'configuracion_encontrada': False,
                'mensaje': 'El pergamino de configuración del guardián SSH no se encuentra en el templo'
            }
        
        configuraciones_inseguras = []
        configuraciones_seguras = []
        
        # Configuraciones que deben ser verificadas
        verificaciones = {
            'PermitRootLogin': {'seguro': 'no', 'riesgo': 'CRITICO'},
            'PasswordAuthentication': {'seguro': 'no', 'riesgo': 'ALTO'},
            'PermitEmptyPasswords': {'seguro': 'no', 'riesgo': 'CRITICO'},
            'X11Forwarding': {'seguro': 'no', 'riesgo': 'MEDIO'},
            'UsePAM': {'seguro': 'yes', 'riesgo': 'MEDIO'},
            'Protocol': {'seguro': '2', 'riesgo': 'ALTO'}
        }
        
        try:
            with open(ruta_config, 'r') as archivo:
                contenido = archivo.read()
            
            for config, valores in verificaciones.items():
                patron = rf'^\s*{config}\s+(\S+)'
                coincidencia = re.search(patron, contenido, re.MULTILINE | re.IGNORECASE)
                
                if coincidencia:
                    valor_actual = coincidencia.group(1).lower()
                    valor_seguro = valores['seguro'].lower()
                    
                    config_info = {
                        'configuracion': config,
                        'valor_actual': valor_actual,
                        'valor_seguro': valor_seguro,
                        'nivel_riesgo': valores['riesgo']
                    }
                    
                    if valor_actual != valor_seguro:
                        config_info['mensaje'] = f"El guardián SSH permite '{config}' con valor inseguro: {valor_actual}"
                        configuraciones_inseguras.append(config_info)
                    else:
                        config_info['mensaje'] = f"El guardián SSH protege correctamente '{config}'"
                        configuraciones_seguras.append(config_info)
                else:
                    # Configuración no encontrada - usar valor por defecto
                    configuraciones_inseguras.append({
                        'configuracion': config,
                        'valor_actual': 'no especificado (por defecto)',
                        'valor_seguro': valores['seguro'],
                        'nivel_riesgo': 'MEDIO',
                        'mensaje': f"La configuración '{config}' no está explícitamente definida"
                    })
        
        except Exception as e:
            return {
                'configuracion_encontrada': True,
                'error': True,
                'mensaje': f'Una tormenta impide leer el pergamino del guardián SSH: {e}'
            }
        
        return {
            'configuracion_encontrada': True,
            'configuraciones_inseguras': len(configuraciones_inseguras),
            'configuraciones_seguras': len(configuraciones_seguras),
            'detalles_inseguras': configuraciones_inseguras,
            'detalles_seguras': configuraciones_seguras,
            'mensaje_general': self._generar_mensaje_ssh(len(configuraciones_inseguras))
        }
    
    def _generar_mensaje_permisos(self, num_vulnerabilidades: int) -> str:
        """Genera mensaje general sobre permisos."""
        if num_vulnerabilidades == 0:
            return "Los pergaminos sagrados están protegidos bajo el sello divino"
        elif num_vulnerabilidades <= 2:
            return f"Se detectan {num_vulnerabilidades} grietas menores en las protecciones del reino"
        else:
            return f"¡Alerta! {num_vulnerabilidades} vulnerabilidades graves comprometen los pergaminos sagrados"
    
    def _generar_mensaje_servicios(self, num_riesgosos: int) -> str:
        """Genera mensaje general sobre servicios."""
        if num_riesgosos == 0:
            return "Los guardianes de los puertos mantienen vigilancia segura"
        elif num_riesgosos <= 2:
            return f"Se detectan {num_riesgosos} guardianes que requieren atención divina"
        else:
            return f"¡Peligro! {num_riesgosos} guardianes exponen el reino a amenazas"
    
    def _generar_mensaje_ssh(self, num_inseguras: int) -> str:
        """Genera mensaje sobre configuración SSH."""
        if num_inseguras == 0:
            return "El guardián SSH está perfectamente configurado para defender el reino"
        elif num_inseguras <= 2:
            return f"El guardián SSH tiene {num_inseguras} configuraciones que requieren atención"
        else:
            return f"¡El guardián SSH está mal configurado! {num_inseguras} vulnerabilidades detectadas"


class EscaneadorVulnerabilidadesSistema:
    """El Gran Inspector de Vulnerabilidades - Orquesta todos los análisis de seguridad."""
    
    def __init__(self, siem=None):
        """Inicializa el gran inspector de vulnerabilidades del reino."""
        self.logger = configurar_logger_modulo("escaneador_vulnerabilidades_principal")
        self.siem = siem
        self.vigia_grietas = VigiaGrietasRealm()
        
        self.logger.info("El gran inspector de vulnerabilidades ha comenzado su ronda de vigilancia")
    
    def escaneo_completo_vulnerabilidades(self) -> Dict[str, Any]:
        """
        Realiza un escaneo completo de vulnerabilidades del sistema.
        
        Returns:
            Dict con resultados completos del escaneo
        """
        self.logger.info("Iniciando escaneo completo de vulnerabilidades del reino")
        
        resultado = {
            'timestamp': datetime.now().isoformat(),
            'estado': 'iniciado',
            'vulnerabilidades_totales': 0,
            'nivel_riesgo_general': 'BAJO'
        }
        
        try:
            # Verificar permisos de archivos críticos
            permisos_resultado = self.vigia_grietas.verificar_permisos_archivos_criticos()
            resultado['permisos_archivos'] = permisos_resultado
            
            # Verificar servicios expuestos
            servicios_resultado = self.vigia_grietas.verificar_servicios_expuestos()
            resultado['servicios_expuestos'] = servicios_resultado
            
            # Verificar configuración SSH
            ssh_resultado = self.vigia_grietas.verificar_configuracion_ssh()
            resultado['configuracion_ssh'] = ssh_resultado
            
            # Calcular vulnerabilidades totales y riesgo general
            vulnerabilidades_totales = (
                permisos_resultado.get('vulnerabilidades_detectadas', 0) +
                servicios_resultado.get('servicios_riesgosos', 0) +
                ssh_resultado.get('configuraciones_inseguras', 0)
            )
            
            resultado['vulnerabilidades_totales'] = vulnerabilidades_totales
            resultado['nivel_riesgo_general'] = self._evaluar_riesgo_general(vulnerabilidades_totales)
            resultado['mensaje_general'] = self._generar_mensaje_general(
                vulnerabilidades_totales, 
                resultado['nivel_riesgo_general']
            )
            
            resultado['estado'] = 'completado'
            resultado['recomendaciones'] = self._generar_recomendaciones(resultado)
            
            self.logger.info(f"Escaneo completado: {vulnerabilidades_totales} vulnerabilidades detectadas")
        
        except Exception as e:
            resultado['estado'] = 'error'
            resultado['mensaje'] = f'Una tormenta divina ha interrumpido la inspección: {e}'
            self.logger.error(f"Error en escaneo de vulnerabilidades: {e}")
        
        return resultado
    
    def _evaluar_riesgo_general(self, vulnerabilidades_totales: int) -> str:
        """Evalúa el riesgo general basado en el número total de vulnerabilidades."""
        if vulnerabilidades_totales >= 10:
            return 'CRITICO'
        elif vulnerabilidades_totales >= 5:
            return 'ALTO'
        elif vulnerabilidades_totales >= 2:
            return 'MEDIO'
        else:
            return 'BAJO'
    
    def _generar_mensaje_general(self, vulnerabilidades: int, nivel_riesgo: str) -> str:
        """Genera mensaje general del estado de seguridad."""
        mensajes = {
            'BAJO': f"El reino está bien protegido. {vulnerabilidades} grietas menores detectadas",
            'MEDIO': f"El reino requiere atención. {vulnerabilidades} vulnerabilidades requieren acción",
            'ALTO': f"¡El reino está en peligro! {vulnerabilidades} vulnerabilidades críticas detectadas",
            'CRITICO': f"¡ALERTA MÁXIMA! {vulnerabilidades} vulnerabilidades comprometen gravemente el reino"
        }
        
        return mensajes.get(nivel_riesgo, f"Estado de seguridad: {vulnerabilidades} vulnerabilidades")
    
    def _generar_recomendaciones(self, resultado: Dict[str, Any]) -> List[str]:
        """Genera recomendaciones basadas en los resultados del escaneo."""
        recomendaciones = []
        
        # Recomendaciones para permisos
        permisos = resultado.get('permisos_archivos', {})
        if permisos.get('vulnerabilidades_detectadas', 0) > 0:
            recomendaciones.append("Corrige los permisos de archivos críticos para fortalecer las defensas del reino")
        
        # Recomendaciones para servicios
        servicios = resultado.get('servicios_expuestos', {})
        if servicios.get('servicios_riesgosos', 0) > 0:
            recomendaciones.append("Revisa los servicios expuestos y desactiva aquellos que no sean necesarios")
        
        # Recomendaciones para SSH
        ssh = resultado.get('configuracion_ssh', {})
        if ssh.get('configuraciones_inseguras', 0) > 0:
            recomendaciones.append("Fortalece la configuración del guardián SSH para mejor protección")
        
        # Recomendación general
        if resultado.get('nivel_riesgo_general') in ['ALTO', 'CRITICO']:
            recomendaciones.append("Ejecuta medidas de seguridad inmediatas - el reino está en peligro")
        
        return recomendaciones
    
    def generar_reporte_vulnerabilidades_markdown(self, resultado: Dict[str, Any]) -> str:
        """
        Genera un reporte detallado de vulnerabilidades en formato Markdown.
        
        Args:
            resultado: Resultado del escaneo de vulnerabilidades
            
        Returns:
            Reporte en formato Markdown
        """
        md = f"# 🛡️ Reporte de Vulnerabilidades del Reino\n\n"
        md += f"**Fecha de Inspección:** {resultado['timestamp']}\n"
        md += f"**Estado del Escaneo:** {resultado['estado']}\n"
        md += f"**Vulnerabilidades Totales:** {resultado.get('vulnerabilidades_totales', 0)}\n"
        md += f"**Nivel de Riesgo General:** {resultado.get('nivel_riesgo_general', 'DESCONOCIDO')}\n\n"
        
        if resultado['estado'] != 'completado':
            md += f"**Mensaje:** {resultado.get('mensaje', 'Inspección incompleta')}\n"
            return md
        
        md += f"## 📊 Resumen del Estado del Reino\n\n"
        md += f"{resultado.get('mensaje_general', 'Sin mensaje general')}\n\n"
        
        # Permisos de archivos
        permisos = resultado.get('permisos_archivos', {})
        if permisos:
            md += f"## 📜 Estado de los Pergaminos Sagrados\n\n"
            md += f"- **Vulnerabilidades detectadas:** {permisos.get('vulnerabilidades_detectadas', 0)}\n"
            md += f"- **Archivos seguros:** {permisos.get('archivos_seguros', 0)}\n"
            md += f"- **Mensaje:** {permisos.get('mensaje_general', 'Sin información')}\n\n"
            
            vulnerabilidades_permisos = permisos.get('vulnerabilidades', [])
            if vulnerabilidades_permisos:
                md += f"### Vulnerabilidades de Permisos Detectadas\n\n"
                for vuln in vulnerabilidades_permisos[:10]:  # Limitar a 10
                    md += f"- **{vuln['ruta']}**: {vuln.get('mensaje', 'Sin descripción')}\n"
                md += "\n"
        
        # Servicios expuestos
        servicios = resultado.get('servicios_expuestos', {})
        if servicios:
            md += f"## 🚪 Estado de los Guardianes de los Puertos\n\n"
            md += f"- **Servicios detectados:** {servicios.get('servicios_detectados', 0)}\n"
            md += f"- **Servicios riesgosos:** {servicios.get('servicios_riesgosos', 0)}\n"
            md += f"- **Mensaje:** {servicios.get('mensaje_general', 'Sin información')}\n\n"
            
            servicios_riesgo = servicios.get('servicios_alto_riesgo', [])
            if servicios_riesgo:
                md += f"### Servicios de Alto Riesgo\n\n"
                for servicio in servicios_riesgo:
                    md += f"- **Puerto {servicio['puerto']}** ({servicio.get('servicio', 'desconocido')}): {servicio.get('mensaje', 'Sin descripción')}\n"
                md += "\n"
        
        # Configuración SSH
        ssh = resultado.get('configuracion_ssh', {})
        if ssh and ssh.get('configuracion_encontrada', False):
            md += f"## 🔐 Estado del Guardián SSH\n\n"
            md += f"- **Configuraciones inseguras:** {ssh.get('configuraciones_inseguras', 0)}\n"
            md += f"- **Configuraciones seguras:** {ssh.get('configuraciones_seguras', 0)}\n"
            md += f"- **Mensaje:** {ssh.get('mensaje_general', 'Sin información')}\n\n"
            
            configs_inseguras = ssh.get('detalles_inseguras', [])
            if configs_inseguras:
                md += f"### Configuraciones SSH Inseguras\n\n"
                for config in configs_inseguras:
                    md += f"- **{config['configuracion']}**: {config.get('mensaje', 'Sin descripción')}\n"
                md += "\n"
        
        # Recomendaciones
        recomendaciones = resultado.get('recomendaciones', [])
        if recomendaciones:
            md += f"## ⚔️ Decretos del Égida (Recomendaciones)\n\n"
            for recom in recomendaciones:
                md += f"- {recom}\n"
            md += "\n"
        
        md += "---\n\n"
        md += "*Inspección completada por el Gran Inspector de Vulnerabilidades del Égida*\n"
        
        return md
