#!/usr/bin/env python3
"""
Controlador de Auditoría Avanzada de Seguridad para Ares Aegis
==============================================================

Este controlador orquesta auditorías de seguridad avanzadas integrando:
- Auditoría de autenticación PAM
- Análisis de vulnerabilidades del sistema
- Gestión de cuarentena automatizada
- Generación de reportes integrados

Desarrollado exclusivamente para Kali Linux siguiendo principios SOLID/DRY/MVC.
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

# Importaciones locales del proyecto
from ..modelo.modelo_hallazgos_seguridad import (
    Hallazgo, HallazgoAutenticacion, TipoHallazgo, 
    PrioridadHallazgo, ResultadoEscaneo
)
from ..modelo.modelo_auditor_autenticacion import AuditorPAM
from ..modelo.modelo_escaneador_vulnerabilidades_sistema import VigiaGrietasRealm
from ..modelo.modelo_utilidades_sistema import UtilidadesSistema
from .controlador_cuarentena import ControladorCuarentena
from .controlador_reportes import ControladorReportes


class ControladorAuditoriaAvanzada:
    """
    Controlador principal para auditorías avanzadas de seguridad.
    
    Responsabilidades:
    - Coordinar auditorías PAM y vulnerabilidades del sistema
    - Gestionar acciones de cuarentena basadas en prioridades
    - Generar reportes integrados de seguridad
    - Mantener historial de auditorías
    """
    
    def __init__(self, gestor_cuarentena=None, siem=None, config_path: Optional[str] = None, controlador_reportes=None):
        """
        Inicializa el controlador de auditoría avanzada.
        
        Args:
            gestor_cuarentena: Instancia del gestor de cuarentena (opcional)
            siem: Instancia del SIEM (opcional)
            config_path: Ruta opcional al archivo de configuración
            controlador_reportes: Instancia del controlador de reportes (opcional)
        """
        self.logger = logging.getLogger(__name__)
        self.config_path = config_path or "configuracion/ares_aegis_config.json"
        
        # Inicializar componentes especializados
        self.auditor_pam = AuditorPAM()
        self.escaneador_sistema = VigiaGrietasRealm()
        self.utilidades = UtilidadesSistema()
        
        # Controladores de apoyo (inicialización condicional)
        if gestor_cuarentena and siem:
            try:
                self.controlador_cuarentena = ControladorCuarentena(gestor_cuarentena, siem)
            except Exception as e:
                self.logger.warning(f"Error inicializando controlador de cuarentena: {e}")
                self.controlador_cuarentena = None
        else:
            self.logger.warning("Gestor de cuarentena o SIEM no proporcionados, funcionalidad limitada")
            self.controlador_cuarentena = None
            
        # Usar controlador de reportes proporcionado o crear uno si se proporciona SIEM
        if controlador_reportes:
            self.controlador_reportes = controlador_reportes
        elif siem:
            try:
                self.controlador_reportes = ControladorReportes(siem)
            except Exception as e:
                self.logger.warning(f"Error inicializando controlador de reportes: {e}")
                self.controlador_reportes = None
        else:
            self.logger.warning("No se proporcionó controlador de reportes ni SIEM")
            self.controlador_reportes = None
        
        # Estado de la auditoría
        self.auditoria_activa = False
        self.thread_auditoria = None
        self.ultima_auditoria = None
        self.estadisticas = {
            'auditorias_completadas': 0,
            'hallazgos_criticos_total': 0,
            'hallazgos_altos_total': 0,
            'archivos_cuarentena_total': 0
        }
        
        self.logger.info("🛡️ Controlador de Auditoría Avanzada inicializado para Kali Linux")
    
    def ejecutar_auditoria_completa(self, incluir_pam: bool = True, 
                                   incluir_sistema: bool = True,
                                   incluir_servicios: bool = True) -> ResultadoEscaneo:
        """
        Ejecuta una auditoría completa de seguridad integrando múltiples componentes.
        
        Args:
            incluir_pam: Si incluir auditoría de autenticación PAM
            incluir_sistema: Si incluir análisis de vulnerabilidades del sistema
            incluir_servicios: Si incluir verificación de servicios expuestos
            
        Returns:
            ResultadoEscaneo con todos los hallazgos integrados
        """
        if self.auditoria_activa:
            self.logger.warning("⚠️ Auditoría ya en progreso, cancelando nueva solicitud")
            return self._crear_resultado_error("Auditoría en progreso")
        
        self.logger.info("🔥 INICIANDO AUDITORÍA AVANZADA DE SEGURIDAD")
        self.auditoria_activa = True
        fecha_inicio = datetime.now()
        
        try:
            # Recopilar todos los hallazgos
            todos_hallazgos = []
            hallazgos_pam = []
            
            # 1. Auditoría de Autenticación PAM
            if incluir_pam:
                self.logger.info("🔐 Ejecutando auditoría de autenticación PAM...")
                hallazgos_pam = self.auditor_pam.auditar_configuracion_completa()
                todos_hallazgos.extend(hallazgos_pam)
                self.logger.info(f"✅ PAM: {len(hallazgos_pam)} hallazgos de autenticación detectados")
            
            # 2. Auditoría de Vulnerabilidades del Sistema
            if incluir_sistema:
                self.logger.info("🔍 Ejecutando análisis de vulnerabilidades del sistema...")
                hallazgos_sistema = self.escaneador_sistema.auditar_permisos_criticos()
                todos_hallazgos.extend(hallazgos_sistema)
                self.logger.info(f"✅ Sistema: {len(hallazgos_sistema)} vulnerabilidades detectadas")
            
            # 3. Verificación de Servicios Expuestos
            if incluir_servicios:
                self.logger.info("🚪 Verificando servicios expuestos...")
                hallazgos_servicios = self.escaneador_sistema.verificar_servicios_expuestos()
                todos_hallazgos.extend(hallazgos_servicios)
                self.logger.info(f"✅ Servicios: {len(hallazgos_servicios)} servicios riesgosos detectados")
            
            # 4. Procesamiento de acciones automáticas
            acciones_ejecutadas = self._procesar_acciones_automaticas(todos_hallazgos)
            
            # 5. Crear resultado integrado
            resultado = self._crear_resultado_integrado(
                todos_hallazgos, hallazgos_pam, fecha_inicio, acciones_ejecutadas
            )
            
            # 6. Generar reporte
            self._generar_reporte_auditoria(resultado)
            
            # 7. Actualizar estadísticas
            self._actualizar_estadisticas(resultado)
            
            self.ultima_auditoria = datetime.now()
            self.logger.info("🎯 AUDITORÍA AVANZADA COMPLETADA EXITOSAMENTE")
            
            return resultado
            
        except Exception as e:
            self.logger.error(f"❌ Error en auditoría avanzada: {e}")
            return self._crear_resultado_error(f"Error ejecutando auditoría: {e}")
            
        finally:
            self.auditoria_activa = False
    
    def _procesar_acciones_automaticas(self, hallazgos: List[Hallazgo]) -> Dict[str, int]:
        """
        Procesa acciones automáticas basadas en la prioridad de los hallazgos.
        
        Args:
            hallazgos: Lista de hallazgos detectados
            
        Returns:
            Diccionario con el conteo de acciones ejecutadas
        """
        acciones = {
            'archivos_cuarentena': 0,
            'permisos_corregidos': 0,
            'servicios_deshabilitados': 0,
            'notificaciones_enviadas': 0
        }
        
        try:
            for hallazgo in hallazgos:
                # Cuarentena automática para hallazgos críticos
                if hallazgo.prioridad == PrioridadHallazgo.CRITICA:
                    if hallazgo.tipo_anomalia in [TipoHallazgo.MALWARE_DETECTADO, TipoHallazgo.ARCHIVO_SOSPECHOSO]:
                        if self._enviar_a_cuarentena(hallazgo):
                            acciones['archivos_cuarentena'] += 1
                    
                    # Notificación inmediata para críticos
                    self._enviar_notificacion_critica(hallazgo)
                    acciones['notificaciones_enviadas'] += 1
                
                # Corrección automática de permisos para hallazgos de sistema
                elif (hallazgo.prioridad == PrioridadHallazgo.ALTA and 
                      hallazgo.tipo_anomalia == TipoHallazgo.VULNERABILIDAD_SISTEMA):
                    if self._intentar_correccion_permisos(hallazgo):
                        acciones['permisos_corregidos'] += 1
            
            self.logger.info(f"🔧 Acciones automáticas ejecutadas: {acciones}")
            
        except Exception as e:
            self.logger.error(f"Error procesando acciones automáticas: {e}")
        
        return acciones
    
    def _enviar_a_cuarentena(self, hallazgo: Hallazgo) -> bool:
        """Envía un archivo a cuarentena si es posible."""
        try:
            if not self.controlador_cuarentena:
                self.logger.warning("Controlador de cuarentena no disponible")
                return False
                
            if hallazgo.ruta_afectada and self.utilidades.archivo_existe(hallazgo.ruta_afectada):
                return self.controlador_cuarentena.poner_en_cuarentena(
                    hallazgo.ruta_afectada, 
                    f"Cuarentena automática: {hallazgo.detalle_especifico}"
                )
        except Exception as e:
            self.logger.error(f"Error enviando a cuarentena {hallazgo.ruta_afectada}: {e}")
        return False
    
    def _intentar_correccion_permisos(self, hallazgo: Hallazgo) -> bool:
        """Intenta corregir permisos automáticamente si es seguro."""
        try:
            # Solo para archivos específicos conocidos
            archivos_seguros = ['/etc/passwd', '/etc/group']
            
            if (hallazgo.ruta_afectada in archivos_seguros and 
                'chmod 644' in hallazgo.recomendacion):
                
                comando = ['chmod', '644', hallazgo.ruta_afectada]
                resultado = self.utilidades.ejecutar_comando_sistema(comando)
                
                if resultado.get('exitcode') == 0:
                    self.logger.info(f"✅ Permisos corregidos automáticamente: {hallazgo.ruta_afectada}")
                    return True
                    
        except Exception as e:
            self.logger.error(f"Error corrigiendo permisos: {e}")
        return False
    
    def _enviar_notificacion_critica(self, hallazgo: Hallazgo):
        """Envía notificación para hallazgos críticos."""
        try:
            mensaje = f"🚨 HALLAZGO CRÍTICO: {hallazgo.detalle_especifico}"
            # Aquí se podría integrar con sistemas de notificación externos
            self.logger.critical(mensaje)
        except Exception as e:
            self.logger.error(f"Error enviando notificación: {e}")
    
    def _crear_resultado_integrado(self, todos_hallazgos: List[Hallazgo], 
                                  hallazgos_pam: List[Hallazgo],
                                  fecha_inicio: datetime,
                                  acciones_ejecutadas: Dict[str, int]) -> ResultadoEscaneo:
        """Crea un resultado integrado de la auditoría."""
        
        # Clasificar hallazgos por prioridad
        clasificacion = {
            PrioridadHallazgo.CRITICA: [],
            PrioridadHallazgo.ALTA: [],
            PrioridadHallazgo.MEDIA: [],
            PrioridadHallazgo.BAJA: [],
            PrioridadHallazgo.INFORMATIVA: []
        }
        
        for hallazgo in todos_hallazgos:
            if hallazgo.prioridad in clasificacion:
                clasificacion[hallazgo.prioridad].append(hallazgo)
            else:
                # Manejar prioridades no reconocidas como informativas
                self.logger.warning(f"Prioridad no reconocida: {hallazgo.prioridad}, tratando como informativa")
                clasificacion[PrioridadHallazgo.INFORMATIVA].append(hallazgo)
        
        # Generar resumen ejecutivo
        resumen = self._generar_resumen_ejecutivo(clasificacion, acciones_ejecutadas)
        
        # Recomendaciones priorizadas
        recomendaciones = self._generar_recomendaciones_priorizadas(todos_hallazgos)
        
        return ResultadoEscaneo(
            hallazgos=todos_hallazgos,
            timestamp_inicio=fecha_inicio,
            timestamp_fin=datetime.now(),
            rutas_escaneadas=["/etc", "/proc", "/var/log"],
            estadisticas={
                'total_hallazgos': len(todos_hallazgos),
                'hallazgos_criticos': len(clasificacion.get(PrioridadHallazgo.CRITICA, [])),
                'hallazgos_altos': len(clasificacion.get(PrioridadHallazgo.ALTA, [])),
                'duracion_segundos': (datetime.now() - fecha_inicio).total_seconds(),
                'acciones_automaticas': acciones_ejecutadas,
                'resumen_ejecutivo': resumen,
                'recomendaciones_prioritarias': recomendaciones,
                'hallazgos_autenticacion': hallazgos_pam
            },
            metadatos={
                'total_hallazgos': len(todos_hallazgos),
                'hallazgos_criticos': len(clasificacion.get(PrioridadHallazgo.CRITICA, [])),
                'hallazgos_altos': len(clasificacion.get(PrioridadHallazgo.ALTA, [])),
                'acciones_automaticas': acciones_ejecutadas,
                'version_ares_aegis': '2.0.0',
                'sistema_operativo': 'Kali Linux'
            }
        )
    
    def _generar_resumen_ejecutivo(self, clasificacion: Dict[PrioridadHallazgo, List[Hallazgo]], 
                                  acciones: Dict[str, int]) -> str:
        """Genera un resumen ejecutivo de la auditoría."""
        
        total_criticos = len(clasificacion.get(PrioridadHallazgo.CRITICA, []))
        total_altos = len(clasificacion.get(PrioridadHallazgo.ALTA, []))
        total_medios = len(clasificacion.get(PrioridadHallazgo.MEDIA, []))
        total_bajos = len(clasificacion.get(PrioridadHallazgo.BAJA, []))
        total_informativos = len(clasificacion.get(PrioridadHallazgo.INFORMATIVA, []))
        
        resumen = f"""
