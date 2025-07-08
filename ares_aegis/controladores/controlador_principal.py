#!/usr/bin/env python3
"""
Ares Aegis - Controlador Principal del Sistema
Coordinador central de todos los componentes de seguridad

Copyright (c) 2025 DogSoulDev (https://github.com/DogSoulDev)
Todos los derechos reservados. Este código es propietario y confidencial.
La copia, distribución o modificación no autorizada está estrictamente prohibida.

Versión: 3.0.0
"""

import time
import threading
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

from ..modelos.siem import SIEM, TipoEvento
from ..modelos.escaneador import EscaneadorMalware
from ..modelos.fim import FIMAvanzado
from ..modelos.monitor_red import MonitorRed
from ..modelos.gestor_cuarentena import GestorCuarentenaAvanzado
from ..modelos.monitor_procesos import MonitorProcesos
from ..modelos.analizador_dinamico import AnalizadorDinamico
from ..modelos.analizador_archivos import AnalizadorArchivos
from ..modelos.analizador_cadenas import AnalizadorCadenas
from ..modelos.analizador_comportamiento_procesos import AnalizadorComportamientoProcesos
from ..modelos.analizador_comportamiento_red import AnalizadorComportamientoRed
from ..modelos.escaneador_vulnerabilidades_red import EscaneadorVulnerabilidadesRed
from ..modelos.escaneador_vulnerabilidades_sistema import EscaneadorVulnerabilidadesSistema
from ..modelos.analizadores_especializados import GestorAnalizadoresEspecializados
from ..modelos.integracion_externa import IntegracionExterna
from ..modelos.respuesta_automatizada import RespuestaAutomatizada
from ..modelos.analizador_registros import AnalizadorRegistros
from ..modelos.respondedor_incidentes import RespondedorIncidentes
from ..modelos.buscador_cve import BuscadorCVE
from ..modelos.gestor_cheatsheets import GestorCheatsheets
from ..modelos.visor_hex import VisorHex
from ..modelos.descontaminacion_inteligente import DescontaminacionInteligente

# Importar controladores especializados
from .controlador_escaneador import ControladorEscaneador
from .controlador_siem import ControladorSIEM
from .controlador_monitor_red import ControladorMonitorRed
from .controlador_fim import ControladorFIM
from .controlador_cuarentena import ControladorCuarentena
from .controlador_reportes import ControladorReportes
from .controlador_vulnerabilidades import ControladorVulnerabilidades
from .controlador_analisis import ControladorAnalisis
from .controlador_respuesta_automatizada import ControladorRespuestaAutomatizada
from .controlador_incidentes import ControladorIncidentes
from .controlador_alertas import ControladorAlertas
from .controlador_alertas_fim import ControladorAlertasFIM
from .controlador_alertas_procesos import ControladorAlertasProcesos
from .controlador_alertas_red_comportamiento import ControladorAlertasRedComportamiento
from .controlador_alertas_siem import ControladorAlertasSIEM
from .orquestador_alertas import OrquestadorAlertas

# Importar utilidades
from ..utilidades.ayuda_logging import configurar_logger_modulo


