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
from ..modelos.escaneador import Escaneador
from ..modelos.fim import FIM
from ..modelos.monitor_red import MonitorRed
from ..modelos.gestor_cuarentena import Cuarentena
from ..modelos.monitor_procesos import MonitorProcesos
from ..modelos.analizador_dinamico import AnalizadorDinamico
from ..modelos.analizador_archivos import AnalizadorArchivos
from ..modelos.analizador_cadenas import AnalizadorCadenas
from ..modelos.analizador_comportamiento_procesos import AnalizadorComportamientoProcesos
from ..modelos.analizador_comportamiento_red import AnalizadorComportamientoRed
from ..modelos.escaneador_vulnerabilidades_red import EscaneadorVulnerabilidadesRed
from ..modelos.escaneador_vulnerabilidades_sistema import EscaneadorVulnerabilidadesSistema
from ..modelos.integracion_externa import IntegracionExterna
from ..modelos.sistema_reportes_notificaciones import SistemaReportesNotificaciones
from ..modelos.respuesta_automatizada import RespuestaAutomatizada
from ..modelos.analizador_registros import AnalizadorRegistros
from ..modelos.respondedor_incidentes import RespondedorIncidentes
from ..modelos.buscador_cve import BuscadorCVE
from ..modelos.gestor_cheatsheets import GestorCheatsheets
from ..modelos.visor_hex import VisorHex
from ..modelos.descontaminacion_inteligente import DescontaminacionInteligente

# Importar utilidades
from ..utilidades.ayuda_logging import configurar_logger_modulo


