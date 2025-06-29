#!/usr/bin/env python3
"""
Pruebas unitarias para el Analizador de Logs
Tests para src/modelos/analizador_logs.py

Autor: DogSoulDev
Versión: 2.0.0
"""

import unittest
import sys
import os
import tempfile
from unittest.mock import Mock, patch, mock_open
from datetime import datetime, timedelta

# Agregar src al path para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from modelos.analizador_logs import AnalizadorLogs, EventoLog


class TestEventoLog(unittest.TestCase):
    """Tests para la clase EventoLog."""
    
    def setUp(self):
        """Configurar datos de prueba."""
        self.evento = EventoLog(
            timestamp=datetime.now(),
            nivel="ERROR",
            fuente="sshd",
            mensaje="Failed password for user from 192.168.1.100",
            archivo_origen="/var/log/auth.log"
        )
    
    def test_inicializacion_evento(self):
        """Prueba la inicialización correcta de EventoLog."""
        self.assertEqual(self.evento.nivel, "ERROR")
        self.assertEqual(self.evento.fuente, "sshd")
        self.assertEqual(self.evento.archivo_origen, "/var/log/auth.log")
        self.assertFalse(self.evento.sospechoso)
        self.assertEqual(self.evento.categoria, 'General')
        self.assertEqual(len(self.evento.razones_sospecha), 0)
    
    def test_marcar_como_sospechoso(self):
        """Prueba marcar evento como sospechoso."""
        razon = "Fallo de autenticación"
        self.evento.marcar_como_sospechoso(razon)
        
        self.assertTrue(self.evento.sospechoso)
        self.assertIn(razon, self.evento.razones_sospecha)
    
    def test_asignar_categoria(self):
        """Prueba asignación de categoría."""
        categoria = "autenticacion_fallida"
        self.evento.asignar_categoria(categoria)
        
        self.assertEqual(self.evento.categoria, categoria)
    
    def test_to_dict(self):
        """Prueba la conversión a diccionario."""
        self.evento.marcar_como_sospechoso("Test reason")
        self.evento.asignar_categoria("test_categoria")
        dict_evento = self.evento.to_dict()
        
        self.assertIsInstance(dict_evento, dict)
        self.assertEqual(dict_evento['nivel'], "ERROR")
        self.assertEqual(dict_evento['fuente'], "sshd")
        self.assertEqual(dict_evento['categoria'], "test_categoria")
        self.assertTrue(dict_evento['sospechoso'])
        self.assertIn("Test reason", dict_evento['razones_sospecha'])


