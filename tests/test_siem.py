"""
Tests para el módulo SIEM de Ares Aegis
Implementa pruebas unitarias siguiendo el patrón TDD.
"""

import unittest
import tempfile
import json
from pathlib import Path
from datetime import datetime, timedelta
import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from modelos.siem import SIEM, TipoEvento, Evento


class TestEvento(unittest.TestCase):
    """Tests para la clase Evento."""
    
    def test_crear_evento_basico(self):
        """Test creación básica de evento."""
        evento = Evento(TipoEvento.INFO, "Mensaje de prueba")
        
        self.assertEqual(evento.tipo, TipoEvento.INFO)
        self.assertEqual(evento.mensaje, "Mensaje de prueba")
        self.assertIsInstance(evento.timestamp, datetime)
        self.assertEqual(evento.detalles, {})
        self.assertIsNotNone(evento.id_evento)
    
    def test_crear_evento_con_detalles(self):
        """Test creación de evento con detalles."""
        detalles = {"archivo": "/test/file.txt", "tamaño": 1024}
        evento = Evento(TipoEvento.ESCANEO, "Archivo escaneado", detalles)
        
        self.assertEqual(evento.detalles, detalles)
    
    def test_evento_to_dict(self):
        """Test conversión de evento a diccionario."""
        evento = Evento(TipoEvento.ERROR, "Error de prueba", {"codigo": 500})
        evento_dict = evento.to_dict()
        
        self.assertIn("id", evento_dict)
        self.assertIn("timestamp", evento_dict)
        self.assertIn("tipo", evento_dict)
        self.assertIn("mensaje", evento_dict)
        self.assertIn("detalles", evento_dict)
        
        self.assertEqual(evento_dict["tipo"], TipoEvento.ERROR)
        self.assertEqual(evento_dict["mensaje"], "Error de prueba")
        self.assertEqual(evento_dict["detalles"]["codigo"], 500)
    
    def test_evento_str(self):
        """Test representación en string del evento."""
        evento = Evento(TipoEvento.AMENAZA_DETECTADA, "Malware detectado")
        evento_str = str(evento)
        
        self.assertIn("AMENAZA_DETECTADA", evento_str)
        self.assertIn("Malware detectado", evento_str)
        self.assertIn(evento.timestamp.strftime('%Y-%m-%d'), evento_str)


