import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, deque
import threading
import time
import hashlib
from ..utils.utils_ayuda_logging import configurar_logger_modulo
from ..utils.utils_ayuda_rutas import crear_ruta_segura


# Importar utilidades SIEM básicas
from ..utils.utils_siem import (
    TipoEvento as TipoEventoBase, 
    NivelCriticidad as NivelCriticidadBase,
    ReglaCorrelacion as ReglaCorrelacionBase,
    EventoSIEMUtils,
    MotorCorrelacionUtils,
    SIEMUtils
)

# Clases locales simplificadas
class TipoEvento(TipoEventoBase):
    """Extensión local de tipos de evento"""
    pass

class NivelCriticidad(NivelCriticidadBase):
    """Extensión local de niveles de criticidad"""
    pass

class ReglaCorrelacion(ReglaCorrelacionBase):
    """Extensión local de reglas de correlación"""
    pass


class EventoSIEM:
    """Evento SIEM simplificado que usa utilidades"""
    
    def __init__(self, tipo: str, mensaje: str, detalles: Optional[Dict[str, Any]] = None,
                 nivel_criticidad: str = NivelCriticidad.MEDIO, fuente_ip: Optional[str] = None,
                 usuario: Optional[str] = None, proceso: Optional[str] = None, origen: str = "Sistema"):
        """Inicializa un evento SIEM"""
        self.id = EventoSIEMUtils.generar_id_evento()
        self.id_evento = self.id  # Compatibilidad con código existente
        self.tipo = tipo
        self.mensaje = mensaje
        self.timestamp = datetime.now()
        self.nivel_criticidad = nivel_criticidad
        self.detalles = detalles or {}
        self.contexto_hash = EventoSIEMUtils.calcular_hash_contexto(tipo, mensaje, self.detalles)
        self.fuente_ip = fuente_ip
        self.usuario = usuario
        self.proceso = proceso
        self.origen = origen
        self.correlaciones = []
        self.patrones = []
        self.correlacionado = False
        self.reglas_activadas = []
        self.eventos_relacionados = []
    
    def agregar_correlacion(self, regla_nombre: str, eventos_relacionados: List[str]):
        """Agrega información de correlación"""
        self.correlacionado = True
        if regla_nombre not in self.reglas_activadas:
            self.reglas_activadas.append(regla_nombre)
        self.eventos_relacionados.extend(eventos_relacionados)
    
    def establecer_patron(self, patron: str):
        """Establece patrón detectado"""
        if patron not in self.patrones:
            self.patrones.append(patron)
    
    def obtener_prioridad_numerica(self) -> int:
        """Obtiene prioridad numérica"""
        return EventoSIEMUtils.obtener_prioridad_numerica(self.nivel_criticidad)
    
    def es_critico(self) -> bool:
        """Verifica si es crítico"""
        return self.nivel_criticidad in [NivelCriticidad.CRITICO, NivelCriticidad.ALTO]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario"""
        return EventoSIEMUtils.evento_to_dict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EventoSIEM':
        """Crea desde diccionario"""
        evento_data = EventoSIEMUtils.evento_from_dict(data)
        evento = cls(**evento_data)
        
        # Restaurar timestamp si existe en los datos originales
        if 'timestamp' in data:
            try:
                if isinstance(data['timestamp'], str):
                    evento.timestamp = datetime.fromisoformat(data['timestamp'])
                elif isinstance(data['timestamp'], datetime):
                    evento.timestamp = data['timestamp']
            except (ValueError, TypeError) as e:
                # Si no se puede parsear el timestamp, usar el actual
                pass
                
        # Restaurar otros atributos específicos del evento
        if 'id' in data or 'id_evento' in data:
            evento.id_evento = data.get('id', data.get('id_evento', evento.id_evento))
            evento.id = evento.id_evento  # Compatibilidad
        
        return evento
    
    def to_markdown(self) -> str:
        """Convierte a Markdown"""
        return EventoSIEMUtils.evento_to_markdown(self)
    
    def __str__(self) -> str:
        """Representación en string"""
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] [{self.nivel_criticidad}] {self.tipo}: {self.mensaje}"


class MotorCorrelacion:
    """Motor de correlación simplificado que usa utilidades"""
    
    def __init__(self):
        """Inicializa el motor de correlación"""
        # Usar funciones de utilidades para crear reglas predefinidas
        reglas_base = MotorCorrelacionUtils.crear_reglas_predefinidas()
        self.reglas = []
        # Convertir a tipo local para compatibilidad
        for regla_base in reglas_base:
            regla_local = ReglaCorrelacion(
                regla_base.nombre,
                regla_base.tipos_eventos,
                regla_base.ventana_tiempo,
                regla_base.umbral_eventos,
                regla_base.accion,
                regla_base.descripcion
            )
            self.reglas.append(regla_local)
        
        self.ventana_eventos: deque = deque(maxlen=1000)
        self.patrones_detectados: Dict[str, List[str]] = {}
        self.estadisticas_correlacion = {
            'reglas_activadas': 0,
            'patrones_detectados': 0,
            'eventos_correlacionados': 0
        }
    
    def agregar_regla(self, regla: ReglaCorrelacion):
        """Agrega una nueva regla de correlación"""
        self.reglas.append(regla)
    
    def procesar_evento(self, evento: EventoSIEM) -> List[str]:
        """Procesa un evento y verifica correlaciones"""
        self.ventana_eventos.append(evento)
        reglas_activadas = []
        
        # Verificar cada regla usando utilidades
        for regla in self.reglas:
            if not regla.activa:
                continue
                
            if regla.evaluar(evento, list(self.ventana_eventos)):
                reglas_activadas.append(regla.nombre)
                self.estadisticas_correlacion['reglas_activadas'] += 1
                
                # Marcar eventos relacionados
                eventos_relacionados = self._obtener_eventos_relacionados(regla)
                for evento_rel in eventos_relacionados:
                    evento_rel.agregar_correlacion(regla.nombre, [e.id_evento for e in eventos_relacionados])
                
                # Registrar patrón detectado
                patron_key = f"{regla.nombre}_{int(time.time())}"
                self.patrones_detectados[patron_key] = [e.id_evento for e in eventos_relacionados]
                self.estadisticas_correlacion['patrones_detectados'] += 1
        
        if reglas_activadas:
            evento.correlacionado = True
            evento.reglas_activadas.extend(reglas_activadas)
            self.estadisticas_correlacion['eventos_correlacionados'] += 1
        
        return reglas_activadas
    
    def _obtener_eventos_relacionados(self, regla: ReglaCorrelacion) -> List[EventoSIEM]:
        """Obtiene los eventos relacionados para una regla activada"""
        tiempo_limite = datetime.now() - timedelta(seconds=regla.ventana_tiempo)
        return [
            e for e in self.ventana_eventos 
            if e.timestamp >= tiempo_limite and e.tipo in regla.tipos_eventos
        ]
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas del motor de correlación"""
        return {
            'reglas_activas': len([r for r in self.reglas if r.activa]),
            'total_reglas': len(self.reglas),
            'eventos_en_ventana': len(self.ventana_eventos),
            'patrones_detectados_total': len(self.patrones_detectados),
            **self.estadisticas_correlacion
        }
    
    def obtener_patrones_recientes(self, limite: int = 10) -> List[Dict[str, Any]]:
        """Obtiene los patrones detectados más recientes"""
        patrones_ordenados = sorted(
            self.patrones_detectados.items(),
            key=lambda x: x[0].split('_')[-1] if '_' in x[0] else '0',
            reverse=True
        )
        
        return [
            {
                'patron': patron.split('_')[0] if '_' in patron else patron,
                'timestamp': patron.split('_')[-1] if '_' in patron else 'unknown',
                'eventos_relacionados': eventos
            }
            for patron, eventos in patrones_ordenados[:limite]
        ]
    
    def analizar_patrones_temporales(self, ventana_minutos: int = 60) -> Dict[str, Any]:
        """Analiza patrones temporales usando utilidades"""
        eventos_lista = list(self.ventana_eventos)
        return MotorCorrelacionUtils.analizar_patron_temporal(eventos_lista, ventana_minutos)
    
    def detectar_patrones_avanzados(self) -> List[Dict[str, Any]]:
        """Detecta patrones avanzados usando utilidades"""
        eventos_lista = list(self.ventana_eventos)
        return MotorCorrelacionUtils.detectar_patrones_avanzados(eventos_lista)