class TestAnalizadorLogs(unittest.TestCase):
    """Tests para la clase AnalizadorLogs."""
    
    def setUp(self):
        """Configurar analizador de prueba."""
        self.siem_mock = Mock()
        self.analizador = AnalizadorLogs(self.siem_mock)
    
    def test_inicializacion_analizador(self):
        """Prueba la inicialización del analizador."""
        self.assertIsInstance(self.analizador.patrones_sospechosos, dict)
        self.assertIsInstance(self.analizador.rutas_logs, list)
        self.assertIsInstance(self.analizador.palabras_clave_seguridad, list)
        self.assertEqual(self.analizador.siem, self.siem_mock)
    
    def test_cargar_patrones_sospechosos(self):
        """Prueba la carga de patrones sospechosos."""
        patrones = self.analizador._cargar_patrones_sospechosos()
        
        self.assertIsInstance(patrones, dict)
        self.assertIn('autenticacion_fallida', patrones)
        self.assertIn('escalada_privilegios', patrones)
        self.assertIn('acceso_root', patrones)
        
        # Verificar que hay patrones en cada categoría
        for categoria, lista_patrones in patrones.items():
            self.assertIsInstance(lista_patrones, list)
            self.assertGreater(len(lista_patrones), 0)
    
    def test_cargar_palabras_clave(self):
        """Prueba la carga de palabras clave de seguridad."""
        palabras = self.analizador._cargar_palabras_clave()
        
        self.assertIsInstance(palabras, list)
        self.assertGreater(len(palabras), 0)
        self.assertIn('failed', palabras)
        self.assertIn('sudo', palabras)
        self.assertIn('error', palabras)
    
    @patch('os.path.exists')
    def test_cargar_rutas_logs_filtrado(self, mock_exists):
        """Prueba que solo se cargan rutas de archivos existentes."""
        # Simular que solo algunos archivos existen
        def side_effect(path):
            return path in ['/var/log/auth.log', '/var/log/syslog']
        
        mock_exists.side_effect = side_effect
        
        analizador = AnalizadorLogs()
        rutas = analizador.rutas_logs
        
        # Solo deben estar las rutas que "existen"
        self.assertIn('/var/log/auth.log', rutas)
        self.assertIn('/var/log/syslog', rutas)
        self.assertNotIn('/var/log/archivo_inexistente.log', rutas)
    
    def test_parsear_linea_syslog_valida(self):
        """Prueba el parseo de una línea válida de syslog."""
        linea = "Dec 25 10:30:45 hostname sshd[1234]: Failed password for admin from 192.168.1.100"
        
        evento = self.analizador.parsear_linea_syslog(linea, "/var/log/auth.log")
        
        self.assertIsNotNone(evento)
        self.assertEqual(evento.fuente, "sshd")
        self.assertEqual(evento.nivel, "ERROR")  # Contiene "Failed"
        self.assertIn("Failed password", evento.mensaje)
        self.assertEqual(evento.archivo_origen, "/var/log/auth.log")
    
    def test_parsear_linea_syslog_con_warning(self):
        """Prueba el parseo de línea con warning."""
        linea = "Dec 25 10:30:45 hostname kernel: WARNING: possible hardware malfunction"
        
        evento = self.analizador.parsear_linea_syslog(linea, "/var/log/kern.log")
        
        self.assertIsNotNone(evento)
        self.assertEqual(evento.nivel, "WARNING")
    
    def test_parsear_linea_syslog_con_critical(self):
        """Prueba el parseo de línea crítica."""
        linea = "Dec 25 10:30:45 hostname kernel: CRITICAL: system panic imminent"
        
        evento = self.analizador.parsear_linea_syslog(linea, "/var/log/kern.log")
        
        self.assertIsNotNone(evento)
        self.assertEqual(evento.nivel, "CRITICAL")
    
    def test_parsear_linea_syslog_invalida(self):
        """Prueba el parseo de línea inválida."""
        linea = "Esta no es una línea de syslog válida"
        
        evento = self.analizador.parsear_linea_syslog(linea, "/var/log/test.log")
        
        self.assertIsNone(evento)
    
    def test_leer_archivo_log_normal(self):
        """Prueba lectura de archivo normal."""
        contenido = "Línea 1\nLínea 2\nLínea 3\n"
        
        with patch('builtins.open', mock_open(read_data=contenido)):
            lineas = list(self.analizador.leer_archivo_log("/test/path.log", lineas_max=10))
        
        self.assertEqual(len(lineas), 3)
        self.assertEqual(lineas[0], "Línea 1")
        self.assertEqual(lineas[1], "Línea 2")
        self.assertEqual(lineas[2], "Línea 3")
    
    def test_leer_archivo_log_con_limite(self):
        """Prueba lectura con límite de líneas."""
        contenido = "Línea 1\nLínea 2\nLínea 3\nLínea 4\nLínea 5\n"
        
        with patch('builtins.open', mock_open(read_data=contenido)):
            lineas = list(self.analizador.leer_archivo_log("/test/path.log", lineas_max=3))
        
        self.assertEqual(len(lineas), 3)
    
    @patch('gzip.open')
    def test_leer_archivo_log_comprimido(self, mock_gzip_open):
        """Prueba lectura de archivo comprimido."""
        mock_file = Mock()
        mock_file.__iter__ = Mock(return_value=iter(["Línea 1", "Línea 2"]))
        mock_gzip_open.return_value.__enter__ = Mock(return_value=mock_file)
        mock_gzip_open.return_value.__exit__ = Mock(return_value=None)
        
        lineas = list(self.analizador.leer_archivo_log("/test/path.log.gz"))
        
        self.assertEqual(len(lineas), 2)
        mock_gzip_open.assert_called_once()
    
    def test_leer_archivo_log_error_io(self):
        """Prueba manejo de error de E/S."""
        with patch('builtins.open', side_effect=IOError("No se puede leer")):
            lineas = list(self.analizador.leer_archivo_log("/test/inexistente.log"))
        
        self.assertEqual(len(lineas), 0)
        self.siem_mock.registrar_evento.assert_called()
    
    def test_analizar_eventos_sospechosos_autenticacion(self):
        """Prueba análisis de eventos de autenticación fallida."""
        eventos = [
            EventoLog(
                timestamp=datetime.now(),
                nivel="ERROR",
                fuente="sshd",
                mensaje="Failed password for admin from 192.168.1.100",
                archivo_origen="/var/log/auth.log"
            ),
            EventoLog(
                timestamp=datetime.now(),
                nivel="INFO",
                fuente="sshd", 
                mensaje="Accepted password for user from 192.168.1.200",
                archivo_origen="/var/log/auth.log"
            )
        ]
        
        sospechosos = self.analizador.analizar_eventos_sospechosos(eventos)
        
        self.assertEqual(len(sospechosos), 1)
        self.assertTrue(sospechosos[0].sospechoso)
        self.assertIn("Failed password", sospechosos[0].mensaje)
    
    def test_analizar_eventos_sospechosos_escalada_privilegios(self):
        """Prueba análisis de eventos de escalada de privilegios."""
        evento = EventoLog(
            timestamp=datetime.now(),
            nivel="INFO",
            fuente="sudo",
            mensaje="user : TTY=pts/1 ; PWD=/home/user ; USER=root ; COMMAND=/bin/bash",
            archivo_origen="/var/log/auth.log"
        )
        
        sospechosos = self.analizador.analizar_eventos_sospechosos([evento])
        
        self.assertEqual(len(sospechosos), 1)
        self.assertEqual(sospechosos[0].categoria, "escalada_privilegios")
    
    def test_analizar_eventos_sospechosos_kernel(self):
        """Prueba análisis de eventos críticos del kernel."""
        evento = EventoLog(
            timestamp=datetime.now(),
            nivel="CRITICAL",
            fuente="kernel",
            mensaje="Oops: 0000 [#1] SMP",
            archivo_origen="/var/log/kern.log"
        )
        
        sospechosos = self.analizador.analizar_eventos_sospechosos([evento])
        
        self.assertEqual(len(sospechosos), 1)
        self.assertEqual(sospechosos[0].categoria, "kernel")
    
    def test_detectar_ataques_brute_force_exitoso(self):
        """Prueba detección exitosa de ataques de fuerza bruta."""
        base_time = datetime.now()
        eventos = []
        
        # Crear múltiples eventos de fallo de autenticación desde la misma IP
        for i in range(6):  # Más del umbral de 5
            evento = EventoLog(
                timestamp=base_time + timedelta(seconds=i * 30),
                nivel="ERROR",
                fuente="sshd",
                mensaje=f"Failed password for user{i} from 192.168.1.100",
                archivo_origen="/var/log/auth.log"
            )
            evento.asignar_categoria("autenticacion")
            eventos.append(evento)
        
        ataques = self.analizador.detectar_ataques_brute_force(eventos, ventana_tiempo=300)
        
        self.assertEqual(len(ataques), 1)
        self.assertEqual(ataques[0]['ip_origen'], "192.168.1.100")
        self.assertEqual(ataques[0]['intentos_totales'], 6)
        self.assertEqual(ataques[0]['tipo'], 'brute_force')
    
    def test_detectar_ataques_brute_force_sin_ataques(self):
        """Prueba cuando no hay ataques de fuerza bruta."""
        eventos = [
            EventoLog(
                timestamp=datetime.now(),
                nivel="ERROR",
                fuente="sshd",
                mensaje="Failed password for user from 192.168.1.100",
                archivo_origen="/var/log/auth.log"
            )
        ]
        eventos[0].asignar_categoria("autenticacion")
        
        ataques = self.analizador.detectar_ataques_brute_force(eventos)
        
        self.assertEqual(len(ataques), 0)
    
    def test_detectar_ataques_brute_force_fuera_de_ventana(self):
        """Prueba ataques fuera de la ventana de tiempo."""
        base_time = datetime.now()
        eventos = []
        
        # Crear eventos espaciados fuera de la ventana de tiempo
        for i in range(6):
            evento = EventoLog(
                timestamp=base_time + timedelta(minutes=i * 10),  # 10 minutos entre cada uno
                nivel="ERROR",
                fuente="sshd",
                mensaje=f"Failed password for user{i} from 192.168.1.100",
                archivo_origen="/var/log/auth.log"
            )
            evento.asignar_categoria("autenticacion")
            eventos.append(evento)
        
        ataques = self.analizador.detectar_ataques_brute_force(eventos, ventana_tiempo=300)  # 5 minutos
        
        self.assertEqual(len(ataques), 0)
    
    @patch.object(AnalizadorLogs, 'leer_archivo_log')
    @patch.object(AnalizadorLogs, '_cargar_rutas_logs')
    def test_analizar_periodo_exitoso(self, mock_rutas, mock_leer):
        """Prueba análisis exitoso de período."""
        # Configurar mocks
        mock_rutas.return_value = ["/var/log/auth.log"]
        mock_leer.return_value = [
            "Dec 25 10:30:45 host sshd[1234]: Failed password for admin from 192.168.1.100"
        ]
        
        resultado = self.analizador.analizar_periodo(horas_atras=24)
        
        self.assertIsInstance(resultado, dict)
        self.assertIn('timestamp', resultado)
        self.assertIn('estadisticas', resultado)
        self.assertIn('eventos_sospechosos', resultado)
        self.assertIn('ataques_detectados', resultado)
        
        # Verificar estadísticas
        stats = resultado['estadisticas']
        self.assertIsInstance(stats['total_eventos'], int)
        self.assertIsInstance(stats['tiempo_procesamiento'], float)
    
    def test_buscar_patrones_personalizados(self):
        """Prueba búsqueda de patrones personalizados."""
        lineas_test = [
            "Dec 25 10:30:45 host app[1234]: CUSTOM_PATTERN detected",
            "Dec 25 10:31:45 host app[1234]: Normal log entry",
            "Dec 25 10:32:45 host app[1234]: Another CUSTOM_PATTERN here"
        ]
        
        with patch.object(self.analizador, 'leer_archivo_log', return_value=lineas_test):
            with patch.object(self.analizador, 'rutas_logs', ['/test/log.log']):
                eventos = self.analizador.buscar_patrones_personalizados("CUSTOM_PATTERN", horas_atras=24)
        
        self.assertEqual(len(eventos), 2)
        for evento in eventos:
            self.assertTrue(evento.sospechoso)
            self.assertIn("CUSTOM_PATTERN", evento.mensaje)
    
    def test_exportar_reporte_markdown_estructura(self):
        """Prueba la estructura del reporte Markdown."""
        # Crear datos de prueba
        resultado_mock = {
            'timestamp': datetime.now().isoformat(),
            'periodo_analizado': {
                'desde': (datetime.now() - timedelta(hours=24)).isoformat(),
                'hasta': datetime.now().isoformat(),
                'horas': 24
            },
            'estadisticas': {
                'total_eventos': 1000,
                'eventos_sospechosos': 15,
                'ataques_brute_force': 2,
                'archivos_procesados': 3,
                'tiempo_procesamiento': 5.2,
                'eventos_por_nivel': {'ERROR': 50, 'WARNING': 30, 'INFO': 920},
                'eventos_por_fuente': {'sshd': 100, 'kernel': 50, 'systemd': 850},
                'categorias_sospechosas': {'autenticacion_fallida': 10, 'escalada_privilegios': 5}
            },
            'eventos_sospechosos': [
                {
                    'timestamp': datetime.now().isoformat(),
                    'nivel': 'ERROR',
                    'fuente': 'sshd',
                    'mensaje': 'Failed password for admin from 192.168.1.100',
                    'categoria': 'autenticacion_fallida',
                    'razones_sospecha': ['Fallo de autenticación']
                }
            ],
            'ataques_detectados': [
                {
                    'ip_origen': '192.168.1.100',
                    'intentos_totales': 10,
                    'primer_intento': datetime.now().isoformat(),
                    'ultimo_intento': datetime.now().isoformat(),
                    'duracion_segundos': 300,
                    'tipo': 'brute_force'
                }
            ],
            'resumen_por_archivo': {
                '/var/log/auth.log': 500,
                '/var/log/syslog': 300,
                '/var/log/kern.log': 200
            }
        }
        
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            temp_path = f.name
        
        try:
            archivo_reporte = self.analizador.exportar_reporte_markdown(resultado_mock, temp_path)
            
            # Verificar que se creó el archivo
            self.assertTrue(os.path.exists(archivo_reporte))
            
            # Leer contenido
            with open(archivo_reporte, 'r', encoding='utf-8') as f:
                contenido = f.read()
            
            # Verificar estructura básica
            self.assertIn('# Reporte de Análisis de Logs', contenido)
            self.assertIn('## Resumen Ejecutivo', contenido)
            self.assertIn('## Ataques Detectados', contenido)
            self.assertIn('## Eventos Sospechosos por Categoría', contenido)
            self.assertIn('192.168.1.100', contenido)  # IP del ataque
            self.assertIn('Failed password', contenido)  # Evento sospechoso
            
        finally:
            # Limpiar archivo temporal
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestIntegracionAnalizadorLogs(unittest.TestCase):
    """Tests de integración para el Analizador de Logs."""
    
    def setUp(self):
        """Configurar test de integración."""
        self.analizador = AnalizadorLogs()
    
    @patch('os.path.exists')
    def test_analizar_periodo_sin_archivos(self, mock_exists):
        """Prueba análisis cuando no hay archivos de log."""
        mock_exists.return_value = False
        
        analizador = AnalizadorLogs()
        resultado = analizador.analizar_periodo(horas_atras=1)
        
        self.assertIsInstance(resultado, dict)
        self.assertEqual(resultado['estadisticas']['total_eventos'], 0)
        self.assertEqual(resultado['estadisticas']['archivos_procesados'], 0)
    
    def test_patrones_regex_validos(self):
        """Prueba que todos los patrones regex son válidos."""
        import re
        
        for categoria, patrones in self.analizador.patrones_sospechosos.items():
            for patron in patrones:
                with self.subTest(categoria=categoria, patron=patron):
                    try:
                        re.compile(patron)
                    except re.error as e:
                        self.fail(f"Patrón regex inválido en {categoria}: {patron} - {e}")


if __name__ == '__main__':
    # Configurar logging para tests
    import logging
    logging.basicConfig(level=logging.WARNING)
    
    # Ejecutar tests
    unittest.main(verbosity=2)
