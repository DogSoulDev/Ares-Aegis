#!/usr/bin/env python3
"""
Creado por DogSoulDev (https://github.com/DogSoulDev)
Todos los derechos reservados. Este código es propietario y confidencial.

Auditor de Autenticación PAM para Kali Linux - Ares Aegis
"""

import re
import os
import platform
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from .modelo_hallazgos_seguridad import (
    Hallazgo, HallazgoAutenticacion, TipoHallazgo, 
    PrioridadHallazgo, EstadoHallazgo
)
from .modelo_utilidades_sistema import utilidades_sistema
from ..utils.utils_ayuda_logging import configurar_logger_modulo


class AuditorPAM:
    """
    El Guardián de las Credenciales Sagradas.
    Audita la configuración de autenticación PAM en Kali Linux.
    """
    
    def __init__(self):
        """Inicializa el auditor de autenticación PAM."""
        self.logger = configurar_logger_modulo("auditor_pam")
        
        # Rutas críticas de configuración PAM
        self.rutas_pam = {
            'directorio_pam': '/etc/pam.d',
            'configuracion_faillock': '/etc/security/faillock.conf',
            'configuracion_pwquality': '/etc/security/pwquality.conf',
            'configuracion_login': '/etc/login.defs',
            'configuracion_securetty': '/etc/securetty',
            'configuracion_passwd': '/etc/passwd',
            'configuracion_shadow': '/etc/shadow'
        }
        
        # Servicios PAM críticos para auditar
        self.servicios_pam_criticos = [
            'common-auth', 'common-account', 'common-password', 'common-session',
            'login', 'sshd', 'sudo', 'su', 'passwd'
        ]
        
        self.logger.info("🔐 El Guardián de las Credenciales Sagradas ha iniciado su vigilancia")
    
    def auditar_configuracion_completa(self) -> List[Hallazgo]:
        """
        Realiza una auditoría completa de la configuración PAM.
        
        Returns:
            Lista de hallazgos detectados
        """
        self.logger.info("Iniciando auditoría completa de configuración PAM")
        hallazgos = []
        
        # Verificar si estamos en Linux
        if platform.system() != 'Linux':
            self.logger.warning(f"Sistema operativo {platform.system()} detectado. PAM es específico de sistemas Linux.")
            hallazgo_informativo = HallazgoAutenticacion(
                tipo_anomalia=TipoHallazgo.INFORMATIVO,
                ruta_afectada="Sistema",
                detalle_especifico=f"Auditoría PAM no aplicable en {platform.system()}. PAM (Pluggable Authentication Modules) es específico de sistemas Linux/Unix.",
                prioridad=PrioridadHallazgo.INFORMATIVA,
                recomendacion="Esta auditoría debe ejecutarse en un sistema Kali Linux o similar para obtener resultados válidos.",
                fecha_deteccion=datetime.now()
            )
            if not hasattr(hallazgo_informativo, 'metadatos') or hallazgo_informativo.metadatos is None:
                hallazgo_informativo.metadatos = {}
            hallazgo_informativo.metadatos.update({
                'sistema_operativo': platform.system(),
                'razon': 'PAM no disponible en este sistema operativo'
            })
            return [hallazgo_informativo]
        
        try:
            # Auditar políticas de contraseñas
            hallazgos.extend(self.analizar_politicas_pam())
            
            # Verificar módulos de bloqueo por intentos fallidos
            hallazgos.extend(self.verificar_modulos_bloqueo())
            
            # Auditar configuración global de login.defs
            hallazgos.extend(self.verificar_configuracion_global_login_defs())
            
            # Verificar configuración de securetty
            hallazgos.extend(self.verificar_securetty_entradas())
            
            # Validar permisos de archivos críticos
            hallazgos.extend(self.validar_permisos_archivos_criticos())
            
            # Auditar configuraciones específicas de servicios
            hallazgos.extend(self.auditar_servicios_pam_criticos())
            
            self.logger.info(f"Auditoría PAM completada: {len(hallazgos)} hallazgos detectados")
            
        except Exception as e:
            self.logger.error(f"Error durante auditoría PAM: {e}")
            hallazgo_error = HallazgoAutenticacion(
                tipo_anomalia=TipoHallazgo.VULNERABILIDAD_SISTEMA,
                ruta_afectada="/etc/pam.d",
                detalle_especifico=f"Error durante auditoría PAM: {e}",
                prioridad=PrioridadHallazgo.MEDIA,
                recomendacion="Verificar manualmente la configuración PAM",
                fecha_deteccion=datetime.now()
            )
            hallazgos.append(hallazgo_error)
        
        return hallazgos
    
    def analizar_politicas_pam(self) -> List[Hallazgo]:
        """
        Analiza las políticas de contraseñas en configuraciones PAM.
        
        Returns:
            Lista de hallazgos relacionados con políticas de contraseñas
        """
        hallazgos = []
        
        # Analizar pwquality.conf
        hallazgos.extend(self._analizar_pwquality_conf())
        
        # Analizar common-password
        hallazgos.extend(self._analizar_common_password())
        
        return hallazgos
    
    def _analizar_pwquality_conf(self) -> List[Hallazgo]:
        """Analiza el archivo pwquality.conf."""
        hallazgos = []
        ruta_pwquality = self.rutas_pam['configuracion_pwquality']
        
        contenido = utilidades_sistema.leer_contenido_archivo(ruta_pwquality)
        if not contenido:
            hallazgo = HallazgoAutenticacion(
                tipo_anomalia=TipoHallazgo.CONFIGURACION_INSEGURA,
                ruta_afectada=ruta_pwquality,
                detalle_especifico="Archivo de configuración pwquality.conf no encontrado o inaccesible",
                prioridad=PrioridadHallazgo.ALTA,
                recomendacion="Crear y configurar /etc/security/pwquality.conf con políticas seguras",
                fecha_deteccion=datetime.now()
            )
            hallazgos.append(hallazgo)
            return hallazgos
        
        # Configuraciones recomendadas para pwquality
        configuraciones_recomendadas = {
            'minlen': {'valor_minimo': 12, 'mensaje': 'Longitud mínima de contraseña muy baja'},
            'dcredit': {'valor_maximo': -1, 'mensaje': 'Requiere al menos un dígito'},
            'ucredit': {'valor_maximo': -1, 'mensaje': 'Requiere al menos una mayúscula'},
            'lcredit': {'valor_maximo': -1, 'mensaje': 'Requiere al menos una minúscula'},
            'ocredit': {'valor_maximo': -1, 'mensaje': 'Requiere al menos un carácter especial'},
            'minclass': {'valor_minimo': 3, 'mensaje': 'Clases de caracteres mínimas insuficientes'},
            'maxrepeat': {'valor_maximo': 2, 'mensaje': 'Permite demasiadas repeticiones de caracteres'},
            'difok': {'valor_minimo': 3, 'mensaje': 'Diferencias mínimas con contraseña anterior insuficientes'}
        }
        
        for config, criterio in configuraciones_recomendadas.items():
            patron = rf'^\s*{config}\s*=\s*(-?\d+)'
            coincidencia = re.search(patron, contenido, re.MULTILINE)
            
            if coincidencia:
                valor_actual = int(coincidencia.group(1))
                
                # Verificar según el tipo de criterio
                es_problematico = False
                if 'valor_minimo' in criterio and valor_actual < criterio['valor_minimo']:
                    es_problematico = True
                elif 'valor_maximo' in criterio and valor_actual > criterio['valor_maximo']:
                    es_problematico = True
                
                if es_problematico:
                    hallazgo = HallazgoAutenticacion(
                        tipo_anomalia=TipoHallazgo.CONFIGURACION_INSEGURA,
                        ruta_afectada=ruta_pwquality,
                        detalle_especifico=f"Configuración {config}={valor_actual}: {criterio['mensaje']}",
                        prioridad=PrioridadHallazgo.MEDIA,
                        recomendacion=f"Ajustar {config} a un valor más seguro en {ruta_pwquality}",
                        fecha_deteccion=datetime.now()
                    )
                    if not hasattr(hallazgo, 'metadatos') or hallazgo.metadatos is None:
                        hallazgo.metadatos = {}
                    hallazgo.metadatos.update({
                        'configuracion': config,
                        'valor_actual': valor_actual,
                        'valor_recomendado': criterio.get('valor_minimo') or criterio.get('valor_maximo')
                    })
                    hallazgos.append(hallazgo)
            else:
                # Configuración no especificada
                hallazgo = HallazgoAutenticacion(
                    tipo_anomalia=TipoHallazgo.CONFIGURACION_INSEGURA,
                    ruta_afectada=ruta_pwquality,
                    detalle_especifico=f"Configuración {config} no especificada: {criterio['mensaje']}",
                    prioridad=PrioridadHallazgo.BAJA,
                    recomendacion=f"Especificar {config} en {ruta_pwquality}",
                    fecha_deteccion=datetime.now()
                )
                hallazgos.append(hallazgo)
        
        return hallazgos
    
    def _analizar_common_password(self) -> List[Hallazgo]:
        """Analiza el archivo common-password."""
        hallazgos = []
        ruta_common_password = f"{self.rutas_pam['directorio_pam']}/common-password"
        
        contenido = utilidades_sistema.leer_contenido_archivo(ruta_common_password)
        if not contenido:
            hallazgo = HallazgoAutenticacion(
                tipo_anomalia=TipoHallazgo.CONFIGURACION_INSEGURA,
                ruta_afectada=ruta_common_password,
                detalle_especifico="Archivo common-password no encontrado o inaccesible",
                prioridad=PrioridadHallazgo.CRITICA,
                recomendacion="Verificar y restaurar la configuración PAM de contraseñas",
                fecha_deteccion=datetime.now()
            )
            hallazgos.append(hallazgo)
            return hallazgos
        
        # Verificar módulo pam_pwquality
        if 'pam_pwquality.so' not in contenido:
            if 'pam_cracklib.so' not in contenido:
                hallazgo = HallazgoAutenticacion(
                    tipo_anomalia=TipoHallazgo.CONFIGURACION_INSEGURA,
                    ruta_afectada=ruta_common_password,
                    detalle_especifico="No se encontró módulo de calidad de contraseñas (pam_pwquality.so o pam_cracklib.so)",
                    prioridad=PrioridadHallazgo.ALTA,
                    recomendacion="Configurar pam_pwquality.so en common-password para validación de contraseñas",
                    fecha_deteccion=datetime.now()
                )
                hallazgos.append(hallazgo)
        
        # Verificar nullok (permite contraseñas vacías)
        if re.search(r'nullok', contenido, re.IGNORECASE):
            hallazgo = HallazgoAutenticacion(
                tipo_anomalia=TipoHallazgo.AUTENTICACION_DEBIL,
                ruta_afectada=ruta_common_password,
                detalle_especifico="Configuración 'nullok' permite contraseñas vacías - vulnerabilidad crítica",
                prioridad=PrioridadHallazgo.CRITICA,
                recomendacion="Eliminar la opción 'nullok' de todas las líneas en common-password",
                fecha_deteccion=datetime.now()
            )
            hallazgos.append(hallazgo)
        
        return hallazgos
    
    def verificar_modulos_bloqueo(self) -> List[Hallazgo]:
        """
        Verifica la configuración de módulos de bloqueo por intentos fallidos.
        
        Returns:
            Lista de hallazgos relacionados con módulos de bloqueo
        """
        hallazgos = []
        
        # Verificar common-auth para faillock o tally2
        ruta_common_auth = f"{self.rutas_pam['directorio_pam']}/common-auth"
        contenido_auth = utilidades_sistema.leer_contenido_archivo(ruta_common_auth)
        
        if not contenido_auth:
            hallazgo = HallazgoAutenticacion(
                tipo_anomalia=TipoHallazgo.CONFIGURACION_INSEGURA,
                ruta_afectada=ruta_common_auth,
                detalle_especifico="Archivo common-auth no encontrado o inaccesible",
                prioridad=PrioridadHallazgo.CRITICA,
                recomendacion="Verificar y restaurar la configuración PAM de autenticación",
                fecha_deteccion=datetime.now()
            )
            hallazgos.append(hallazgo)
            return hallazgos
        
        # Buscar módulos de bloqueo
        tiene_faillock = 'pam_faillock.so' in contenido_auth
        tiene_tally2 = 'pam_tally2.so' in contenido_auth
        
        if not tiene_faillock and not tiene_tally2:
            hallazgo = HallazgoAutenticacion(
                tipo_anomalia=TipoHallazgo.AUTENTICACION_DEBIL,
                ruta_afectada=ruta_common_auth,
                detalle_especifico="No se encontró módulo de bloqueo por intentos fallidos (pam_faillock.so o pam_tally2.so)",
                prioridad=PrioridadHallazgo.ALTA,
                recomendacion="Configurar pam_faillock.so para bloquear cuentas tras intentos fallidos",
                fecha_deteccion=datetime.now()
            )
            hallazgos.append(hallazgo)
        
        # Si tiene faillock, verificar configuración
        if tiene_faillock:
            hallazgos.extend(self._verificar_configuracion_faillock())
        
        return hallazgos
    
    def _verificar_configuracion_faillock(self) -> List[Hallazgo]:
        """Verifica la configuración específica de faillock."""
        hallazgos = []
        ruta_faillock = self.rutas_pam['configuracion_faillock']
        
        contenido = utilidades_sistema.leer_contenido_archivo(ruta_faillock)
        if not contenido:
            # Buscar configuración en common-auth directamente
            ruta_common_auth = f"{self.rutas_pam['directorio_pam']}/common-auth"
            contenido = utilidades_sistema.leer_contenido_archivo(ruta_common_auth) or ""
        
        # Verificar parámetros de faillock
        configuraciones_faillock = {
            'deny': {'valor_maximo': 5, 'descripcion': 'Intentos máximos antes del bloqueo'},
            'unlock_time': {'valor_minimo': 300, 'descripcion': 'Tiempo de bloqueo en segundos'},
            'fail_interval': {'valor_maximo': 900, 'descripcion': 'Ventana de tiempo para contar fallos'}
        }
        
        for config, criterio in configuraciones_faillock.items():
            # Buscar en líneas de pam_faillock
            patron = rf'pam_faillock\.so.*{config}=(\d+)'
            coincidencia = re.search(patron, contenido)
            
            if coincidencia:
                valor = int(coincidencia.group(1))
                es_problematico = False
                
                if 'valor_maximo' in criterio and valor > criterio['valor_maximo']:
                    es_problematico = True
                elif 'valor_minimo' in criterio and valor < criterio['valor_minimo']:
                    es_problematico = True
                
                if es_problematico:
                    hallazgo = HallazgoAutenticacion(
                        tipo_anomalia=TipoHallazgo.CONFIGURACION_INSEGURA,
                        ruta_afectada=ruta_faillock,
                        detalle_especifico=f"Configuración faillock {config}={valor} no es segura: {criterio['descripcion']}",
                        prioridad=PrioridadHallazgo.MEDIA,
                        recomendacion=f"Ajustar {config} a un valor más seguro en la configuración faillock",
                        fecha_deteccion=datetime.now()
                    )
                    hallazgos.append(hallazgo)
        
        return hallazgos
    
    def verificar_configuracion_global_login_defs(self) -> List[Hallazgo]:
        """
        Verifica la configuración global en login.defs.
        
        Returns:
            Lista de hallazgos relacionados con login.defs
        """
        hallazgos = []
        ruta_login_defs = self.rutas_pam['configuracion_login']
        
        contenido = utilidades_sistema.leer_contenido_archivo(ruta_login_defs)
        if not contenido:
            hallazgo = HallazgoAutenticacion(
                tipo_anomalia=TipoHallazgo.CONFIGURACION_INSEGURA,
                ruta_afectada=ruta_login_defs,
                detalle_especifico="Archivo login.defs no encontrado o inaccesible",
                prioridad=PrioridadHallazgo.ALTA,
                recomendacion="Verificar y restaurar /etc/login.defs",
                fecha_deteccion=datetime.now()
            )
            hallazgos.append(hallazgo)
            return hallazgos
        
        # Configuraciones importantes en login.defs
        configuraciones_login = {
            'PASS_MAX_DAYS': {'valor_maximo': 90, 'descripcion': 'Días máximos de validez de contraseña'},
            'PASS_MIN_DAYS': {'valor_minimo': 1, 'descripcion': 'Días mínimos entre cambios de contraseña'},
            'PASS_WARN_AGE': {'valor_minimo': 7, 'descripcion': 'Días de advertencia antes de expiración'},
            'LOGIN_RETRIES': {'valor_maximo': 3, 'descripcion': 'Intentos máximos de login'},
            'LOGIN_TIMEOUT': {'valor_maximo': 60, 'descripcion': 'Timeout de login en segundos'},
            'UMASK': {'valor_esperado': '027', 'descripcion': 'Máscara de permisos por defecto'}
        }
        
        for config, criterio in configuraciones_login.items():
            patron = rf'^\s*{config}\s+(\w+)'
            coincidencia = re.search(patron, contenido, re.MULTILINE)
            
            if coincidencia:
                valor_str = coincidencia.group(1)
                
                if config == 'UMASK':
                    if valor_str != criterio['valor_esperado']:
                        hallazgo = HallazgoAutenticacion(
                            tipo_anomalia=TipoHallazgo.CONFIGURACION_INSEGURA,
                            ruta_afectada=ruta_login_defs,
                            detalle_especifico=f"UMASK {valor_str} permite permisos demasiado permisivos",
                            prioridad=PrioridadHallazgo.MEDIA,
                            recomendacion=f"Configurar UMASK {criterio['valor_esperado']} en login.defs",
                            fecha_deteccion=datetime.now()
                        )
                        hallazgos.append(hallazgo)
                else:
                    try:
                        valor = int(valor_str)
                        es_problematico = False
                        
                        if 'valor_maximo' in criterio and valor > criterio['valor_maximo']:
                            es_problematico = True
                        elif 'valor_minimo' in criterio and valor < criterio['valor_minimo']:
                            es_problematico = True
                        
                        if es_problematico:
                            hallazgo = HallazgoAutenticacion(
                                tipo_anomalia=TipoHallazgo.CONFIGURACION_INSEGURA,
                                ruta_afectada=ruta_login_defs,
                                detalle_especifico=f"Configuración {config}={valor} no es segura: {criterio['descripcion']}",
                                prioridad=PrioridadHallazgo.MEDIA,
                                recomendacion=f"Ajustar {config} a un valor más seguro en login.defs",
                                fecha_deteccion=datetime.now()
                            )
                            hallazgos.append(hallazgo)
                    except ValueError:
                        continue
            else:
                # Configuración no especificada
                hallazgo = HallazgoAutenticacion(
                    tipo_anomalia=TipoHallazgo.CONFIGURACION_INSEGURA,
                    ruta_afectada=ruta_login_defs,
                    detalle_especifico=f"Configuración {config} no especificada: {criterio['descripcion']}",
                    prioridad=PrioridadHallazgo.BAJA,
                    recomendacion=f"Especificar {config} en login.defs",
                    fecha_deteccion=datetime.now()
                )
                hallazgos.append(hallazgo)
        
        return hallazgos
    
    def verificar_securetty_entradas(self) -> List[Hallazgo]:
        """
        Verifica las entradas en /etc/securetty.
        
        Returns:
            Lista de hallazgos relacionados con securetty
        """
        hallazgos = []
        ruta_securetty = self.rutas_pam['configuracion_securetty']
        
        contenido = utilidades_sistema.leer_contenido_archivo(ruta_securetty)
        if not contenido:
            # securetty puede no existir, lo cual es aceptable
            return hallazgos
        
        # Buscar entradas problemáticas
        lineas = contenido.split('\n')
        entradas_problematicas = []
        
        for linea in lineas:
            linea = linea.strip()
            if not linea or linea.startswith('#'):
                continue
            
            # Verificar entradas pts (pseudo-terminales)
            if linea.startswith('pts/'):
                entradas_problematicas.append(f"pts/{linea[4:]} permite login root remoto")
            elif 'tty' not in linea and linea not in ['console']:
                entradas_problematicas.append(f"{linea} puede permitir acceso root no físico")
        
        if entradas_problematicas:
            detalle = "Entradas problemáticas en securetty: " + ", ".join(entradas_problematicas)
            hallazgo = HallazgoAutenticacion(
                tipo_anomalia=TipoHallazgo.CONFIGURACION_INSEGURA,
                ruta_afectada=ruta_securetty,
                detalle_especifico=detalle,
                prioridad=PrioridadHallazgo.ALTA,
                recomendacion="Revisar y restringir entradas en /etc/securetty para limitar login root",
                fecha_deteccion=datetime.now()
            )
            hallazgos.append(hallazgo)
        
        return hallazgos
    
    def validar_permisos_archivos_criticos(self) -> List[Hallazgo]:
        """
        Valida permisos de archivos críticos de autenticación.
        
        Returns:
            Lista de hallazgos relacionados con permisos
        """
        hallazgos = []
        
        # Permisos esperados para archivos críticos
        archivos_permisos = {
            '/etc/passwd': {'permisos': '644', 'propietario': 'root'},
            '/etc/shadow': {'permisos': '640', 'propietario': 'root'},
            '/etc/securetty': {'permisos': '644', 'propietario': 'root'},
            '/etc/login.defs': {'permisos': '644', 'propietario': 'root'},
            '/etc/security/pwquality.conf': {'permisos': '644', 'propietario': 'root'},
            '/etc/security/faillock.conf': {'permisos': '644', 'propietario': 'root'}
        }
        
        for ruta, esperados in archivos_permisos.items():
            resultado = utilidades_sistema.validar_permisos_archivo_critico(
                ruta, 
                esperados['permisos'], 
                esperados['propietario']
            )
            
            if not resultado['es_valido'] and resultado['informacion']:
                problemas = "; ".join(resultado['problemas'])
                hallazgo = HallazgoAutenticacion(
                    tipo_anomalia=TipoHallazgo.PERMISOS_INCORRECTOS,
                    ruta_afectada=ruta,
                    detalle_especifico=f"Permisos incorrectos en archivo crítico: {problemas}",
                    prioridad=PrioridadHallazgo.ALTA if '/shadow' in ruta else PrioridadHallazgo.MEDIA,
                    recomendacion=f"Corregir permisos: chown {esperados['propietario']}:{esperados['propietario']} {ruta} && chmod {esperados['permisos']} {ruta}",
                    fecha_deteccion=datetime.now()
                )
                if not hasattr(hallazgo, 'metadatos') or hallazgo.metadatos is None:
                    hallazgo.metadatos = {}
                hallazgo.metadatos.update({
                    'permisos_actuales': resultado['informacion']['permisos_octales'],
                    'permisos_esperados': esperados['permisos'],
                    'propietario_actual': resultado['informacion']['propietario'],
                    'propietario_esperado': esperados['propietario']
                })
                hallazgos.append(hallazgo)
        
        return hallazgos
    
    def auditar_servicios_pam_criticos(self) -> List[Hallazgo]:
        """
        Audita configuraciones PAM de servicios críticos.
        
        Returns:
            Lista de hallazgos relacionados con servicios PAM críticos
        """
        hallazgos = []
        
        for servicio in self.servicios_pam_criticos:
            ruta_servicio = f"{self.rutas_pam['directorio_pam']}/{servicio}"
            contenido = utilidades_sistema.leer_contenido_archivo(ruta_servicio)
            
            if not contenido:
                if servicio in ['login', 'sshd', 'sudo']:  # Servicios críticos
                    hallazgo = HallazgoAutenticacion(
                        tipo_anomalia=TipoHallazgo.CONFIGURACION_INSEGURA,
                        ruta_afectada=ruta_servicio,
                        detalle_especifico=f"Configuración PAM crítica para {servicio} no encontrada",
                        prioridad=PrioridadHallazgo.ALTA,
                        recomendacion=f"Verificar y restaurar configuración PAM para {servicio}",
                        fecha_deteccion=datetime.now()
                    )
                    hallazgos.append(hallazgo)
                continue
            
            # Verificaciones específicas por servicio
            if servicio == 'sshd':
                hallazgos.extend(self._auditar_pam_sshd(contenido, ruta_servicio))
            elif servicio == 'sudo':
                hallazgos.extend(self._auditar_pam_sudo(contenido, ruta_servicio))
            elif servicio == 'login':
                hallazgos.extend(self._auditar_pam_login(contenido, ruta_servicio))
        
        return hallazgos
    
    def _auditar_pam_sshd(self, contenido: str, ruta: str) -> List[Hallazgo]:
        """Audita configuración PAM específica de SSH."""
        hallazgos = []
        
        # Verificar que use common-auth (configuración centralizada)
        if '@include common-auth' not in contenido:
            hallazgo = HallazgoAutenticacion(
                tipo_anomalia=TipoHallazgo.CONFIGURACION_INSEGURA,
                ruta_afectada=ruta,
                detalle_especifico="SSH no usa configuración PAM centralizada (common-auth)",
                prioridad=PrioridadHallazgo.MEDIA,
                recomendacion="Configurar SSH para usar @include common-auth",
                fecha_deteccion=datetime.now()
            )
            hallazgos.append(hallazgo)
        
        return hallazgos
    
    def _auditar_pam_sudo(self, contenido: str, ruta: str) -> List[Hallazgo]:
        """Audita configuración PAM específica de sudo."""
        hallazgos = []
        
        # Verificar que use common-auth
        if '@include common-auth' not in contenido:
            hallazgo = HallazgoAutenticacion(
                tipo_anomalia=TipoHallazgo.CONFIGURACION_INSEGURA,
                ruta_afectada=ruta,
                detalle_especifico="sudo no usa configuración PAM centralizada (common-auth)",
                prioridad=PrioridadHallazgo.MEDIA,
                recomendacion="Configurar sudo para usar @include common-auth",
                fecha_deteccion=datetime.now()
            )
            hallazgos.append(hallazgo)
        
        return hallazgos
    
    def _auditar_pam_login(self, contenido: str, ruta: str) -> List[Hallazgo]:
        """Audita configuración PAM específica de login."""
        hallazgos = []
        
        # Verificar securetty
        if 'pam_securetty.so' not in contenido:
            hallazgo = HallazgoAutenticacion(
                tipo_anomalia=TipoHallazgo.CONFIGURACION_INSEGURA,
                ruta_afectada=ruta,
                detalle_especifico="Login no verifica securetty para restricciones de root",
                prioridad=PrioridadHallazgo.MEDIA,
                recomendacion="Agregar pam_securetty.so a la configuración PAM de login",
                fecha_deteccion=datetime.now()
            )
            hallazgos.append(hallazgo)
        
        return hallazgos