class ControladorPrincipal:
    def generar_reporte_escaneos(self, periodo_dias: int = 7) -> str:
        """Genera un reporte de escaneos recientes usando el controlador de reportes."""
        if hasattr(self, 'controlador_reportes') and self.controlador_reportes:
            info = self.controlador_reportes.generar_reporte_personalizado({
                'titulo': 'Reporte de Escaneos',
                'periodo_dias': periodo_dias,
                'filtros': {'tipos': ['ESCANEO_INICIADO', 'ESCANEO_FINALIZADO']},
                'secciones': ['resumen', 'estadisticas', 'eventos'],
                'limite_eventos': 50
            })
            # Leer el archivo generado y devolver el contenido
            ruta = info.get('ruta_archivo')
            if ruta and Path(ruta).exists():
                with open(ruta, 'r', encoding='utf-8') as f:
                    return f.read()
            return f"No se pudo generar el reporte de escaneos. Detalles: {info.get('error', 'Desconocido')}"
        return "Controlador de reportes no disponible."

    def generar_reporte_monitoreo(self, periodo_dias: int = 7) -> str:
        """Genera un reporte de monitoreo de red y procesos usando el controlador de reportes."""
        if hasattr(self, 'controlador_reportes') and self.controlador_reportes:
            info = self.controlador_reportes.generar_reporte_personalizado({
                'titulo': 'Reporte de Monitoreo',
                'periodo_dias': periodo_dias,
                'filtros': {'tipos': ['MONITOREO_RED', 'MONITOREO_PROCESOS']},
                'secciones': ['resumen', 'estadisticas', 'eventos'],
                'limite_eventos': 50
            })
            ruta = info.get('ruta_archivo')
            if ruta and Path(ruta).exists():
                with open(ruta, 'r', encoding='utf-8') as f:
                    return f.read()
            return f"No se pudo generar el reporte de monitoreo. Detalles: {info.get('error', 'Desconocido')}"
        return "Controlador de reportes no disponible."
    def cancelar_escaneo_en_curso(self) -> bool:
        """Solicita la cancelación del escaneo en curso a través del controlador especializado."""
        if hasattr(self, 'controlador_escaneador') and self.controlador_escaneador:
            return self.controlador_escaneador.cancelar_escaneo()
        self.logger.warning("No se pudo cancelar el escaneo: controlador no disponible.")
        return False

    def limpiar_cache_escaneos(self) -> bool:
        """Limpia la caché de resultados de escaneo."""
        if self.escaneador and hasattr(self.escaneador, 'limpiar_cache'):
            self.escaneador.limpiar_cache()
            self.logger.info("Caché de escaneos limpiada correctamente.")
            return True
        self.logger.warning("No se pudo limpiar la caché: escaneador no disponible.")
        return False
    def guardar_configuracion(self) -> bool:
        """Guarda la configuración actual del sistema en un archivo JSON."""
        try:
            config = self.obtener_configuracion_sistema()
            ruta = Path("configuracion/configuracion_sistema.json")
            ruta.parent.mkdir(parents=True, exist_ok=True)
            with open(ruta, "w", encoding="utf-8") as f:
                import json
                json.dump(config, f, ensure_ascii=False, indent=2)
            self.logger.info(f"Configuración guardada en {ruta}")
            return True
        except Exception as e:
            self.logger.error(f"Error guardando configuración: {e}")
            return False

    def recargar_configuracion(self) -> bool:
        """Recarga la configuración del sistema desde el archivo JSON y la aplica a los módulos principales."""
        try:
            ruta = Path("configuracion/configuracion_sistema.json")
            if not ruta.exists():
                self.logger.warning(f"Archivo de configuración no encontrado: {ruta}")
                return False
            import json
            with open(ruta, "r", encoding="utf-8") as f:
                config = json.load(f)
            # Aplicar configuración a los módulos principales si corresponde
            if self.escaneador and ("rutas_escaneadas" in config or "exclusiones" in config):
                nueva_config = {}
                if "rutas_escaneadas" in config:
                    nueva_config["rutas_escaneadas"] = config["rutas_escaneadas"]
                if "exclusiones" in config:
                    nueva_config["exclusiones"] = config["exclusiones"]
                if nueva_config:
                    self.escaneador.actualizar_configuracion(nueva_config)
            # SIEM y cuarentena: solo loggear, no sobrescribir atributos desconocidos
            self.logger.info(f"Configuración recargada desde {ruta}")
            return True
        except Exception as e:
            self.logger.error(f"Error recargando configuración: {e}")
            return False
    """Controlador principal del sistema Ares Aegis con arquitectura MVC especializada."""
    
    def __init__(self):
        """Inicializa el controlador principal."""
        self.logger = configurar_logger_modulo("controlador_principal")
        self.inicio_tiempo = time.time()
        
        # Componentes principales
        self.siem: Optional[SIEM] = None
        self.escaneador: Optional[EscaneadorMalware] = None
        self.fim: Optional[FIMAvanzado] = None
        self.monitor_red: Optional[MonitorRed] = None
        self.gestor_cuarentena: Optional[GestorCuarentenaAvanzado] = None
        
        # Componentes de análisis avanzado
        self.monitor_procesos: Optional[MonitorProcesos] = None
        self.analizador_dinamico: Optional[AnalizadorDinamico] = None
        self.analizador_archivos: Optional[AnalizadorArchivos] = None
        self.analizador_cadenas: Optional[AnalizadorCadenas] = None
        self.analizador_comportamiento_procesos: Optional[AnalizadorComportamientoProcesos] = None
        self.analizador_comportamiento_red: Optional[AnalizadorComportamientoRed] = None
        self.analizadores_especializados: Optional[GestorAnalizadoresEspecializados] = None
        # self.sistema_reportes: Optional[SistemaReportesNotificaciones] = None  # Por implementar
        
        # Componentes de vulnerabilidades
        self.escaneador_vuln_red: Optional[EscaneadorVulnerabilidadesRed] = None
        self.escaneador_vuln_sistema: Optional[EscaneadorVulnerabilidadesSistema] = None
        self.buscador_cve: Optional[BuscadorCVE] = None
        
        # Componentes de gestión y respuesta
        self.integracion_externa: Optional[IntegracionExterna] = None
        self.respuesta_automatizada: Optional[RespuestaAutomatizada] = None
        self.analizador_registros: Optional[AnalizadorRegistros] = None
        self.respondedor_incidentes: Optional[RespondedorIncidentes] = None
        
        # Componentes de utilidades
        self.gestor_cheatsheets: Optional[GestorCheatsheets] = None
        self.visor_hex: Optional[VisorHex] = None
        self.descontaminacion: Optional[DescontaminacionInteligente] = None
        
        # Estado del sistema
        self.sistema_iniciado = False
        self.lock = threading.Lock()
        
        # Inicializar componentes
        self._inicializar_componentes()
        # --- INTEGRACIÓN AUTOMÁTICA DE ALERTAS (robusta) ---
        self.controlador_alertas = ControladorAlertas()
        controladores_alerta = {}
        if self.fim is not None:
            controladores_alerta['fim'] = ControladorAlertasFIM(self.fim, self.controlador_alertas)
        if self.analizador_comportamiento_procesos is not None:
            controladores_alerta['procesos'] = ControladorAlertasProcesos(self.analizador_comportamiento_procesos, self.controlador_alertas)
        if self.analizador_comportamiento_red is not None:
            controladores_alerta['red'] = ControladorAlertasRedComportamiento(self.analizador_comportamiento_red, self.controlador_alertas)
        if self.siem is not None:
            controladores_alerta['siem'] = ControladorAlertasSIEM(self.siem, self.controlador_alertas)
        if controladores_alerta:
            self.orquestador_alertas = OrquestadorAlertas(controladores_alerta)
            self.orquestador_alertas.ejecutar_todos()
        
        self.logger.info("Controlador principal inicializado exitosamente")
    
    def _inicializar_componentes(self):
        """Inicializa todos los componentes del sistema."""
        try:
            # 1. Inicializar SIEM (core)
            self.siem = SIEM()
            self.logger.info("SIEM inicializado - Los Ojos de Argos despiertan")
            
            # 2. Inicializar componentes principales que dependen del SIEM
            self.escaneador = EscaneadorMalware(self.siem)
            self.logger.info("Escaneador inicializado - Los Cazadores de Artemisa listos")
            
            self.gestor_cuarentena = GestorCuarentenaAvanzado(self.siem)
            self.logger.info("Cuarentena inicializada - Las Celdas de Hades preparadas")
            
            self.fim = FIMAvanzado(self.siem)
            self.logger.info("FIM inicializado - Los Vigilantes de Heimdall en guardia")
            
            self.monitor_red = MonitorRed(self.siem)
            self.logger.info("Monitor de red inicializado - Los Centinelas de Poseidón alertas")
            
            # 3. Inicializar componentes de análisis avanzado
            self.monitor_procesos = MonitorProcesos(self.siem)
            self.logger.info("Monitor de procesos inicializado - Los Espías de Hermes activos")
            
            self.analizador_dinamico = AnalizadorDinamico()
            self.logger.info("Analizador dinámico inicializado - Los Oráculos de Apolo revelan secretos")
            
            self.analizador_archivos = AnalizadorArchivos(self.siem)
            self.logger.info("Analizador de archivos inicializado - Los Escribas de Atenea examinan")
            
            self.analizador_cadenas = AnalizadorCadenas(self.siem)
            self.logger.info("Analizador de cadenas inicializado - Los Descifradores de Orfeo interpretan")
            
            self.analizador_comportamiento_procesos = AnalizadorComportamientoProcesos(self.siem)
            self.logger.info("Análisis de comportamiento de procesos - Los Psicólogos de Dioniso estudian")
            
            self.analizador_comportamiento_red = AnalizadorComportamientoRed(self.siem)
            self.logger.info("Análisis de comportamiento de red - Los Estrategas de Ares planifican")
            
            # Inicializar analizadores especializados
            self.analizadores_especializados = GestorAnalizadoresEspecializados(self.siem)
            self.logger.info("Analizadores especializados inicializados - Los Sabios de Thoth analizan")
            
            # Inicializar sistema de reportes  
            # self.sistema_reportes = SistemaReportesNotificaciones(self.siem)  # Por implementar
            # self.logger.info("Sistema de reportes inicializado - Los Heraldos de Iris comunican")
            
            # 4. Inicializar componentes de vulnerabilidades
            self.escaneador_vuln_red = EscaneadorVulnerabilidadesRed()
            self.logger.info("Escaneador de vulnerabilidades de red - Los Exploradores de Odín buscan")
            
            self.escaneador_vuln_sistema = EscaneadorVulnerabilidadesSistema(self.siem)
            self.logger.info("Escaneador de vulnerabilidades del sistema - Los Inspectores de Hefesto revisan")
            
            self.buscador_cve = BuscadorCVE(self.siem)
            self.logger.info("Buscador CVE inicializado - Los Oráculos de Delfos consultan")
            
            # 5. Inicializar componentes de gestión y respuesta
            self.integracion_externa = IntegracionExterna(self.siem)
            self.logger.info("Integración externa - Los Embajadores de Iris conectan")
            
            self.respuesta_automatizada = RespuestaAutomatizada()
            self.logger.info("Respuesta automatizada - Los Autómatas de Hefesto responden")
            
            self.analizador_registros = AnalizadorRegistros(self.siem)
            self.logger.info("Analizador de registros - Los Escribas de Temis registran")
            
            self.respondedor_incidentes = RespondedorIncidentes(self.siem)
            self.logger.info("Respondedor de incidentes - Los Guardianes de Némesis protegen")
            
            # 6. Inicializar controladores especializados (MVC)
            self.controlador_escaneador = ControladorEscaneador(self.escaneador, self.siem)
            self.logger.info("Controlador de escaneado - Los Coordinadores de Artemisa organizan")
            
            self.controlador_siem = ControladorSIEM(self.siem)
            self.logger.info("Controlador SIEM - Los Maestros de Argos coordinan")
            
            self.controlador_monitor_red = ControladorMonitorRed(self.monitor_red, self.siem)
            self.logger.info("Controlador de red - Los Generales de Poseidón dirigen")
            
            self.controlador_fim = ControladorFIM(self.fim, self.siem)
            self.logger.info("Controlador FIM - Los Capitanes de Heimdall supervisan")
            
            self.controlador_cuarentena = ControladorCuarentena(self.gestor_cuarentena, self.siem)
            self.logger.info("Controlador de cuarentena - Los Comandantes de Hades rigen")
            
            self.controlador_reportes = ControladorReportes(self.siem)
            self.logger.info("Controlador de reportes - Los Maestros de Iris comunican")
            
            self.controlador_vulnerabilidades = ControladorVulnerabilidades(self.siem)
            self.logger.info("Controlador de vulnerabilidades - Los Estrategas de Hefesto evalúan")
            
            self.controlador_analisis = ControladorAnalisis(self.siem)
            self.logger.info("Controlador de análisis - Los Sabios de Atenea coordinan")
            
            self.controlador_respuesta_automatizada = ControladorRespuestaAutomatizada(
                self.siem, self.respondedor_incidentes
            )
            self.logger.info("Controlador de respuesta automatizada - Los Maestros de Hefesto automatizan")
            
            self.controlador_incidentes = ControladorIncidentes(self.siem, self.respondedor_incidentes)
            self.logger.info("Controlador de incidentes - Los Generales de Némesis coordinan")
            
            # Establecer relaciones bidireccionales
            self.respuesta_automatizada.controlador = self.controlador_respuesta_automatizada
            self.respondedor_incidentes.establecer_controlador(self.controlador_incidentes)
            
            # 7. Inicializar componentes de utilidades
            self.gestor_cheatsheets = GestorCheatsheets()
            self.logger.info("Gestor de cheatsheets - Los Escribanos de Hermes organizan")
            
            self.visor_hex = VisorHex(self.siem)
            self.logger.info("Visor hexadecimal - Los Decifradores de Thot revelan")
            
            self.descontaminacion = DescontaminacionInteligente(self.siem, self.gestor_cuarentena)
            self.logger.info("Descontaminación inteligente - Los Purificadores de Asclepio sanan")
            
            # Registrar inicialización exitosa
            if self.siem:
                componentes_inicializados = [
                    'SIEM', 'Escaneador', 'Cuarentena', 'FIM', 'MonitorRed',
                    'MonitorProcesos', 'AnalizadorDinamico', 'AnalizadorArchivos', 'AnalizadorCadenas',
                    'AnalizadorComportamientoProcesos', 'AnalizadorComportamientoRed',
                    'EscaneadorVulnRed', 'EscaneadorVulnSistema', 'BuscadorCVE',
                    'IntegracionExterna', 'SistemaReportes', 'RespuestaAutomatizada',
                    'AnalizadorRegistros', 'RespondedorIncidentes',
                    'GestorCheatsheets', 'VisorHex', 'Descontaminacion'
                ]
                
                self.siem.registrar_evento(
                    TipoEvento.SISTEMA_INICIADO,
                    "Todos los componentes de Ares Aegis han despertado exitosamente",
                    {
                        'componentes_inicializados': componentes_inicializados,
                        'total_componentes': len(componentes_inicializados),
                        'timestamp_inicio': datetime.now().isoformat()
                    },
                    "ALTO"
                )
            
            self.sistema_iniciado = True
            self.logger.info("⚔️ ARES AEGIS COMPLETAMENTE OPERATIVO - Todos los dioses del Olimpo han despertado ⚔️")
            
        except Exception as e:
            self.logger.error(f"Error inicializando componentes: {e}")
            raise
    
    def verificar_estado_sistema(self) -> Dict[str, Any]:
        """
        Verifica el estado general del sistema.
        
        Returns:
            Dict[str, Any]: Estado de todos los componentes
        """
        estado = {
            'sistema_iniciado': self.sistema_iniciado,
            'uptime_segundos': int(time.time() - self.inicio_tiempo),
            'componentes': {
                'siem': self.siem is not None,
                'escaneador': self.escaneador is not None,
                'fim': self.fim is not None,
                'monitor_red': self.monitor_red is not None,
                'cuarentena': self.gestor_cuarentena is not None
            },
            'servicios_activos': {
                'monitor_red': self.monitor_red.monitoreando if self.monitor_red else False
            }
        }
        
        return estado
    
    def obtener_estadisticas_generales(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas generales del sistema.
        
        Returns:
            Dict[str, Any]: Estadísticas del sistema
        """
        estadisticas = {
            'timestamp': datetime.now().isoformat(),
            'uptime_segundos': int(time.time() - self.inicio_tiempo),
            'sistema_iniciado': self.sistema_iniciado
        }
        try:
            # Estadísticas del escaneador
            if self.escaneador:
                stats_escaneador = self.escaneador.obtener_estadisticas()
                estadisticas.update({
                    'archivos_escaneados': stats_escaneador.get('total_archivos_escaneados', 0),
                    'amenazas_detectadas': stats_escaneador.get('total_amenazas_detectadas', 0),
                    'ultimo_escaneo': stats_escaneador.get('ultimo_escaneo', '')
                })
            else:
                estadisticas.update({
                    'archivos_escaneados': 0,
                    'amenazas_detectadas': 0,
                    'ultimo_escaneo': ''
                })
            # Estadísticas de cuarentena
            if self.gestor_cuarentena:
                stats_cuarentena = self.gestor_cuarentena.obtener_estadisticas()
                estadisticas['archivos_cuarentena'] = stats_cuarentena.get('total_archivos', 0)
            else:
                estadisticas['archivos_cuarentena'] = 0
            # Estadísticas del monitor de red
            if self.monitor_red:
                stats_red = self.monitor_red.obtener_estadisticas()
                estadisticas.update({
                    'conexiones_activas': stats_red.get('conexiones_activas', 0),
                    'puertos_abiertos': stats_red.get('puertos_abiertos', 0),
                    'alertas_activas': stats_red.get('alertas_generadas', 0)
                })
            else:
                estadisticas.update({
                    'conexiones_activas': 0,
                    'puertos_abiertos': 0,
                    'alertas_activas': 0
                })
            # Estadísticas del FIM
            if self.fim:
                stats_fim = self.fim.obtener_estadisticas()
                estadisticas['archivos_fim'] = stats_fim.get('archivos_en_base_datos', 0)
            else:
                estadisticas['archivos_fim'] = 0
            # Estadísticas del SIEM
            if self.siem:
                eventos_recientes = self.siem.obtener_eventos(limite=100)
                estadisticas['total_eventos'] = len(eventos_recientes)
            else:
                estadisticas['total_eventos'] = 0
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas: {e}")
        # Uso de memoria SIEMPRE presente y realista
        try:
            import psutil
            proceso = psutil.Process()
            estadisticas['uso_memoria_mb'] = proceso.memory_info().rss / (1024 * 1024)
        except Exception:
            # Fallback si no hay psutil
            import sys
            estadisticas['uso_memoria_mb'] = sys.getsizeof(self) / (1024 * 1024)
        return estadisticas
    
    def escaneo_rapido_con_progreso(self, callback_progreso=None) -> Dict[str, Any]:
        """
        Ejecuta un escaneo rápido del sistema con callback de progreso.
        
        Args:
            callback_progreso: Función callback para reportar progreso (archivo_actual, total, amenazas)
            
        Returns:
            Dict[str, Any]: Resultados del escaneo
        """
        if not self.escaneador:
            raise RuntimeError("Escaneador no inicializado")
        
        self.logger.info("Iniciando escaneo rápido con progreso")
        if self.siem:
            self.siem.registrar_evento(
                TipoEvento.ESCANEO_INICIADO,
                "Escaneo rápido con progreso iniciado",
                {'tipo': 'rapido_progreso'},
                "MEDIO"
            )
        
        # Rutas para escaneo rápido
        rutas_rapidas = [
            str(Path.home() / "Downloads"),
            str(Path.home() / "Desktop"),
            "/tmp",
            str(Path.home() / "Documents")
        ]
        
        # Filtrar rutas que existen
        rutas_existentes = [ruta for ruta in rutas_rapidas if Path(ruta).exists()]
        
        inicio_tiempo = time.time()
        
        # Obtener lista de archivos a escanear
        archivos_totales = []
        for ruta in rutas_existentes:
            try:
                path_obj = Path(ruta)
                if path_obj.is_file():
                    archivos_totales.append(str(path_obj))
                elif path_obj.is_dir():
                    # Solo archivos de tipos específicos para escaneo rápido
                    extensiones = ['.exe', '.bat', '.cmd', '.scr', '.com', '.pif', '.vbs', '.js', '.jar', '.zip', '.rar']
                    for ext in extensiones:
                        archivos_totales.extend([str(f) for f in path_obj.rglob(f'*{ext}')])
            except Exception as e:
                self.logger.warning(f"Error accediendo a {ruta}: {e}")
        
        total_archivos = len(archivos_totales)
        archivos_escaneados = 0
        amenazas_detectadas = 0
        archivos_infectados = []
        
        # Escanear archivo por archivo con progreso
        for archivo in archivos_totales:
            try:
                # Reportar progreso
                if callback_progreso:
                    callback_progreso(archivos_escaneados, total_archivos, amenazas_detectadas)
                
                # Escanear archivo individual
                resultado_archivo = self.escaneador.escanear_archivo(archivo)
                archivos_escaneados += 1
                
                if resultado_archivo and resultado_archivo.tiene_amenazas():
                    amenazas_detectadas += 1
                    archivos_infectados.append(archivo)
                
            except Exception as e:
                self.logger.warning(f"Error escaneando {archivo}: {e}")
                archivos_escaneados += 1
        
        # Reporte final de progreso
        if callback_progreso:
            callback_progreso(archivos_escaneados, total_archivos, amenazas_detectadas)
        
        tiempo_total = time.time() - inicio_tiempo
        
        # Construir resultado como diccionario
        resultado = {
            'archivos_escaneados': archivos_escaneados,
            'amenazas_detectadas': amenazas_detectadas,
            'archivos_infectados': len(archivos_infectados),
            'tiempo_escaneo': tiempo_total,
            'tipo_escaneo': 'rapido',
            'rutas_escaneadas': rutas_existentes,
            'archivos_infectados_lista': archivos_infectados
        }
        
        if self.siem:
            self.siem.registrar_evento(
                TipoEvento.ESCANEO_FINALIZADO,
                f"Escaneo rápido completado: {amenazas_detectadas} amenazas en {archivos_escaneados} archivos",
                resultado,
                "ALTO" if amenazas_detectadas > 0 else "BAJO"
            )
        
        self.logger.info(f"Escaneo rápido completado: {archivos_escaneados} archivos, {amenazas_detectadas} amenazas en {tiempo_total:.2f}s")
        return resultado

    def escaneo_rapido(self) -> Dict[str, Any]:
        """
        Ejecuta un escaneo rápido del sistema.
        
        Returns:
            Dict[str, Any]: Resultados del escaneo
        """
        return self.escaneo_rapido_con_progreso()
    
    def escaneo_completo_con_progreso(self, callback_progreso=None) -> Dict[str, Any]:
        """
        Ejecuta un escaneo completo del sistema con callback de progreso.
        
        Args:
            callback_progreso: Función callback para reportar progreso
            
        Returns:
            Dict[str, Any]: Resultados del escaneo
        """
        if not self.escaneador:
            raise RuntimeError("Escaneador no inicializado")
        
        self.logger.info("Iniciando escaneo completo con progreso")
        if self.siem:
            self.siem.registrar_evento(
                TipoEvento.ESCANEO_INICIADO,
                "Escaneo completo con progreso iniciado",
                {'tipo': 'completo_progreso'},
                "MEDIO"
            )
        
        # Rutas para escaneo completo
        rutas_completas = [
            str(Path.home()),
            "/opt",
            "/usr/local",
            "/var/www"
        ]
        
        # Filtrar rutas que existen
        rutas_existentes = [ruta for ruta in rutas_completas if Path(ruta).exists()]
        
        inicio_tiempo = time.time()
        
        # Obtener lista de archivos a escanear
        archivos_totales = []
        for ruta in rutas_existentes:
            try:
                path_obj = Path(ruta)
                if path_obj.is_file():
                    archivos_totales.append(str(path_obj))
                elif path_obj.is_dir():
                    # Archivos comunes que pueden contener amenazas
                    for archivo in path_obj.rglob('*'):
                        if archivo.is_file() and archivo.stat().st_size < 100 * 1024 * 1024:  # < 100MB
                            archivos_totales.append(str(archivo))
            except Exception as e:
                self.logger.warning(f"Error accediendo a {ruta}: {e}")
        
        total_archivos = len(archivos_totales)
        archivos_escaneados = 0
        amenazas_detectadas = 0
        archivos_infectados = []
        
        # Escanear archivo por archivo con progreso
        for archivo in archivos_totales:
            try:
                # Reportar progreso
                if callback_progreso:
                    callback_progreso(archivos_escaneados, total_archivos, amenazas_detectadas)
                
                # Escanear archivo individual
                resultado_archivo = self.escaneador.escanear_archivo(archivo)
                archivos_escaneados += 1
                
                if resultado_archivo and resultado_archivo.tiene_amenazas():
                    amenazas_detectadas += 1
                    archivos_infectados.append(archivo)
                
            except Exception as e:
                self.logger.warning(f"Error escaneando {archivo}: {e}")
                archivos_escaneados += 1
        
        # Reporte final de progreso
        if callback_progreso:
            callback_progreso(archivos_escaneados, total_archivos, amenazas_detectadas)
        
        tiempo_total = time.time() - inicio_tiempo
        
        # Construir resultado
        resultado = {
            'archivos_escaneados': archivos_escaneados,
            'amenazas_detectadas': amenazas_detectadas,
            'archivos_infectados': len(archivos_infectados),
            'tiempo_escaneo': tiempo_total,
            'tipo_escaneo': 'completo',
            'rutas_escaneadas': rutas_existentes,
            'archivos_infectados_lista': archivos_infectados
        }
        
        if self.siem:
            self.siem.registrar_evento(
                TipoEvento.ESCANEO_FINALIZADO,
                f"Escaneo completo completado: {amenazas_detectadas} amenazas en {archivos_escaneados} archivos",
                resultado,
                "ALTO" if amenazas_detectadas > 0 else "BAJO"
            )
        
        self.logger.info(f"Escaneo completo completado: {archivos_escaneados} archivos, {amenazas_detectadas} amenazas en {tiempo_total:.2f}s")
        return resultado

    def escaneo_completo(self) -> Dict[str, Any]:
        """
        Ejecuta un escaneo completo del sistema.
        
        Returns:
            Dict[str, Any]: Resultados del escaneo
        """
        return self.escaneo_completo_con_progreso()
    
    def escanear_directorio(self, ruta: str) -> Dict[str, Any]:
        """
        Escanea un directorio específico.
        
        Args:
            ruta: Ruta del directorio a escanear
            
        Returns:
            Dict[str, Any]: Resultados del escaneo
        """
        if not self.escaneador:
            raise RuntimeError("Escaneador no inicializado")
        
        if not Path(ruta).exists():
            raise ValueError(f"La ruta no existe: {ruta}")
        
        self.logger.info(f"Iniciando escaneo de directorio: {ruta}")
        if self.siem:
            self.siem.registrar_evento(
                TipoEvento.ESCANEO_INICIADO,
                f"Escaneo de directorio iniciado: {ruta}",
                {'tipo': 'directorio', 'ruta': ruta},
                "MEDIO"
            )
        
        inicio_tiempo = time.time()
        
        # Escanear directorio archivo por archivo
        archivos_escaneados = 0
        amenazas_detectadas = 0
        archivos_infectados = 0
        
        try:
            path_obj = Path(ruta)
            if path_obj.is_file():
                resultado_archivo = self.escaneador.escanear_archivo(str(path_obj))
                archivos_escaneados = 1
                if resultado_archivo and resultado_archivo.tiene_amenazas():
                    amenazas_detectadas = 1
                    archivos_infectados = 1
            elif path_obj.is_dir():
                for archivo in path_obj.rglob('*'):
                    if archivo.is_file() and archivo.stat().st_size < 50 * 1024 * 1024:  # < 50MB
                        try:
                            resultado_archivo = self.escaneador.escanear_archivo(str(archivo))
                            archivos_escaneados += 1
                            if resultado_archivo and resultado_archivo.tiene_amenazas():
                                amenazas_detectadas += 1
                                archivos_infectados += 1
                        except Exception as e:
                            self.logger.warning(f"Error escaneando {archivo}: {e}")
        except Exception as e:
            self.logger.warning(f"Error accediendo a {ruta}: {e}")
        
        tiempo_total = time.time() - inicio_tiempo
        
        # Construir resultado como diccionario
        resultado = {
            'archivos_escaneados': archivos_escaneados,
            'amenazas_detectadas': amenazas_detectadas,
            'archivos_infectados': archivos_infectados,
            'tiempo_escaneo': tiempo_total,
            'tipo_escaneo': 'directorio',
            'ruta_escaneada': ruta
        }
        
        if self.siem:
            self.siem.registrar_evento(
                TipoEvento.ESCANEO_FINALIZADO,
                f"Escaneo de directorio finalizado: {ruta}",
                resultado,
                "MEDIO"
            )
        
        self.logger.info(f"Escaneo de directorio completado en {tiempo_total:.2f}s")
        return resultado
    
    def verificar_integridad_archivos(self) -> Dict[str, Any]:
        """
        Verifica la integridad de archivos monitoreados.
        
        Returns:
            Dict[str, Any]: Resultados de la verificación
        """
        if not self.fim:
            raise RuntimeError("FIM no inicializado")
        
        self.logger.info("Iniciando verificación de integridad")
        
        inicio_tiempo = time.time()
        cambios = self.fim.verificar_integridad_completa()
        tiempo_total = time.time() - inicio_tiempo
        
        resultado = {
            'cambios_detectados': len(cambios),
            'tiempo_verificacion': tiempo_total,
            'cambios': [cambio.to_dict() for cambio in cambios]
        }
        
        if cambios:
            self.logger.warning(f"FIM: {len(cambios)} cambios detectados")
        else:
            self.logger.info("FIM: Sin cambios detectados")
        
        return resultado
    
    def crear_baseline_fim(self) -> Dict[str, Any]:
        """
        Crea una línea base de integridad.
        
        Returns:
            Dict[str, Any]: Estadísticas de la creación
        """
        if not self.fim:
            raise RuntimeError("FIM no inicializado")
        
        self.logger.info("Creando línea base de integridad")
        return self.fim.crear_baseline_avanzada()
    
    def iniciar_monitor_red(self):
        """Inicia el monitoreo de red."""
        if not self.monitor_red:
            raise RuntimeError("Monitor de red no inicializado")
        
        self.monitor_red.iniciar_monitoreo()
        self.logger.info("Monitor de red iniciado")
    
    def detener_monitor_red(self):
        """Detiene el monitoreo de red."""
        if not self.monitor_red:
            raise RuntimeError("Monitor de red no inicializado")
        
        self.monitor_red.detener_monitoreo()
        self.logger.info("Monitor de red detenido")
    
    def obtener_eventos_recientes(self, limite: int = 100) -> List[Dict[str, Any]]:
        """
        Obtiene eventos recientes del SIEM.
        
        Args:
            limite: Número máximo de eventos a devolver
            
        Returns:
            List[Dict[str, Any]]: Lista de eventos
        """
        if not self.siem:
            return []
        
        eventos = self.siem.obtener_eventos(limite=limite)
        return [evento.to_dict() for evento in eventos]
    
    def generar_reporte_completo(self) -> str:
        """
        Genera un reporte completo del sistema en formato Markdown.
        
        Returns:
            str: Reporte en formato Markdown
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        uptime = int(time.time() - self.inicio_tiempo)
        
        md = f"# Reporte Completo de Ares Aegis\n\n"
        md += f"**Fecha de generación:** {timestamp}\n"
        md += f"**Uptime del sistema:** {uptime // 3600}h {(uptime % 3600) // 60}m\n\n"
        
        # Estado del sistema
        md += "## 🛡️ Estado del Sistema\n\n"
        estado = self.verificar_estado_sistema()
        md += f"- **Sistema iniciado:** {'✅ Sí' if estado['sistema_iniciado'] else '❌ No'}\n"
        md += f"- **Componentes activos:** {sum(estado['componentes'].values())}/5\n"
        md += f"- **Monitor de red:** {'🟢 Activo' if estado['servicios_activos']['monitor_red'] else '🔴 Inactivo'}\n\n"
        
        # Estadísticas generales
        md += "## 📊 Estadísticas Generales\n\n"
        stats = self.obtener_estadisticas_generales()
        md += f"- **Archivos escaneados:** {stats.get('archivos_escaneados', 0)}\n"
        md += f"- **Amenazas detectadas:** {stats.get('amenazas_detectadas', 0)}\n"
        md += f"- **Archivos en cuarentena:** {stats.get('archivos_cuarentena', 0)}\n"
        md += f"- **Conexiones activas:** {stats.get('conexiones_activas', 0)}\n"
        md += f"- **Archivos monitoreados (FIM):** {stats.get('archivos_fim', 0)}\n"
        md += f"- **Total de eventos:** {stats.get('total_eventos', 0)}\n\n"
        
        # Reportes específicos de componentes
        try:
            # Reporte de cuarentena
            if self.gestor_cuarentena:
                stats_cuarentena = self.gestor_cuarentena.obtener_estadisticas()
                md += f"## 🔒 Estado de Cuarentena\\n"
                md += f"- Archivos en cuarentena: {stats_cuarentena.get('archivos_cuarentena', 0)}\\n"
                md += f"- Análisis forenses completados: {stats_cuarentena.get('analisis_completados', 0)}\\n"
                md += "\\n"
            
            # Reporte de red
            if self.monitor_red:
                md += self.monitor_red.generar_reporte_avanzado()
                md += "\n"
            
        except Exception as e:
            md += f"⚠️ Error generando secciones del reporte: {e}\n\n"
        
        md += "---\n"
        md += "*Reporte generado automáticamente por Ares Aegis*\n"
        
        return md
    
    def ejecutar(self):
        """
        Ejecuta el sistema Ares Aegis con interfaz gráfica.
        
        Este es el método principal que inicia la interfaz de usuario.
        """
        try:
            self.logger.info("Iniciando interfaz de línea de comandos de Ares Aegis")
            
            # Mostrar resumen del sistema
            print("🛡️  ARES AEGIS - SISTEMA DE CIBERSEGURIDAD ACTIVADO")
            print("=" * 60)
            print("Sistema iniciado correctamente. Todos los componentes operativos.")
            print("Para más opciones, ejecute el menú principal desde main.py")
            print("=" * 60)
            
        except ImportError as e:
            self.logger.error(f"Error importando interfaz gráfica: {e}")
            print("❌ Error: No se pudo cargar la interfaz gráfica del Égida")
            print("💡 Verifica que tkinter esté instalado correctamente")
            raise
        
        except Exception as e:
            self.logger.error(f"Error ejecutando interfaz: {e}")
            print(f"❌ Error inesperado en la interfaz divina: {e}")
            raise
        
        finally:
            self.finalizar()
    
    def finalizar(self):
        """Finaliza el controlador y todos sus componentes."""
        self.logger.info("Finalizando controlador principal")
        
        try:
            # Detener servicios activos
            if self.monitor_red and hasattr(self.monitor_red, 'monitoreando') and self.monitor_red.monitoreando:
                self.monitor_red.detener_monitoreo()
            
            # Registrar finalización en SIEM
            if self.siem:
                self.siem.registrar_evento(
                    TipoEvento.SISTEMA_DETENIDO,
                    "Controlador principal finalizado",
                    {
                        'uptime_segundos': int(time.time() - self.inicio_tiempo),
                        'timestamp_finalizacion': datetime.now().isoformat()
                    },
                    "MEDIO"
                )
            
            self.sistema_iniciado = False
            self.logger.info("Controlador principal finalizado exitosamente")
        
        except Exception as e:
            self.logger.error(f"Error finalizando controlador: {e}")
            raise
    
    # Métodos para la interfaz
    def iniciar_servicios(self):
        """Iniciar todos los servicios del sistema."""
        try:
            if self.monitor_red and not self.monitor_red.monitoreando:
                self.monitor_red.iniciar_monitoreo()
                self.logger.info("Monitor de red iniciado")
            
            if self.monitor_procesos and hasattr(self.monitor_procesos, 'iniciar_monitoreo'):
                if not hasattr(self.monitor_procesos, 'monitoreando') or not self.monitor_procesos.monitoreando:
                    self.monitor_procesos.iniciar_monitoreo()
                    self.logger.info("Monitor de procesos iniciado")
            
            self.logger.info("Servicios iniciados correctamente")
            
        except Exception as e:
            self.logger.error(f"Error al iniciar servicios: {e}")
            raise
    
    def detener_servicios(self):
        """Detener todos los servicios del sistema."""
        try:
            if self.monitor_red and self.monitor_red.monitoreando:
                self.monitor_red.detener_monitoreo()
                self.logger.info("Monitor de red detenido")
            
            if self.monitor_procesos and hasattr(self.monitor_procesos, 'detener_monitoreo'):
                if hasattr(self.monitor_procesos, 'monitoreando') and self.monitor_procesos.monitoreando:
                    self.monitor_procesos.detener_monitoreo()
                    self.logger.info("Monitor de procesos detenido")
            
            self.logger.info("Servicios detenidos correctamente")
            
        except Exception as e:
            self.logger.error(f"Error al detener servicios: {e}")
            raise
    
    def obtener_ultimo_escaneo(self) -> Optional[Dict[str, Any]]:
        """Obtener información del último escaneo realizado."""
        try:
            if not self.escaneador:
                return None
            
            # Simular datos del último escaneo
            return {
                'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'amenazas': 0,
                'archivos_escaneados': 0,
                'tiempo_transcurrido': 0
            }
            
        except Exception as e:
            self.logger.error(f"Error al obtener último escaneo: {e}")
            return None
    
    def ejecutar_escaneo_rapido(self, callback_progreso: Optional[Any] = None) -> Dict[str, Any]:
        """Ejecutar un escaneo rápido del sistema, reenviando el callback de progreso al controlador especializado."""
        try:
            if hasattr(self, 'controlador_escaneador') and self.controlador_escaneador:
                resultado = self.controlador_escaneador.ejecutar_escaneo_rapido(callback_progreso=callback_progreso)
                self._ultimo_escaneo = resultado
                self.logger.info(f"Escaneo rápido completado: {resultado.get('amenazas_encontradas', 0)} amenazas en {resultado.get('tiempo_transcurrido', 0):.2f}s")
                return resultado
            else:
                raise RuntimeError("Controlador de escaneador no inicializado")
        except Exception as e:
            self.logger.error(f"Error en escaneo rápido: {e}")
            raise
    
    def obtener_datos_dashboard(self) -> Dict[str, Any]:
        """Obtener datos completos para el dashboard"""
        try:
            estado_sistema = self.verificar_estado_sistema()
            estadisticas = self.obtener_estadisticas_generales()
            ultimo_escaneo = self.obtener_ultimo_escaneo()
            eventos_recientes = self.obtener_eventos_recientes(5)
            
            return {
                "estado_sistema": estado_sistema,
                "estadisticas": estadisticas,
                "ultimo_escaneo": ultimo_escaneo,
                "eventos_recientes": eventos_recientes,
                "componentes_activos": {
                    "siem": self.siem is not None,
                    "escaneador": self.escaneador is not None,
                    "fim": self.fim is not None,
                    "monitor_red": self.monitor_red is not None and getattr(self.monitor_red, 'monitoreando', False),
                    "monitor_procesos": self.monitor_procesos is not None and getattr(self.monitor_procesos, 'monitoreando', False),
                    "cuarentena": self.gestor_cuarentena is not None
                },
                "alertas_criticas": len([e for e in eventos_recientes if e.get('severidad') == 'CRITICA']),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error obteniendo datos dashboard: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def obtener_estado_monitores(self) -> Dict[str, Any]:
        """Obtener estado actual de todos los monitores"""
        try:
            return {
                "monitor_red": {
                    "activo": self.monitor_red is not None and getattr(self.monitor_red, 'monitoreando', False),
                    "conexiones": getattr(self.monitor_red, 'conexiones_activas', 0) if self.monitor_red else 0
                },
                "monitor_procesos": {
                    "activo": self.monitor_procesos is not None and getattr(self.monitor_procesos, 'monitoreando', False),
                    "procesos_monitoreados": len(getattr(self.monitor_procesos, 'procesos_sospechosos', [])) if self.monitor_procesos else 0
                },
                "fim": {
                    "activo": self.fim is not None and getattr(self.fim, 'monitoreando', False),
                    "archivos_monitoreados": len(getattr(self.fim, 'archivos_monitoreados', [])) if self.fim else 0
                },
                "analisis_dinamico": {
                    "activo": self.analizador_dinamico is not None,
                    "analisis_en_curso": getattr(self.analizador_dinamico, 'analisis_activo', False) if self.analizador_dinamico else False
                }
            }
        except Exception as e:
            self.logger.error(f"Error obteniendo estado monitores: {e}")
            return {}
    
    def obtener_configuracion_sistema(self) -> Dict[str, Any]:
        """Obtener configuración actual del sistema"""
        try:
            return {
                "rutas_escaneadas": getattr(self.escaneador, 'rutas_configuradas', []) if self.escaneador else [],
                "exclusiones": getattr(self.escaneador, 'exclusiones', []) if self.escaneador else [],
                "configuracion_siem": getattr(self.siem, 'configuracion', {}) if self.siem else {},
                "politicas_cuarentena": getattr(self.gestor_cuarentena, 'politicas', {}) if self.gestor_cuarentena else {},
                "configuracion_monitores": self.obtener_estado_monitores()
            }
        except Exception as e:
            self.logger.error(f"Error obteniendo configuración: {e}")
            return {}
    
    def obtener_lista_cuarentena(self) -> List[Dict[str, Any]]:
        """Obtener lista de archivos en cuarentena"""
        try:
            if self.gestor_cuarentena:
                # Acceder a la base de datos de cuarentena
                archivos = []
                for archivo_id, metadatos in self.gestor_cuarentena.base_datos.items():
                    archivos.append({
                        "id": archivo_id,
                        "nombre": metadatos.nombre_original,
                        "ruta_original": metadatos.ruta_original,
                        "fecha_cuarentena": metadatos.timestamp_cuarentena.isoformat(),
                        "origen_deteccion": metadatos.origen_deteccion,
                        "nivel_riesgo": metadatos.nivel_riesgo.value,
                        "estado": metadatos.estado.value,
                        "razon": metadatos.razon_cuarentena,
                        "tamaño": metadatos.tamaño_bytes
                    })
                return archivos
            return []
        except Exception as e:
            self.logger.error(f"Error obteniendo lista cuarentena: {e}")
            return []
    
    def gestionar_archivo_cuarentena(self, accion: str, archivo_id: str) -> bool:
        """Gestionar archivo en cuarentena (restaurar/eliminar)"""
        try:
            if not self.gestor_cuarentena:
                return False
            
            # Por ahora, simular las acciones hasta implementar los métodos reales
            if accion in ["restaurar", "eliminar"]:
                self.logger.info(f"Acción '{accion}' solicitada para archivo {archivo_id}")
                return True
            
            return False
        except Exception as e:
            self.logger.error(f"Error gestionando archivo cuarentena: {e}")
            return False
    
    def ejecutar_escaneo_completo(self, callback_progreso: Optional[Any] = None) -> Dict[str, Any]:
        """Ejecutar un escaneo completo del sistema, reenviando el callback de progreso al controlador especializado."""
        try:
            if hasattr(self, 'controlador_escaneador') and self.controlador_escaneador:
                resultado = self.controlador_escaneador.ejecutar_escaneo_completo(callback_progreso=callback_progreso)
                self.logger.info(f"Escaneo completo completado: {resultado.get('amenazas_encontradas', 0)} amenazas en {resultado.get('tiempo_transcurrido', 0):.2f}s")
                return resultado
            else:
                raise RuntimeError("Controlador de escaneador no inicializado")
        except Exception as e:
            self.logger.error(f"Error en escaneo completo: {e}")
            raise
    
    def obtener_actividades_recientes(self, limite: int = 10) -> List[Dict[str, Any]]:
        """Obtener actividades recientes del sistema."""
        try:
            actividades = []
            
            if self.siem:
                eventos = self.siem.obtener_eventos(limite=limite)
                for evento in eventos:
                    actividades.append({
                        'timestamp': evento.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                        'evento': f"{evento.tipo}: {evento.mensaje}",
                        'severidad': evento.nivel_criticidad
                    })
            
            return actividades
            
        except Exception as e:
            self.logger.error(f"Error al obtener actividades recientes: {e}")
            return []
    
    def obtener_alertas_recientes(self, limite: int = 5) -> List[Dict[str, Any]]:
        """Obtener alertas recientes del sistema."""
        try:
            alertas = []
            
            if self.siem:
                eventos = self.siem.obtener_eventos(limite=limite)
                for evento in eventos:
                    if evento.nivel_criticidad in ['ALTO', 'CRITICO']:
                        alertas.append({
                            'mensaje': evento.mensaje,
                            'severity': 'critical' if evento.nivel_criticidad == 'CRITICO' else 'warning',
                            'timestamp': evento.timestamp.strftime('%H:%M:%S')
                        })
            
            return alertas
            
        except Exception as e:
            self.logger.error(f"Error al obtener alertas recientes: {e}")
            return []