class SIEM:
    """
    Sistema de Información y Gestión de Eventos con capacidades avanzadas.
    
    Características principales:
    - Gestión centralizada de eventos de seguridad
    - Motor de correlación con detección de patrones
    - Persistencia y análisis de eventos históricos
    - Métricas y estadísticas en tiempo real
    - Alertas automáticas y respuesta a incidentes
    """
    
    def __init__(self, archivo_eventos: Optional[str] = None):
        """
        Inicializa el SIEM con capacidades avanzadas.
        
        Args:
            archivo_eventos: Ruta del archivo para persistir eventos
        """
        self.logger = configurar_logger_modulo("siem")
        
        # Configurar archivo de eventos
        if archivo_eventos is None:
            self.archivo_eventos = self._determinar_ruta_eventos()
        else:
            self.archivo_eventos = archivo_eventos
        
        self.eventos: List[EventoSIEM] = []
        self.max_eventos_memoria = 2000  # Máximo de eventos en memoria
        
        # Inicializar motor de correlación
        self.motor_correlacion = MotorCorrelacion()
        
        # Estadísticas del SIEM
        self.estadisticas = {
            'eventos_totales': 0,
            'eventos_criticos': 0,
            'eventos_altos': 0,
            'ultimo_evento': None,
            'tiempo_inicio': datetime.now(),
            'alertas_generadas': 0
        }
        
        # Cargar eventos existentes
        self._cargar_eventos()
        
        self.logger.info(f"SIEM avanzado inicializado. Archivo: {self.archivo_eventos}")
        
        # Registrar evento de inicio del SIEM
        self.registrar_evento(
            TipoEvento.SISTEMA_INICIADO,
            "SIEM de Ares Aegis iniciado con capacidades avanzadas",
            {
                'archivo_eventos': str(self.archivo_eventos),
                'motor_correlacion': True,
                'max_eventos_memoria': self.max_eventos_memoria
            },
            NivelCriticidad.INFORMATIVO
        )
    
    def _determinar_ruta_eventos(self) -> str:
        """Determina la ruta del archivo de eventos."""
        # Intentar usar directorio del sistema primero
        try:
            ruta_sistema = "/var/log/ares_aegis/eventos_siem.json"
            crear_ruta_segura(ruta_sistema)
            
            # Verificar permisos de escritura
            if os.access(Path(ruta_sistema).parent, os.W_OK):
                return ruta_sistema
        except Exception:
            pass
        
        # Si no se puede usar el directorio del sistema, usar directorio local
        ruta_local = Path.cwd() / "eventos_siem.json"
        return str(ruta_local)
    
    def _cargar_eventos(self):
        """Carga eventos existentes del archivo, robusto ante entradas mal formadas o no dict. Limpia el archivo si es necesario."""
        try:
            if os.path.exists(self.archivo_eventos):
                with open(self.archivo_eventos, 'r', encoding='utf-8') as archivo:
                    datos_archivo = json.load(archivo)

                # Detectar si el archivo tiene estructura de dict (nuevo formato) o lista (antiguo)
                if isinstance(datos_archivo, dict) and 'eventos' in datos_archivo:
                    eventos_lista = datos_archivo['eventos']
                    otros_campos = {k: v for k, v in datos_archivo.items() if k != 'eventos'}
                elif isinstance(datos_archivo, list):
                    eventos_lista = datos_archivo
                    otros_campos = {}
                else:
                    eventos_lista = []
                    otros_campos = {}

                # Filtrar solo eventos válidos (dict)
                eventos_validos = []
                for datos_evento in eventos_lista[-self.max_eventos_memoria:]:
                    if not isinstance(datos_evento, dict):
                        self.logger.warning(f"Evento omitido por no ser un diccionario: {datos_evento}")
                        continue
                    try:
                        if hasattr(EventoSIEM, 'from_dict'):
                            evento = EventoSIEM.from_dict(datos_evento)
                        else:
                            evento = EventoSIEM(
                                tipo=datos_evento['tipo'],
                                mensaje=datos_evento['mensaje'],
                                detalles=datos_evento.get('detalles', {}),
                                nivel_criticidad=datos_evento.get('nivel_criticidad', NivelCriticidad.MEDIO),
                                origen=datos_evento.get('origen', 'Sistema')
                            )
                            evento.id_evento = datos_evento.get('id', evento.id_evento)
                            if 'timestamp' in datos_evento:
                                evento.timestamp = datetime.fromisoformat(datos_evento['timestamp'])
                        self.eventos.append(evento)
                        eventos_validos.append(datos_evento)
                        self.estadisticas['eventos_totales'] += 1
                        if evento.nivel_criticidad == NivelCriticidad.CRITICO:
                            self.estadisticas['eventos_criticos'] += 1
                        elif evento.nivel_criticidad == NivelCriticidad.ALTO:
                            self.estadisticas['eventos_altos'] += 1
                    except Exception as e:
                        self.logger.warning(f"Error al cargar evento: {e}")
                        continue

                # Si hay eventos inválidos, limpiar el archivo en disco
                if len(eventos_validos) < len(eventos_lista):
                    self.logger.warning("Se detectaron eventos inválidos en el archivo, limpiando archivo en disco...")
                    try:
                        if otros_campos:
                            datos_archivo_limpio = dict(otros_campos)
                            datos_archivo_limpio['eventos'] = eventos_validos
                        else:
                            datos_archivo_limpio = eventos_validos
                        with open(self.archivo_eventos, 'w', encoding='utf-8') as archivo:
                            json.dump(datos_archivo_limpio, archivo, ensure_ascii=False, indent=2)
                        self.logger.info("Archivo de eventos SIEM limpiado correctamente.")
                    except Exception as e:
                        self.logger.error(f"Error limpiando archivo de eventos: {e}")

                self.logger.info(f"Cargados {len(self.eventos)} eventos válidos del archivo")
        except Exception as e:
            self.logger.warning(f"Error cargando eventos: {e}")
    
    def _guardar_eventos(self):
        """Guarda eventos en el archivo, robusto ante entradas no dict y preservando estructura si existe."""
        try:
            crear_ruta_segura(self.archivo_eventos)

            # Leer archivo existente para preservar estructura (dict con 'eventos' o lista)
            eventos_existentes = []
            otros_campos = {}
            if os.path.exists(self.archivo_eventos):
                try:
                    with open(self.archivo_eventos, 'r', encoding='utf-8') as archivo:
                        datos_archivo = json.load(archivo)
                    if isinstance(datos_archivo, dict) and 'eventos' in datos_archivo:
                        eventos_existentes = datos_archivo['eventos']
                        otros_campos = {k: v for k, v in datos_archivo.items() if k != 'eventos'}
                    elif isinstance(datos_archivo, list):
                        eventos_existentes = datos_archivo
                except Exception:
                    eventos_existentes = []
                    otros_campos = {}

            # Filtrar solo eventos válidos (dict)
            eventos_existentes = [e for e in eventos_existentes if isinstance(e, dict)]
            ids_existentes = {evento.get('id') for evento in eventos_existentes}

            # Agregar nuevos eventos (solo los que no están ya en el archivo)
            for evento in self.eventos:
                if evento.id_evento not in ids_existentes:
                    eventos_existentes.append(evento.to_dict())

            # Mantener solo los últimos 10000 eventos
            if len(eventos_existentes) > 10000:
                eventos_existentes = eventos_existentes[-10000:]

            # Guardar con la estructura original
            if otros_campos:
                datos_archivo_limpio = dict(otros_campos)
                datos_archivo_limpio['eventos'] = eventos_existentes
            else:
                datos_archivo_limpio = eventos_existentes

            with open(self.archivo_eventos, 'w', encoding='utf-8') as archivo:
                json.dump(datos_archivo_limpio, archivo, ensure_ascii=False, indent=2)

        except Exception as e:
            self.logger.error(f"Error guardando eventos: {e}")
    
    def registrar_evento(self, tipo: str, mensaje: str, 
                        detalles: Optional[Dict[str, Any]] = None,
                        nivel_criticidad: str = NivelCriticidad.MEDIO,
                        origen: str = "Sistema") -> str:
        """
        Registra un nuevo evento en el SIEM con correlación automática.
        
        Args:
            tipo: Tipo del evento (usar constantes de TipoEvento)
            mensaje: Descripción detallada del evento
            detalles: Información adicional
            nivel_criticidad: Nivel de criticidad
            origen: Sistema que origina el evento
            
        Returns:
            str: ID del evento registrado
        """
        evento = EventoSIEM(tipo, mensaje, detalles, nivel_criticidad, origen)
        
        # Procesar correlación
        reglas_activadas = self.motor_correlacion.procesar_evento(evento)
        
        # Agregar a memoria
        self.eventos.append(evento)
        
        # Actualizar estadísticas
        self.estadisticas['eventos_totales'] += 1
        self.estadisticas['ultimo_evento'] = evento.timestamp
        
        if evento.es_critico():
            if nivel_criticidad == NivelCriticidad.CRITICO:
                self.estadisticas['eventos_criticos'] += 1
            elif nivel_criticidad == NivelCriticidad.ALTO:
                self.estadisticas['eventos_altos'] += 1
        
        # Generar alertas si hay correlaciones
        if reglas_activadas:
            self.estadisticas['alertas_generadas'] += 1
            self._generar_alerta_correlacion(evento, reglas_activadas)
        
        # Mantener límite de eventos en memoria
        if len(self.eventos) > self.max_eventos_memoria:
            self.eventos = self.eventos[-self.max_eventos_memoria:]
        
        # Guardar al archivo de forma asíncrona en background
        try:
            self._guardar_eventos()
        except Exception as e:
            self.logger.error(f"Error guardando evento: {e}")
        
        # Log según criticidad con información adicional
        log_msg = f"[{origen}] {tipo}: {mensaje}"
        if reglas_activadas:
            log_msg += f" [CORRELACIÓN: {', '.join(reglas_activadas)}]"
            
        if nivel_criticidad == NivelCriticidad.CRITICO:
            self.logger.critical(log_msg)
        elif nivel_criticidad == NivelCriticidad.ALTO:
            self.logger.error(log_msg)
        elif nivel_criticidad == NivelCriticidad.MEDIO:
            self.logger.warning(log_msg)
        elif nivel_criticidad == NivelCriticidad.BAJO:
            self.logger.info(log_msg)
        else:
            self.logger.debug(log_msg)
        
        return evento.id_evento
    
    def _generar_alerta_correlacion(self, evento: EventoSIEM, reglas_activadas: List[str]):
        """Genera alertas cuando se detectan correlaciones."""
        for regla in reglas_activadas:
            alerta_evento = EventoSIEM(
                TipoEvento.PATRON_ATAQUE_DETECTADO,
                f"Patrón de amenaza detectado: {regla}",
                {
                    'regla_activada': regla,
                    'evento_trigger': evento.id_evento,
                    'nivel_amenaza': 'ALTA',
                    'requiere_atencion': True
                },
                NivelCriticidad.ALTO,
                "Motor de Correlación"
            )
            
            # Agregar a eventos sin recursión
            self.eventos.append(alerta_evento)
            self.logger.error(f"ALERTA DE CORRELACIÓN: {regla} - Evento trigger: {evento.id_evento}")
        
        return evento.id_evento
    
    def obtener_eventos(self, limite: int = 100, 
                       filtro_tipo: Optional[str] = None,
                       filtro_criticidad: Optional[str] = None,
                       solo_correlacionados: bool = False) -> List[EventoSIEM]:
        """
        Obtiene eventos del SIEM con filtros opcionales avanzados.
        
        Args:
            limite: Número máximo de eventos a devolver
            filtro_tipo: Filtrar por tipo de evento
            filtro_criticidad: Filtrar por nivel de criticidad
            solo_correlacionados: Solo eventos que han sido correlacionados
            
        Returns:
            Lista de eventos filtrados ordenados por timestamp (más recientes primero)
        """
        eventos_filtrados = self.eventos.copy()
        
        # Aplicar filtros
        if filtro_tipo:
            eventos_filtrados = [e for e in eventos_filtrados if e.tipo == filtro_tipo]
        
        if filtro_criticidad:
            eventos_filtrados = [e for e in eventos_filtrados if e.nivel_criticidad == filtro_criticidad]
            
        if solo_correlacionados:
            eventos_filtrados = [e for e in eventos_filtrados if e.correlacionado]
        
        # Ordenar por timestamp (más recientes primero) y aplicar límite
        eventos_filtrados.sort(key=lambda x: x.timestamp, reverse=True)
        return eventos_filtrados[:limite]
    
    def obtener_eventos_criticos(self, limite: int = 50) -> List[EventoSIEM]:
        """Obtiene solo eventos críticos y de alta prioridad."""
        return self.obtener_eventos(
            limite=limite,
            filtro_criticidad=None  # Filtraremos manualmente
        )[:limite] if any(e.es_critico() for e in self.eventos) else []
    
    def obtener_patrones_detectados(self, limite: int = 20) -> List[Dict[str, Any]]:
        """Obtiene los patrones de amenaza detectados recientemente."""
        return self.motor_correlacion.obtener_patrones_recientes(limite)
    
    def obtener_estadisticas_completas(self) -> Dict[str, Any]:
        """Obtiene estadísticas completas del SIEM."""
        tiempo_funcionamiento = datetime.now() - self.estadisticas['tiempo_inicio']
        
        # Calcular estadísticas por criticidad
        eventos_por_criticidad = {}
        for nivel in [NivelCriticidad.CRITICO, NivelCriticidad.ALTO, 
                     NivelCriticidad.MEDIO, NivelCriticidad.BAJO, NivelCriticidad.INFORMATIVO]:
            eventos_por_criticidad[nivel] = len([e for e in self.eventos if e.nivel_criticidad == nivel])
        
        # Obtener estadísticas del motor de correlación
        stats_correlacion = self.motor_correlacion.obtener_estadisticas()
        
        return {
            'eventos_en_memoria': len(self.eventos),
            'tiempo_funcionamiento_horas': tiempo_funcionamiento.total_seconds() / 3600,
            'eventos_por_criticidad': eventos_por_criticidad,
            'correlacion': stats_correlacion,
            **self.estadisticas
        }
    
    def buscar_eventos(self, termino_busqueda: str, limite: int = 50) -> List[EventoSIEM]:
        """
        Busca eventos que contengan el término especificado.
        
        Args:
            termino_busqueda: Término a buscar en mensaje y detalles
            limite: Número máximo de resultados
            
        Returns:
            Lista de eventos que coinciden con la búsqueda
        """
        termino_lower = termino_busqueda.lower()
        eventos_encontrados = []
        
        for evento in self.eventos:
            # Buscar en mensaje
            if termino_lower in evento.mensaje.lower():
                eventos_encontrados.append(evento)
                continue
                
            # Buscar en detalles
            for valor in evento.detalles.values():
                if isinstance(valor, str) and termino_lower in valor.lower():
                    eventos_encontrados.append(evento)
                    break
        
        # Ordenar por timestamp descendente y limitar
        eventos_encontrados.sort(key=lambda x: x.timestamp, reverse=True)
        return eventos_encontrados[:limite]
    
    def limpiar_eventos_antiguos(self, dias_antiguedad: int = 30) -> int:
        """Limpia eventos anteriores al número de días especificado usando utilidades"""
        eventos_antes = len(self.eventos)
        
        # Usar utilidades para limpiar eventos
        self.eventos = SIEMUtils.limpiar_eventos_antiguos(self.eventos, dias_antiguedad)
        eventos_eliminados = eventos_antes - len(self.eventos)
        
        if eventos_eliminados > 0:
            self.logger.info(f"Limpieza completada: {eventos_eliminados} eventos eliminados")
            # Registrar evento de limpieza
            self.registrar_evento(
                TipoEvento.SISTEMA_INICIADO,
                f"Limpieza automática de eventos: {eventos_eliminados} eventos eliminados",
                {'eventos_eliminados': eventos_eliminados, 'dias_antiguedad': dias_antiguedad},
                NivelCriticidad.INFORMATIVO
            )
        
        return eventos_eliminados
    
    def generar_reporte_markdown(self, limite: int = 50) -> str:
        """
        Genera un reporte de eventos en formato Markdown.
        
        Args:
            limite: Número máximo de eventos a incluir
            
        Returns:
            str: Reporte en formato Markdown
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        md = f"# Reporte SIEM de Ares Aegis\n\n"
        md += f"**Fecha de Generación:** {timestamp}\n\n"
        
        # Estadísticas generales
        estadisticas = self.obtener_estadisticas_completas()
        md += "## Estadísticas Generales\n\n"
        md += f"- **Total de Eventos:** {estadisticas['eventos_totales']}\n"
        md += f"- **Eventos en Memoria:** {estadisticas['eventos_en_memoria']}\n"
        md += f"- **Tiempo de Funcionamiento:** {estadisticas['tiempo_funcionamiento_horas']:.2f} horas\n"
        md += f"- **Eventos Críticos:** {estadisticas['eventos_criticos']}\n"
        md += f"- **Eventos Altos:** {estadisticas['eventos_altos']}\n"
        md += f"- **Alertas Generadas:** {estadisticas['alertas_generadas']}\n\n"
        
        # Distribución por criticidad
        md += "### Distribución por Criticidad\n\n"
        for criticidad, cantidad in estadisticas['eventos_por_criticidad'].items():
            emoji = {
                NivelCriticidad.BAJO: '',
                NivelCriticidad.MEDIO: '', 
                NivelCriticidad.ALTO: '',
                NivelCriticidad.CRITICO: '',
                NivelCriticidad.INFORMATIVO: ''
            }.get(criticidad, '')
            md += f"- {emoji} **{criticidad}:** {cantidad}\n"
        md += "\n"
        
        # Estadísticas de correlación
        correlacion = estadisticas['correlacion']
        md += "### Motor de Correlación\n\n"
        md += f"- **Reglas Activas:** {correlacion['reglas_activas']}/{correlacion['total_reglas']}\n"
        md += f"- **Eventos Correlacionados:** {correlacion['eventos_correlacionados']}\n"
        md += f"- **Patrones Detectados:** {correlacion['patrones_detectados_total']}\n"
        md += f"- **Eventos en Ventana:** {correlacion['eventos_en_ventana']}\n\n"
        
        # Patrones recientes
        patrones_recientes = self.obtener_patrones_detectados(5)
        if patrones_recientes:
            md += "### Patrones de Amenaza Detectados\n\n"
            for patron in patrones_recientes:
                md += f"- **{patron['patron']}** - Eventos: {len(patron['eventos_relacionados'])}\n"
            md += "\n"
        
        # Eventos recientes
        eventos_recientes = self.obtener_eventos(limite)
        md += f"## Eventos Recientes (últimos {len(eventos_recientes)})\n\n"
        
        for evento in eventos_recientes:
            md += evento.to_markdown()
            md += "---\n\n"
        
        return md
    
    def exportar_eventos(self, ruta_archivo: str, formato: str = "json") -> bool:
        """
        Exporta eventos a un archivo externo con múltiples formatos.
        
        Args:
            ruta_archivo: Ruta del archivo destino
            formato: Formato de exportación (json, markdown, csv)
            
        Returns:
            bool: True si la exportación fue exitosa
        """
        try:
            crear_ruta_segura(ruta_archivo)
            
            if formato.lower() == "json":
                with open(ruta_archivo, 'w', encoding='utf-8') as archivo:
                    datos_eventos = [evento.to_dict() for evento in self.eventos]
                    json.dump(datos_eventos, archivo, ensure_ascii=False, indent=2)
            
            elif formato.lower() == "markdown":
                with open(ruta_archivo, 'w', encoding='utf-8') as archivo:
                    archivo.write(self.generar_reporte_markdown(len(self.eventos)))
                    
            elif formato.lower() == "csv":
                import csv
                with open(ruta_archivo, 'w', newline='', encoding='utf-8') as archivo:
                    writer = csv.writer(archivo)
                    writer.writerow(['ID', 'Timestamp', 'Tipo', 'Mensaje', 'Criticidad', 'Origen', 'Correlacionado'])
                    
                    for evento in self.eventos:
                        writer.writerow([
                            evento.id_evento,
                            evento.timestamp.isoformat(),
                            evento.tipo,
                            evento.mensaje,
                            evento.nivel_criticidad,
                            evento.origen,
                            'Sí' if evento.correlacionado else 'No'
                        ])
            
            else:
                self.logger.error(f"Formato de exportación no soportado: {formato}")
                return False
            
            self.logger.info(f"Eventos exportados a {ruta_archivo} en formato {formato}")
            
            # Registrar evento de exportación
            self.registrar_evento(
                TipoEvento.INFORMACION,
                f"Eventos exportados en formato {formato.upper()}",
                {
                    'archivo_destino': ruta_archivo,
                    'formato': formato,
                    'cantidad_eventos': len(self.eventos)
                },
                NivelCriticidad.INFORMATIVO
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error exportando eventos: {e}")
            return False
    
    def obtener_resumen_seguridad(self) -> Dict[str, Any]:
        """Obtiene un resumen del estado de seguridad usando utilidades SIEM"""
        # Usar utilidades para generar resumen básico
        resumen_base = SIEMUtils.generar_resumen_seguridad(self.eventos)
        
        # Agregar información específica del motor de correlación
        stats_correlacion = self.motor_correlacion.obtener_estadisticas()
        patrones_recientes = self.obtener_patrones_detectados(10)
        
        # Combinar información
        return {
            **resumen_base,
            'patrones_detectados': len(patrones_recientes),
            'eventos_correlacionados': stats_correlacion['eventos_correlacionados'],
            'reglas_activas': stats_correlacion['reglas_activas'],
            'motor_correlacion_activo': True,
            'recomendaciones': self._generar_recomendaciones_seguridad(
                resumen_base.get('estado', 'NORMAL'), 
                resumen_base.get('eventos_criticos', 0),
                resumen_base.get('eventos_altos', 0)
            )
        }
    
    def _generar_recomendaciones_seguridad(self, nivel_amenaza: str, criticos: int, altos: int) -> List[str]:
        """Genera recomendaciones basadas en el estado de seguridad."""
        recomendaciones = []
        
        if nivel_amenaza == "CRÍTICO":
            recomendaciones.extend([
                " Revisión inmediata del sistema requerida",
                " Considerar aislar sistemas comprometidos",
                " Notificar al equipo de respuesta a incidentes",
                "[STATS] Ejecutar análisis forense completo"
            ])
        elif nivel_amenaza == "ALTO":
            recomendaciones.extend([
                " Monitoreo intensivo recomendado",
                " Revisar logs de eventos críticos",
                "[SHIELD] Verificar configuraciones de seguridad",
                " Actualizar reglas de detección"
            ])
        elif nivel_amenaza == "MEDIO":
            recomendaciones.extend([
                " Mantener vigilancia de eventos",
                "[REFRESH] Revisar patrones de actividad",
                " Monitorear tendencias de amenazas"
            ])
        else:
            recomendaciones.extend([
                "[OK] Sistema operando normalmente",
                "[REFRESH] Continuar monitoreo rutinario",
                " Programar revisión periódica"
            ])
        
        return recomendaciones
    
    def cerrar(self):
        """Cierra el SIEM guardando eventos pendientes."""
        self.registrar_evento(
            TipoEvento.SISTEMA_DETENIDO,
            "SIEM de Ares Aegis detenido",
            nivel_criticidad="MEDIO"
        )
        self._guardar_eventos()
        self.logger.info("SIEM cerrado correctamente")
    
    def buscar_eventos_avanzada(self, tipo_evento: Optional[str] = None, 
                      nivel_criticidad: Optional[str] = None,
                      fecha_inicio: Optional[datetime] = None,
                      fecha_fin: Optional[datetime] = None,
                      texto_busqueda: Optional[str] = None,
                      limite: int = 100) -> List[EventoSIEM]:
        """
        Búsqueda avanzada de eventos con múltiples filtros.
        
        Args:
            tipo_evento: Filtrar por tipo de evento
            nivel_criticidad: Filtrar por nivel de criticidad
            fecha_inicio: Fecha de inicio para filtrar
            fecha_fin: Fecha de fin para filtrar
            texto_busqueda: Texto a buscar en mensaje o detalles
            limite: Número máximo de eventos a devolver
            
        Returns:
            List[EventoSIEM]: Lista de eventos que cumplen los filtros
        """
        eventos_filtrados = self.eventos.copy()
        
        # Filtrar por tipo de evento
        if tipo_evento:
            eventos_filtrados = [e for e in eventos_filtrados if e.tipo == tipo_evento]
        
        # Filtrar por nivel de criticidad
        if nivel_criticidad:
            eventos_filtrados = [e for e in eventos_filtrados if e.nivel_criticidad == nivel_criticidad]
        
        # Filtrar por rango de fechas
        if fecha_inicio:
            eventos_filtrados = [e for e in eventos_filtrados if e.timestamp >= fecha_inicio]
        
        if fecha_fin:
            eventos_filtrados = [e for e in eventos_filtrados if e.timestamp <= fecha_fin]
        
        # Filtrar por texto
        if texto_busqueda:
            texto_lower = texto_busqueda.lower()
            eventos_filtrados = [
                e for e in eventos_filtrados 
                if (texto_lower in e.mensaje.lower() or 
                    (e.detalles and texto_lower in str(e.detalles).lower()))
            ]
        
        # Ordenar por timestamp descendente y limitar
        eventos_filtrados.sort(key=lambda x: x.timestamp, reverse=True)
        
        return eventos_filtrados[:limite]
    
    def rotar_logs(self) -> bool:
        """
        Rota los logs del SIEM manteniendo solo eventos recientes.
        
        Returns:
            bool: True si la rotación fue exitosa
        """
        try:
            eventos_eliminados = self.limpiar_eventos_antiguos(30)  # 30 días de retención
            self.logger.info(f"Rotación de logs completada: {eventos_eliminados} eventos antiguos eliminados")
            return True
        except Exception as e:
            self.logger.error(f"Error en rotación de logs: {e}")
            return False
    
    def inicializar(self) -> bool:
        """Inicializar el SIEM"""
        try:
            self.activo = True
            self.logger.info("SIEM inicializado correctamente")
            return True
        except Exception as e:
            self.logger.error(f"Error inicializando SIEM: {e}")
            return False
    
    def finalizar(self):
        """Finalizar el SIEM y limpiar recursos"""
        try:
            self.activo = False
            self.logger.info("SIEM finalizado correctamente")
        except Exception as e:
            self.logger.error(f"Error finalizando SIEM: {e}")
    
    def obtener_eventos_recientes(self, limite: int = 10) -> List[Dict[str, Any]]:
        """Obtener eventos recientes del SIEM"""
        try:
            eventos_recientes = sorted(
                self.eventos, 
                key=lambda x: x.timestamp if hasattr(x, 'timestamp') else '', 
                reverse=True
            )
            return [evento.__dict__ for evento in eventos_recientes[:limite]]
        except Exception as e:
            self.logger.error(f"Error obteniendo eventos recientes: {e}")
            return []