🛡️ RESUMEN EJECUTIVO - AUDITORÍA AVANZADA DE SEGURIDAD
=====================================================

📊 ESTADO GENERAL:
- Hallazgos Críticos: {total_criticos}
- Hallazgos Altos: {total_altos}  
- Hallazgos Medios: {total_medios}
- Hallazgos Bajos: {total_bajos}
- Hallazgos Informativos: {total_informativos}

🔧 ACCIONES AUTOMÁTICAS EJECUTADAS:
- Archivos en cuarentena: {acciones['archivos_cuarentena']}
- Permisos corregidos: {acciones['permisos_corregidos']}
- Notificaciones enviadas: {acciones['notificaciones_enviadas']}

⚡ NIVEL DE RIESGO GENERAL: {'CRÍTICO' if total_criticos > 0 else 'ALTO' if total_altos > 0 else 'MEDIO'}
"""
        
        if total_criticos > 0:
            resumen += "\n🚨 ATENCIÓN INMEDIATA REQUERIDA: Se detectaron vulnerabilidades críticas"
        
        return resumen
    
    def _generar_recomendaciones_priorizadas(self, hallazgos: List[Hallazgo]) -> List[str]:
        """Genera recomendaciones priorizadas basadas en los hallazgos."""
        recomendaciones = []
        
        # Agrupar por tipo y prioridad
        criticos = [h for h in hallazgos if h.prioridad == PrioridadHallazgo.CRITICA]
        altos = [h for h in hallazgos if h.prioridad == PrioridadHallazgo.ALTA]
        
        if criticos:
            recomendaciones.append("🚨 INMEDIATO: Revisar y corregir todos los hallazgos críticos")
            for hallazgo in criticos[:3]:  # Mostrar top 3 críticos
                recomendaciones.append(f"   - {hallazgo.recomendacion}")
        
        if altos:
            recomendaciones.append("⚠️  URGENTE: Atender hallazgos de alta prioridad")
            for hallazgo in altos[:2]:  # Mostrar top 2 altos
                recomendaciones.append(f"   - {hallazgo.recomendacion}")
        
        # Recomendaciones generales
        recomendaciones.extend([
            "🔐 Revisar configuración PAM regularmente",
            "🔍 Programar auditorías automáticas cada 24 horas",
            "📝 Mantener logs de auditoría actualizados",
            "🛡️ Considerar implementar monitoreo en tiempo real"
        ])
        
        return recomendaciones
    
    def _generar_reporte_auditoria(self, resultado: ResultadoEscaneo):
        """Genera y guarda el reporte de la auditoría."""
        try:
            if not self.controlador_reportes:
                self.logger.warning("Controlador de reportes no disponible, saltando generación de reporte")
                return
                
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_reporte = f"auditoria_avanzada_{timestamp}.html"
            
            self.controlador_reportes.generar_reporte_html(resultado, nombre_reporte)
            self.logger.info(f"📊 Reporte generado: {nombre_reporte}")
            
        except Exception as e:
            self.logger.error(f"Error generando reporte: {e}")
    
    def _actualizar_estadisticas(self, resultado: ResultadoEscaneo):
        """Actualiza las estadísticas del controlador."""
        try:
            self.estadisticas['auditorias_completadas'] += 1
            self.estadisticas['hallazgos_criticos_total'] += resultado.estadisticas.get('hallazgos_criticos', 0)
            self.estadisticas['hallazgos_altos_total'] += resultado.estadisticas.get('hallazgos_altos', 0)
            self.estadisticas['archivos_cuarentena_total'] += resultado.estadisticas.get('acciones_automaticas', {}).get('archivos_cuarentena', 0)
            
        except Exception as e:
            self.logger.error(f"Error actualizando estadísticas: {e}")
    
    def _crear_resultado_error(self, mensaje: str) -> ResultadoEscaneo:
        """Crea un resultado de error."""
        return ResultadoEscaneo(
            hallazgos=[],
            timestamp_inicio=datetime.now(),
            timestamp_fin=datetime.now(),
            rutas_escaneadas=[],
            estadisticas={
                'total_hallazgos': 0,
                'duracion_segundos': 0,
                'error': mensaje
            },
            metadatos={'error': mensaje}
        )
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Retorna las estadísticas del controlador."""
        return {
            **self.estadisticas,
            'ultima_auditoria': self.ultima_auditoria.isoformat() if self.ultima_auditoria else None,
            'auditoria_activa': self.auditoria_activa
        }
    
    def auditar_solo_pam(self) -> List[Hallazgo]:
        """Ejecuta únicamente auditoría PAM."""
        self.logger.info("🔐 Ejecutando auditoría PAM exclusiva...")
        return self.auditor_pam.auditar_configuracion_completa()
    
    def auditar_solo_sistema(self) -> List[Hallazgo]:
        """Ejecuta únicamente auditoría de sistema."""
        self.logger.info("🔍 Ejecutando auditoría de sistema exclusiva...")
        hallazgos = []
        hallazgos.extend(self.escaneador_sistema.auditar_permisos_criticos())
        hallazgos.extend(self.escaneador_sistema.verificar_servicios_expuestos())
        return hallazgos
    
    def cancelar_auditoria(self) -> bool:
        """
        Cancela la auditoría actualmente en progreso.
        
        Returns:
            bool: True si se canceló exitosamente, False si no había auditoría activa
        """
        if not self.auditoria_activa:
            self.logger.warning("No hay auditoría activa para cancelar")
            return False
            
        self.logger.info("🚫 Cancelando auditoría en progreso...")
        self.auditoria_activa = False
        
        # El thread se detendrá en la próxima verificación de self.auditoria_activa
        if self.thread_auditoria and self.thread_auditoria.is_alive():
            self.logger.info("Esperando que termine el hilo de auditoría...")
            # No usamos join() para evitar bloquear la UI
            
        self.logger.info("✅ Auditoría cancelada exitosamente")
        return True
    
    def esta_auditoria_activa(self) -> bool:
        """Verifica si hay una auditoría activa"""
        return self.auditoria_activa
