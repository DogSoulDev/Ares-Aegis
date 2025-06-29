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
from modelos.monitor_red import MonitorRed


class ControladorPrincipal:
    """Controlador principal que coordina todos los módulos del sistema."""
    
    def __init__(self):
        """Inicializa el controlador principal."""
        self.logger = logging.getLogger(__name__)
        
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
            self.monitor_red = MonitorRed(self.siem)
            
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
            
            # Verificar privilegios de root
            if not self._verificar_privilegios():
                raise PermissionError("Se requieren privilegios de root para ejecutar Ares Aegis")
            
            # Crear directorios necesarios
            self._crear_directorios_sistema()
            
            # Inicializar configuraciones
            self._cargar_configuraciones()
            
            self.sistema_iniciado = True
            self.siem.log_evento(TipoEvento.SISTEMA_EVENTO, 'Sistema Ares Aegis iniciado correctamente')
            self.logger.info("Sistema Ares Aegis iniciado correctamente")
            
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
        directorios = [
            "/var/log/ares-aegis",
            "/var/lib/ares-aegis",
            "/var/lib/ares-aegis/cuarentena",
            "/var/lib/ares-aegis/firmas",
            "/var/lib/ares-aegis/baselines"
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
    
    def detener_sistema(self):
        """Detiene el sistema de forma controlada."""
        try:
            self.siem.log_evento(TipoEvento.SISTEMA_EVENTO, 'Deteniendo sistema Ares Aegis')
            self.sistema_iniciado = False
            self.logger.info("Sistema Ares Aegis detenido correctamente")
            
        except Exception as e:
            self.logger.error(f"Error deteniendo sistema: {e}")