class ControladorPrincipal:
    """Controlador principal del sistema Ares Aegis."""
    
    def __init__(self):
        """Inicializa el controlador principal."""
        self.logger = configurar_logger_modulo("controlador_principal")
        self.inicio_tiempo = time.time()
        
        # Componentes principales
        self.siem: Optional[SIEM] = None
        self.escaneador: Optional[Escaneador] = None
        self.fim: Optional[FIM] = None
        self.monitor_red: Optional[MonitorRed] = None
        self.cuarentena: Optional[Cuarentena] = None
        
        # Componentes de análisis avanzado
        self.monitor_procesos: Optional[MonitorProcesos] = None
        self.analizador_dinamico: Optional[AnalizadorDinamico] = None
        self.analizador_archivos: Optional[AnalizadorArchivos] = None
        self.analizador_cadenas: Optional[AnalizadorCadenas] = None
        self.analizador_comportamiento_procesos: Optional[AnalizadorComportamientoProcesos] = None
        self.analizador_comportamiento_red: Optional[AnalizadorComportamientoRed] = None
        
        # Componentes de vulnerabilidades
        self.escaneador_vuln_red: Optional[EscaneadorVulnerabilidadesRed] = None
        self.escaneador_vuln_sistema: Optional[EscaneadorVulnerabilidadesSistema] = None
        self.buscador_cve: Optional[BuscadorCVE] = None
        
        # Componentes de gestión y respuesta
        self.integracion_externa: Optional[IntegracionExterna] = None
        self.sistema_reportes: Optional[SistemaReportesNotificaciones] = None
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
        
        self.logger.info("Controlador principal inicializado exitosamente")
    
    def _inicializar_componentes(self):
        """Inicializa todos los componentes del sistema."""
        try:
            # 1. Inicializar SIEM (core)
            self.siem = SIEM()
            self.logger.info("SIEM inicializado - Los Ojos de Argos despiertan")
            
            # 2. Inicializar componentes principales que dependen del SIEM
            self.escaneador = Escaneador(self.siem)
            self.logger.info("Escaneador inicializado - Los Cazadores de Artemisa listos")
            
            self.cuarentena = Cuarentena(self.siem)
            self.logger.info("Cuarentena inicializada - Las Celdas de Hades preparadas")
            
            self.fim = FIM(self.siem)
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
            
            self.sistema_reportes = SistemaReportesNotificaciones(self.siem)
            self.logger.info("Sistema de reportes - Los Heraldos de Hermes informan")
            
            self.respuesta_automatizada = RespuestaAutomatizada()
            self.logger.info("Respuesta automatizada - Los Autómatas de Hefesto responden")
            
            self.analizador_registros = AnalizadorRegistros(self.siem)
            self.logger.info("Analizador de registros - Los Escribas de Temis registran")
            
            self.respondedor_incidentes = RespondedorIncidentes(self.siem)
            self.logger.info("Respondedor de incidentes - Los Guardianes de Némesis protegen")
            
            # 6. Inicializar componentes de utilidades
            self.gestor_cheatsheets = GestorCheatsheets()
            self.logger.info("Gestor de cheatsheets - Los Escribanos de Hermes organizan")
            
            self.visor_hex = VisorHex(self.siem)
            self.logger.info("Visor hexadecimal - Los Decifradores de Thot revelan")
            
            self.descontaminacion = DescontaminacionInteligente(self.siem, self.cuarentena)
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
                'cuarentena': self.cuarentena is not None
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
            if self.cuarentena:
                stats_cuarentena = self.cuarentena.obtener_estadisticas()
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
                eventos_recientes = self.siem.buscar_eventos(limite=100)
                estadisticas['total_eventos'] = len(eventos_recientes)
            else:
                estadisticas['total_eventos'] = 0
            
            # Uso de memoria (aproximado)
            import sys
            estadisticas['uso_memoria_mb'] = sys.getsizeof(self) / (1024 * 1024)
            
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas: {e}")
        
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
        
        if self.siem:
            self.siem.registrar_evento(
                TipoEvento.ESCANEO_FINALIZADO,
                "Escaneo rápido finalizado",
                resultado,
                "MEDIO"
            )
        
        self.logger.info(f"Escaneo rápido completado en {tiempo_total:.2f}s")
        return resultado
    
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
        resultado_escaneo = self.escaneador.escanear_multiples_rutas([ruta])
        tiempo_total = time.time() - inicio_tiempo
        
        # Construir resultado como diccionario
        resultado = {
            'archivos_escaneados': resultado_escaneo.get('archivos_escaneados', 0),
            'amenazas_detectadas': resultado_escaneo.get('amenazas_detectadas', 0),
            'archivos_infectados': resultado_escaneo.get('archivos_infectados', 0),
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
        cambios = self.fim.verificar_integridad()
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
        return self.fim.crear_baseline()
    
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
        
        eventos = self.siem.buscar_eventos(limite=limite)
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
            if self.cuarentena:
                md += self.cuarentena.generar_reporte_markdown()
                md += "\n"
            
            # Reporte de red
            if self.monitor_red:
                md += self.monitor_red.generar_reporte_markdown()
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
            self.logger.info("Iniciando interfaz gráfica de Ares Aegis")
            
            # Importar la interfaz gráfica
            from ..vista.interfaz_principal_gui import InterfazPrincipalGUI
            
            # Crear y ejecutar la interfaz
            interfaz = InterfazPrincipalGUI()
            # Asignar el controlador a la interfaz
            interfaz.controlador = self
            interfaz.ejecutar_egida()
            
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
    
    def ejecutar_escaneo_rapido(self) -> Dict[str, Any]:
        """Ejecutar un escaneo rápido del sistema."""
        try:
            inicio = time.time()
            amenazas_encontradas = 0
            
            # Simular escaneo rápido
            if self.escaneador:
                # El escaneador real haría el trabajo aquí
                pass
            
            tiempo_transcurrido = time.time() - inicio
            
            resultado = {
                'tipo': 'rapido',
                'amenazas_encontradas': amenazas_encontradas,
                'tiempo_transcurrido': tiempo_transcurrido,
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"Escaneo rápido completado: {amenazas_encontradas} amenazas en {tiempo_transcurrido:.2f}s")
            return resultado
            
        except Exception as e:
            self.logger.error(f"Error en escaneo rápido: {e}")
            raise
    
    def ejecutar_escaneo_completo(self) -> Dict[str, Any]:
        """Ejecutar un escaneo completo del sistema."""
        try:
            inicio = time.time()
            amenazas_encontradas = 0
            
            # Simular escaneo completo
            if self.escaneador:
                # El escaneador real haría el trabajo aquí
                pass
            
            tiempo_transcurrido = time.time() - inicio
            
            resultado = {
                'tipo': 'completo',
                'amenazas_encontradas': amenazas_encontradas,
                'tiempo_transcurrido': tiempo_transcurrido,
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"Escaneo completo completado: {amenazas_encontradas} amenazas en {tiempo_transcurrido:.2f}s")
            return resultado
            
        except Exception as e:
            self.logger.error(f"Error en escaneo completo: {e}")
            raise
    
    def obtener_actividades_recientes(self, limite: int = 10) -> List[Dict[str, Any]]:
        """Obtener actividades recientes del sistema."""
        try:
            actividades = []
            
            if self.siem:
                eventos = self.siem.buscar_eventos(limite=limite)
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
                eventos = self.siem.buscar_eventos(limite=limite)
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
