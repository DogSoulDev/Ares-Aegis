"""
Controlador del Mini-SIEM para integración con Ares Aegis
"""

import logging
from typing import Optional
from antivirus_kali.mini_siem.controlador_siem import ControladorMiniSiem

logger = logging.getLogger(__name__)

class ControladorMiniSiemIntegracion:
    """
    Controlador para integrar el Mini-SIEM con el sistema principal de Ares Aegis
    """
    
    def __init__(self):
        self.siem = None
        self.activo = False
        
    async def inicializar(self):
        """Inicializar el controlador del Mini-SIEM"""
        try:
            # Crear instancia del Mini-SIEM
            self.siem = ControladorMiniSiem()
            
            # Configurar callbacks para integración con el antivirus
            self.siem.agregar_callback_alerta(self.callback_alerta_antivirus)
            self.siem.agregar_callback_evento(self.callback_evento_antivirus)
            
            logger.info("Controlador Mini-SIEM inicializado")
            
        except Exception as e:
            logger.error(f"Error inicializando controlador Mini-SIEM: {e}")
            raise
            
    async def iniciar_monitoreo(self):
        """Iniciar monitoreo del Mini-SIEM"""
        if not self.siem:
            await self.inicializar()
            
        if self.siem:
            try:
                await self.siem.iniciar()
                self.activo = True
                logger.info("Mini-SIEM iniciado y monitoreando")
                
            except Exception as e:
                logger.error(f"Error iniciando Mini-SIEM: {e}")
                raise
        else:
            raise RuntimeError("No se pudo inicializar el Mini-SIEM")
            
    async def detener_monitoreo(self):
        """Detener monitoreo del Mini-SIEM"""
        if self.siem and self.activo:
            try:
                await self.siem.detener()
                self.activo = False
                logger.info("Mini-SIEM detenido")
                
            except Exception as e:
                logger.error(f"Error deteniendo Mini-SIEM: {e}")
                
    def obtener_estadisticas(self):
        """Obtener estadísticas del Mini-SIEM"""
        if self.siem:
            return self.siem.obtener_estadisticas_completas()
        return {}
        
    def obtener_estadisticas_completas(self):
        """Obtener estadísticas completas del Mini-SIEM (alias para compatibilidad)"""
        return self.obtener_estadisticas()
        
    def obtener_eventos_recientes(self, limite=50):
        """Obtener eventos recientes"""
        if self.siem:
            return self.siem.consultar_eventos_recientes(limite=limite)
        return []
        
    def obtener_alertas_activas(self):
        """Obtener alertas activas"""
        if self.siem:
            return self.siem.obtener_alertas_activas()
        return []
        
    async def callback_alerta_antivirus(self, alerta):
        """Callback para alertas del Mini-SIEM integradas con el antivirus"""
        try:
            # Integrar alerta con sistema principal del antivirus
            logger.warning(f"INTEGRACIÓN ANTIVIRUS - Alerta SIEM: {alerta.titulo}")
            
            # Aquí se pueden tomar acciones específicas según el tipo de alerta
            if alerta.severidad.value in ['HIGH', 'CRITICAL']:
                # Activar protecciones adicionales
                await self._activar_protecciones_emergencia(alerta)
                
        except Exception as e:
            logger.error(f"Error en callback de alerta: {e}")
            
    async def callback_evento_antivirus(self, evento):
        """Callback para eventos del Mini-SIEM integrados con el antivirus"""
        try:
            # Procesar eventos que puedan ser relevantes para el antivirus
            categoria = evento.get('event.category', '')
            
            if categoria == 'package' and evento.get('event.type') == 'package_install':
                # Notificar al motor antivirus sobre nuevos paquetes instalados
                logger.info(f"Nuevo paquete instalado detectado por SIEM: {evento.get('package.name')}")
                
        except Exception as e:
            logger.error(f"Error en callback de evento: {e}")
            
    async def _activar_protecciones_emergencia(self, alerta):
        """Activar protecciones de emergencia en respuesta a alertas críticas"""
        try:
            # Implementar acciones automáticas de respuesta
            if 'brute_force' in alerta.id.lower():
                logger.info("Activando protecciones contra fuerza bruta")
                # Aquí se podría integrar con fail2ban o iptables
                
            elif 'privilege_escalation' in alerta.id.lower():
                logger.critical("Escalada de privilegios detectada - Activando monitoreo intensivo")
                # Activar monitoreo más frecuente
                
        except Exception as e:
            logger.error(f"Error activando protecciones de emergencia: {e}")
            
    def esta_activo(self) -> bool:
        """Verificar si el Mini-SIEM está activo"""
        return self.activo
        
    def configurar_notificaciones(self, desktop=True, terminal=True, log=True):
        """Configurar notificaciones del Mini-SIEM"""
        if self.siem:
            self.siem.configurar_notificaciones(
                desktop=desktop,
                terminal=terminal,
                log=log
            )
            
    def agregar_regla_personalizada(self, config_regla):
        """Agregar regla personalizada de correlación"""
        if self.siem:
            self.siem.agregar_regla_personalizada(config_regla)
            
    async def realizar_diagnostico(self):
        """Realizar diagnóstico del sistema"""
        if self.siem:
            return await self.siem.realizar_diagnostico()
        return {'error': 'Mini-SIEM no inicializado'}
        
    def exportar_informe(self, archivo, desde=None, hasta=None):
        """Exportar informe de seguridad"""
        if self.siem:
            self.siem.exportar_informe_seguridad(archivo, desde, hasta)
        
    async def iniciar(self):
        """Iniciar el Mini-SIEM (alias para iniciar_monitoreo)"""
        await self.iniciar_monitoreo()
        
    async def detener(self):
        """Detener el Mini-SIEM (alias para detener_monitoreo)"""
        await self.detener_monitoreo()
        
    def realizar_diagnostico_siem(self):
        """Realizar diagnóstico del Mini-SIEM"""
        try:
            import time
            diagnostico = {
                'activo': self.esta_activo(),
                'timestamp': str(time.time()),
                'eventos_procesados': len(self.obtener_eventos_recientes(10)),
                'alertas_activas': len(self.obtener_alertas_activas()),
                'estado': 'OK' if self.esta_activo() else 'INACTIVO'
            }
            return diagnostico
        except Exception as e:
            return {
                'error': str(e),
                'estado': 'ERROR'
            }
