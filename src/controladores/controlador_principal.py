#!/usr/bin/env python3
"""
Controlador Principal - Ares Aegis
Controlador principal que coordina todos los módulos del sistema

Autor: DogSoulDev
Versión: 2.0.0
"""

import os
import logging
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

# Añadir el directorio padre al path para importaciones
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Importar modelos
from modelos.siem import SIEM, TipoEvento
from modelos.escaneador import Escaneador, ResultadoEscaneo
from modelos.cuarentena import GestorCuarentena
from modelos.monitor_integridad import MonitorIntegridad

# Importar modelos opcionales
try:
    from modelos.monitor_red import MonitorRed
    MONITOR_RED_DISPONIBLE = True
except ImportError:
    MonitorRed = None
    MONITOR_RED_DISPONIBLE = False


class ControladorPrincipal:
    """Controlador principal que coordina todos los módulos del sistema."""
    
    def __init__(self):
        """Inicializa el controlador principal."""
        self.logger = logging.getLogger(__name__)
        
        # Modo de privilegios ('root' o 'limitado')
        self.modo_privilegios = 'limitado'  # Por defecto modo limitado
        
        # Inicializar SIEM como núcleo central
        self.siem = SIEM()
        
        # Inicializar módulos principales
        self._inicializar_modulos()
        
        # Estado del sistema
        self.sistema_iniciado = False
        
        self.siem.log_evento(TipoEvento.SISTEMA_EVENTO, 'Controlador principal inicializado')
    
    def _inicializar_modulos(self):
        """Inicializa todos los módulos del sistema."""
        try:
            # Módulos de seguridad
            self.escaneador = Escaneador(self.siem)
            self.gestor_cuarentena = GestorCuarentena(None, self.siem)  # directorio por defecto
            self.monitor_integridad = MonitorIntegridad(None, self.siem)  # directorio por defecto
            
            # Inicializar monitor de red si está disponible
            if MONITOR_RED_DISPONIBLE and MonitorRed is not None:
                self.monitor_red = MonitorRed(self.siem)
            else:
                self.monitor_red = None
            
            self.logger.info("Todos los módulos inicializados correctamente")
            self.siem.log_evento(TipoEvento.SISTEMA_EVENTO, 'Módulos inicializados correctamente')
            
        except Exception as e:
            self.logger.error(f"Error inicializando módulos: {e}")
            self.siem.log_evento(TipoEvento.ERROR, f'Error inicializando módulos: {e}')
            raise
    
    def iniciar_sistema(self) -> bool:
        """Inicia el sistema completo."""
        try:
            if self.sistema_iniciado:
                self.logger.warning("El sistema ya está iniciado")
                return True
            
            # Verificar privilegios según el modo
            if self.modo_privilegios == 'root':
                if not self._verificar_privilegios():
                    self.logger.warning("Se esperaban privilegios de root pero no se detectaron")
                else:
                    self.logger.info("Privilegios de root confirmados")
            else:
                self.logger.info("Iniciando en modo limitado")
            
            # Crear directorios necesarios (solo si tenemos permisos)
            self._crear_directorios_sistema()
            
            # Inicializar configuraciones
            self._cargar_configuraciones()
            
            self.sistema_iniciado = True
            
            if self.modo_privilegios == 'root':
                mensaje = 'Sistema Ares Aegis iniciado con privilegios completos'
            else:
                mensaje = 'Sistema Ares Aegis iniciado en modo limitado'
                
            self.siem.log_evento(TipoEvento.SISTEMA_EVENTO, mensaje)
            self.logger.info(mensaje)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error iniciando sistema: {e}")
            self.siem.log_evento(TipoEvento.ERROR, f'Error iniciando sistema: {e}')
            return False
    
    def _verificar_privilegios(self) -> bool:
        """Verifica si se están ejecutando con privilegios de root."""
        return os.geteuid() == 0
    
    def _crear_directorios_sistema(self):
        """Crea los directorios necesarios para el funcionamiento del sistema."""
        if self.modo_privilegios == 'root':
            # Directorios del sistema con privilegios completos
            directorios = [
                "/var/log/ares-aegis",
                "/var/lib/ares-aegis",
                "/var/lib/ares-aegis/cuarentena",
                "/var/lib/ares-aegis/firmas",
                "/var/lib/ares-aegis/baselines"
            ]
        else:
            # Directorios en modo limitado (directorio del usuario)
            base_dir = Path.home() / ".ares_aegis"
            directorios = [
                str(base_dir),
                str(base_dir / "logs"),
                str(base_dir / "cuarentena"),
                str(base_dir / "firmas"),
                str(base_dir / "baselines")
            ]
        
        for directorio in directorios:
            try:
                Path(directorio).mkdir(parents=True, exist_ok=True)
                self.logger.debug(f"Directorio creado/verificado: {directorio}")
            except Exception as e:
                self.logger.warning(f"No se pudo crear directorio {directorio}: {e}")
    
    def _cargar_configuraciones(self):
        """Carga las configuraciones del sistema."""
        try:
            # Cargar configuraciones de cada módulo
            # Por ahora usamos configuraciones por defecto
            self.logger.info("Configuraciones cargadas correctamente")
            
        except Exception as e:
            self.logger.warning(f"Error cargando configuraciones: {e}")
    
    # === MÉTODOS DE ESCANEO ===
    
    def escanear_archivo(self, ruta_archivo: str) -> ResultadoEscaneo:
        """Escanea un archivo individual."""
        try:
            self.siem.log_evento(TipoEvento.ESCANEO, f'Iniciando escaneo de archivo: {ruta_archivo}')
            resultado = self.escaneador.escanear_archivo(ruta_archivo)
            
            # Si se detectan amenazas, enviar a cuarentena
            if not resultado.es_limpio():
                self.logger.warning(f"Amenazas detectadas en {ruta_archivo}")
                try:
                    self.gestor_cuarentena.poner_en_cuarentena(ruta_archivo, f"Amenazas: {', '.join(resultado.amenazas)}")
                except Exception as e:
                    self.logger.error(f"Error enviando archivo a cuarentena: {e}")
            
            return resultado
            
        except Exception as e:
            self.logger.error(f"Error escaneando archivo {ruta_archivo}: {e}")
            self.siem.log_evento(TipoEvento.ERROR, f'Error escaneando archivo {ruta_archivo}: {e}')
            raise
    
    def escanear_directorio(self, ruta_directorio: str) -> Dict[str, Any]:
        """Escanea un directorio completo."""
        try:
            self.siem.log_evento(TipoEvento.SISTEMA_EVENTO, f'Iniciando escaneo de directorio: {ruta_directorio}')
            resultados_lista = self.escaneador.escanear_directorio(ruta_directorio)
            resultados = self.escaneador.generar_reporte_directorio(resultados_lista)
            
            # Procesar archivos infectados
            archivos_infectados = resultados.get('archivos_infectados', [])
            for archivo_infectado in archivos_infectados:
                try:
                    ruta_archivo = archivo_infectado['ruta']
                    amenazas = archivo_infectado['amenazas']
                    self.gestor_cuarentena.poner_en_cuarentena(ruta_archivo, f"Amenazas: {', '.join(amenazas)}")
                except Exception as e:
                    self.logger.error(f"Error enviando archivo infectado a cuarentena: {e}")
            
            return resultados
            
        except Exception as e:
            self.logger.error(f"Error escaneando directorio {ruta_directorio}: {e}")
            self.siem.log_evento(TipoEvento.ERROR, f'Error escaneando directorio {ruta_directorio}: {e}')
            raise
    
    # === MÉTODOS DE MONITOREO ===
    
    def crear_baseline_integridad(self, directorios: List[str]) -> Dict[str, Any]:
        """Crea una línea base de integridad para los directorios especificados."""
        try:
            self.siem.log_evento(TipoEvento.SISTEMA_EVENTO, f'Creando baseline para: {", ".join(directorios)}')
            # Agregar directorios al monitoreo
            for directorio in directorios:
                self.monitor_integridad.agregar_ruta_monitoreo(directorio)
            # Inicializar base de datos
            archivos_procesados = self.monitor_integridad.inicializar_base_datos()
            estadisticas = {
                'archivos_procesados': archivos_procesados,
                'directorios_monitoreados': len(directorios),
                'errores': 0
            }
            return estadisticas
            
        except Exception as e:
            self.logger.error(f"Error creando baseline de integridad: {e}")
            self.siem.log_evento(TipoEvento.ERROR, f'Error creando baseline: {e}')
            raise
    
    def verificar_integridad(self) -> List[Dict[str, Any]]:
        """Verifica la integridad de archivos monitoreados."""
        try:
            self.siem.log_evento(TipoEvento.INTEGRIDAD_ARCHIVO, 'Verificando integridad de archivos')
            cambios = self.monitor_integridad.verificar_integridad()
            
            if cambios:
                self.logger.warning(f"Se detectaron {len(cambios)} cambios en la integridad")
                for cambio in cambios:
                    self.siem.log_evento(TipoEvento.INTEGRIDAD_ARCHIVO, 
                                             f'Cambio detectado: {cambio["ruta"]} - {cambio.get("tipo_cambio", "modificado")}')
            
            return cambios
            
        except Exception as e:
            self.logger.error(f"Error verificando integridad: {e}")
            self.siem.log_evento(TipoEvento.ERROR, f'Error verificando integridad: {e}')
            raise
    
    def monitorear_red(self) -> Dict[str, Any]:
        """Ejecuta monitoreo de red y detecta conexiones sospechosas."""
        try:
            self.siem.log_evento(TipoEvento.RED_ACTIVIDAD, 'Iniciando monitoreo de red')
            
            if self.monitor_red is None:
                self.logger.warning("Monitor de red no disponible")
                return {
                    'error': 'Monitor de red no disponible',
                    'estadisticas': {'total_conexiones': 0},
                    'conexiones_sospechosas': [],
                    'puertos_sospechosos': [],
                    'total_conexiones': 0
                }
            
            # Obtener conexiones activas
            conexiones = self.monitor_red.obtener_conexiones_activas()
            
            # Detectar conexiones sospechosas
            conexiones_sospechosas = self.monitor_red.detectar_conexiones_sospechosas()
            puertos_sospechosos = self.monitor_red.detectar_puertos_en_escucha_sospechosos()
            
            # Obtener estadísticas
            estadisticas = self.monitor_red.obtener_estadisticas_red()
            
            resultado = {
                'estadisticas': estadisticas,
                'conexiones_sospechosas': [c.a_dict() for c in conexiones_sospechosas],
                'puertos_sospechosos': [p.a_dict() for p in puertos_sospechosos],
                'total_conexiones': len(conexiones)
            }
            
            if conexiones_sospechosas or puertos_sospechosos:
                self.logger.warning(f"Red: {len(conexiones_sospechosas)} conexiones sospechosas, {len(puertos_sospechosos)} puertos sospechosos")
            
            return resultado
            
        except Exception as e:
            self.logger.error(f"Error en monitoreo de red: {e}")
            self.siem.log_evento(TipoEvento.ERROR, f'Error en monitoreo de red: {e}')
            raise
    
    # === MÉTODOS DE CUARENTENA ===
    
    def listar_cuarentena(self) -> List[Dict[str, Any]]:
        """Lista todos los archivos en cuarentena."""
        try:
            archivos = self.gestor_cuarentena.listar_archivos()
            return [archivo.a_dict() for archivo in archivos]
            
        except Exception as e:
            self.logger.error(f"Error listando cuarentena: {e}")
            self.siem.log_evento(TipoEvento.ERROR, f'Error listando cuarentena: {e}')
            raise
    
    def restaurar_archivo_cuarentena(self, id_archivo: str) -> bool:
        """Restaura un archivo de la cuarentena."""
        try:
            exito = self.gestor_cuarentena.restaurar_archivo(id_archivo)
            if exito:
                self.siem.log_evento(TipoEvento.ARCHIVO_CUARENTENA, f'Archivo restaurado de cuarentena: {id_archivo}')
            return exito
            
        except Exception as e:
            self.logger.error(f"Error restaurando archivo {id_archivo}: {e}")
            self.siem.log_evento(TipoEvento.ERROR, f'Error restaurando archivo {id_archivo}: {e}')
            raise
    
    def eliminar_archivo_cuarentena(self, id_archivo: str) -> bool:
        """Elimina permanentemente un archivo de la cuarentena."""
        try:
            exito = self.gestor_cuarentena.eliminar_definitivamente(id_archivo)
            if exito:
                self.siem.log_evento(TipoEvento.ARCHIVO_CUARENTENA, f'Archivo eliminado de cuarentena: {id_archivo}')
            return exito
            
        except Exception as e:
            self.logger.error(f"Error eliminando archivo {id_archivo}: {e}")
            self.siem.log_evento(TipoEvento.ERROR, f'Error eliminando archivo {id_archivo}: {e}')
            raise
    
    def limpiar_cuarentena_antigua(self, dias: int) -> int:
        """Limpia archivos antiguos de la cuarentena."""
        try:
            eliminados = self.gestor_cuarentena.limpiar_cuarentena_antigua(dias)
            self.siem.log_evento(TipoEvento.ARCHIVO_CUARENTENA, f'Limpieza de cuarentena: {eliminados} archivos eliminados')
            return eliminados
            
        except Exception as e:
            self.logger.error(f"Error limpiando cuarentena: {e}")
            self.siem.log_evento(TipoEvento.ERROR, f'Error limpiando cuarentena: {e}')
            raise
    
    # === MÉTODOS DE REPORTE ===
    
    def generar_reporte_sistema(self) -> str:
        """Genera un reporte completo del estado del sistema."""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            reporte = f"# Reporte del Sistema Ares Aegis\n\n"
            reporte += f"**Fecha de generación:** {timestamp}\n\n"
            
            # Estado del sistema
            reporte += "## Estado del Sistema\n\n"
            reporte += f"- **Sistema iniciado:** {'Sí' if self.sistema_iniciado else 'No'}\n"
            reporte += f"- **Privilegios de root:** {'Sí' if self._verificar_privilegios() else 'No'}\n\n"
            
            # Estadísticas de cuarentena
            try:
                archivos_cuarentena = self.listar_cuarentena()
                reporte += f"- **Archivos en cuarentena:** {len(archivos_cuarentena)}\n\n"
            except:
                reporte += "- **Archivos en cuarentena:** Error obteniendo datos\n\n"
            
            # Estadísticas de red
            try:
                datos_red = self.monitorear_red()
                reporte += "## Estado de Red\n\n"
                for clave, valor in datos_red['estadisticas'].items():
                    reporte += f"- **{clave.replace('_', ' ').title()}:** {valor}\n"
                reporte += "\n"
            except:
                reporte += "## Estado de Red\n\n- Error obteniendo datos de red\n\n"
            
            # Eventos recientes del SIEM
            try:
                eventos_recientes = self.siem.obtener_eventos(limite=10)
                reporte += "## Eventos Recientes del SIEM\n\n"
                for evento in eventos_recientes:
                    reporte += f"- **{evento.timestamp}** [{evento.tipo}] {evento.mensaje}\n"
                reporte += "\n"
            except:
                reporte += "## Eventos Recientes del SIEM\n\n- Error obteniendo eventos\n\n"
            
            return reporte
            
        except Exception as e:
            self.logger.error(f"Error generando reporte del sistema: {e}")
            raise
    
    def obtener_eventos_siem(self, limite: int = 100) -> str:
        """Obtiene eventos del SIEM en formato Markdown."""
        try:
            return self.siem.obtener_eventos_markdown(limite=limite)
        except Exception as e:
            self.logger.error(f"Error obteniendo eventos SIEM: {e}")
            raise
    
    # === MÉTODOS DE CONFIGURACIÓN Y ESTADO ===
    
    def obtener_funciones_disponibles(self) -> Dict[str, bool]:
        """
        Retorna un diccionario con las funciones disponibles según el modo de privilegios.
        
        Returns:
            Dict[str, bool]: Diccionario con funciones y su disponibilidad
        """
        if self.modo_privilegios == 'root':
            return {
                'escaneo_sistema_completo': True,
                'monitoreo_procesos_criticos': True,
                'analisis_logs_sistema': True,
                'acceso_directorios_protegidos': True,
                'cuarentena_sistema': True,
                'monitoreo_red_completo': True,
                'integridad_archivos_sistema': True,
                'actualizacion_firmas': True,
                'gestion_servicios': True,
                'analisis_memoria': True
            }
        else:
            return {
                'escaneo_sistema_completo': False,
                'monitoreo_procesos_criticos': False,
                'analisis_logs_sistema': False,
                'acceso_directorios_protegidos': False,
                'cuarentena_sistema': False,
                'monitoreo_red_completo': False,
                'integridad_archivos_sistema': False,
                'actualizacion_firmas': False,
                'gestion_servicios': False,
                'analisis_memoria': False,
                'escaneo_directorio_usuario': True,
                'cuarentena_local': True,
                'monitoreo_red_basico': True,
                'integridad_archivos_usuario': True
            }
    
    def obtener_modo_privilegios(self) -> str:
        """
        Retorna el modo de privilegios actual.
        
        Returns:
            str: 'root' o 'limitado'
        """
        return self.modo_privilegios
    
    def es_modo_root(self) -> bool:
        """
        Verifica si está ejecutándose en modo root.
        
        Returns:
            bool: True si es modo root, False si es limitado
        """
        return self.modo_privilegios == 'root'
    
    def detener_sistema(self):
        """Detiene el sistema de forma controlada."""
        try:
            self.siem.log_evento(TipoEvento.SISTEMA_EVENTO, 'Deteniendo sistema Ares Aegis')
            self.sistema_iniciado = False
            self.logger.info("Sistema Ares Aegis detenido correctamente")
            
        except Exception as e:
            self.logger.error(f"Error deteniendo sistema: {e}")
