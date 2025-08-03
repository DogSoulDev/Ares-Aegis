import asyncio
import time
import threading
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

from ..modelo.modelo_siem import SIEM
from ..modelo.modelo_escaneador import EscaneadorMalware
from ..modelo.modelo_fim import FIM
from ..modelo.modelo_monitor_red import MonitorRed
from ..modelo.modelo_gestor_cuarentena import GestorCuarentenaAvanzado
from ..modelo.modelo_monitor_procesos import MonitorProcesos
from ..modelo.modelo_analizadores import AnalizadoresUnificados
from ..modelo.modelo_constructor_wordlists import ConstructorWordlists

from .controlador_base import ControladorBase, ControladorBaseException
from ..utils.utils_gestor_configuracion import gestor_configuracion, ConfiguracionGlobal
from .controlador_escaneador import ControladorEscaneador
from .controlador_siem import ControladorSIEM
from .controlador_fim import ControladorFIM
from .controlador_monitor_red import ControladorMonitorRed
from .controlador_cuarentena import ControladorCuarentena
from .controlador_reportes import ControladorReportes
from .controlador_auditoria_avanzada import ControladorAuditoriaAvanzada
from .controlador_auditoria_simple import ControladorAuditoriaSimple

# Importar utilidades disponibles
from ..utils.utils_principal import MonitorSistemaUtils


