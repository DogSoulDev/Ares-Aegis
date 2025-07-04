#!/usr/bin/env python3
"""
Copyright (c) 2025 DogSoulDev (https://github.com/DogSoulDev)
Todos los derechos reservados. Este código es propietario y confidencial.

SIEM - Sistema de Información y Gestión de Eventos
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from ..utilidades.ayuda_logging import configurar_logger_modulo
from ..utilidades.ayuda_rutas import crear_ruta_segura


class TipoEvento:
    """Constantes para tipos de eventos del SIEM."""
    ESCANEO_INICIADO = "ESCANEO_INICIADO"
    ESCANEO_FINALIZADO = "ESCANEO_FINALIZADO"
    AMENAZA_DETECTADA = "AMENAZA_DETECTADA"
    ARCHIVO_CUARENTENA = "ARCHIVO_CUARENTENA"
    ARCHIVO_RESTAURADO = "ARCHIVO_RESTAURADO"
    INTEGRIDAD_VIOLADA = "INTEGRIDAD_VIOLADA"
    CONEXION_SOSPECHOSA = "CONEXION_SOSPECHOSA"
    PROCESO_SOSPECHOSO = "PROCESO_SOSPECHOSO"
    VULNERABILIDAD_DETECTADA = "VULNERABILIDAD_DETECTADA"
    SISTEMA_INICIADO = "SISTEMA_INICIADO"
    SISTEMA_DETENIDO = "SISTEMA_DETENIDO"
    ERROR_SISTEMA = "ERROR_SISTEMA"
    ADVERTENCIA = "ADVERTENCIA"
    INFORMACION = "INFORMACION"
    IP_BLOQUEADA = "IP_BLOQUEADA"


class EventoSIEM:
    """Representa un evento individual del SIEM."""
    
    def __init__(self, tipo: str, mensaje: str, detalles: Optional[Dict[str, Any]] = None,
                 nivel_criticidad: str = "MEDIO"):
        """
        Inicializa un evento del SIEM.
        
        Args:
            tipo: Tipo del evento (usar constantes de TipoEvento)
            mensaje: Descripción del evento
            detalles: Información adicional del evento
            nivel_criticidad: Nivel de criticidad (BAJO, MEDIO, ALTO, CRITICO)
        """
        self.timestamp = datetime.now()
        self.tipo = tipo
        self.mensaje = mensaje
        self.detalles = detalles or {}
        self.nivel_criticidad = nivel_criticidad
        self.id_evento = self._generar_id_evento()
    
    def _generar_id_evento(self) -> str:
        """Genera un ID único para el evento."""
        timestamp_str = self.timestamp.strftime('%Y%m%d%H%M%S')
        hash_mensaje = abs(hash(self.mensaje)) % 10000
        return f"{timestamp_str}-{hash_mensaje:04d}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el evento a diccionario para serialización."""
        return {
            'id': self.id_evento,
            'timestamp': self.timestamp.isoformat(),
            'tipo': self.tipo,
            'mensaje': self.mensaje,
            'detalles': self.detalles,
            'nivel_criticidad': self.nivel_criticidad
        }
    
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


