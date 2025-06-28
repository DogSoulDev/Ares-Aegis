"""
Motor de correlación de eventos para el Mini-SIEM
Implementa reglas de detección de amenazas y correlación de eventos de seguridad
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any, Union
from dataclasses import dataclass
from collections import defaultdict, deque
import re
import json
from enum import Enum

logger = logging.getLogger(__name__)

class SeveridadAlerta(Enum):
    """Niveles de severidad para alertas"""
    INFO = "INFO"
    WARNING = "WARNING"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

@dataclass
class Alerta:
    """Estructura de una alerta de seguridad"""
    id: str
    titulo: str
    descripcion: str
    severidad: SeveridadAlerta
    categoria: str
    eventos_relacionados: List[Dict]
    timestamp: datetime
    acciones_recomendadas: List[str]
    datos_adicionales: Dict[str, Any]

class ReglaCorrelacion:
    """Clase base para reglas de correlación"""
    
    def __init__(self, nombre: str, descripcion: str, severidad: SeveridadAlerta):
        self.nombre = nombre
        self.descripcion = descripcion
        self.severidad = severidad
        self.eventos_ventana = deque(maxlen=1000)  # Ventana deslizante de eventos
        self.contador_coincidencias = defaultdict(int)
        
    def evaluar(self, evento: Dict) -> Optional[Alerta]:
        """Evaluar evento contra la regla"""
        raise NotImplementedError
        
    def reset(self):
        """Resetear estado de la regla"""
        self.eventos_ventana.clear()
        self.contador_coincidencias.clear()

class ReglaUmbral(ReglaCorrelacion):
    """Regla basada en umbral de eventos"""
    
    def __init__(self, nombre: str, descripcion: str, severidad: SeveridadAlerta,
                 umbral: int, ventana_tiempo: int, campo_agrupacion: Optional[str] = None,
                 filtros: Optional[Dict] = None):
        super().__init__(nombre, descripcion, severidad)
        self.umbral = umbral
        self.ventana_tiempo = ventana_tiempo  # segundos
        self.campo_agrupacion = campo_agrupacion
        self.filtros = filtros or {}
        self.grupos_eventos = defaultdict(deque)
        
    def evaluar(self, evento: Dict) -> Optional[Alerta]:
        """Evaluar evento contra umbral"""
        # Verificar si el evento cumple los filtros
        if not self._cumple_filtros(evento):
            return None
            
        ahora = datetime.now()
        timestamp_evento = self._parsear_timestamp(evento.get('timestamp'))
        
        # Determinar clave de agrupación
        if self.campo_agrupacion:
            clave_grupo = str(evento.get(self.campo_agrupacion, 'default'))
        else:
            clave_grupo = 'default'
            
        # Agregar evento al grupo
        self.grupos_eventos[clave_grupo].append({
            'evento': evento,
            'timestamp': timestamp_evento
        })
        
        # Limpiar eventos fuera de la ventana de tiempo
        self._limpiar_eventos_antiguos(clave_grupo, ahora)
        
        # Verificar si se alcanzó el umbral
        if len(self.grupos_eventos[clave_grupo]) >= self.umbral:
            return self._crear_alerta_umbral(clave_grupo)
            
        return None
        
    def _cumple_filtros(self, evento: Dict) -> bool:
        """Verificar si evento cumple filtros de la regla"""
        for campo, valor_esperado in self.filtros.items():
            valor_evento = evento.get(campo)
            if isinstance(valor_esperado, str):
                if valor_evento != valor_esperado:
                    return False
            elif isinstance(valor_esperado, list):
                if valor_evento not in valor_esperado:
                    return False
            elif isinstance(valor_esperado, dict) and 'regex' in valor_esperado:
                if not re.search(valor_esperado['regex'], str(valor_evento or '')):
                    return False
        return True
        
    def _parsear_timestamp(self, timestamp_str: Union[str, None]) -> datetime:
        """Parsear timestamp del evento"""
        if not timestamp_str:
            return datetime.now()
        try:
            if timestamp_str.endswith('Z'):
                return datetime.fromisoformat(timestamp_str[:-1])
            return datetime.fromisoformat(timestamp_str)
        except:
            return datetime.now()
            
    def _limpiar_eventos_antiguos(self, clave_grupo: str, ahora: datetime):
        """Limpiar eventos fuera de la ventana de tiempo"""
        ventana_limite = ahora - timedelta(seconds=self.ventana_tiempo)
        
        while (self.grupos_eventos[clave_grupo] and 
               self.grupos_eventos[clave_grupo][0]['timestamp'] < ventana_limite):
            self.grupos_eventos[clave_grupo].popleft()
            
    def _crear_alerta_umbral(self, clave_grupo: str) -> Alerta:
        """Crear alerta cuando se alcanza el umbral"""
        eventos = [item['evento'] for item in self.grupos_eventos[clave_grupo]]
        
        return Alerta(
            id=f"{self.nombre}_{clave_grupo}_{datetime.now().isoformat()}",
            titulo=f"{self.nombre} - Umbral Alcanzado",
            descripcion=f"{self.descripcion}. Detectados {len(eventos)} eventos en {self.ventana_tiempo} segundos.",
            severidad=self.severidad,
            categoria="threshold_detection",
            eventos_relacionados=eventos,
            timestamp=datetime.now(),
            acciones_recomendadas=[
                "Revisar los eventos relacionados",
                "Verificar la legitimidad de la actividad",
                "Considerar bloquear la fuente si es maliciosa"
            ],
            datos_adicionales={
                'umbral': self.umbral,
                'eventos_detectados': len(eventos),
                'ventana_tiempo': self.ventana_tiempo,
                'campo_agrupacion': self.campo_agrupacion,
                'grupo': clave_grupo
            }
        )

class ReglaSecuencial(ReglaCorrelacion):
    """Regla para detectar secuencias de eventos"""
    
    def __init__(self, nombre: str, descripcion: str, severidad: SeveridadAlerta,
                 secuencia_eventos: List[Dict], ventana_tiempo: int,
                 campo_agrupacion: Optional[str] = None):
        super().__init__(nombre, descripcion, severidad)
        self.secuencia_eventos = secuencia_eventos
        self.ventana_tiempo = ventana_tiempo
        self.campo_agrupacion = campo_agrupacion
        self.secuencias_parciales = defaultdict(list)
        
    def evaluar(self, evento: Dict) -> Optional[Alerta]:
        """Evaluar evento contra secuencia"""
        # Determinar clave de agrupación
        if self.campo_agrupacion:
            clave_grupo = str(evento.get(self.campo_agrupacion, 'default'))
        else:
            clave_grupo = 'default'
            
        ahora = datetime.now()
        timestamp_evento = self._parsear_timestamp(evento.get('timestamp'))
        
        # Limpiar secuencias antiguas
        self._limpiar_secuencias_antiguas(clave_grupo, ahora)
        
        # Verificar si el evento coincide con algún paso de la secuencia
        for i, paso_secuencia in enumerate(self.secuencia_eventos):
            if self._evento_coincide_paso(evento, paso_secuencia):
                # Agregar evento a secuencias parciales
                self._agregar_a_secuencia_parcial(clave_grupo, i, evento, timestamp_evento)
                
                # Verificar si se completó la secuencia
                if self._secuencia_completada(clave_grupo):
                    return self._crear_alerta_secuencial(clave_grupo)
                    
        return None
        
    def _evento_coincide_paso(self, evento: Dict, paso: Dict) -> bool:
        """Verificar si evento coincide con paso de secuencia"""
        for campo, valor_esperado in paso.items():
            if evento.get(campo) != valor_esperado:
                return False
        return True
        
    def _agregar_a_secuencia_parcial(self, clave_grupo: str, paso: int, 
                                   evento: Dict, timestamp: datetime):
        """Agregar evento a secuencia parcial"""
        if clave_grupo not in self.secuencias_parciales:
            self.secuencias_parciales[clave_grupo] = []
            
        # Buscar secuencia existente donde agregar este paso
        for secuencia in self.secuencias_parciales[clave_grupo]:
            if len(secuencia) == paso:
                secuencia.append({
                    'evento': evento,
                    'timestamp': timestamp,
                    'paso': paso
                })
                return
                
        # Si es el primer paso, crear nueva secuencia
        if paso == 0:
            self.secuencias_parciales[clave_grupo].append([{
                'evento': evento,
                'timestamp': timestamp,
                'paso': paso
            }])
            
    def _secuencia_completada(self, clave_grupo: str) -> bool:
        """Verificar si alguna secuencia se completó"""
        for secuencia in self.secuencias_parciales[clave_grupo]:
            if len(secuencia) == len(self.secuencia_eventos):
                return True
        return False
        
    def _limpiar_secuencias_antiguas(self, clave_grupo: str, ahora: datetime):
        """Limpiar secuencias fuera de ventana de tiempo"""
        if clave_grupo not in self.secuencias_parciales:
            return
            
        ventana_limite = ahora - timedelta(seconds=self.ventana_tiempo)
        
        # Filtrar secuencias que tienen eventos dentro de la ventana
        secuencias_validas = []
        for secuencia in self.secuencias_parciales[clave_grupo]:
            if any(item['timestamp'] >= ventana_limite for item in secuencia):
                secuencias_validas.append(secuencia)
                
        self.secuencias_parciales[clave_grupo] = secuencias_validas
        
    def _crear_alerta_secuencial(self, clave_grupo: str) -> Alerta:
        """Crear alerta para secuencia completada"""
        # Encontrar secuencia completada
        secuencia_completada = None
        for secuencia in self.secuencias_parciales[clave_grupo]:
            if len(secuencia) == len(self.secuencia_eventos):
                secuencia_completada = secuencia
                break
                
        if not secuencia_completada:
            # Fallback - usar la primera secuencia disponible
            secuencia_completada = self.secuencias_parciales[clave_grupo][0] if self.secuencias_parciales[clave_grupo] else []
        
        eventos = [item['evento'] for item in secuencia_completada]
        
        return Alerta(
            id=f"{self.nombre}_{clave_grupo}_{datetime.now().isoformat()}",
            titulo=f"{self.nombre} - Secuencia Detectada",
            descripcion=f"{self.descripcion}. Secuencia de {len(eventos)} eventos completada.",
            severidad=self.severidad,
            categoria="sequence_detection",
            eventos_relacionados=eventos,
            timestamp=datetime.now(),
            acciones_recomendadas=[
                "Analizar la secuencia de eventos completa",
                "Verificar si la actividad es legítima",
                "Investigar posible actividad maliciosa"
            ],
            datos_adicionales={
                'secuencia_eventos': self.secuencia_eventos,
                'eventos_detectados': len(eventos),
                'ventana_tiempo': self.ventana_tiempo,
                'grupo': clave_grupo
            }
        )
        
    def _parsear_timestamp(self, timestamp_str: Union[str, None]) -> datetime:
        """Parsear timestamp del evento"""
        if not timestamp_str:
            return datetime.now()
        try:
            if timestamp_str.endswith('Z'):
                return datetime.fromisoformat(timestamp_str[:-1])
            return datetime.fromisoformat(timestamp_str)
        except:
            return datetime.now()

class MotorCorrelacion:
    """Motor principal de correlación de eventos"""
    
    def __init__(self):
        self.reglas: List[ReglaCorrelacion] = []
        self.callbacks_alerta: List[Callable] = []
        self.estadisticas = {
            'eventos_procesados': 0,
            'alertas_generadas': 0,
            'reglas_activas': 0
        }
        
        # Cargar reglas predefinidas para Kali Linux
        self._cargar_reglas_predefinidas()
        
    def agregar_regla(self, regla: ReglaCorrelacion):
        """Agregar regla de correlación"""
        self.reglas.append(regla)
        self.estadisticas['reglas_activas'] = len(self.reglas)
        logger.info(f"Regla agregada: {regla.nombre}")
        
    def remover_regla(self, nombre_regla: str):
        """Remover regla por nombre"""
        self.reglas = [r for r in self.reglas if r.nombre != nombre_regla]
        self.estadisticas['reglas_activas'] = len(self.reglas)
        logger.info(f"Regla removida: {nombre_regla}")
        
    def agregar_callback_alerta(self, callback: Callable):
        """Agregar callback para alertas"""
        self.callbacks_alerta.append(callback)
        
    async def procesar_evento(self, evento: Dict):
        """Procesar evento contra todas las reglas"""
        self.estadisticas['eventos_procesados'] += 1
        
        for regla in self.reglas:
            try:
                alerta = regla.evaluar(evento)
                if alerta:
                    await self._enviar_alerta(alerta)
            except Exception as e:
                logger.error(f"Error procesando regla {regla.nombre}: {e}")
                
    async def _enviar_alerta(self, alerta: Alerta):
        """Enviar alerta a todos los callbacks"""
        self.estadisticas['alertas_generadas'] += 1
        logger.warning(f"ALERTA: {alerta.titulo} - {alerta.severidad.value}")
        
        for callback in self.callbacks_alerta:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(alerta)
                else:
                    callback(alerta)
            except Exception as e:
                logger.error(f"Error en callback de alerta: {e}")
                
    def _cargar_reglas_predefinidas(self):
        """Cargar reglas predefinidas para detección de amenazas comunes"""
        
        # Regla: Detección de fuerza bruta SSH
        regla_fuerza_bruta = ReglaUmbral(
            nombre="ssh_brute_force",
            descripcion="Detección de ataque de fuerza bruta SSH",
            severidad=SeveridadAlerta.HIGH,
            umbral=5,
            ventana_tiempo=300,  # 5 minutos
            campo_agrupacion="source.ip",
            filtros={
                "event.category": "authentication",
                "event.type": "failed_password"
            }
        )
        self.agregar_regla(regla_fuerza_bruta)
        
        # Regla: Escalada de privilegios
        regla_escalada = ReglaSecuencial(
            nombre="privilege_escalation",
            descripcion="Intento de escalada de privilegios",
            severidad=SeveridadAlerta.CRITICAL,
            secuencia_eventos=[
                {"event.category": "authentication", "event.type": "login_success"},
                {"event.category": "process", "process.name": "sudo"}
            ],
            ventana_tiempo=60,  # 1 minuto
            campo_agrupacion="user.name"
        )
        self.agregar_regla(regla_escalada)
        
        # Regla: Instalación de software sospechoso
        regla_software_sospechoso = ReglaUmbral(
            nombre="suspicious_package_install",
            descripcion="Instalación masiva de paquetes no autorizados",
            severidad=SeveridadAlerta.WARNING,
            umbral=10,
            ventana_tiempo=1800,  # 30 minutos
            filtros={
                "event.category": "package",
                "event.type": "package_install"
            }
        )
        self.agregar_regla(regla_software_sospechoso)
        
        # Regla: Actividad de red sospechosa
        regla_escaneo_red = ReglaUmbral(
            nombre="network_scanning",
            descripcion="Posible escaneo de red o actividad masiva de conexiones",
            severidad=SeveridadAlerta.WARNING,
            umbral=50,
            ventana_tiempo=300,  # 5 minutos
            campo_agrupacion="source.ip",
            filtros={
                "event.category": "network"
            }
        )
        self.agregar_regla(regla_escaneo_red)
        
        # Regla: Fallos de autenticación masivos
        regla_auth_masivo = ReglaUmbral(
            nombre="mass_auth_failures",
            descripcion="Fallos masivos de autenticación desde múltiples fuentes",
            severidad=SeveridadAlerta.HIGH,
            umbral=20,
            ventana_tiempo=600,  # 10 minutos
            filtros={
                "event.category": "authentication",
                "action": "failed"
            }
        )
        self.agregar_regla(regla_auth_masivo)
        
        logger.info(f"Cargadas {len(self.reglas)} reglas predefinidas")
        
    def obtener_estadisticas(self) -> Dict:
        """Obtener estadísticas del motor de correlación"""
        return {
            **self.estadisticas,
            'reglas_configuradas': [
                {
                    'nombre': regla.nombre,
                    'descripcion': regla.descripcion,
                    'severidad': regla.severidad.value,
                    'tipo': regla.__class__.__name__
                }
                for regla in self.reglas
            ]
        }
        
    def cargar_reglas_desde_archivo(self, archivo_config: str):
        """Cargar reglas desde archivo de configuración JSON"""
        try:
            with open(archivo_config, 'r', encoding='utf-8') as f:
                config = json.load(f)
                    
            for regla_config in config.get('reglas', []):
                regla = self._crear_regla_desde_config(regla_config)
                if regla:
                    self.agregar_regla(regla)
                    
        except Exception as e:
            logger.error(f"Error cargando reglas desde archivo: {e}")
            
    def _crear_regla_desde_config(self, config: Dict) -> Optional[ReglaCorrelacion]:
        """Crear regla desde configuración"""
        try:
            tipo_regla = config.get('tipo', 'umbral')
            severidad = SeveridadAlerta(config.get('severidad', 'WARNING'))
            
            if tipo_regla == 'umbral':
                return ReglaUmbral(
                    nombre=config['nombre'],
                    descripcion=config['descripcion'],
                    severidad=severidad,
                    umbral=config['umbral'],
                    ventana_tiempo=config['ventana_tiempo'],
                    campo_agrupacion=config.get('campo_agrupacion'),
                    filtros=config.get('filtros', {})
                )
            elif tipo_regla == 'secuencial':
                return ReglaSecuencial(
                    nombre=config['nombre'],
                    descripcion=config['descripcion'],
                    severidad=severidad,
                    secuencia_eventos=config['secuencia_eventos'],
                    ventana_tiempo=config['ventana_tiempo'],
                    campo_agrupacion=config.get('campo_agrupacion')
                )
        except Exception as e:
            logger.error(f"Error creando regla desde config: {e}")
            
        return None
        
    def reset_estadisticas(self):
        """Reset estadísticas del motor"""
        self.estadisticas = {
            'eventos_procesados': 0,
            'alertas_generadas': 0,
            'reglas_activas': len(self.reglas)
        }
        
        # Reset estado de todas las reglas
        for regla in self.reglas:
            regla.reset()