class TestSIEM(unittest.TestCase):
    """Tests para la clase SIEM."""
    
    def setUp(self):
        """Configuración previa a cada test."""
        # Crear archivo temporal para tests
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.temp_file.close()
        self.temp_path = Path(self.temp_file.name)
        
        # Crear instancia SIEM con archivo temporal
        self.siem = SIEM(archivo_eventos=self.temp_path)
    
    def tearDown(self):
        """Limpieza posterior a cada test."""
        # Eliminar archivo temporal
        if self.temp_path.exists():
            self.temp_path.unlink()
    
    def test_inicializacion_siem(self):
        """Test inicialización del SIEM."""
        self.assertIsInstance(self.siem, SIEM)
        self.assertEqual(self.siem.archivo_eventos, self.temp_path)
        self.assertIsInstance(self.siem.eventos, list)
    
    def test_log_evento_basico(self):
        """Test logging básico de evento."""
        id_evento = self.siem.log_evento(TipoEvento.INFO, "Mensaje de prueba")
        
        self.assertIsNotNone(id_evento)
        self.assertEqual(len(self.siem.eventos), 1)
        
        evento = self.siem.eventos[0]
        self.assertEqual(evento.tipo, TipoEvento.INFO)
        self.assertEqual(evento.mensaje, "Mensaje de prueba")
    
    def test_log_evento_con_detalles(self):
        """Test logging de evento con detalles."""
        detalles = {"usuario": "admin", "accion": "login"}
        id_evento = self.siem.log_evento(TipoEvento.SISTEMA_EVENTO, "Usuario logueado", detalles)
        
        evento = self.siem.eventos[0]
        self.assertEqual(evento.detalles, detalles)
    
    def test_obtener_eventos_sin_filtro(self):
        """Test obtener todos los eventos."""
        # Agregar eventos de prueba
        self.siem.log_evento(TipoEvento.INFO, "Evento 1")
        self.siem.log_evento(TipoEvento.ERROR, "Evento 2")
        self.siem.log_evento(TipoEvento.ADVERTENCIA, "Evento 3")
        
        eventos = self.siem.obtener_eventos()
        self.assertEqual(len(eventos), 3)
    
    def test_obtener_eventos_con_filtro_tipo(self):
        """Test obtener eventos filtrados por tipo."""
        self.siem.log_evento(TipoEvento.INFO, "Evento info")
        self.siem.log_evento(TipoEvento.ERROR, "Evento error")
        self.siem.log_evento(TipoEvento.INFO, "Otro evento info")
        
        eventos_info = self.siem.obtener_eventos(tipo_filtro=TipoEvento.INFO)
        self.assertEqual(len(eventos_info), 2)
        
        for evento in eventos_info:
            self.assertEqual(evento.tipo, TipoEvento.INFO)
    
    def test_obtener_eventos_con_limite(self):
        """Test obtener eventos con límite."""
        for i in range(10):
            self.siem.log_evento(TipoEvento.INFO, f"Evento {i}")
        
        eventos_limitados = self.siem.obtener_eventos(limite=5)
        self.assertEqual(len(eventos_limitados), 5)
    
    def test_obtener_eventos_markdown(self):
        """Test generar eventos en formato Markdown."""
        self.siem.log_evento(TipoEvento.ESCANEO, "Archivo escaneado", {"archivo": "test.txt"})
        self.siem.log_evento(TipoEvento.AMENAZA_DETECTADA, "Malware encontrado")
        
        markdown = self.siem.obtener_eventos_markdown()
        
        self.assertIn("## Log de Eventos del SIEM", markdown)
        self.assertIn("ESCANEO", markdown)
        self.assertIn("AMENAZA_DETECTADA", markdown)
        self.assertIn("Archivo escaneado", markdown)
        self.assertIn("Malware encontrado", markdown)
    
    def test_persistencia_eventos(self):
        """Test persistencia de eventos en archivo."""
        # Agregar eventos
        self.siem.log_evento(TipoEvento.INFO, "Evento persistente")
        
        # Crear nuevo SIEM con el mismo archivo
        siem2 = SIEM(archivo_eventos=self.temp_path)
        
        # Verificar que los eventos se cargaron
        self.assertEqual(len(siem2.eventos), 1)
        self.assertEqual(siem2.eventos[0].mensaje, "Evento persistente")
    
    def test_limpiar_eventos_antiguos(self):
        """Test limpieza de eventos antiguos."""
        # Agregar evento actual
        self.siem.log_evento(TipoEvento.INFO, "Evento reciente")
        
        # Simular evento antiguo modificando timestamp
        evento_antiguo = Evento(TipoEvento.INFO, "Evento antiguo")
        evento_antiguo.timestamp = datetime.now() - timedelta(days=40)
        self.siem.eventos.append(evento_antiguo)
        
        # Limpiar eventos más antiguos de 30 días
        eliminados = self.siem.limpiar_eventos_antiguos(30)
        
        self.assertEqual(eliminados, 1)
        self.assertEqual(len(self.siem.eventos), 2)  # 1 reciente + 1 del log de limpieza
    
    def test_obtener_estadisticas(self):
        """Test obtener estadísticas del SIEM."""
        self.siem.log_evento(TipoEvento.INFO, "Info 1")
        self.siem.log_evento(TipoEvento.INFO, "Info 2")
        self.siem.log_evento(TipoEvento.ERROR, "Error 1")
        
        stats = self.siem.obtener_estadisticas()
        
        self.assertEqual(stats["total"], 3)
        self.assertIn("por_tipo", stats)
        self.assertEqual(stats["por_tipo"][TipoEvento.INFO], 2)
        self.assertEqual(stats["por_tipo"][TipoEvento.ERROR], 1)
        self.assertIn("evento_mas_reciente", stats)
        self.assertIn("evento_mas_antiguo", stats)


class TestTipoEvento(unittest.TestCase):
    """Tests para las constantes de TipoEvento."""
    
    def test_constantes_tipo_evento(self):
        """Test que las constantes estén definidas correctamente."""
        self.assertEqual(TipoEvento.ESCANEO, "ESCANEO")
        self.assertEqual(TipoEvento.AMENAZA_DETECTADA, "AMENAZA_DETECTADA")
        self.assertEqual(TipoEvento.ARCHIVO_CUARENTENA, "ARCHIVO_CUARENTENA")
        self.assertEqual(TipoEvento.INTEGRIDAD_ARCHIVO, "INTEGRIDAD_ARCHIVO")
        self.assertEqual(TipoEvento.PROCESO_SOSPECHOSO, "PROCESO_SOSPECHOSO")
        self.assertEqual(TipoEvento.RED_ACTIVIDAD, "RED_ACTIVIDAD")
        self.assertEqual(TipoEvento.SISTEMA_EVENTO, "SISTEMA_EVENTO")
        self.assertEqual(TipoEvento.ERROR, "ERROR")
        self.assertEqual(TipoEvento.ADVERTENCIA, "ADVERTENCIA")
        self.assertEqual(TipoEvento.INFO, "INFO")
        self.assertEqual(TipoEvento.GUI_ACCION, "GUI_ACCION")


if __name__ == '__main__':
    unittest.main()