class SIEM:
    """Sistema de Información y Gestión de Eventos."""
    
    def __init__(self, archivo_eventos: Optional[str] = None):
        """
        Inicializa el SIEM.
        
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
        self.max_eventos_memoria = 1000  # Máximo de eventos en memoria
        
        # Cargar eventos existentes
        self._cargar_eventos()
        
        self.logger.info(f"SIEM inicializado. Archivo de eventos: {self.archivo_eventos}")
        
        # Registrar evento de inicio del SIEM
        self.registrar_evento(
            TipoEvento.SISTEMA_INICIADO,
            "SIEM de Ares Aegis iniciado",
            {'archivo_eventos': str(self.archivo_eventos)},
            "MEDIO"
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
                        evento = EventoSIEM(
                            tipo=datos_evento['tipo'],
                            mensaje=datos_evento['mensaje'],
                            detalles=datos_evento.get('detalles', {}),
                            nivel_criticidad=datos_evento.get('nivel_criticidad', 'MEDIO')
                        )
                        # Restaurar timestamp e ID originales
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
                        nivel_criticidad: str = "MEDIO") -> str:
        """
        Registra un nuevo evento en el SIEM.
        
        Args:
            tipo: Tipo del evento
            mensaje: Descripción del evento
            detalles: Información adicional
            nivel_criticidad: Nivel de criticidad
            
        Returns:
            str: ID del evento registrado
        """
        evento = EventoSIEM(tipo, mensaje, detalles, nivel_criticidad)
        
        # Agregar a memoria
        self.eventos.append(evento)
        
        # Mantener límite de eventos en memoria
        if len(self.eventos) > self.max_eventos_memoria:
            self.eventos = self.eventos[-self.max_eventos_memoria:]
        
        # Guardar al archivo
        self._guardar_eventos()
        
        # Log según criticidad
        if nivel_criticidad == "CRITICO":
            self.logger.critical(f"{tipo}: {mensaje}")
        elif nivel_criticidad == "ALTO":
            self.logger.error(f"{tipo}: {mensaje}")
        elif nivel_criticidad == "MEDIO":
            self.logger.warning(f"{tipo}: {mensaje}")
        else:
            self.logger.info(f"{tipo}: {mensaje}")
        
        return evento.id_evento
    
    def obtener_eventos(self, limite: int = 100, 
                       filtro_tipo: Optional[str] = None,
                       filtro_criticidad: Optional[str] = None) -> List[EventoSIEM]:
        """
        Obtiene eventos del SIEM con filtros opcionales.
        
        Args:
            limite: Número máximo de eventos a devolver
            filtro_tipo: Filtrar por tipo de evento
            filtro_criticidad: Filtrar por nivel de criticidad
            
        Returns:
            List[EventoSIEM]: Lista de eventos
        """
        eventos_filtrados = self.eventos.copy()
        
        # Aplicar filtros
        if filtro_tipo:
            eventos_filtrados = [e for e in eventos_filtrados if e.tipo == filtro_tipo]
        
        if filtro_criticidad:
            eventos_filtrados = [e for e in eventos_filtrados if e.nivel_criticidad == filtro_criticidad]
        
        # Ordenar por timestamp descendente y limitar
        eventos_filtrados.sort(key=lambda x: x.timestamp, reverse=True)
        return eventos_filtrados[:limite]
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de los eventos del SIEM.
        
        Returns:
            Dict[str, Any]: Estadísticas de eventos
        """
        total_eventos = len(self.eventos)
        
        # Contar por tipo
        conteo_tipos = {}
        conteo_criticidad = {}
        
        for evento in self.eventos:
            conteo_tipos[evento.tipo] = conteo_tipos.get(evento.tipo, 0) + 1
            conteo_criticidad[evento.nivel_criticidad] = conteo_criticidad.get(evento.nivel_criticidad, 0) + 1
        
        # Eventos de las últimas 24 horas
        ahora = datetime.now()
        hace_24h = ahora.replace(hour=ahora.hour-24) if ahora.hour >= 24 else ahora.replace(day=ahora.day-1, hour=ahora.hour+24-24)
        eventos_24h = [e for e in self.eventos if e.timestamp >= hace_24h]
        
        return {
            'total_eventos': total_eventos,
            'eventos_24h': len(eventos_24h),
            'conteo_por_tipo': conteo_tipos,
            'conteo_por_criticidad': conteo_criticidad,
            'archivo_eventos': self.archivo_eventos
        }
    
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
        
        # Estadísticas
        estadisticas = self.obtener_estadisticas()
        md += "## Estadísticas Generales\n\n"
        md += f"- **Total de Eventos:** {estadisticas['total_eventos']}\n"
        md += f"- **Eventos Últimas 24h:** {estadisticas['eventos_24h']}\n"
        md += f"- **Archivo de Eventos:** {estadisticas['archivo_eventos']}\n\n"
        
        # Conteo por criticidad
        md += "### Distribución por Criticidad\n\n"
        for criticidad, cantidad in estadisticas['conteo_por_criticidad'].items():
            emoji = {
                'BAJO': '🔵',
                'MEDIO': '🟡', 
                'ALTO': '🟠',
                'CRITICO': '🔴'
            }.get(criticidad, '⚪')
            md += f"- {emoji} **{criticidad}:** {cantidad}\n"
        md += "\n"
        
        # Eventos recientes
        eventos_recientes = self.obtener_eventos(limite)
        md += f"## Eventos Recientes (últimos {len(eventos_recientes)})\n\n"
        
        for evento in eventos_recientes:
            md += evento.to_markdown()
            md += "---\n\n"
        
        return md
    
    def limpiar_eventos_antiguos(self, dias: int = 30) -> int:
        """
        Limpia eventos más antiguos que el número de días especificado.
        
        Args:
            dias: Número de días de retención
            
        Returns:
            int: Número de eventos eliminados
        """
        ahora = datetime.now()
        fecha_limite = ahora.replace(day=ahora.day-dias) if ahora.day > dias else ahora.replace(month=ahora.month-1, day=ahora.day+30-dias)
        
        eventos_antes = len(self.eventos)
        self.eventos = [e for e in self.eventos if e.timestamp >= fecha_limite]
        eventos_eliminados = eventos_antes - len(self.eventos)
        
        if eventos_eliminados > 0:
            self._guardar_eventos()
            self.logger.info(f"Limpieza de eventos: {eventos_eliminados} eventos eliminados")
        
        return eventos_eliminados
    
    def exportar_eventos(self, ruta_archivo: str, formato: str = "json") -> bool:
        """
        Exporta eventos a un archivo externo.
        
        Args:
            ruta_archivo: Ruta del archivo destino
            formato: Formato de exportación (json, markdown)
            
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
            
            else:
                self.logger.error(f"Formato de exportación no soportado: {formato}")
                return False
            
            self.logger.info(f"Eventos exportados a {ruta_archivo} en formato {formato}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exportando eventos: {e}")
            return False
    
    def cerrar(self):
        """Cierra el SIEM guardando eventos pendientes."""
        self.registrar_evento(
            TipoEvento.SISTEMA_DETENIDO,
            "SIEM de Ares Aegis detenido",
            nivel_criticidad="MEDIO"
        )
        self._guardar_eventos()
        self.logger.info("SIEM cerrado correctamente")
    
    def buscar_eventos(self, tipo_evento: Optional[str] = None, 
                      nivel_criticidad: Optional[str] = None,
                      fecha_inicio: Optional[datetime] = None,
                      fecha_fin: Optional[datetime] = None,
                      texto_busqueda: Optional[str] = None,
                      limite: int = 100) -> List[EventoSIEM]:
        """
        Busca eventos con filtros específicos.
        
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
