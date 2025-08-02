#!/usr/bin/env python3
"""
Creado por DogSoulDev (https://github.com/DogSoulDev)
Todos los derechos reservados. Este código es propietario y confidencial.

Escaneador de Vulnerabilidades del Sistema para Kali Linux - Ares Aegis
"""

import os
import subprocess
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

from .modelo_hallazgos_seguridad import (
    Hallazgo, HallazgoAutenticacion, HallazgoConfiguracion, HallazgoPermisos,
    TipoHallazgo, PrioridadHallazgo, EstadoHallazgo, ResultadoEscaneo
)
from .modelo_utilidades_sistema import utilidades_sistema
from .modelo_auditor_autenticacion import AuditorPAM
from ..utils.ayuda_logging import configurar_logger_modulo


class VigiaGrietasRealm:
    """
    El Vigía de las Grietas - Busca debilidades en los cimientos del reino digital.
    Refactorizado siguiendo principios SOLID/DRY para Kali Linux.
    """
    
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
        
        # Puertos conocidos y su clasificación de riesgo
        self.puertos_conocidos = {
            '21': {'servicio': 'ftp', 'riesgo': PrioridadHallazgo.ALTA},
            '22': {'servicio': 'ssh', 'riesgo': PrioridadHallazgo.MEDIA},
            '23': {'servicio': 'telnet', 'riesgo': PrioridadHallazgo.CRITICA},
            '25': {'servicio': 'smtp', 'riesgo': PrioridadHallazgo.MEDIA},
            '53': {'servicio': 'dns', 'riesgo': PrioridadHallazgo.BAJA},
            '80': {'servicio': 'http', 'riesgo': PrioridadHallazgo.BAJA},
            '110': {'servicio': 'pop3', 'riesgo': PrioridadHallazgo.MEDIA},
            '143': {'servicio': 'imap', 'riesgo': PrioridadHallazgo.MEDIA},
            '443': {'servicio': 'https', 'riesgo': PrioridadHallazgo.BAJA},
            '993': {'servicio': 'imaps', 'riesgo': PrioridadHallazgo.BAJA},
            '995': {'servicio': 'pop3s', 'riesgo': PrioridadHallazgo.BAJA},
            '3306': {'servicio': 'mysql', 'riesgo': PrioridadHallazgo.ALTA},
            '5432': {'servicio': 'postgresql', 'riesgo': PrioridadHallazgo.ALTA},
            '6379': {'servicio': 'redis', 'riesgo': PrioridadHallazgo.ALTA},
            '27017': {'servicio': 'mongodb', 'riesgo': PrioridadHallazgo.ALTA}
        }
        
        self.logger.info("🔍 El vigía de las grietas ha comenzado su vigilancia eterna sobre el reino")
    
    def verificar_permisos_archivos_criticos(self) -> List[Hallazgo]:
        """
        Examina los permisos de los pergaminos sagrados del reino.
        Refactorizado para devolver objetos Hallazgo consistentes.
        
        Returns:
            Lista de hallazgos relacionados con permisos
        """
        self.logger.info("🔐 Iniciando inspección de permisos en los pergaminos sagrados")
        hallazgos = []
        
        # Configuraciones seguras esperadas para cada archivo
        permisos_esperados = {
            '/etc/passwd': {'permisos': '644', 'propietario': 'root'},
            '/etc/shadow': {'permisos': '640', 'propietario': 'root'},
            '/etc/sudoers': {'permisos': '440', 'propietario': 'root'},
            '/etc/ssh/sshd_config': {'permisos': '644', 'propietario': 'root'},
            '/etc/hosts': {'permisos': '644', 'propietario': 'root'},
            '/etc/crontab': {'permisos': '644', 'propietario': 'root'}
        }
        
        for ruta in self.rutas_criticas:
            if not os.path.exists(ruta):
                continue
                
            if os.path.isfile(ruta):
                resultado = self._verificar_permisos_archivo(ruta, permisos_esperados.get(ruta, {}))
                if resultado:
                    hallazgos.append(resultado)
            elif os.path.isdir(ruta):
                resultado = self._verificar_permisos_directorio(ruta)
                if resultado:
                    hallazgos.append(resultado)
        
        self.logger.info(f"📊 Inspección de permisos completada: {len(hallazgos)} problemas detectados")
        return hallazgos
    
    def _verificar_permisos_archivo(self, ruta: str, config_esperada: Dict[str, str]) -> Optional[Hallazgo]:
        """Verifica permisos de un archivo específico."""
        if not config_esperada:
            return None
            
        resultado = utilidades_sistema.validar_permisos_archivo_critico(
            ruta,
            config_esperada.get('permisos', '644'),
            config_esperada.get('propietario', 'root')
        )
        
        if not resultado['es_valido'] and resultado['informacion']:
            problemas = "; ".join(resultado['problemas'])
            
            # Determinar prioridad basada en el archivo
            prioridad = PrioridadHallazgo.ALTA if '/shadow' in ruta or '/sudoers' in ruta else PrioridadHallazgo.MEDIA
            
            return HallazgoPermisos(
                tipo_anomalia=TipoHallazgo.PERMISOS_INCORRECTOS,
                ruta_afectada=ruta,
                detalle_especifico=f"Permisos incorrectos en pergamino sagrado: {problemas}",
                prioridad=prioridad,
                recomendacion=f"Ejecutar: sudo chown {config_esperada['propietario']}:{config_esperada['propietario']} {ruta} && sudo chmod {config_esperada['permisos']} {ruta}",
                fecha_deteccion=datetime.now(),
                permisos_actuales=resultado['informacion']['permisos_octales'],
                permisos_recomendados=config_esperada['permisos'],
                propietario_actual=resultado['informacion']['propietario'],
                propietario_recomendado=config_esperada['propietario']
            )
        
        return None
    
    def _verificar_permisos_directorio(self, ruta: str) -> Optional[Hallazgo]:
        """Verifica permisos de un directorio crítico."""
        info = utilidades_sistema.obtener_informacion_permisos(ruta)
        if not info:
            return None
        
        # Verificar permisos peligrosos en directorios
        if self._son_permisos_directorio_peligrosos(ruta, info['permisos_octales']):
            return HallazgoPermisos(
                tipo_anomalia=TipoHallazgo.PERMISOS_INCORRECTOS,
                ruta_afectada=ruta,
                detalle_especifico=f"Directorio sagrado '{ruta}' tiene permisos peligrosos: {info['permisos_octales']}",
                prioridad=PrioridadHallazgo.ALTA,
                recomendacion=f"Revisar y restringir permisos del directorio {ruta}",
                fecha_deteccion=datetime.now(),
                permisos_actuales=info['permisos_octales'],
                permisos_recomendados="755",
                propietario_actual=info['propietario'],
                propietario_recomendado="root"
            )
        
        return None
    
    def _son_permisos_directorio_peligrosos(self, ruta: str, permisos: str) -> bool:
        """Evalúa si los permisos de directorio son peligrosos."""
        # Directorios como /tmp/ pueden ser world-writable por diseño
        if ruta in ['/tmp/', '/var/tmp/']:
            return False
        
        # Otros directorios críticos no deberían ser world-writable
        if permisos[2] in ['2', '3', '6', '7']:
            return True
        
        return False
    
    def verificar_servicios_expuestos(self) -> List[Hallazgo]:
        """
        Examina los servicios que escuchan en los puertos del reino.
        Refactorizado para devolver objetos Hallazgo consistentes.
        
        Returns:
            Lista de hallazgos relacionados con servicios expuestos
        """
        self.logger.info("🚪 Inspeccionando servicios que escuchan en las puertas del reino")
        hallazgos = []
        
        try:
            # Usar utilidades_sistema para obtener puertos
            puertos = utilidades_sistema.obtener_puertos_escuchando()
            
            for puerto_info in puertos:
                hallazgo = self._evaluar_puerto_expuesto(puerto_info)
                if hallazgo:
                    hallazgos.append(hallazgo)
            
            self.logger.info(f"🔍 Verificación de servicios completada: {len(hallazgos)} servicios riesgosos detectados")
            
        except Exception as e:
            self.logger.error(f"Error verificando servicios: {e}")
            hallazgo_error = Hallazgo(
                tipo_anomalia=TipoHallazgo.VULNERABILIDAD_SISTEMA,
                ruta_afectada="/proc/net",
                detalle_especifico=f"Error verificando servicios expuestos: {e}",
                prioridad=PrioridadHallazgo.MEDIA,
                recomendacion="Verificar manualmente los servicios en ejecución con 'netstat -tuln'",
                fecha_deteccion=datetime.now()
            )
            hallazgos.append(hallazgo_error)
        
        return hallazgos
    
    def _evaluar_puerto_expuesto(self, puerto_info: Dict[str, Any]) -> Optional[Hallazgo]:
        """Evalúa si un puerto expuesto representa un riesgo."""
        puerto_str = str(puerto_info['puerto'])
        info_puerto = self.puertos_conocidos.get(puerto_str, {
            'servicio': 'desconocido',
            'riesgo': PrioridadHallazgo.MEDIA
        })
        
        # Solo reportar servicios de riesgo medio o alto
        if info_puerto['riesgo'] in [PrioridadHallazgo.MEDIA, PrioridadHallazgo.ALTA, PrioridadHallazgo.CRITICA]:
            mensaje = self._generar_mensaje_servicio(info_puerto['servicio'], info_puerto['riesgo'])
            
            return Hallazgo(
                tipo_anomalia=TipoHallazgo.SERVICIO_EXPUESTO,
                ruta_afectada=f"Puerto {puerto_info['puerto']}/{puerto_info['protocolo']}",
                detalle_especifico=f"Servicio {info_puerto['servicio']} escuchando en puerto {puerto_info['puerto']}: {mensaje}",
                prioridad=info_puerto['riesgo'],
                recomendacion=self._generar_recomendacion_puerto(info_puerto['servicio'], puerto_info),
                fecha_deteccion=datetime.now(),
                metadatos={
                    'puerto': puerto_info['puerto'],
                    'protocolo': puerto_info['protocolo'],
                    'servicio': info_puerto['servicio'],
                    'direccion': puerto_info['direccion'],
                    'solo_local': puerto_info.get('solo_local', False)
                }
            )
        
        return None
    
    def _generar_mensaje_servicio(self, servicio: str, riesgo: PrioridadHallazgo) -> str:
        """Genera mensaje descriptivo para un servicio según su riesgo."""
        mensajes = {
            'telnet': 'El demonio Telnet susurra secretos sin protección - ¡gran peligro!',
            'ftp': 'El puerto FTP está abierto - las credenciales pueden viajar desnudas',
            'ssh': 'El guardián SSH vigila la puerta - mantén sus llaves seguras',
            'http': 'El heraldo HTTP proclama contenido al reino',
            'https': 'El mensajero HTTPS porta el sello de la encriptación',
            'mysql': 'La base de datos MySQL late en el corazón del sistema',
            'postgresql': 'El oráculo PostgreSQL guarda secretos en sus tablas',
            'redis': 'El guardián Redis almacena tesoros en memoria',
            'mongodb': 'El archivo MongoDB contiene pergaminos digitales'
        }
        
        mensaje_base = mensajes.get(servicio, f'El servicio {servicio} escucha en las sombras del reino')
        
        if riesgo == PrioridadHallazgo.CRITICA:
            return f"¡PELIGRO EXTREMO! {mensaje_base}"
        elif riesgo == PrioridadHallazgo.ALTA:
            return f"⚠️  ALTO RIESGO: {mensaje_base}"
        else:
            return mensaje_base
    
    def _generar_recomendacion_puerto(self, servicio: str, puerto_info: Dict[str, Any]) -> str:
        """Genera recomendación específica para un servicio."""
        recomendaciones = {
            'telnet': 'DESHABILITAR inmediatamente Telnet y usar SSH en su lugar',
            'ftp': 'Considerar deshabilitar FTP o migrar a SFTP/FTPS',
            'ssh': 'Verificar configuración SSH: deshabilitar root login, usar claves SSH',
            'mysql': 'Verificar que MySQL no esté expuesto externamente, usar firewall',
            'postgresql': 'Configurar autenticación fuerte y restricciones de red',
            'redis': 'Configurar autenticación Redis y restricciones de red',
            'mongodb': 'Habilitar autenticación MongoDB y configurar firewall'
        }
        
        recomendacion_base = recomendaciones.get(servicio, f'Revisar necesidad del servicio {servicio}')
        
        if not puerto_info.get('solo_local', False):
            recomendacion_base += f" - Considerar restricción a localhost solamente"
        
        return recomendacion_base
    
    def auditar_permisos_criticos(self) -> List[Hallazgo]:
        """
        Audita permisos de archivos críticos del sistema.
        Método principal que integra toda la funcionalidad de auditoría.
        
        Returns:
            Lista de hallazgos relacionados con permisos incorrectos
        """
        self.logger.info("🔐 Iniciando auditoría completa de permisos críticos del sistema")
        hallazgos = []
        
        try:
            # Definir archivos críticos para auditoría
            archivos_criticos = {
                'passwd': '/etc/passwd',
                'shadow': '/etc/shadow', 
                'group': '/etc/group',
                'gshadow': '/etc/gshadow',
                'sudoers': '/etc/sudoers',
                'ssh_config': '/etc/ssh/sshd_config',
                'hosts': '/etc/hosts',
                'crontab': '/etc/crontab'
            }
            
            # Verificar cada archivo crítico
            for archivo, ruta_real in archivos_criticos.items():
                if os.path.exists(ruta_real):  # Usar os.path.exists para compatibilidad
                    # Evaluar cada archivo crítico
                    problema = self._verificar_archivo_critico(archivo, ruta_real)
                    if problema:
                        hallazgos.append(problema)
                        
            # Verificar permisos de directorios importantes
            directorios_importantes = [
                '/etc/passwd', '/etc/shadow', '/etc/sudoers',
                '/root', '/home', '/var/log'
            ]
            
            for directorio in directorios_importantes:
                if os.path.exists(directorio):  # Usar os.path.exists para compatibilidad
                    problema = self._verificar_permisos_directorio(directorio)
                    if problema:
                        hallazgos.append(problema)
                        
            self.logger.info(f"🔐 Auditoría de permisos completada: {len(hallazgos)} problemas identificados")
            
        except Exception as e:
            self.logger.error(f"Error en auditoría de permisos: {e}")
            hallazgo_error = Hallazgo(
                tipo_anomalia=TipoHallazgo.VULNERABILIDAD_SISTEMA,
                ruta_afectada="/",
                detalle_especifico=f"Error verificando permisos del sistema: {e}",
                prioridad=PrioridadHallazgo.MEDIA,
                recomendacion="Verificar manualmente los permisos de archivos críticos del sistema",
                fecha_deteccion=datetime.now()
            )
            hallazgos.append(hallazgo_error)
        
        return hallazgos
    
    def _verificar_archivo_critico(self, archivo: str, ruta: str) -> Optional[Hallazgo]:
        """Verifica permisos específicos de un archivo crítico."""
        try:
            permisos = utilidades_sistema.obtener_permisos_archivo(ruta)
            
            # Criterios específicos por archivo
            problemas = []
            
            if archivo in ['passwd', 'group']:
                if permisos['otros_pueden_escribir']:
                    problemas.append("Otros usuarios pueden escribir en este archivo crítico")
                if permisos['propietario'] != 'root':
                    problemas.append(f"Propietario debería ser root, actual: {permisos['propietario']}")
                    
            elif archivo in ['shadow', 'gshadow']:
                if permisos['otros_pueden_leer']:
                    problemas.append("Archivo de contraseñas legible por otros usuarios")
                if permisos['grupo_puede_leer']:
                    problemas.append("Archivo de contraseñas legible por el grupo")
                if permisos['propietario'] != 'root':
                    problemas.append(f"Propietario debería ser root, actual: {permisos['propietario']}")
                    
            elif archivo == 'sudoers':
                if permisos['otros_pueden_leer'] or permisos['otros_pueden_escribir']:
                    problemas.append("Archivo sudoers tiene permisos inseguros")
                    
            if problemas:
                return Hallazgo(
                    tipo_anomalia=TipoHallazgo.VULNERABILIDAD_SISTEMA,
                    ruta_afectada=ruta,
                    detalle_especifico=f"Permisos inseguros en {archivo}: {'; '.join(problemas)}",
                    prioridad=PrioridadHallazgo.ALTA if archivo in ['shadow', 'sudoers'] else PrioridadHallazgo.MEDIA,
                    recomendacion=f"Corregir permisos: chmod 644 {ruta}" if archivo in ['passwd', 'group'] else f"chmod 600 {ruta}",
                    fecha_deteccion=datetime.now(),
                    metadatos={
                        'archivo_tipo': archivo,
                        'permisos_actuales': permisos['permisos_oct'],
                        'propietario': permisos['propietario'],
                        'grupo': permisos['grupo']
                    }
                )
                
        except Exception as e:
            self.logger.warning(f"Error verificando {ruta}: {e}")
            
        return None
    
    def _verificar_permisos_directorio(self, directorio: str) -> Optional[Hallazgo]:
        """Verifica permisos de directorios importantes."""
        try:
            permisos = utilidades_sistema.obtener_permisos_archivo(directorio)
            problemas = []
            
            if directorio == '/root':
                if permisos['otros_pueden_leer'] or permisos['otros_pueden_escribir']:
                    problemas.append("Directorio root accesible por otros usuarios")
            elif directorio == '/etc/shadow' or directorio == '/etc/sudoers':
                if permisos['otros_pueden_escribir']:
                    problemas.append("Directorio crítico escribible por otros")
                    
            if problemas:
                return Hallazgo(
                    tipo_anomalia=TipoHallazgo.VULNERABILIDAD_SISTEMA,
                    ruta_afectada=directorio,
                    detalle_especifico=f"Permisos inseguros en directorio: {'; '.join(problemas)}",
                    prioridad=PrioridadHallazgo.MEDIA,
                    recomendacion=f"Revisar y corregir permisos del directorio {directorio}",
                    fecha_deteccion=datetime.now()
                )
                
        except Exception as e:
            self.logger.warning(f"Error verificando directorio {directorio}: {e}")
            
        return None

