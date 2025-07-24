#!/usr/bin/env python3
"""
Controlador Constructor de Wordlists para Ares Aegis
Coordinación entre vista y modelo para la generación de wordlists

Creado por DogSoulDev para Ares Aegis
Controlador siguiendo patrón MVC de Ares Aegis.
"""

import threading
import os
from typing import Dict, List, Optional, Any, Callable
from ..modelos.constructor_wordlists import ConstructorWordlists
from ..utils.ayuda_logging import configurar_logger_modulo
from .controlador_base import ControladorBase


class ControladorConstructorWordlists(ControladorBase):
    """
    Controlador para el Constructor de Wordlists.
    
    Maneja la coordinación entre la vista y el modelo,
    así como operaciones asíncronas.
    """
    
    def __init__(self):
        """Inicializa el controlador."""
        super().__init__("constructor_wordlists")
        self.logger = configurar_logger_modulo("controlador_constructor_wordlists")
        
        # Modelo
        self.constructor = ConstructorWordlists()
        
        # Estado del controlador
        self.procesando = False
        self.hilo_procesamiento = None
        self.callback_progreso = None
        self.callback_completado = None
        
        # Datos de la sesión actual
        self.palabras_generadas = []
        self.configuracion_actual = {}
        
        self.logger.info("🎛️ Controlador Constructor de Wordlists inicializado")
    
    async def _inicializar_impl(self) -> bool:
        """Implementación específica de inicialización."""
        try:
            # El constructor de wordlists ya se inicializa en __init__
            self.logger.info("Constructor de wordlists inicializado correctamente")
            return True
        except Exception as e:
            self.logger.error(f"Error inicializando constructor de wordlists: {e}")
            return False
    
    async def _finalizar_impl(self) -> bool:
        """Implementación específica de finalización."""
        try:
            if self.hilo_procesamiento and self.hilo_procesamiento.is_alive():
                self.logger.info("Deteniendo hilo de procesamiento...")
                # Marcar como no procesando para detener bucles
                self.procesando = False
                self.hilo_procesamiento.join(timeout=2)
            
            self.logger.info("🔧 Recursos del constructor de wordlists liberados")
            return True
            
        except Exception as e:
            self.logger.error(f"Error finalizando controlador: {e}")
            return False
    
    # === GESTIÓN DE LISTAS BASE ===
    
    async def _inicializar_impl(self) -> bool:
        """Implementación específica de inicialización."""
        try:
            # No hay inicialización asíncrona específica requerida
            self.logger.info("✅ Controlador Constructor de Wordlists inicializado correctamente")
            return True
        except Exception as e:
            self.logger.error(f"Error inicializando controlador: {e}")
            return False
    
    async def _finalizar_impl(self) -> bool:
        """Implementación específica de finalización."""
        try:
            if self.hilo_procesamiento and self.hilo_procesamiento.is_alive():
                self.logger.info("Deteniendo hilo de procesamiento...")
                # Marcar como no procesando para detener bucles
                self.procesando = False
                self.hilo_procesamiento.join(timeout=2)
            
            self.logger.info("🔧 Recursos del constructor de wordlists liberados")
            return True
            
        except Exception as e:
            self.logger.error(f"Error finalizando controlador: {e}")
            return False
    
    # === GESTIÓN DE LISTAS BASE ===
    
    def obtener_listas_base(self) -> Dict[str, List[str]]:
        """Obtiene todas las listas base."""
        try:
            return self.constructor.obtener_listas_base()
        except Exception as e:
            self.logger.error(f"Error obteniendo listas base: {e}")
            return {}
    
    def obtener_nombres_listas_base(self) -> List[str]:
        """Obtiene los nombres de las listas base."""
        try:
            return self.constructor.obtener_nombres_listas_base()
        except Exception as e:
            self.logger.error(f"Error obteniendo nombres de listas: {e}")
            return []
    
    def crear_lista_base(self, nombre: str, palabras: List[str]) -> Dict[str, Any]:
        """
        Crea una nueva lista base.
        
        Args:
            nombre (str): Nombre de la lista
            palabras (List[str]): Lista de palabras
            
        Returns:
            Dict[str, Any]: Resultado de la operación
        """
        try:
            if not nombre.strip():
                return {'exito': False, 'mensaje': 'El nombre no puede estar vacío'}
            
            if not palabras:
                return {'exito': False, 'mensaje': 'Debe proporcionar al menos una palabra'}
            
            exito = self.constructor.crear_lista_base(nombre, palabras)
            
            if exito:
                self.logger.info(f"Lista base '{nombre}' creada exitosamente")
                return {
                    'exito': True,
                    'mensaje': f'Lista "{nombre}" creada con {len(set(palabras))} palabras únicas'
                }
            else:
                return {'exito': False, 'mensaje': 'Error interno al crear la lista'}
                
        except Exception as e:
            error_msg = f"Error creando lista base: {e}"
            self.logger.error(error_msg)
            return {'exito': False, 'mensaje': error_msg}
    
    def obtener_listas_disponibles(self) -> List[str]:
        """Obtiene la lista de nombres de wordlists disponibles."""
        try:
            return self.constructor.obtener_nombres_listas_base()
        except Exception as e:
            self.logger.error(f"Error obteniendo listas disponibles: {e}")
            return []
    
    def obtener_info_listas(self) -> Dict[str, Dict[str, Any]]:
        """Obtiene información detallada de todas las listas base."""
        try:
            listas_base = self.constructor.obtener_listas_base()
            info = {}
            
            for nombre, palabras in listas_base.items():
                info[nombre] = {
                    'palabras': len(palabras),
                    'tamaño': f"{len(palabras)} palabras"
                }
            
            return info
        except Exception as e:
            self.logger.error(f"Error obteniendo info de listas: {e}")
            return {}
    
    def agregar_lista_base(self, nombre: str, archivo_ruta: str) -> Dict[str, Any]:
        """
        Agrega una nueva lista base desde un archivo.
        
        Args:
            nombre (str): Nombre de la lista
            archivo_ruta (str): Ruta del archivo
            
        Returns:
            Dict[str, Any]: Resultado de la operación
        """
        try:
            if not nombre.strip():
                return {'exito': False, 'mensaje': 'El nombre no puede estar vacío'}
            
            if not os.path.exists(archivo_ruta):
                return {'exito': False, 'mensaje': 'El archivo no existe'}
            
            # Leer el archivo
            palabras = []
            with open(archivo_ruta, 'r', encoding='utf-8', errors='ignore') as f:
                for linea in f:
                    palabra = linea.strip()
                    if palabra and not palabra.startswith('#'):
                        palabras.append(palabra)
            
            if not palabras:
                return {'exito': False, 'mensaje': 'El archivo no contiene palabras válidas'}
            
            # Crear la lista
            exito = self.constructor.crear_lista_base(nombre, palabras)
            
            if exito:
                return {
                    'exito': True,
                    'mensaje': f'Lista "{nombre}" agregada con {len(palabras)} palabras'
                }
            else:
                return {'exito': False, 'mensaje': 'Error interno al agregar la lista'}
                
        except Exception as e:
            error_msg = f"Error agregando lista desde archivo: {e}"
            self.logger.error(error_msg)
            return {'exito': False, 'mensaje': error_msg}
    
    def eliminar_lista_base(self, nombre: str) -> Dict[str, Any]:
        """
        Elimina una lista base.
        
        Args:
            nombre (str): Nombre de la lista a eliminar
            
        Returns:
            Dict[str, Any]: Resultado de la operación
        """
        try:
            if nombre not in self.constructor.listas_base:
                return {'exito': False, 'mensaje': 'La lista no existe'}
            
            del self.constructor.listas_base[nombre]
            
            # Guardar cambios
            exito = self.constructor._guardar_json(
                self.constructor.listas_base, 
                self.constructor.archivo_listas_base
            )
            
            if exito:
                self.logger.info(f"Lista base '{nombre}' eliminada")
                return {'exito': True, 'mensaje': f'Lista "{nombre}" eliminada exitosamente'}
            else:
                return {'exito': False, 'mensaje': 'Error guardando cambios'}
                
        except Exception as e:
            error_msg = f"Error eliminando lista base: {e}"
            self.logger.error(error_msg)
            return {'exito': False, 'mensaje': error_msg}
    
    def eliminar_lista_base(self, nombre: str) -> Dict[str, Any]:
        """Elimina una lista base."""
        try:
            exito = self.constructor.eliminar_lista_base(nombre)
            
            if exito:
                return {'exito': True, 'mensaje': f'Lista "{nombre}" eliminada'}
            else:
                return {'exito': False, 'mensaje': 'Lista no encontrada o error al eliminar'}
                
        except Exception as e:
            error_msg = f"Error eliminando lista base: {e}"
            self.logger.error(error_msg)
            return {'exito': False, 'mensaje': error_msg}
    
    def actualizar_lista_base(self, nombre: str, nuevas_palabras: List[str]) -> Dict[str, Any]:
        """Actualiza una lista base existente."""
        try:
            exito = self.constructor.actualizar_lista_base(nombre, nuevas_palabras)
            
            if exito:
                return {
                    'exito': True,
                    'mensaje': f'Lista "{nombre}" actualizada con {len(set(nuevas_palabras))} palabras'
                }
            else:
                return {'exito': False, 'mensaje': 'Lista no encontrada o error al actualizar'}
                
        except Exception as e:
            error_msg = f"Error actualizando lista base: {e}"
            self.logger.error(error_msg)
            return {'exito': False, 'mensaje': error_msg}
    
    # === GENERACIÓN DE WORDLISTS ===
    
    def generar_wordlist_asincrono(
        self,
        configuracion: Dict[str, Any],
        callback_progreso: Optional[Callable] = None,
        callback_completado: Optional[Callable] = None
    ) -> bool:
        """
        Genera una wordlist de forma asíncrona.
        
        Args:
            configuracion (Dict[str, Any]): Configuración de la generación
            callback_progreso (Callable): Callback para reportar progreso
            callback_completado (Callable): Callback cuando se complete
            
        Returns:
            bool: True si se inició la generación
        """
        try:
            if self.procesando:
                self.logger.warning("Ya hay una generación en progreso")
                return False
            
            self.procesando = True
            self.configuracion_actual = configuracion
            self.callback_progreso = callback_progreso
            self.callback_completado = callback_completado
            
            # Iniciar hilo de procesamiento
            self.hilo_procesamiento = threading.Thread(
                target=self._procesar_generacion,
                daemon=True
            )
            self.hilo_procesamiento.start()
            
            self.logger.info("Generación asíncrona iniciada")
            return True
            
        except Exception as e:
            self.procesando = False
            error_msg = f"Error iniciando generación: {e}"
            self.logger.error(error_msg)
            if callback_completado:
                callback_completado({'exito': False, 'mensaje': error_msg})
            return False
    
    def _procesar_generacion(self):
        """Procesa la generación en un hilo separado."""
        try:
            config = self.configuracion_actual
            
            # Reportar inicio
            if self.callback_progreso:
                self.callback_progreso("Iniciando generación...", 0)
            
            # Paso 1: Obtener palabras base
            if self.callback_progreso:
                self.callback_progreso("Obteniendo palabras base...", 10)
            
            palabras_base = []
            listas_seleccionadas = config.get('listas_seleccionadas', [])
            
            for nombre_lista in listas_seleccionadas:
                if not self.procesando:  # Verificar si se debe cancelar
                    return
                
                if nombre_lista in self.constructor.listas_base:
                    palabras_base.extend(self.constructor.listas_base[nombre_lista])
            
            # Palabras personalizadas
            palabras_personalizadas = config.get('palabras_personalizadas', [])
            if palabras_personalizadas:
                palabras_base.extend(palabras_personalizadas)
            
            if not palabras_base:
                if self.callback_completado:
                    self.callback_completado({
                        'exito': False,
                        'mensaje': 'No hay palabras base para procesar'
                    })
                return
            
            # Eliminar duplicados iniciales
            palabras_base = list(set(palabras_base))
            
            # Paso 2: Generar combinaciones
            if self.callback_progreso:
                self.callback_progreso("Generando combinaciones...", 30)
            
            palabras_resultado = list(palabras_base)
            
            # Si hay múltiples listas, generar combinaciones
            if len(listas_seleccionadas) > 1:
                tipo_combinacion = config.get('tipo_combinacion', 'concatenacion')
                combinaciones = self.constructor.generar_combinaciones(
                    listas_seleccionadas, tipo_combinacion
                )
                palabras_resultado.extend(combinaciones)
            
            # Paso 3: Aplicar mutaciones
            if self.callback_progreso:
                self.callback_progreso("Aplicando mutaciones...", 50)
            
            opciones_mutacion = config.get('opciones_mutacion', {})
            if any(opciones_mutacion.values()):
                palabras_mutadas = self.constructor.aplicar_mutaciones(
                    palabras_resultado, opciones_mutacion
                )
                palabras_resultado = palabras_mutadas
            
            # Paso 4: Aplicar filtros
            if self.callback_progreso:
                self.callback_progreso("Aplicando filtros...", 70)
            
            filtros = config.get('filtros', {})
            if any(v for v in filtros.values() if v is not None and v != ''):
                palabras_resultado = self.constructor.aplicar_filtros(
                    palabras_resultado, filtros
                )
            
            # Eliminar duplicados finales y ordenar
            palabras_resultado = sorted(list(set(palabras_resultado)))
            
            # Paso 5: Exportar si se solicita
            if self.callback_progreso:
                self.callback_progreso("Finalizando...", 90)
            
            exportar = config.get('exportar', False)
            archivo_exportado = None
            
            if exportar:
                nombre_archivo = config.get('nombre_archivo', 'wordlist_generada')
                if self.constructor.exportar_wordlist(palabras_resultado, nombre_archivo):
                    archivo_exportado = f"{nombre_archivo}.txt"
            
            # Guardar en historial
            info_generacion = {
                'total_palabras': len(palabras_resultado),
                'configuracion': config,
                'archivo_exportado': archivo_exportado,
                'estado': 'Completado'
            }
            self.constructor.agregar_al_historial(info_generacion)
            
            # Guardar resultado en el controlador
            self.palabras_generadas = palabras_resultado
            
            # Reportar completado
            if self.callback_progreso:
                self.callback_progreso("¡Completado!", 100)
            
            if self.callback_completado:
                self.callback_completado({
                    'exito': True,
                    'mensaje': f'Wordlist generada con {len(palabras_resultado)} palabras',
                    'total_palabras': len(palabras_resultado),
                    'archivo_exportado': archivo_exportado,
                    'palabras': palabras_resultado[:100]  # Solo las primeras 100 para previsualizar
                })
            
            self.logger.info(f"Generación completada: {len(palabras_resultado)} palabras")
            
        except Exception as e:
            error_msg = f"Error durante la generación: {e}"
            self.logger.error(error_msg)
            
            if self.callback_completado:
                self.callback_completado({
                    'exito': False,
                    'mensaje': error_msg
                })
        finally:
            self.procesando = False
    
    def cancelar_generacion(self) -> bool:
        """Cancela la generación actual."""
        try:
            if self.procesando:
                self.procesando = False
                self.logger.info("Generación cancelada por el usuario")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error cancelando generación: {e}")
            return False
    
    def obtener_palabras_generadas(self, inicio: int = 0, cantidad: int = 100) -> List[str]:
        """Obtiene una porción de las palabras generadas."""
        try:
            fin = inicio + cantidad
            return self.palabras_generadas[inicio:fin]
        except Exception as e:
            self.logger.error(f"Error obteniendo palabras generadas: {e}")
            return []
    
    def obtener_total_palabras_generadas(self) -> int:
        """Obtiene el total de palabras generadas en la sesión actual."""
        return len(self.palabras_generadas)
    
    # === GESTIÓN DE RECETAS ===
    
    def obtener_recetas(self) -> Dict[str, Dict]:
        """Obtiene todas las recetas."""
        try:
            return self.constructor.obtener_recetas()
        except Exception as e:
            self.logger.error(f"Error obteniendo recetas: {e}")
            return {}
    
    def guardar_receta(self, nombre: str, configuracion: Dict[str, Any], descripcion: str = "") -> Dict[str, Any]:
        """Guarda una receta de configuración."""
        try:
            if not nombre.strip():
                return {'exito': False, 'mensaje': 'El nombre no puede estar vacío'}
            
            exito = self.constructor.guardar_receta(nombre, configuracion, descripcion)
            
            if exito:
                return {'exito': True, 'mensaje': f'Receta "{nombre}" guardada'}
            else:
                return {'exito': False, 'mensaje': 'Error interno al guardar la receta'}
                
        except Exception as e:
            error_msg = f"Error guardando receta: {e}"
            self.logger.error(error_msg)
            return {'exito': False, 'mensaje': error_msg}
    
    def cargar_receta(self, nombre: str) -> Dict[str, Any]:
        """Carga una receta específica."""
        try:
            configuracion = self.constructor.cargar_receta(nombre)
            
            if configuracion:
                return {
                    'exito': True,
                    'configuracion': configuracion,
                    'mensaje': f'Receta "{nombre}" cargada exitosamente'
                }
            else:
                return {'exito': False, 'mensaje': 'Receta no encontrada'}
                
        except Exception as e:
            error_msg = f"Error cargando receta: {e}"
            self.logger.error(error_msg)
            return {'exito': False, 'mensaje': error_msg}
    
    def eliminar_receta(self, nombre: str) -> Dict[str, Any]:
        """Elimina una receta."""
        try:
            exito = self.constructor.eliminar_receta(nombre)
            
            if exito:
                return {'exito': True, 'mensaje': f'Receta "{nombre}" eliminada'}
            else:
                return {'exito': False, 'mensaje': 'Receta no encontrada o error al eliminar'}
                
        except Exception as e:
            error_msg = f"Error eliminando receta: {e}"
            self.logger.error(error_msg)
            return {'exito': False, 'mensaje': error_msg}
    
    # === HISTORIAL Y ESTADÍSTICAS ===
    
    def obtener_historial(self, limite: int = 20) -> List[Dict[str, Any]]:
        """Obtiene el historial de generaciones."""
        try:
            return self.constructor.obtener_historial(limite)
        except Exception as e:
            self.logger.error(f"Error obteniendo historial: {e}")
            return []
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas generales."""
        try:
            stats = self.constructor.obtener_estadisticas()
            
            # Añadir estadísticas de la sesión actual
            stats['palabras_sesion_actual'] = len(self.palabras_generadas)
            stats['procesando_actualmente'] = self.procesando
            
            return stats
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas: {e}")
            return {}
    
    def obtener_fuentes_populares(self) -> List[Dict[str, str]]:
        """Obtiene lista de fuentes populares de wordlists."""
        try:
            return self.constructor.obtener_fuentes_populares()
        except Exception as e:
            self.logger.error(f"Error obteniendo fuentes populares: {e}")
            return []
    
    # === UTILIDADES ===
    
    def validar_configuracion(self, configuracion: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida una configuración de generación.
        
        Args:
            configuracion (Dict[str, Any]): Configuración a validar
            
        Returns:
            Dict[str, Any]: Resultado de la validación
        """
        try:
            errores = []
            warnings = []
            
            # Verificar listas seleccionadas
            listas_seleccionadas = configuracion.get('listas_seleccionadas', [])
            palabras_personalizadas = configuracion.get('palabras_personalizadas', [])
            
            if not listas_seleccionadas and not palabras_personalizadas:
                errores.append("Debe seleccionar al menos una lista base o añadir palabras personalizadas")
            
            # Verificar que las listas existen
            listas_disponibles = self.constructor.obtener_nombres_listas_base()
            for lista in listas_seleccionadas:
                if lista not in listas_disponibles:
                    errores.append(f"La lista '{lista}' no existe")
            
            # Verificar filtros
            filtros = configuracion.get('filtros', {})
            min_len = filtros.get('min_len')
            max_len = filtros.get('max_len')
            
            if min_len is not None and max_len is not None:
                if min_len > max_len:
                    errores.append("La longitud mínima no puede ser mayor que la máxima")
            
            # Estimar tamaño de salida
            estimacion = self._estimar_tamaño_wordlist(configuracion)
            if estimacion > 1000000:  # Más de 1 millón
                warnings.append(f"La wordlist estimada tendrá ~{estimacion:,} palabras, puede tardar mucho")
            
            return {
                'valida': len(errores) == 0,
                'errores': errores,
                'warnings': warnings,
                'estimacion_tamaño': estimacion
            }
            
        except Exception as e:
            self.logger.error(f"Error validando configuración: {e}")
            return {
                'valida': False,
                'errores': [f"Error de validación: {e}"],
                'warnings': [],
                'estimacion_tamaño': 0
            }
    
    def _estimar_tamaño_wordlist(self, configuracion: Dict[str, Any]) -> int:
        """Estima el tamaño de la wordlist a generar."""
        try:
            # Contar palabras base
            total_base = 0
            listas_seleccionadas = configuracion.get('listas_seleccionadas', [])
            
            for lista in listas_seleccionadas:
                if lista in self.constructor.listas_base:
                    total_base += len(self.constructor.listas_base[lista])
            
            # Añadir palabras personalizadas
            palabras_personalizadas = configuracion.get('palabras_personalizadas', [])
            total_base += len(palabras_personalizadas)
            
            if total_base == 0:
                return 0
            
            # Multiplicadores por mutaciones
            opciones_mutacion = configuracion.get('opciones_mutacion', {})
            multiplicador = 1
            
            if opciones_mutacion.get('mayusculas'):
                multiplicador += 1
            if opciones_mutacion.get('minusculas'):
                multiplicador += 1
            if opciones_mutacion.get('capitalizar'):
                multiplicador += 1
            if opciones_mutacion.get('leetspeak'):
                multiplicador += 2  # Aproximado
            if opciones_mutacion.get('numeros_comunes'):
                multiplicador += 8  # 8 números comunes
            
            # Prefijos y sufijos
            prefijos = len(opciones_mutacion.get('prefijos', []))
            sufijos = len(opciones_mutacion.get('sufijos', []))
            multiplicador += prefijos + sufijos
            
            return int(total_base * multiplicador)
            
        except Exception as e:
            self.logger.error(f"Error estimando tamaño: {e}")
            return 0
    
    def es_procesando(self) -> bool:
        """Verifica si hay una generación en progreso."""
        return self.procesando
