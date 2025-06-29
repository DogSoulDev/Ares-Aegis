#!/usr/bin/env python3
"""
Sistema SIEM - Ares Aegis
Centralización y gestión de eventos de seguridad

Autor: DogSoulDev
Versión: 2.0.0
"""

import json
import logging
import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional


class TipoEvento:
    """Constantes para los tipos de eventos del SIEM."""
    ESCANEO = "ESCANEO"
    AMENAZA_DETECTADA = "AMENAZA_DETECTADA"
    ARCHIVO_CUARENTENA = "ARCHIVO_CUARENTENA"
    INTEGRIDAD_ARCHIVO = "INTEGRIDAD_ARCHIVO"
    PROCESO_SOSPECHOSO = "PROCESO_SOSPECHOSO"
    RED_ACTIVIDAD = "RED_ACTIVIDAD"
    SISTEMA_EVENTO = "SISTEMA_EVENTO"
    ERROR = "ERROR"
    ADVERTENCIA = "ADVERTENCIA"
    INFO = "INFO"
    GUI_ACCION = "GUI_ACCION"


class Evento:
    """Clase para representar un evento individual del SIEM."""
    
    def __init__(self, tipo: str, mensaje: str, detalles: Optional[Dict[str, Any]] = None):
        """
        Inicializa un nuevo evento.
        
        Args:
            tipo: Tipo del evento (usar constantes de TipoEvento)
            mensaje: Descripción del evento
            detalles: Información adicional del evento (opcional)
        """
        self.timestamp = datetime.datetime.now()
        self.tipo = tipo
        self.mensaje = mensaje
        self.detalles = detalles or {}
        self.id_evento = self._generar_id_evento()
    
    def _generar_id_evento(self) -> str:
        """Genera un ID único para el evento."""
        return f"{self.timestamp.strftime('%Y%m%d%H%M%S')}-{hash(self.mensaje) % 10000:04d}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el evento a diccionario para serialización."""
        return {
            "id": self.id_evento,
            "timestamp": self.timestamp.isoformat(),
            "tipo": self.tipo,
            "mensaje": self.mensaje,
            "detalles": self.detalles
        }
    
    def __str__(self) -> str:
        """Representación en string del evento."""
        timestamp_str = self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        return f"[{timestamp_str}] {self.tipo}: {self.mensaje}"


