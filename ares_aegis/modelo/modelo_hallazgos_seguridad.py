#!/usr/bin/env python3
"""
Creado por DogSoulDev (https://github.com/DogSoulDev)
Todos los derechos reservados. Este código es propietario y confidencial.

Modelos de Datos para Hallazgos de Seguridad - Ares Aegis
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pathlib import Path


class TipoHallazgo(Enum):
    """Tipos de hallazgos de seguridad."""
    CONFIGURACION_INSEGURA = "configuracion_insegura"
    PERMISOS_INCORRECTOS = "permisos_incorrectos"
    SERVICIO_EXPUESTO = "servicio_expuesto"
    AUTENTICACION_DEBIL = "autenticacion_debil"
    ARCHIVO_SOSPECHOSO = "archivo_sospechoso"
    VULNERABILIDAD_SISTEMA = "vulnerabilidad_sistema"
    MALWARE_DETECTADO = "malware_detectado"
    IOC_DETECTADO = "ioc_detectado"
    INFORMATIVO = "informativo"


class PrioridadHallazgo(Enum):
    """Prioridades de los hallazgos."""
    CRITICA = "critica"
    ALTA = "alta"
    MEDIA = "media"
    BAJA = "baja"
    INFORMATIVA = "informativa"


class EstadoHallazgo(Enum):
    """Estados posibles de un hallazgo."""
    DETECTADO = "detectado"
    VERIFICADO = "verificado"
    EN_PROCESO = "en_proceso"
    RESUELTO = "resuelto"
    FALSO_POSITIVO = "falso_positivo"
    IGNORADO = "ignorado"


@dataclass
class Hallazgo:
    """
    Clase base para representar un hallazgo de seguridad.
    
    Atributos:
        tipo_anomalia: Tipo específico del hallazgo
        ruta_afectada: Ruta del archivo/directorio afectado
        detalle_especifico: Descripción detallada del problema
        prioridad: Nivel de prioridad del hallazgo
        recomendacion: Recomendación para resolver el problema
        fecha_deteccion: Timestamp de cuando se detectó
        estado: Estado actual del hallazgo
        metadatos: Información adicional específica del hallazgo
    """
    tipo_anomalia: TipoHallazgo
    ruta_afectada: str
    detalle_especifico: str
    prioridad: PrioridadHallazgo
    recomendacion: str
    fecha_deteccion: datetime
    estado: EstadoHallazgo = EstadoHallazgo.DETECTADO
    metadatos: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validaciones post-inicialización."""
        if not self.ruta_afectada:
            raise ValueError("La ruta afectada no puede estar vacía")
        if not self.detalle_especifico:
            raise ValueError("El detalle específico no puede estar vacío")
        if not self.recomendacion:
            raise ValueError("La recomendación no puede estar vacía")
        if self.metadatos is None:
            self.metadatos = {}
    
    def es_critico(self) -> bool:
        """Verifica si el hallazgo es de prioridad crítica."""
        return self.prioridad == PrioridadHallazgo.CRITICA
    
    def requiere_cuarentena(self) -> bool:
        """Determina si este hallazgo requiere cuarentena del archivo."""
        tipos_cuarentena = {
            TipoHallazgo.MALWARE_DETECTADO,
            TipoHallazgo.ARCHIVO_SOSPECHOSO
        }
        return (self.tipo_anomalia in tipos_cuarentena and 
                self.prioridad in [PrioridadHallazgo.CRITICA, PrioridadHallazgo.ALTA])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el hallazgo a diccionario para serialización."""
        return {
            'tipo_anomalia': self.tipo_anomalia.value,
            'ruta_afectada': self.ruta_afectada,
            'detalle_especifico': self.detalle_especifico,
            'prioridad': self.prioridad.value,
            'recomendacion': self.recomendacion,
            'fecha_deteccion': self.fecha_deteccion.isoformat(),
            'estado': self.estado.value,
            'metadatos': self.metadatos or {}
        }


@dataclass
class HallazgoAutenticacion(Hallazgo):
    """Hallazgo específico para problemas de autenticación PAM."""
    
    def __post_init__(self):
        """Validaciones específicas para autenticación."""
        super().__post_init__()
        
        # Los hallazgos de autenticación nunca deben cuarentenarse
        if not self.metadatos:
            self.metadatos = {}
        self.metadatos['permite_cuarentena'] = False
        self.metadatos['requiere_revision_manual'] = True
    
    def requiere_cuarentena(self) -> bool:
        """Los archivos de configuración de autenticación nunca se cuarentenan."""
        return False


@dataclass 
class HallazgoConfiguracion(Hallazgo):
    """Hallazgo específico para configuraciones inseguras."""
    
    configuracion_actual: str = ""
    configuracion_recomendada: str = ""
    
    def __post_init__(self):
        """Validaciones específicas para configuraciones."""
        super().__post_init__()
        
        if not self.metadatos:
            self.metadatos = {}
        self.metadatos['configuracion_actual'] = self.configuracion_actual
        self.metadatos['configuracion_recomendada'] = self.configuracion_recomendada
        self.metadatos['permite_cuarentena'] = False


@dataclass
class HallazgoPermisos(Hallazgo):
    """Hallazgo específico para problemas de permisos."""
    
    permisos_actuales: str = ""
    permisos_recomendados: str = ""
    propietario_actual: str = ""
    propietario_recomendado: str = ""
    
    def __post_init__(self):
        """Validaciones específicas para permisos."""
        super().__post_init__()
        
        if not self.metadatos:
            self.metadatos = {}
        self.metadatos.update({
            'permisos_actuales': self.permisos_actuales,
            'permisos_recomendados': self.permisos_recomendados,
            'propietario_actual': self.propietario_actual,
            'propietario_recomendado': self.propietario_recomendado,
            'permite_cuarentena': False
        })


@dataclass
class ResultadoEscaneo:
    """
    Resultado completo de un escaneo de seguridad.
    
    Atributos:
        hallazgos: Lista de todos los hallazgos detectados
        timestamp_inicio: Cuándo comenzó el escaneo
        timestamp_fin: Cuándo terminó el escaneo
        rutas_escaneadas: Rutas que fueron analizadas
        estadisticas: Estadísticas del escaneo
        metadatos: Información adicional del escaneo
    """
    hallazgos: List[Hallazgo]
    timestamp_inicio: datetime
    timestamp_fin: datetime
    rutas_escaneadas: List[str]
    estadisticas: Dict[str, Any]
    metadatos: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validaciones post-inicialización."""
        if self.metadatos is None:
            self.metadatos = {}
    
    @property
    def duracion_escaneo(self) -> float:
        """Duración del escaneo en segundos."""
        return (self.timestamp_fin - self.timestamp_inicio).total_seconds()
    
    @property
    def total_hallazgos(self) -> int:
        """Total de hallazgos detectados."""
        return len(self.hallazgos)
    
    @property
    def hallazgos_criticos(self) -> List[Hallazgo]:
        """Filtra solo los hallazgos críticos."""
        return [h for h in self.hallazgos if h.prioridad == PrioridadHallazgo.CRITICA]
    
    @property
    def hallazgos_por_tipo(self) -> Dict[TipoHallazgo, int]:
        """Cuenta hallazgos por tipo."""
        conteo = {}
        for hallazgo in self.hallazgos:
            conteo[hallazgo.tipo_anomalia] = conteo.get(hallazgo.tipo_anomalia, 0) + 1
        return conteo
    
    @property
    def hallazgos_por_prioridad(self) -> Dict[PrioridadHallazgo, int]:
        """Cuenta hallazgos por prioridad."""
        conteo = {}
        for hallazgo in self.hallazgos:
            conteo[hallazgo.prioridad] = conteo.get(hallazgo.prioridad, 0) + 1
        return conteo
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el resultado a diccionario para serialización."""
        return {
            'hallazgos': [h.to_dict() for h in self.hallazgos],
            'timestamp_inicio': self.timestamp_inicio.isoformat(),
            'timestamp_fin': self.timestamp_fin.isoformat(),
            'duracion_segundos': self.duracion_escaneo,
            'rutas_escaneadas': self.rutas_escaneadas,
            'estadisticas': self.estadisticas,
            'metadatos': self.metadatos or {},
            'resumen': {
                'total_hallazgos': self.total_hallazgos,
                'hallazgos_por_tipo': {k.value: v for k, v in self.hallazgos_por_tipo.items()},
                'hallazgos_por_prioridad': {k.value: v for k, v in self.hallazgos_por_prioridad.items()}
            }
        }
