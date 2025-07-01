#!/usr/bin/env python3
"""
Controlador Principal - Ares Aegis
Controlador principal que coordina todos los componentes del sistema

Autor: DogSoulDev
Versión: 2.0.0
"""

import time
import threading
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

# Importar modelos
from ..modelos.siem import SIEM, TipoEvento
from ..modelos.escaneador import Escaneador
from ..modelos.fim import FIM
from ..modelos.monitor_red import MonitorRed
from ..modelos.cuarentena import Cuarentena

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
            self.logger.info("SIEM inicializado")
            
            # 2. Inicializar componentes que dependen del SIEM
            self.escaneador = Escaneador(self.siem)
            self.logger.info("Escaneador inicializado")
            
            self.cuarentena = Cuarentena(self.siem)
            self.logger.info("Sistema de cuarentena inicializado")
            
            self.fim = FIM(self.siem)
            self.logger.info("FIM inicializado")
            
            self.monitor_red = MonitorRed(self.siem)
            self.logger.info("Monitor de red inicializado")
            
            # Registrar inicialización exitosa
            if self.siem:
                self.siem.registrar_evento(
                    TipoEvento.SISTEMA_INICIADO,
                    "Controlador principal inicializado exitosamente",
                    {
                        'componentes_inicializados': [
                            'SIEM', 'Escaneador', 'Cuarentena', 'FIM', 'MonitorRed'
                        ],
                        'timestamp_inicio': datetime.now().isoformat()
                    },
                    "MEDIO"
                )
            
            self.sistema_iniciado = True
            
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
    
    def escaneo_rapido(self) -> Dict[str, Any]:
        """
        Ejecuta un escaneo rápido del sistema.
        
        Returns:
            Dict[str, Any]: Resultados del escaneo
        """
        if not self.escaneador:
            raise RuntimeError("Escaneador no inicializado")
        
        self.logger.info("Iniciando escaneo rápido")
        if self.siem:
            self.siem.registrar_evento(
                TipoEvento.ESCANEO_INICIADO,
                "Escaneo rápido iniciado",
                {'tipo': 'rapido'},
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
        resultado_escaneo = self.escaneador.escanear_multiples_rutas(rutas_existentes)
        tiempo_total = time.time() - inicio_tiempo
        
        # Construir resultado como diccionario
        resultado = {
            'archivos_escaneados': resultado_escaneo.get('archivos_escaneados', 0),
            'amenazas_detectadas': resultado_escaneo.get('amenazas_detectadas', 0),
            'archivos_infectados': resultado_escaneo.get('archivos_infectados', 0),
            'tiempo_escaneo': tiempo_total,
            'tipo_escaneo': 'rapido',
            'rutas_escaneadas': rutas_existentes
        }
        
        if self.siem:
            self.siem.registrar_evento(
                TipoEvento.ESCANEO_FINALIZADO,
                "Escaneo rápido finalizado",
                resultado,
                "MEDIO"
            )
        
        self.logger.info(f"Escaneo rápido completado en {tiempo_total:.2f}s")
        return resultado
    
    def escaneo_completo(self) -> Dict[str, Any]:
        """
        Ejecuta un escaneo completo del sistema.
        
        Returns:
            Dict[str, Any]: Resultados del escaneo
        """
        if not self.escaneador:
            raise RuntimeError("Escaneador no inicializado")
        
        self.logger.info("Iniciando escaneo completo")
        if self.siem:
            self.siem.registrar_evento(
                TipoEvento.ESCANEO_INICIADO,
                "Escaneo completo iniciado",
                {'tipo': 'completo'},
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
        resultado_escaneo = self.escaneador.escanear_multiples_rutas(rutas_existentes)
        tiempo_total = time.time() - inicio_tiempo
        
        # Construir resultado como diccionario
        resultado = {
            'archivos_escaneados': resultado_escaneo.get('archivos_escaneados', 0),
            'amenazas_detectadas': resultado_escaneo.get('amenazas_detectadas', 0),
            'archivos_infectados': resultado_escaneo.get('archivos_infectados', 0),
            'tiempo_escaneo': tiempo_total,
            'tipo_escaneo': 'completo',
            'rutas_escaneadas': rutas_existentes
        }
        
        if self.siem:
            self.siem.registrar_evento(
                TipoEvento.ESCANEO_FINALIZADO,
                "Escaneo completo finalizado",
                resultado,
                "MEDIO"
            )
        
        self.logger.info(f"Escaneo completo completado en {tiempo_total:.2f}s")
        return resultado
    
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
