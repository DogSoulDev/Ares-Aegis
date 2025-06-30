"""
Almacenamiento de eventos para el Mini-SIEM
Gestiona el almacenamiento eficiente de eventos de seguridad en SQLite
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import threading
import queue
import asyncio

logger = logging.getLogger(__name__)

class AlmacenadorEventos:
    """
    Gestor de almacenamiento de eventos de seguridad usando SQLite
    Optimizado para alto rendimiento y escalabilidad
    """
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            # Crear base de datos en directorio de datos del proyecto
            base_dir = Path(__file__).resolve().parent.parent
            datos_dir = base_dir / "data"
            datos_dir.mkdir(exist_ok=True)
            self.db_path = str(datos_dir / "mini_siem_events.db")
        else:
            self.db_path = db_path
            
        self.conexion = None
        self.batch_queue = queue.Queue()
        self.batch_size = 100
        self.batch_timeout = 5  # segundos
        self.running = False
        self.batch_thread = None
        
        # Inicializar base de datos
        self.inicializar_db()
        
    def inicializar_db(self):
        """Inicializar esquema de base de datos"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("PRAGMA journal_mode=WAL")  # Mejor concurrencia
                conn.execute("PRAGMA synchronous=NORMAL")  # Mejor rendimiento
                
                # Tabla principal de eventos
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS eventos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        event_category TEXT,
                        event_type TEXT,
                        severity TEXT,
                        host_name TEXT,
                        source_ip TEXT,
                        destination_ip TEXT,
                        user_name TEXT,
                        process_name TEXT,
                        process_pid INTEGER,
                        action TEXT,
                        message TEXT,
                        raw_log TEXT,
                        source_type TEXT,
                        source_file TEXT,
                        event_data TEXT,  -- JSON adicional
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Índices para mejorar rendimiento de consultas
                indices = [
                    "CREATE INDEX IF NOT EXISTS idx_timestamp ON eventos(timestamp)",
                    "CREATE INDEX IF NOT EXISTS idx_category ON eventos(event_category)",
                    "CREATE INDEX IF NOT EXISTS idx_severity ON eventos(severity)",
                    "CREATE INDEX IF NOT EXISTS idx_source_ip ON eventos(source_ip)",
                    "CREATE INDEX IF NOT EXISTS idx_user_name ON eventos(user_name)",
                    "CREATE INDEX IF NOT EXISTS idx_process_name ON eventos(process_name)",
                    "CREATE INDEX IF NOT EXISTS idx_created_at ON eventos(created_at)"
                ]
                
                for indice in indices:
                    conn.execute(indice)
                    
                # Tabla de estadísticas para dashboard
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS estadisticas_eventos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        fecha DATE NOT NULL,
                        categoria TEXT NOT NULL,
                        severidad TEXT NOT NULL,
                        contador INTEGER DEFAULT 1,
                        UNIQUE(fecha, categoria, severidad)
                    )
                """)
                
                conn.commit()
                logger.info(f"Base de datos inicializada: {self.db_path}")
                
        except Exception as e:
            logger.error(f"Error inicializando base de datos: {e}")
            raise
            
    def iniciar_procesamiento_batch(self):
        """Iniciar procesamiento de eventos en lotes"""
        self.running = True
        self.batch_thread = threading.Thread(target=self._procesar_batch_eventos)
        self.batch_thread.daemon = True
        self.batch_thread.start()
        logger.info("Procesamiento en lotes iniciado")
        
    def detener_procesamiento_batch(self):
        """Detener procesamiento en lotes"""
        self.running = False
        if self.batch_thread and self.batch_thread.is_alive():
            self.batch_thread.join(timeout=10)
        logger.info("Procesamiento en lotes detenido")
        
    def almacenar_evento(self, evento: Dict):
        """Agregar evento a la cola de procesamiento"""
        if self.running:
            self.batch_queue.put(evento)
        else:
            # Procesamiento directo si batch no está activo
            self._insertar_evento_directo(evento)
            
    def _procesar_batch_eventos(self):
        """Procesar eventos en lotes para mejor rendimiento"""
        eventos_batch = []
        ultimo_flush = datetime.now()
        
        while self.running:
            try:
                # Intentar obtener evento con timeout
                try:
                    evento = self.batch_queue.get(timeout=1)
                    eventos_batch.append(evento)
                except queue.Empty:
                    pass
                    
                # Procesar batch si alcanza el tamaño o timeout
                ahora = datetime.now()
                debe_procesar = (
                    len(eventos_batch) >= self.batch_size or
                    (eventos_batch and (ahora - ultimo_flush).seconds >= self.batch_timeout)
                )
                
                if debe_procesar and eventos_batch:
                    self._insertar_eventos_batch(eventos_batch)
                    eventos_batch.clear()
                    ultimo_flush = ahora
                    
            except Exception as e:
                logger.error(f"Error en procesamiento batch: {e}")
                
        # Procesar eventos restantes al finalizar
        if eventos_batch:
            self._insertar_eventos_batch(eventos_batch)
            
    def _insertar_eventos_batch(self, eventos: List[Dict]):
        """Insertar múltiples eventos en una transacción"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                datos_eventos = []
                for evento in eventos:
                    datos = self._extraer_campos_evento(evento)
                    datos_eventos.append(datos)
                    
                cursor.executemany("""
                    INSERT INTO eventos (
                        timestamp, event_category, event_type, severity,
                        host_name, source_ip, destination_ip, user_name,
                        process_name, process_pid, action, message,
                        raw_log, source_type, source_file, event_data
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, datos_eventos)
                
                # Actualizar estadísticas
                self._actualizar_estadisticas_batch(conn, eventos)
                
                conn.commit()
                logger.debug(f"Insertados {len(eventos)} eventos en batch")
                
        except Exception as e:
            logger.error(f"Error insertando batch de eventos: {e}")
            
    def _insertar_evento_directo(self, evento: Dict):
        """Insertar un solo evento directamente"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                datos = self._extraer_campos_evento(evento)
                
                cursor.execute("""
                    INSERT INTO eventos (
                        timestamp, event_category, event_type, severity,
                        host_name, source_ip, destination_ip, user_name,
                        process_name, process_pid, action, message,
                        raw_log, source_type, source_file, event_data
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, datos)
                
                # Actualizar estadísticas
                self._actualizar_estadisticas_evento(conn, evento)
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error insertando evento directo: {e}")
            
    def _extraer_campos_evento(self, evento: Dict) -> Tuple:
        """Extraer campos del evento para inserción en DB"""
        # Datos adicionales en JSON
        campos_adicionales = {}
        for key, value in evento.items():
            if key not in ['timestamp', 'event.category', 'event.type', 'severity',
                          'host.name', 'source.ip', 'destination.ip', 'user.name',
                          'process.name', 'process.pid', 'action', 'message',
                          'raw_log', 'source_type', 'source_file']:
                campos_adicionales[key] = value
                
        return (
            evento.get('timestamp'),
            evento.get('event.category'),
            evento.get('event.type'),
            evento.get('severity'),
            evento.get('host.name'),
            evento.get('source.ip'),
            evento.get('destination.ip'),
            evento.get('user.name'),
            evento.get('process.name'),
            evento.get('process.pid'),
            evento.get('action'),
            evento.get('message'),
            evento.get('raw_log'),
            evento.get('source_type'),
            evento.get('source_file'),
            json.dumps(campos_adicionales) if campos_adicionales else None
        )
        
    def _actualizar_estadisticas_batch(self, conn: sqlite3.Connection, eventos: List[Dict]):
        """Actualizar estadísticas para múltiples eventos"""
        contadores = {}
        
        for evento in eventos:
            fecha = datetime.now().strftime('%Y-%m-%d')
            categoria = evento.get('event.category', 'unknown')
            severidad = evento.get('severity', 'INFO')
            
            key = (fecha, categoria, severidad)
            contadores[key] = contadores.get(key, 0) + 1
            
        # Insertar/actualizar estadísticas
        for (fecha, categoria, severidad), contador in contadores.items():
            conn.execute("""
                INSERT OR IGNORE INTO estadisticas_eventos 
                (fecha, categoria, severidad, contador) 
                VALUES (?, ?, ?, 0)
            """, (fecha, categoria, severidad))
            
            conn.execute("""
                UPDATE estadisticas_eventos 
                SET contador = contador + ?
                WHERE fecha = ? AND categoria = ? AND severidad = ?
            """, (contador, fecha, categoria, severidad))
            
    def _actualizar_estadisticas_evento(self, conn: sqlite3.Connection, evento: Dict):
        """Actualizar estadísticas para un evento"""
        fecha = datetime.now().strftime('%Y-%m-%d')
        categoria = evento.get('event.category', 'unknown')
        severidad = evento.get('severity', 'INFO')
        
        conn.execute("""
            INSERT OR IGNORE INTO estadisticas_eventos 
            (fecha, categoria, severidad, contador) 
            VALUES (?, ?, ?, 0)
        """, (fecha, categoria, severidad))
        
        conn.execute("""
            UPDATE estadisticas_eventos 
            SET contador = contador + 1
            WHERE fecha = ? AND categoria = ? AND severidad = ?
        """, (fecha, categoria, severidad))
        
    def consultar_eventos(self, 
                         limite: int = 100,
                         offset: int = 0,
                         categoria: Optional[str] = None,
                         severidad: Optional[str] = None,
                         desde: Optional[datetime] = None,
                         hasta: Optional[datetime] = None) -> List[Dict]:
        """Consultar eventos con filtros"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Construir consulta SQL
                query = "SELECT * FROM eventos WHERE 1=1"
                params = []
                
                if categoria:
                    query += " AND event_category = ?"
                    params.append(categoria)
                    
                if severidad:
                    query += " AND severity = ?"
                    params.append(severidad)
                    
                if desde:
                    query += " AND datetime(timestamp) >= ?"
                    params.append(desde.isoformat())
                    
                if hasta:
                    query += " AND datetime(timestamp) <= ?"
                    params.append(hasta.isoformat())
                    
                query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
                params.extend([limite, offset])
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                # Convertir a diccionarios
                eventos = []
                for row in rows:
                    evento = dict(row)
                    # Parsear datos JSON adicionales
                    if evento['event_data']:
                        try:
                            datos_adicionales = json.loads(evento['event_data'])
                            evento.update(datos_adicionales)
                        except json.JSONDecodeError:
                            pass
                    eventos.append(evento)
                    
                return eventos
                
        except Exception as e:
            logger.error(f"Error consultando eventos: {e}")
            return []
            
    def obtener_estadisticas_dashboard(self, dias: int = 7) -> Dict:
        """Obtener estadísticas para dashboard"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Fecha límite
                fecha_limite = (datetime.now() - timedelta(days=dias)).strftime('%Y-%m-%d')
                
                # Total de eventos por día
                cursor.execute("""
                    SELECT fecha, SUM(contador) as total
                    FROM estadisticas_eventos 
                    WHERE fecha >= ?
                    GROUP BY fecha
                    ORDER BY fecha
                """, (fecha_limite,))
                eventos_por_dia = dict(cursor.fetchall())
                
                # Eventos por categoría
                cursor.execute("""
                    SELECT categoria, SUM(contador) as total
                    FROM estadisticas_eventos 
                    WHERE fecha >= ?
                    GROUP BY categoria
                    ORDER BY total DESC
                """, (fecha_limite,))
                eventos_por_categoria = dict(cursor.fetchall())
                
                # Eventos por severidad
                cursor.execute("""
                    SELECT severidad, SUM(contador) as total
                    FROM estadisticas_eventos 
                    WHERE fecha >= ?
                    GROUP BY severidad
                    ORDER BY total DESC
                """, (fecha_limite,))
                eventos_por_severidad = dict(cursor.fetchall())
                
                # Eventos recientes críticos
                cursor.execute("""
                    SELECT * FROM eventos 
                    WHERE severity IN ('CRITICAL', 'HIGH', 'WARNING')
                    ORDER BY timestamp DESC 
                    LIMIT 10
                """)
                eventos_criticos = [dict(row) for row in cursor.fetchall()]
                
                return {
                    'eventos_por_dia': eventos_por_dia,
                    'eventos_por_categoria': eventos_por_categoria,
                    'eventos_por_severidad': eventos_por_severidad,
                    'eventos_criticos_recientes': eventos_criticos,
                    'total_eventos': sum(eventos_por_dia.values()),
                    'dias_analizados': dias
                }
                
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {}
            
    def limpiar_eventos_antiguos(self, dias_retencion: int = 30):
        """Limpiar eventos antiguos según política de retención"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                fecha_limite = (datetime.now() - timedelta(days=dias_retencion)).isoformat()
                
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM eventos 
                    WHERE datetime(timestamp) < ?
                """, (fecha_limite,))
                
                eventos_eliminados = cursor.rowcount
                
                # Limpiar estadísticas antiguas también
                fecha_limite_stats = (datetime.now() - timedelta(days=dias_retencion)).strftime('%Y-%m-%d')
                cursor.execute("""
                    DELETE FROM estadisticas_eventos 
                    WHERE fecha < ?
                """, (fecha_limite_stats,))
                
                conn.commit()
                
                # Optimizar base de datos después de limpieza
                conn.execute("VACUUM")
                
                logger.info(f"Eliminados {eventos_eliminados} eventos antiguos")
                
        except Exception as e:
            logger.error(f"Error limpiando eventos antiguos: {e}")
            
    def exportar_eventos_csv(self, archivo: str, filtros: Optional[Dict] = None):
        """Exportar eventos a archivo CSV"""
        import csv
        
        try:
            eventos = self.consultar_eventos(
                limite=10000,  # Límite alto para exportación
                categoria=filtros.get('categoria') if filtros else None,
                severidad=filtros.get('severidad') if filtros else None,
                desde=filtros.get('desde') if filtros else None,
                hasta=filtros.get('hasta') if filtros else None
            )
            
            if not eventos:
                logger.warning("No hay eventos para exportar")
                return
                
            with open(archivo, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['timestamp', 'event_category', 'event_type', 'severity',
                             'host_name', 'source_ip', 'user_name', 'process_name',
                             'action', 'message', 'source_type']
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for evento in eventos:
                    # Filtrar solo campos relevantes para CSV
                    row = {field: evento.get(field, '') for field in fieldnames}
                    writer.writerow(row)
                    
            logger.info(f"Exportados {len(eventos)} eventos a {archivo}")
            
        except Exception as e:
            logger.error(f"Error exportando eventos: {e}")
            
    def obtener_metricas_rendimiento(self) -> Dict:
        """Obtener métricas de rendimiento de la base de datos"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Tamaño de la base de datos
                cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
                tamano_db = cursor.fetchone()[0]
                
                # Número total de eventos
                cursor.execute("SELECT COUNT(*) FROM eventos")
                total_eventos = cursor.fetchone()[0]
                
                # Eventos por día (últimos 7 días)
                cursor.execute("""
                    SELECT DATE(created_at) as fecha, COUNT(*) as eventos
                    FROM eventos 
                    WHERE created_at >= date('now', '-7 days')
                    GROUP BY DATE(created_at)
                    ORDER BY fecha
                """)
                eventos_recientes = dict(cursor.fetchall())
                
                return {
                    'tamano_db_bytes': tamano_db,
                    'tamano_db_mb': tamano_db / (1024 * 1024),
                    'total_eventos': total_eventos,
                    'eventos_ultimos_7_dias': eventos_recientes,
                    'batch_queue_size': self.batch_queue.qsize() if hasattr(self, 'batch_queue') else 0
                }
                
        except Exception as e:
            logger.error(f"Error obteniendo métricas: {e}")
            return {}
