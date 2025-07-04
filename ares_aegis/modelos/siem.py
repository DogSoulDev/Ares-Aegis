#!/usr/bin/env python3
"""
Copyright (c) 2025 DogSoulDev (https://github.com/DogSoulDev)
Todos los derechos reservados. Este código es propietario y confidencial.

SIEM - Sistema de Información y Gestión de Eventos Avanzado
Núcleo central del sistema de ciberseguridad con análisis de correlación
y detección de patrones de amenazas en tiempo real.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, deque
import threading
import time
from ..utilidades.ayuda_logging import configurar_logger_modulo
from ..utilidades.ayuda_rutas import crear_ruta_segura


class TipoEvento:
    """Constantes para tipos de eventos del SIEM con clasificación española."""
    # Eventos de Escaneo y Análisis
    ESCANEO_INICIADO = "ESCANEO_INICIADO"
    ESCANEO_FINALIZADO = "ESCANEO_FINALIZADO"
    ESCANEO_INTERRUMPIDO = "ESCANEO_INTERRUMPIDO"
    ANALISIS_INICIADO = "ANALISIS_INICIADO"
    ANALISIS_COMPLETADO = "ANALISIS_COMPLETADO"
    
    # Eventos de Amenazas y Seguridad
    AMENAZA_DETECTADA = "AMENAZA_DETECTADA"
    AMENAZA_BLOQUEADA = "AMENAZA_BLOQUEADA"
    AMENAZA_NEUTRALIZADA = "AMENAZA_NEUTRALIZADA"
    MALWARE_DETECTADO = "MALWARE_DETECTADO"
    VIRUS_ENCONTRADO = "VIRUS_ENCONTRADO"
    TROJAN_DETECTADO = "TROJAN_DETECTADO"
    RANSOMWARE_DETECTADO = "RANSOMWARE_DETECTADO"
    ROOTKIT_DETECTADO = "ROOTKIT_DETECTADO"
    
    # Eventos de Cuarentena
    ARCHIVO_CUARENTENA = "ARCHIVO_CUARENTENA"
    ARCHIVO_RESTAURADO = "ARCHIVO_RESTAURADO"
    CUARENTENA_LIMPIADA = "CUARENTENA_LIMPIADA"
    
    # Eventos de Integridad
    INTEGRIDAD_VIOLADA = "INTEGRIDAD_VIOLADA"
    ARCHIVO_MODIFICADO = "ARCHIVO_MODIFICADO"
    ARCHIVO_ELIMINADO = "ARCHIVO_ELIMINADO"
    ARCHIVO_CREADO = "ARCHIVO_CREADO"
    PERMISOS_MODIFICADOS = "PERMISOS_MODIFICADOS"
    
    # Eventos de Red
    CONEXION_SOSPECHOSA = "CONEXION_SOSPECHOSA"
    TRAFICO_MALICIOSO = "TRAFICO_MALICIOSO"
    IP_BLOQUEADA = "IP_BLOQUEADA"
    PUERTO_ESCANEADO = "PUERTO_ESCANEADO"
    CONEXION_NO_AUTORIZADA = "CONEXION_NO_AUTORIZADA"
    ATAQUE_DENEGACION_SERVICIO = "ATAQUE_DENEGACION_SERVICIO"
    
    # Eventos de Procesos
    PROCESO_SOSPECHOSO = "PROCESO_SOSPECHOSO"
    PROCESO_MALICIOSO = "PROCESO_MALICIOSO"
    PROCESO_TERMINADO = "PROCESO_TERMINADO"
    PROCESO_ELEVACION_PRIVILEGIOS = "PROCESO_ELEVACION_PRIVILEGIOS"
    PROCESO_INYECCION_CODIGO = "PROCESO_INYECCION_CODIGO"
    
    # Eventos de Vulnerabilidades
    VULNERABILIDAD_DETECTADA = "VULNERABILIDAD_DETECTADA"
    VULNERABILIDAD_CRITICA = "VULNERABILIDAD_CRITICA"
    EXPLOIT_DETECTADO = "EXPLOIT_DETECTADO"
    CVE_ENCONTRADA = "CVE_ENCONTRADA"
    
    # Eventos de Sistema
    SISTEMA_INICIADO = "SISTEMA_INICIADO"
    SISTEMA_DETENIDO = "SISTEMA_DETENIDO"
    SERVICIO_INICIADO = "SERVICIO_INICIADO"
    SERVICIO_DETENIDO = "SERVICIO_DETENIDO"
    CONFIGURACION_MODIFICADA = "CONFIGURACION_MODIFICADA"
    
    # Eventos de Autenticación y Acceso
    LOGIN_EXITOSO = "LOGIN_EXITOSO"
    LOGIN_FALLIDO = "LOGIN_FALLIDO"
    ACCESO_DENEGADO = "ACCESO_DENEGADO"
    SESION_EXPIRADA = "SESION_EXPIRADA"
    PRIVILEGIOS_ELEVADOS = "PRIVILEGIOS_ELEVADOS"
    
    # Eventos de Error y Advertencia
    ERROR_SISTEMA = "ERROR_SISTEMA"
    ERROR_CRITICO = "ERROR_CRITICO"
    ADVERTENCIA = "ADVERTENCIA"
    INFORMACION = "INFORMACION"
    
    # Eventos de Correlación
    PATRON_ATAQUE_DETECTADO = "PATRON_ATAQUE_DETECTADO"
    MULTIPLES_INTENTOS_ACCESO = "MULTIPLES_INTENTOS_ACCESO"
    ACTIVIDAD_ANOMALA = "ACTIVIDAD_ANOMALA"
    CORRELACION_AMENAZAS = "CORRELACION_AMENAZAS"


class NivelCriticidad:
    """Niveles de criticidad con descripción española."""
    CRITICO = "CRITICO"          # Amenaza inmediata al sistema
    ALTO = "ALTO"                # Amenaza significativa
    MEDIO = "MEDIO"              # Advertencia importante
    BAJO = "BAJO"                # Información general
    INFORMATIVO = "INFORMATIVO"  # Solo información


class ReglaCorrelacion:
    """Representa una regla de correlación de eventos."""
    
    def __init__(self, nombre: str, tipos_eventos: List[str], 
                 ventana_tiempo: int = 300, umbral_eventos: int = 3,
                 accion: str = "ALERTA", descripcion: str = ""):
        """
        Inicializa una regla de correlación.
        
        Args:
            nombre: Nombre de la regla
            tipos_eventos: Lista de tipos de eventos a correlacionar
            ventana_tiempo: Ventana de tiempo en segundos
            umbral_eventos: Número mínimo de eventos para activar la regla
            accion: Acción a realizar cuando se active la regla
            descripcion: Descripción de la regla
        """
        self.nombre = nombre
        self.tipos_eventos = tipos_eventos
        self.ventana_tiempo = ventana_tiempo
        self.umbral_eventos = umbral_eventos
        self.accion = accion
        self.descripcion = descripcion
        self.activa = True
        self.eventos_detectados = 0


class EventoSIEM:
    """
    Representa un evento en el sistema SIEM con correlación avanzada.
    
    Maneja la información completa del evento incluyendo:
    - Metadatos temporales y de origen
    - Clasificación de criticidad
    - Contexto adicional para correlación
    - Patrones de comportamiento
    """
    
    def __init__(self, tipo: str, mensaje: str, detalles: Optional[Dict[str, Any]] = None,
                 nivel_criticidad: str = NivelCriticidad.MEDIO, origen: str = "Sistema"):
        """
        Inicializa un evento SIEM con información completa.
        
        Args:
            tipo: Tipo de evento (usar constantes de TipoEvento)
            mensaje: Descripción detallada del evento
            detalles: Información adicional del evento
            nivel_criticidad: Nivel de criticidad del evento
            origen: Sistema u origen que genera el evento
        """
        self.timestamp = datetime.now()
        self.tipo = tipo
        self.mensaje = mensaje
        self.detalles = detalles or {}
        self.nivel_criticidad = nivel_criticidad
        self.origen = origen
        self.id_evento = self._generar_id_evento()
        
        # Información adicional para correlación
        self.correlacionado = False
        self.reglas_activadas = []
        self.eventos_relacionados = []
        self.hash_contexto = self._calcular_hash_contexto()
        self.patron_detectado = None
    
    def _generar_id_evento(self) -> str:
        """Genera un ID único para el evento."""
        timestamp_str = self.timestamp.strftime('%Y%m%d%H%M%S')
        hash_mensaje = abs(hash(f"{self.mensaje}{self.tipo}")) % 100000
        return f"EVT-{timestamp_str}-{hash_mensaje:05d}"
    
    def _calcular_hash_contexto(self) -> str:
        """Calcula un hash del contexto para agrupación rápida."""
        import hashlib
        contexto_str = str(sorted(self.detalles.items()))
        return hashlib.md5(f"{self.tipo}{contexto_str}".encode()).hexdigest()[:8]
    
    def agregar_correlacion(self, regla_nombre: str, eventos_relacionados: List[str]):
        """Agrega información de correlación al evento."""
        self.correlacionado = True
        if regla_nombre not in self.reglas_activadas:
            self.reglas_activadas.append(regla_nombre)
        self.eventos_relacionados.extend(eventos_relacionados)
    
    def establecer_patron(self, patron: str):
        """Establece el patrón de amenaza detectado."""
        self.patron_detectado = patron
    
    def obtener_prioridad_numerica(self) -> int:
        """Convierte el nivel de criticidad a valor numérico para ordenamiento."""
        prioridades = {
            NivelCriticidad.CRITICO: 5,
            NivelCriticidad.ALTO: 4,
            NivelCriticidad.MEDIO: 3,
            NivelCriticidad.BAJO: 2,
            NivelCriticidad.INFORMATIVO: 1
        }
        return prioridades.get(self.nivel_criticidad, 3)
    
    def es_critico(self) -> bool:
        """Verifica si el evento es de criticidad alta o crítica."""
        return self.nivel_criticidad in [NivelCriticidad.CRITICO, NivelCriticidad.ALTO]
    
    def obtener_resumen(self) -> str:
        """Obtiene un resumen corto del evento."""
        estado_correlacion = " [CORRELACIONADO]" if self.correlacionado else ""
        patron_info = f" - Patrón: {self.patron_detectado}" if self.patron_detectado else ""
        return f"[{self.nivel_criticidad}] {self.tipo}: {self.mensaje[:100]}...{estado_correlacion}{patron_info}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el evento a diccionario para serialización completa."""
        return {
            'id': self.id_evento,
            'timestamp': self.timestamp.isoformat(),
            'tipo': self.tipo,
            'mensaje': self.mensaje,
            'detalles': self.detalles,
            'nivel_criticidad': self.nivel_criticidad,
            'origen': self.origen,
            'correlacionado': self.correlacionado,
            'reglas_activadas': self.reglas_activadas,
            'eventos_relacionados': self.eventos_relacionados,
            'hash_contexto': self.hash_contexto,
            'patron_detectado': self.patron_detectado
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EventoSIEM':
        """Crea un evento desde un diccionario con información completa."""
        evento = cls(
            data['tipo'], 
            data['mensaje'],
            data.get('detalles', {}),
            data.get('nivel_criticidad', NivelCriticidad.MEDIO),
            data.get('origen', 'Sistema')
        )
        evento.id_evento = data.get('id', evento.id_evento)
        if 'timestamp' in data:
            evento.timestamp = datetime.fromisoformat(data['timestamp'])
        
        # Restaurar información de correlación
        evento.correlacionado = data.get('correlacionado', False)
        evento.reglas_activadas = data.get('reglas_activadas', [])
        evento.eventos_relacionados = data.get('eventos_relacionados', [])
        evento.hash_contexto = data.get('hash_contexto', evento.hash_contexto)
        evento.patron_detectado = data.get('patron_detectado')
        
        return evento
    
    def to_markdown(self) -> str:
        """Convierte el evento a formato Markdown."""
        timestamp_str = self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        
        # Elegir emoji según criticidad
        emoji_criticidad = {
            'BAJO': '🔵',
            'MEDIO': '🟡',
            'ALTO': '🟠',
            'CRITICO': '🔴'
        }.get(self.nivel_criticidad, '⚪')
        
        md = f"### {emoji_criticidad} {self.tipo}\n\n"
        md += f"**ID:** {self.id_evento}\n"
        md += f"**Timestamp:** {timestamp_str}\n"
        md += f"**Criticidad:** {self.nivel_criticidad}\n"
        md += f"**Mensaje:** {self.mensaje}\n\n"
        
        if self.detalles:
            md += "**Detalles:**\n"
            for clave, valor in self.detalles.items():
                md += f"- **{clave}:** {valor}\n"
            md += "\n"
        
        return md
    
    def __str__(self) -> str:
        """Representación en string del evento."""
        timestamp_str = self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        return f"[{timestamp_str}] [{self.nivel_criticidad}] {self.tipo}: {self.mensaje}"


class MotorCorrelacion:
    """Motor de correlación de eventos para detección de patrones."""
    
    def __init__(self):
        """Inicializa el motor de correlación."""
        self.reglas: List[ReglaCorrelacion] = []
        self.ventana_eventos: deque = deque(maxlen=1000)  # Últimos 1000 eventos
        self.patrones_detectados: Dict[str, List[str]] = {}
        self.estadisticas_correlacion = {
            'reglas_activadas': 0,
            'patrones_detectados': 0,
            'eventos_correlacionados': 0
        }
        
        self._inicializar_reglas_predefinidas()
    
    def _inicializar_reglas_predefinidas(self):
        """Inicializa reglas de correlación predefinidas."""
        reglas_base = [
            ReglaCorrelacion(
                "Multiples_Intentos_Acceso",
                [TipoEvento.LOGIN_FALLIDO, TipoEvento.ACCESO_DENEGADO],
                ventana_tiempo=300,  # 5 minutos
                umbral_eventos=5,
                accion="BLOQUEAR_IP",
                descripcion="Detecta múltiples intentos de acceso fallidos"
            ),
            ReglaCorrelacion(
                "Escalada_Privilegios",
                [TipoEvento.PRIVILEGIOS_ELEVADOS, TipoEvento.PROCESO_ELEVACION_PRIVILEGIOS],
                ventana_tiempo=600,  # 10 minutos
                umbral_eventos=3,
                accion="ALERTA_CRITICA",
                descripcion="Detecta intentos de escalada de privilegios"
            ),
            ReglaCorrelacion(
                "Patron_Malware",
                [TipoEvento.MALWARE_DETECTADO, TipoEvento.PROCESO_SOSPECHOSO, TipoEvento.CONEXION_SOSPECHOSA],
                ventana_tiempo=900,  # 15 minutos
                umbral_eventos=3,
                accion="CUARENTENA_AUTOMATICA",
                descripcion="Detecta patrones típicos de actividad malware"
            ),
            ReglaCorrelacion(
                "Intento_Intrusión",
                [TipoEvento.PUERTO_ESCANEADO, TipoEvento.CONEXION_NO_AUTORIZADA, TipoEvento.IP_BLOQUEADA],
                ventana_tiempo=1200,  # 20 minutos
                umbral_eventos=4,
                accion="ALERTA_SEGURIDAD",
                descripcion="Detecta intentos de intrusión en la red"
            ),
            ReglaCorrelacion(
                "Violacion_Integridad_Masiva",
                [TipoEvento.INTEGRIDAD_VIOLADA, TipoEvento.ARCHIVO_MODIFICADO, TipoEvento.PERMISOS_MODIFICADOS],
                ventana_tiempo=300,  # 5 minutos
                umbral_eventos=10,
                accion="ALERTA_CRITICA",
                descripcion="Detecta modificaciones masivas de archivos"
            )
        ]
        
        self.reglas.extend(reglas_base)
    
    def agregar_regla(self, regla: ReglaCorrelacion):
        """Agrega una nueva regla de correlación."""
        self.reglas.append(regla)
    
    def procesar_evento(self, evento: EventoSIEM) -> List[str]:
        """
        Procesa un evento y verifica correlaciones.
        
        Returns:
            Lista de reglas activadas
        """
        self.ventana_eventos.append(evento)
        reglas_activadas = []
        
        # Verificar cada regla
        for regla in self.reglas:
            if not regla.activa:
                continue
                
            if self._verificar_regla(regla, evento):
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
    
    def _verificar_regla(self, regla: ReglaCorrelacion, evento_actual: EventoSIEM) -> bool:
        """Verifica si una regla se activa con el evento actual."""
        if evento_actual.tipo not in regla.tipos_eventos:
            return False
        
        # Obtener eventos en la ventana de tiempo
        tiempo_limite = evento_actual.timestamp - timedelta(seconds=regla.ventana_tiempo)
        eventos_ventana = [
            e for e in self.ventana_eventos 
            if e.timestamp >= tiempo_limite and e.tipo in regla.tipos_eventos
        ]
        
        # Verificar si se alcanza el umbral
        return len(eventos_ventana) >= regla.umbral_eventos
    
    def _obtener_eventos_relacionados(self, regla: ReglaCorrelacion) -> List[EventoSIEM]:
        """Obtiene los eventos relacionados para una regla activada."""
        tiempo_limite = datetime.now() - timedelta(seconds=regla.ventana_tiempo)
        return [
            e for e in self.ventana_eventos 
            if e.timestamp >= tiempo_limite and e.tipo in regla.tipos_eventos
        ]
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas del motor de correlación."""
        return {
            'reglas_activas': len([r for r in self.reglas if r.activa]),
            'total_reglas': len(self.reglas),
            'eventos_en_ventana': len(self.ventana_eventos),
            'patrones_detectados_total': len(self.patrones_detectados),
            **self.estadisticas_correlacion
        }
    
    def obtener_patrones_recientes(self, limite: int = 10) -> List[Dict[str, Any]]:
        """Obtiene los patrones detectados más recientes."""
        patrones_ordenados = sorted(
            self.patrones_detectados.items(),
            key=lambda x: x[0].split('_')[-1],  # Ordenar por timestamp
            reverse=True
        )
        
        return [
            {
                'patron': patron.split('_')[0],
                'timestamp': patron.split('_')[-1],
                'eventos_relacionados': eventos
            }
            for patron, eventos in patrones_ordenados[:limite]
        ]


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
        """Carga eventos existentes del archivo."""
        try:
            if os.path.exists(self.archivo_eventos):
                with open(self.archivo_eventos, 'r', encoding='utf-8') as archivo:
                    datos_eventos = json.load(archivo)
                    
                    # Cargar solo los últimos eventos para no sobrecargar memoria
                    eventos_recientes = datos_eventos[-self.max_eventos_memoria:]
                    
                    for datos_evento in eventos_recientes:
                        try:
                            # Intentar usar el método from_dict si está disponible
                            if hasattr(EventoSIEM, 'from_dict'):
                                evento = EventoSIEM.from_dict(datos_evento)
                            else:
                                # Crear evento manualmente con compatibilidad
                                evento = EventoSIEM(
                                    tipo=datos_evento['tipo'],
                                    mensaje=datos_evento['mensaje'],
                                    detalles=datos_evento.get('detalles', {}),
                                    nivel_criticidad=datos_evento.get('nivel_criticidad', NivelCriticidad.MEDIO),
                                    origen=datos_evento.get('origen', 'Sistema')
                                )
                                # Restaurar timestamp e ID originales
                                evento.id_evento = datos_evento.get('id', evento.id_evento)
                                if 'timestamp' in datos_evento:
                                    evento.timestamp = datetime.fromisoformat(datos_evento['timestamp'])
                            
                            self.eventos.append(evento)
                            self.estadisticas['eventos_totales'] += 1
                            
                            # Actualizar estadísticas por criticidad
                            if evento.nivel_criticidad == NivelCriticidad.CRITICO:
                                self.estadisticas['eventos_criticos'] += 1
                            elif evento.nivel_criticidad == NivelCriticidad.ALTO:
                                self.estadisticas['eventos_altos'] += 1
                                
                        except Exception as e:
                            self.logger.warning(f"Error al cargar evento: {e}")
                            continue
                        evento.timestamp = datetime.fromisoformat(datos_evento['timestamp'])
                        evento.id_evento = datos_evento['id']
                        self.eventos.append(evento)
                        
                self.logger.info(f"Cargados {len(self.eventos)} eventos del archivo")
        
        except Exception as e:
            self.logger.warning(f"Error cargando eventos: {e}")
    
    def _guardar_eventos(self):
        """Guarda eventos en el archivo."""
        try:
            # Crear directorio si no existe
            crear_ruta_segura(self.archivo_eventos)
            
            # Guardar todos los eventos (no solo los de memoria)
            eventos_existentes = []
            
            # Leer eventos existentes del archivo
            if os.path.exists(self.archivo_eventos):
                try:
                    with open(self.archivo_eventos, 'r', encoding='utf-8') as archivo:
                        eventos_existentes = json.load(archivo)
                except Exception:
                    eventos_existentes = []
            
            # Agregar nuevos eventos (solo los que no están ya en el archivo)
            ids_existentes = {evento.get('id') for evento in eventos_existentes}
            
            for evento in self.eventos:
                if evento.id_evento not in ids_existentes:
                    eventos_existentes.append(evento.to_dict())
            
            # Mantener solo los últimos 10000 eventos en el archivo
            if len(eventos_existentes) > 10000:
                eventos_existentes = eventos_existentes[-10000:]
            
            # Guardar al archivo
            with open(self.archivo_eventos, 'w', encoding='utf-8') as archivo:
                json.dump(eventos_existentes, archivo, ensure_ascii=False, indent=2)
                
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
        """
        Limpia eventos anteriores al número de días especificado.
        
        Args:
            dias_antiguedad: Días de antigüedad para considerar eventos antiguos
            
        Returns:
            Número de eventos eliminados
        """
        fecha_limite = datetime.now() - timedelta(days=dias_antiguedad)
        eventos_antes = len(self.eventos)
        
        # Filtrar eventos recientes
        self.eventos = [e for e in self.eventos if e.timestamp >= fecha_limite]
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
                NivelCriticidad.BAJO: '🔵',
                NivelCriticidad.MEDIO: '🟡', 
                NivelCriticidad.ALTO: '🟠',
                NivelCriticidad.CRITICO: '🔴',
                NivelCriticidad.INFORMATIVO: '⚪'
            }.get(criticidad, '⚪')
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
        """
        Obtiene un resumen del estado de seguridad basado en eventos.
        
        Returns:
            Diccionario con el resumen de seguridad
        """
        ahora = datetime.now()
        hace_24h = ahora - timedelta(hours=24)
        hace_1h = ahora - timedelta(hours=1)
        
        # Eventos recientes
        eventos_24h = [e for e in self.eventos if e.timestamp >= hace_24h]
        eventos_1h = [e for e in self.eventos if e.timestamp >= hace_1h]
        
        # Contar eventos críticos y altos
        criticos_24h = len([e for e in eventos_24h if e.nivel_criticidad == NivelCriticidad.CRITICO])
        altos_24h = len([e for e in eventos_24h if e.nivel_criticidad == NivelCriticidad.ALTO])
        
        # Calcular nivel de amenaza
        if criticos_24h > 5 or altos_24h > 10:
            nivel_amenaza = "CRÍTICO"
        elif criticos_24h > 0 or altos_24h > 5:
            nivel_amenaza = "ALTO"
        elif altos_24h > 0 or len(eventos_1h) > 20:
            nivel_amenaza = "MEDIO"
        else:
            nivel_amenaza = "BAJO"
        
        # Patrones detectados
        patrones_recientes = self.obtener_patrones_detectados(10)
        
        # Estadísticas de correlación
        stats_correlacion = self.motor_correlacion.obtener_estadisticas()
        
        return {
            'nivel_amenaza': nivel_amenaza,
            'eventos_ultima_hora': len(eventos_1h),
            'eventos_ultimas_24h': len(eventos_24h),
            'eventos_criticos_24h': criticos_24h,
            'eventos_altos_24h': altos_24h,
            'patrones_detectados': len(patrones_recientes),
            'eventos_correlacionados': stats_correlacion['eventos_correlacionados'],
            'reglas_activas': stats_correlacion['reglas_activas'],
            'timestamp_analisis': ahora.isoformat(),
            'recomendaciones': self._generar_recomendaciones_seguridad(nivel_amenaza, criticos_24h, altos_24h)
        }
    
    def _generar_recomendaciones_seguridad(self, nivel_amenaza: str, criticos: int, altos: int) -> List[str]:
        """Genera recomendaciones basadas en el estado de seguridad."""
        recomendaciones = []
        
        if nivel_amenaza == "CRÍTICO":
            recomendaciones.extend([
                "🚨 Revisión inmediata del sistema requerida",
                "🔒 Considerar aislar sistemas comprometidos",
                "📞 Notificar al equipo de respuesta a incidentes",
                "📊 Ejecutar análisis forense completo"
            ])
        elif nivel_amenaza == "ALTO":
            recomendaciones.extend([
                "⚠️ Monitoreo intensivo recomendado",
                "🔍 Revisar logs de eventos críticos",
                "🛡️ Verificar configuraciones de seguridad",
                "📋 Actualizar reglas de detección"
            ])
        elif nivel_amenaza == "MEDIO":
            recomendaciones.extend([
                "👀 Mantener vigilancia de eventos",
                "🔄 Revisar patrones de actividad",
                "📈 Monitorear tendencias de amenazas"
            ])
        else:
            recomendaciones.extend([
                "✅ Sistema operando normalmente",
                "🔄 Continuar monitoreo rutinario",
                "📅 Programar revisión periódica"
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
