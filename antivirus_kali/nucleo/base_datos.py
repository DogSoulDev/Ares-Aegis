"""
Interacción con la base de datos SQLite.
Gestión de logs, firmas y métricas.
"""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple
from contextlib import contextmanager

from antivirus_kali.utilidades.logger import get_logger

logger = get_logger(__name__)


class BaseDatos:
    """
    Manejador principal de la base de datos SQLite para Ares Aegis.
    Gestiona logs, firmas, métricas y configuraciones.
    """
    
    def __init__(self, ruta_db: str = "data/ares_aegis.db"):
        self.ruta_db = Path(ruta_db)
        self.ruta_db.parent.mkdir(parents=True, exist_ok=True)
        self._inicializar_db()
    
    def _inicializar_db(self):
        """Inicializa la base de datos con las tablas necesarias"""
        try:
            with self.conexion() as conn:
                cursor = conn.cursor()
                
                # Tabla de logs de escaneo
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS logs_escaneo (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        ruta_escaneada TEXT NOT NULL,
                        tipo_escaneo TEXT NOT NULL,
                        archivos_escaneados INTEGER DEFAULT 0,
                        amenazas_encontradas INTEGER DEFAULT 0,
                        tiempo_transcurrido REAL DEFAULT 0.0,
                        estado TEXT DEFAULT 'COMPLETADO',
                        detalles TEXT
                    )
                """)
                
                # Tabla de amenazas detectadas
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS amenazas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        ruta_archivo TEXT NOT NULL,
                        tipo_amenaza TEXT NOT NULL,
                        nombre_amenaza TEXT,
                        hash_archivo TEXT,
                        tamaño_archivo INTEGER,
                        accion_tomada TEXT DEFAULT 'DETECTADO',
                        severidad TEXT DEFAULT 'MEDIA',
                        motor_deteccion TEXT
                    )
                """)
                
                # Tabla de firmas de malware
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS firmas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        nombre_firma TEXT UNIQUE NOT NULL,
                        tipo_firma TEXT NOT NULL,
                        contenido_firma TEXT NOT NULL,
                        descripcion TEXT,
                        severidad TEXT DEFAULT 'MEDIA',
                        activa BOOLEAN DEFAULT 1,
                        version TEXT DEFAULT '1.0'
                    )
                """)
                
                # Tabla de métricas del sistema
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS metricas_sistema (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        uso_cpu REAL DEFAULT 0.0,
                        uso_memoria REAL DEFAULT 0.0,
                        uso_disco REAL DEFAULT 0.0,
                        procesos_activos INTEGER DEFAULT 0,
                        conexiones_red INTEGER DEFAULT 0,
                        temp_cpu REAL DEFAULT 0.0
                    )
                """)
                
                # Tabla de configuraciones
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS configuraciones (
                        clave TEXT PRIMARY KEY,
                        valor TEXT NOT NULL,
                        tipo TEXT DEFAULT 'string',
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Índices para mejorar rendimiento
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs_escaneo(timestamp)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_amenazas_timestamp ON amenazas(timestamp)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_amenazas_tipo ON amenazas(tipo_amenaza)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_firmas_activa ON firmas(activa)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_metricas_timestamp ON metricas_sistema(timestamp)")
                
                conn.commit()
                logger.info("Base de datos inicializada correctamente")
                
        except Exception as e:
            logger.error(f"Error inicializando base de datos: {e}")
            raise
    
    @contextmanager
    def conexion(self):
        """Context manager para conexiones a la base de datos"""
        conn = None
        try:
            conn = sqlite3.connect(self.ruta_db, timeout=30.0)
            conn.row_factory = sqlite3.Row  # Para acceso por nombre de columna
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Error en conexión a base de datos: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def registrar_escaneo(self, ruta: str, tipo: str, archivos: int = 0, 
                         amenazas: int = 0, tiempo: float = 0.0, 
                         estado: str = "COMPLETADO", detalles: Optional[Dict] = None) -> int:
        """
        Registra un escaneo completado
        
        Returns:
            ID del registro insertado
        """
        try:
            with self.conexion() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO logs_escaneo 
                    (ruta_escaneada, tipo_escaneo, archivos_escaneados, 
                     amenazas_encontradas, tiempo_transcurrido, estado, detalles)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (ruta, tipo, archivos, amenazas, tiempo, estado, 
                      json.dumps(detalles) if detalles else None))
                
                conn.commit()
                return cursor.lastrowid or -1
                
        except Exception as e:
            logger.error(f"Error registrando escaneo: {e}")
            return -1
    
    def registrar_amenaza(self, ruta_archivo: str, tipo_amenaza: str, 
                         nombre: Optional[str] = None, hash_archivo: Optional[str] = None,
                         tamaño: int = 0, accion: str = "DETECTADO",
                         severidad: str = "MEDIA", motor: Optional[str] = None) -> int:
        """
        Registra una amenaza detectada
        
        Returns:
            ID del registro insertado
        """
        try:
            with self.conexion() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO amenazas 
                    (ruta_archivo, tipo_amenaza, nombre_amenaza, hash_archivo,
                     tamaño_archivo, accion_tomada, severidad, motor_deteccion)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (ruta_archivo, tipo_amenaza, nombre, hash_archivo,
                      tamaño, accion, severidad, motor))
                
                conn.commit()
                return cursor.lastrowid or -1
                
        except Exception as e:
            logger.error(f"Error registrando amenaza: {e}")
            return -1
    
    def obtener_historial_escaneos(self, limite: int = 100, 
                                  desde: Optional[datetime] = None) -> List[Dict]:
        """Obtiene el historial de escaneos"""
        try:
            with self.conexion() as conn:
                cursor = conn.cursor()
                
                query = "SELECT * FROM logs_escaneo"
                params = []
                
                if desde:
                    query += " WHERE timestamp >= ?"
                    params.append(desde.isoformat())
                
                query += " ORDER BY timestamp DESC LIMIT ?"
                params.append(limite)
                
                cursor.execute(query, params)
                
                resultados = []
                for row in cursor.fetchall():
                    resultado = dict(row)
                    if resultado['detalles']:
                        try:
                            resultado['detalles'] = json.loads(resultado['detalles'])
                        except:
                            resultado['detalles'] = {}
                    resultados.append(resultado)
                
                return resultados
                
        except Exception as e:
            logger.error(f"Error obteniendo historial: {e}")
            return []
    
    def obtener_amenazas(self, limite: int = 100, 
                        tipo_filtro: Optional[str] = None,
                        desde: Optional[datetime] = None) -> List[Dict]:
        """Obtiene lista de amenazas detectadas"""
        try:
            with self.conexion() as conn:
                cursor = conn.cursor()
                
                query = "SELECT * FROM amenazas"
                params = []
                condiciones = []
                
                if tipo_filtro:
                    condiciones.append("tipo_amenaza = ?")
                    params.append(tipo_filtro)
                
                if desde:
                    condiciones.append("timestamp >= ?")
                    params.append(desde.isoformat())
                
                if condiciones:
                    query += " WHERE " + " AND ".join(condiciones)
                
                query += " ORDER BY timestamp DESC LIMIT ?"
                params.append(limite)
                
                cursor.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Error obteniendo amenazas: {e}")
            return []
    
    def obtener_estadisticas(self, periodo_dias: int = 7) -> Dict[str, Any]:
        """Obtiene estadísticas del sistema para un período"""
        try:
            fecha_limite = datetime.now() - timedelta(days=periodo_dias)
            
            with self.conexion() as conn:
                cursor = conn.cursor()
                
                # Estadísticas de escaneos
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_escaneos,
                        SUM(archivos_escaneados) as total_archivos,
                        SUM(amenazas_encontradas) as total_amenazas,
                        AVG(tiempo_transcurrido) as tiempo_promedio
                    FROM logs_escaneo 
                    WHERE timestamp >= ?
                """, (fecha_limite.isoformat(),))
                
                stats_escaneos = dict(cursor.fetchone() or {})
                
                # Top amenazas
                cursor.execute("""
                    SELECT tipo_amenaza, COUNT(*) as cantidad
                    FROM amenazas 
                    WHERE timestamp >= ?
                    GROUP BY tipo_amenaza
                    ORDER BY cantidad DESC
                    LIMIT 10
                """, (fecha_limite.isoformat(),))
                
                top_amenazas = [dict(row) for row in cursor.fetchall()]
                
                # Tendencia por días
                cursor.execute("""
                    SELECT 
                        DATE(timestamp) as fecha,
                        COUNT(*) as escaneos,
                        SUM(amenazas_encontradas) as amenazas
                    FROM logs_escaneo 
                    WHERE timestamp >= ?
                    GROUP BY DATE(timestamp)
                    ORDER BY fecha DESC
                """, (fecha_limite.isoformat(),))
                
                tendencia = [dict(row) for row in cursor.fetchall()]
                
                return {
                    'estadisticas_generales': stats_escaneos,
                    'top_amenazas': top_amenazas,
                    'tendencia_diaria': tendencia,
                    'periodo_dias': periodo_dias
                }
                
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {}
    
    def registrar_metricas_sistema(self, cpu: float, memoria: float, 
                                  disco: float, procesos: int = 0,
                                  conexiones: int = 0, temp_cpu: float = 0.0):
        """Registra métricas del sistema"""
        try:
            with self.conexion() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO metricas_sistema 
                    (uso_cpu, uso_memoria, uso_disco, procesos_activos, 
                     conexiones_red, temp_cpu)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (cpu, memoria, disco, procesos, conexiones, temp_cpu))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error registrando métricas: {e}")
    
    def limpiar_datos_antiguos(self, dias_retener: int = 30):
        """Limpia datos antiguos para mantener la base de datos optimizada"""
        try:
            fecha_limite = datetime.now() - timedelta(days=dias_retener)
            
            with self.conexion() as conn:
                cursor = conn.cursor()
                
                # Limpiar logs antiguos
                cursor.execute("""
                    DELETE FROM logs_escaneo 
                    WHERE timestamp < ?
                """, (fecha_limite.isoformat(),))
                
                logs_eliminados = cursor.rowcount
                
                # Limpiar métricas antiguas (conservar menos tiempo)
                fecha_metricas = datetime.now() - timedelta(days=7)
                cursor.execute("""
                    DELETE FROM metricas_sistema 
                    WHERE timestamp < ?
                """, (fecha_metricas.isoformat(),))
                
                metricas_eliminadas = cursor.rowcount
                
                conn.commit()
                
                logger.info(f"Limpieza completada: {logs_eliminados} logs, {metricas_eliminadas} métricas eliminadas")
                
        except Exception as e:
            logger.error(f"Error en limpieza de datos: {e}")
    
    def guardar_configuracion(self, clave: str, valor: Any, tipo: str = "string"):
        """Guarda una configuración en la base de datos"""
        try:
            valor_str = json.dumps(valor) if tipo == "json" else str(valor)
            
            with self.conexion() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO configuraciones (clave, valor, tipo)
                    VALUES (?, ?, ?)
                """, (clave, valor_str, tipo))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error guardando configuración {clave}: {e}")
    
    def cargar_configuracion(self, clave: str, valor_defecto: Any = None) -> Any:
        """Carga una configuración desde la base de datos"""
        try:
            with self.conexion() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT valor, tipo FROM configuraciones WHERE clave = ?
                """, (clave,))
                
                resultado = cursor.fetchone()
                if not resultado:
                    return valor_defecto
                
                valor, tipo = resultado
                
                if tipo == "json":
                    return json.loads(valor)
                elif tipo == "int":
                    return int(valor)
                elif tipo == "float":
                    return float(valor)
                elif tipo == "bool":
                    return valor.lower() == "true"
                else:
                    return valor
                    
        except Exception as e:
            logger.error(f"Error cargando configuración {clave}: {e}")
            return valor_defecto