class ControladorPrincipal(ControladorBase):
    """Controlador principal optimizado."""
    
    def __init__(self):
        super().__init__("principal")
        
        # Estado del controlador
        self._activo = True
        
        # Configuración centralizada
        self.configuracion: ConfiguracionGlobal = gestor_configuracion.obtener_configuracion()
        
        # Componentes principales (modelos)
        self.siem: Optional[SIEM] = None
        self.escaneador_modelo: Optional[EscaneadorMalware] = None
        self.fim_modelo: Optional[FIM] = None
        self.monitor_red_modelo: Optional[MonitorRed] = None
        self.gestor_cuarentena_modelo: Optional[GestorCuarentenaAvanzado] = None
        self.monitor_procesos_modelo: Optional[MonitorProcesos] = None
        self.analizadores_modelo: Optional[AnalizadoresUnificados] = None
        self.constructor_wordlists_modelo: Optional[ConstructorWordlists] = None
        
        # Controladores especializados
        self.controlador_escaneador: Optional[ControladorEscaneador] = None
        self.controlador_siem: Optional[ControladorSIEM] = None
        self.controlador_fim: Optional[ControladorFIM] = None
        self.controlador_monitor_red: Optional[ControladorMonitorRed] = None
        self.controlador_cuarentena: Optional[ControladorCuarentena] = None
        self.controlador_reportes: Optional[ControladorReportes] = None
        self.controlador_auditoria_avanzada: Optional[ControladorAuditoriaAvanzada] = None
        self.controlador_auditoria_simple: Optional[ControladorAuditoriaSimple] = None
        
        # Utilidades
        self.monitor_sistema = MonitorSistemaUtils(self.logger)
        
        # Estado interno
        self._componentes_inicializados = False
        self._metricas_cache = {}
        self._ultima_actualizacion_cache = None
        
        # Referencia al dashboard para estadísticas en tiempo real
        self.dashboard_vista = None
        
        self.logger.info("Controlador Principal inicializado")
    
    def registrar_dashboard(self, dashboard_vista):
        """Registrar la vista del dashboard para actualizaciones en tiempo real"""
        self.dashboard_vista = dashboard_vista
        self.logger.info("Dashboard registrado para actualizaciones en tiempo real")
    
    def inicializar_componentes(self) -> bool:
        """Inicializar todos los componentes."""
        try:
            if self._componentes_inicializados:
                self.logger.info("Componentes ya inicializados")
                return True
            
            self.logger.info("Iniciando inicialización de componentes...")
            
            # Inicializar SIEM
            try:
                self.siem = SIEM()
                self.logger.info("SIEM inicializado")
            except Exception as e:
                self.logger.error(f"Error inicializando SIEM: {e}")
            
            # Inicializar modelos con parámetros mínimos
            try:
                self.escaneador_modelo = EscaneadorMalware()
                if self.siem:
                    config_dict = {}  # Configuración básica vacía
                    self.fim_modelo = FIM(config_dict)
                    self.gestor_cuarentena_modelo = GestorCuarentenaAvanzado(self.siem)
                self.monitor_red_modelo = MonitorRed()
                self.monitor_procesos_modelo = MonitorProcesos()
                self.analizadores_modelo = AnalizadoresUnificados()
                self.constructor_wordlists_modelo = ConstructorWordlists()
                self.logger.info("Modelos inicializados")
            except Exception as e:
                self.logger.error(f"Error inicializando modelos: {e}")
            
            # Inicializar controladores especializados
            self._inicializar_controladores()
            
            self._componentes_inicializados = True
            self.logger.info("Componentes inicializados exitosamente")
            return True
        
        except Exception as e:
            self.logger.error(f"Error crítico inicializando componentes: {e}")
            return False
    
    def _inicializar_controladores(self):
        """Inicializar controladores especializados."""
        try:
            if self.siem and self.escaneador_modelo:
                self.controlador_escaneador = ControladorEscaneador(
                    self.escaneador_modelo, self.siem
                )
            
            if self.siem:
                self.controlador_siem = ControladorSIEM(self.siem)
            
            if self.fim_modelo and self.siem:
                self.controlador_fim = ControladorFIM(self.fim_modelo, self.siem)
            
            if self.monitor_red_modelo and self.siem:
                self.controlador_monitor_red = ControladorMonitorRed(
                    self.monitor_red_modelo, self.siem
                )
            
            if self.gestor_cuarentena_modelo and self.siem:
                self.controlador_cuarentena = ControladorCuarentena(
                    self.gestor_cuarentena_modelo, self.siem
                )
            
            if self.siem:
                self.controlador_reportes = ControladorReportes(self.siem)
            
            if self.siem:
                self.controlador_auditoria_avanzada = ControladorAuditoriaAvanzada(self.siem)
                self.controlador_auditoria_simple = ControladorAuditoriaSimple()
            
            self.logger.info("Controladores especializados inicializados")
        
        except Exception as e:
            self.logger.error(f"Error inicializando controladores: {e}")
    
    def obtener_estado_sistema(self) -> Dict[str, Any]:
        """Obtener estado completo del sistema."""
        try:
            # Verificar estado de componentes
            componentes_activos = []
            componentes_inactivos = []
            
            if self.siem:
                componentes_activos.append('siem')
            else:
                componentes_inactivos.append('siem')
            
            if self.escaneador_modelo:
                componentes_activos.append('escaneador')
            else:
                componentes_inactivos.append('escaneador')
            
            if self.fim_modelo:
                componentes_activos.append('fim')
            else:
                componentes_inactivos.append('fim')
            
            # Obtener recursos del sistema
            recursos_sistema = self.monitor_sistema.obtener_recursos_sistema()
            
            estado_completo = {
                'timestamp': datetime.now().isoformat(),
                'componentes_activos': componentes_activos,
                'componentes_inactivos': componentes_inactivos,
                'recursos_sistema': recursos_sistema,
                'sistema_saludable': len(componentes_activos) > len(componentes_inactivos)
            }
            
            return estado_completo
        
        except Exception as e:
            self.logger.error(f"Error obteniendo estado del sistema: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'sistema_saludable': False
            }
    
    def obtener_metricas(self) -> Dict[str, Any]:
        """Obtener métricas del sistema con cache."""
        try:
            # Verificar cache
            ahora = datetime.now()
            if (self._ultima_actualizacion_cache and 
                (ahora - self._ultima_actualizacion_cache).seconds < 30):
                return self._metricas_cache
            
            # Generar métricas básicas
            metricas = {
                'timestamp': ahora.isoformat(),
                'componentes_inicializados': self._componentes_inicializados,
                'controladores_activos': 0
            }
            
            # Contar controladores activos
            if self.controlador_siem:
                metricas['controladores_activos'] += 1
            if self.controlador_escaneador:
                metricas['controladores_activos'] += 1
            if self.controlador_fim:
                metricas['controladores_activos'] += 1
            if self.controlador_cuarentena:
                metricas['controladores_activos'] += 1
            
            # Agregar recursos del sistema
            recursos = self.monitor_sistema.obtener_recursos_sistema()
            metricas['recursos_sistema'] = recursos
            
            # Actualizar cache
            self._metricas_cache = metricas
            self._ultima_actualizacion_cache = ahora
            
            return metricas
        
        except Exception as e:
            self.logger.error(f"Error obteniendo métricas: {e}")
            return {'error': str(e)}
    
    def ejecutar_escaneo_completo(self) -> Dict[str, Any]:
        """Ejecutar escaneo completo del sistema."""
        try:
            if not self.controlador_escaneador:
                return {'error': 'Controlador de escaneador no disponible'}
            
            self.logger.info("Iniciando escaneo completo del sistema")
            
            # Ejecutar escaneo usando método disponible
            resultado = self.controlador_escaneador.ejecutar_escaneo_completo()
            
            return resultado
        
        except Exception as e:
            self.logger.error(f"Error en escaneo completo: {e}")
            return {'error': str(e)}
    
    def generar_reporte_completo(self, tipo_reporte: str = "general") -> Dict[str, Any]:
        """Generar reporte completo."""
        try:
            if not self.controlador_reportes:
                return {'error': 'Controlador de reportes no disponible'}
            
            # Usar método disponible del controlador
            resultado_reporte = self.controlador_reportes.generar_reporte_real(tipo_reporte)
            return {
                'reporte': resultado_reporte,
                'tipo': tipo_reporte,
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            self.logger.error(f"Error generando reporte: {e}")
            return {'error': str(e)}
    
    def obtener_alertas_recientes(self, limite: int = 10) -> List[Dict[str, Any]]:
        """Obtener alertas recientes."""
        try:
            if not self.controlador_siem:
                return []
            
            return self.controlador_siem.obtener_eventos_recientes(limite)
        
        except Exception as e:
            self.logger.error(f"Error obteniendo alertas: {e}")
            return []
    
    def realizar_auditoria_sistema(self, tipo_auditoria: str = "simple") -> Dict[str, Any]:
        """Realizar auditoría del sistema."""
        try:
            if tipo_auditoria == "avanzada" and self.controlador_auditoria_avanzada:
                resultado = self.controlador_auditoria_avanzada.ejecutar_auditoria_completa()
                # Convertir a diccionario si es necesario
                if hasattr(resultado, 'to_dict'):
                    return resultado.to_dict()
                return {'resultado': str(resultado)}
            elif tipo_auditoria == "simple" and self.controlador_auditoria_simple:
                return self.controlador_auditoria_simple.ejecutar_auditoria_pam()
            else:
                return {'error': f'Tipo de auditoría no soportado: {tipo_auditoria}'}
        
        except Exception as e:
            self.logger.error(f"Error en auditoría: {e}")
            return {'error': str(e)}
    
    def obtener_archivos_cuarentena(self) -> List[Dict[str, Any]]:
        """Obtener lista de archivos en cuarentena."""
        try:
            if not self.controlador_cuarentena:
                return []
            
            return self.controlador_cuarentena.obtener_lista_cuarentena()
        
        except Exception as e:
            self.logger.error(f"Error obteniendo archivos de cuarentena: {e}")
            return []
    
    def obtener_cambios_fim(self) -> List[Dict[str, Any]]:
        """Obtener cambios detectados por FIM."""
        try:
            if not self.controlador_fim:
                return []
            
            return self.controlador_fim.obtener_cambios_recientes()
        
        except Exception as e:
            self.logger.error(f"Error obteniendo cambios FIM: {e}")
            return []
    
    def obtener_eventos_siem(self, limite: int = 50) -> List[Dict[str, Any]]:
        """Obtener eventos recientes del SIEM."""
        try:
            if not self.controlador_siem:
                return []
            
            return self.controlador_siem.obtener_eventos_recientes(limite)
        
        except Exception as e:
            self.logger.error(f"Error obteniendo eventos SIEM: {e}")
            return []
    
    def iniciar_monitoreo_tiempo_real(self) -> bool:
        """Iniciar monitoreo en tiempo real."""
        try:
            if not self._componentes_inicializados:
                self.logger.error("Componentes no inicializados")
                return False
            
            # Iniciar monitoreo FIM si está disponible
            if self.controlador_fim:
                self.controlador_fim.iniciar_monitoreo()
            
            # Iniciar monitoreo de red si está disponible
            if self.controlador_monitor_red:
                self.controlador_monitor_red.iniciar_monitoreo()
            
            self.logger.info("Monitoreo en tiempo real iniciado")
            return True
        
        except Exception as e:
            self.logger.error(f"Error iniciando monitoreo: {e}")
            return False
    
    def detener_monitoreo_tiempo_real(self) -> bool:
        """Detener monitoreo en tiempo real."""
        try:
            # Detener monitores
            if self.controlador_fim:
                self.controlador_fim.detener_monitoreo()
            
            if self.controlador_monitor_red:
                self.controlador_monitor_red.detener_monitoreo()
            
            self.logger.info("Monitoreo en tiempo real detenido")
            return True
        
        except Exception as e:
            self.logger.error(f"Error deteniendo monitoreo: {e}")
            return False
    
    def shutdown(self):
        """Apagar el sistema de manera ordenada."""
        try:
            self.logger.info("Iniciando apagado del sistema...")
            
            # Detener monitoreo
            self.detener_monitoreo_tiempo_real()
            
            # Detener componentes de manera simple
            if self.controlador_fim:
                self.controlador_fim.detener_monitoreo()
            
            if self.controlador_monitor_red:
                self.controlador_monitor_red.detener_monitoreo()
            
            self._activo = False
            self.logger.info("Sistema apagado correctamente")
        
        except Exception as e:
            self.logger.error(f"Error durante el apagado: {e}")
    
    @property
    def activo(self) -> bool:
        """Verificar si el controlador está activo."""
        return self._activo and self._componentes_inicializados
    
    def obtener_resumen_sistema(self) -> Dict[str, Any]:
        """Obtener resumen completo del sistema."""
        try:
            estado = self.obtener_estado_sistema()
            metricas = self.obtener_metricas()
            alertas = self.obtener_alertas_recientes(5)
            
            return {
                'timestamp': datetime.now().isoformat(),
                'estado_sistema': estado,
                'metricas': metricas,
                'alertas_recientes': alertas,
                'componentes_inicializados': self._componentes_inicializados,
                'sistema_activo': self.activo
            }
        
        except Exception as e:
            self.logger.error(f"Error obteniendo resumen: {e}")
            return {'error': str(e)}
    
    async def _inicializar_impl(self) -> bool:
        """Implementación específica de inicialización del controlador principal."""
        try:
            return self.inicializar_componentes()
        except Exception as e:
            self.logger.error(f"Error en inicialización: {e}")
            return False
    
    async def _finalizar_impl(self) -> bool:
        """Implementación específica de finalización del controlador principal."""
        try:
            self.shutdown()
            return True
        except Exception as e:
            self.logger.error(f"Error en finalización: {e}")
            return False