class SIEM:
    """Sistema de Información y Gestión de Eventos."""
    
    def __init__(self, archivo_eventos: Optional[Path] = None):
        """
        Inicializa el SIEM.
        
        Args:
            archivo_eventos: Ruta del archivo para persistir eventos
        """
        self.logger = logging.getLogger(__name__)
        
        # Configurar archivo de eventos
        if archivo_eventos is None:
            try:
                eventos_dir = Path("/var/log/ares_aegis")
                eventos_dir.mkdir(parents=True, exist_ok=True)
                self.archivo_eventos = eventos_dir / "eventos_siem.json"
            except PermissionError:
                # Fallback para desarrollo
                eventos_dir = Path.home() / ".ares_aegis"
                eventos_dir.mkdir(exist_ok=True)
                self.archivo_eventos = eventos_dir / "eventos_siem.json"
        else:
            self.archivo_eventos = archivo_eventos
        
        self.eventos: List[Evento] = []
        self._cargar_eventos()
        
        self.logger.info(f"SIEM inicializado. Archivo de eventos: {self.archivo_eventos}")
    
    def log_evento(self, tipo: str, mensaje: str, detalles: Optional[Dict[str, Any]] = None) -> str:
        """
        Registra un nuevo evento en el SIEM.
        
        Args:
            tipo: Tipo del evento
            mensaje: Descripción del evento
            detalles: Información adicional (opcional)
            
        Returns:
            ID del evento registrado
        """
        evento = Evento(tipo, mensaje, detalles)
        self.eventos.append(evento)
        
        # Log también en el sistema de logging estándar
        if tipo == TipoEvento.ERROR:
            self.logger.error(f"{mensaje} | Detalles: {detalles}")
        elif tipo == TipoEvento.ADVERTENCIA:
            self.logger.warning(f"{mensaje} | Detalles: {detalles}")
        else:
            self.logger.info(f"{mensaje} | Detalles: {detalles}")
        
        # Persistir eventos
        self._guardar_eventos()
        
        return evento.id_evento
    
    def obtener_eventos(self, tipo_filtro: Optional[str] = None, 
                       limite: Optional[int] = None) -> List[Evento]:
        """
        Obtiene eventos del SIEM con filtros opcionales.
        
        Args:
            tipo_filtro: Filtrar por tipo de evento (opcional)
            limite: Número máximo de eventos a retornar (opcional)
            
        Returns:
            Lista de eventos filtrados
        """
        eventos_filtrados = self.eventos
        
        if tipo_filtro:
            eventos_filtrados = [e for e in eventos_filtrados if e.tipo == tipo_filtro]
        
        # Ordenar por timestamp descendente (más recientes primero)
        eventos_filtrados.sort(key=lambda x: x.timestamp, reverse=True)
        
        if limite:
            eventos_filtrados = eventos_filtrados[:limite]
        
        return eventos_filtrados
    
    def obtener_eventos_markdown(self, tipo_filtro: Optional[str] = None, 
                                limite: Optional[int] = None) -> str:
        """
        Obtiene eventos formateados en Markdown.
        
        Args:
            tipo_filtro: Filtrar por tipo de evento (opcional)
            limite: Número máximo de eventos a retornar (opcional)
            
        Returns:
            String formateado en Markdown con los eventos
        """
        eventos = self.obtener_eventos(tipo_filtro, limite)
        
        markdown = "## Log de Eventos del SIEM\n\n"
        
        if not eventos:
            markdown += "No hay eventos registrados hasta el momento.\n"
            return markdown
        
        markdown += f"**Total de eventos:** {len(eventos)}\n\n"
        
        if tipo_filtro:
            markdown += f"**Filtrado por tipo:** `{tipo_filtro}`\n\n"
        
        markdown += "### Eventos Registrados\n\n"
        
        for evento in eventos:
            markdown += f"#### Evento ID: `{evento.id_evento}`\n\n"
            markdown += f"- **Timestamp:** {evento.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
            markdown += f"- **Tipo:** `{evento.tipo}`\n"
            markdown += f"- **Mensaje:** {evento.mensaje}\n"
            
            if evento.detalles:
                markdown += "- **Detalles:**\n"
                for clave, valor in evento.detalles.items():
                    markdown += f"  - {clave}: `{valor}`\n"
            
            markdown += "\n---\n\n"
        
        return markdown
    
    def limpiar_eventos_antiguos(self, dias: int = 30) -> int:
        """
        Limpia eventos más antiguos que el número de días especificado.
        
        Args:
            dias: Número de días para conservar eventos
            
        Returns:
            Número de eventos eliminados
        """
        fecha_limite = datetime.datetime.now() - datetime.timedelta(days=dias)
        eventos_antes = len(self.eventos)
        
        self.eventos = [e for e in self.eventos if e.timestamp > fecha_limite]
        eventos_eliminados = eventos_antes - len(self.eventos)
        
        if eventos_eliminados > 0:
            self._guardar_eventos()
            self.log_evento(TipoEvento.SISTEMA_EVENTO, 
                          f"Limpieza automática: {eventos_eliminados} eventos eliminados")
        
        return eventos_eliminados
    
    def _cargar_eventos(self):
        """Carga eventos desde el archivo de persistencia."""
        try:
            if self.archivo_eventos.exists():
                with open(self.archivo_eventos, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
                    
                for dato_evento in datos:
                    evento = Evento(dato_evento['tipo'], dato_evento['mensaje'], 
                                  dato_evento.get('detalles', {}))
                    evento.timestamp = datetime.datetime.fromisoformat(dato_evento['timestamp'])
                    evento.id_evento = dato_evento['id']
                    self.eventos.append(evento)
                
                self.logger.info(f"Cargados {len(self.eventos)} eventos desde archivo")
        except Exception as e:
            self.logger.error(f"Error al cargar eventos: {e}")
    
    def _guardar_eventos(self):
        """Guarda eventos en el archivo de persistencia."""
        try:
            with open(self.archivo_eventos, 'w', encoding='utf-8') as f:
                datos = [evento.to_dict() for evento in self.eventos]
                json.dump(datos, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"Error al guardar eventos: {e}")
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de los eventos registrados.
        
        Returns:
            Diccionario con estadísticas de eventos
        """
        total_eventos = len(self.eventos)
        
        if total_eventos == 0:
            return {"total": 0}
        
        # Contar eventos por tipo
        conteo_tipos = {}
        for evento in self.eventos:
            conteo_tipos[evento.tipo] = conteo_tipos.get(evento.tipo, 0) + 1
        
        # Evento más reciente y más antiguo
        timestamps = [e.timestamp for e in self.eventos]
        evento_mas_reciente = max(timestamps)
        evento_mas_antiguo = min(timestamps)
        
        return {
            "total": total_eventos,
            "por_tipo": conteo_tipos,
            "evento_mas_reciente": evento_mas_reciente.isoformat(),
            "evento_mas_antiguo": evento_mas_antiguo.isoformat(),
            "archivo_eventos": str(self.archivo_eventos)
        }
