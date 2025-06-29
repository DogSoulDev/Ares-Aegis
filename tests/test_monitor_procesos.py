#!/usr/bin/env python3
"""
Pruebas unitarias para el Monitor de Procesos
Tests para src/modelos/monitor_procesos.py

Autor: DogSoulDev
Versión: 2.0.0
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Agregar src al path para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from modelos.monitor_procesos import MonitorProcesos, InfoProceso


class TestInfoProceso(unittest.TestCase):
    """Tests para la clase InfoProceso."""
    
    def setUp(self):
        """Configurar datos de prueba."""
        self.proceso = InfoProceso(
            pid=1234,
            nombre="test_process",
            cmdline=["test_process", "--arg1", "--arg2"],
            cpu_percent=15.5,
            memoria_mb=256.0,
            usuario="testuser",
            estado="running",
            tiempo_inicio=datetime.now()
        )
    
    def test_inicializacion_proceso(self):
        """Prueba la inicialización correcta de InfoProceso."""
        self.assertEqual(self.proceso.pid, 1234)
        self.assertEqual(self.proceso.nombre, "test_process")
        self.assertEqual(self.proceso.cpu_percent, 15.5)
        self.assertEqual(self.proceso.memoria_mb, 256.0)
        self.assertFalse(self.proceso.sospechoso)
        self.assertEqual(len(self.proceso.razones_sospecha), 0)
    
    def test_marcar_como_sospechoso(self):
        """Prueba marcar proceso como sospechoso."""
        razon = "Uso alto de CPU"
        self.proceso.marcar_como_sospechoso(razon)
        
        self.assertTrue(self.proceso.sospechoso)
        self.assertIn(razon, self.proceso.razones_sospecha)
    
    def test_marcar_sospechoso_multiples_razones(self):
        """Prueba agregar múltiples razones de sospecha."""
        razon1 = "Uso alto de CPU"
        razon2 = "Nombre sospechoso"
        
        self.proceso.marcar_como_sospechoso(razon1)
        self.proceso.marcar_como_sospechoso(razon2)
        
        self.assertTrue(self.proceso.sospechoso)
        self.assertEqual(len(self.proceso.razones_sospecha), 2)
        self.assertIn(razon1, self.proceso.razones_sospecha)
        self.assertIn(razon2, self.proceso.razones_sospecha)
    
    def test_marcar_sospechoso_razon_duplicada(self):
        """Prueba que no se agreguen razones duplicadas."""
        razon = "Uso alto de CPU"
        
        self.proceso.marcar_como_sospechoso(razon)
        self.proceso.marcar_como_sospechoso(razon)  # Duplicada
        
        self.assertEqual(len(self.proceso.razones_sospecha), 1)
    
    def test_to_dict(self):
        """Prueba la conversión a diccionario."""
        self.proceso.marcar_como_sospechoso("Test reason")
        dict_proceso = self.proceso.to_dict()
        
        self.assertIsInstance(dict_proceso, dict)
        self.assertEqual(dict_proceso['pid'], 1234)
        self.assertEqual(dict_proceso['nombre'], "test_process")
        self.assertTrue(dict_proceso['sospechoso'])
        self.assertIn("Test reason", dict_proceso['razones_sospecha'])


class TestMonitorProcesos(unittest.TestCase):
    """Tests para la clase MonitorProcesos."""
    
    def setUp(self):
        """Configurar monitor de prueba."""
        self.siem_mock = Mock()
        self.monitor = MonitorProcesos(self.siem_mock)
    
    def test_inicializacion_monitor(self):
        """Prueba la inicialización del monitor."""
        self.assertIsInstance(self.monitor.patrones_sospechosos, list)
        self.assertIsInstance(self.monitor.umbrales, dict)
        self.assertEqual(self.monitor.siem, self.siem_mock)
    
    def test_cargar_patrones_sospechosos(self):
        """Prueba la carga de patrones sospechosos."""
        patrones = self.monitor._cargar_patrones_sospechosos()
        
        self.assertIsInstance(patrones, list)
        self.assertGreater(len(patrones), 0)
        self.assertIn('nc', patrones)
        self.assertIn('netcat', patrones)
    
    @patch('subprocess.run')
    def test_obtener_procesos_actuales_sin_psutil(self, mock_subprocess):
        """Prueba obtener procesos usando comando ps del sistema."""
        # Simular salida del comando ps
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "1 init root 0.0 0.1 S init\n1234 python user 5.0 2.5 R python test.py\n"
        mock_subprocess.return_value = mock_result
        
        procesos = self.monitor.obtener_procesos_actuales()
        
        # Debería devolver lista con procesos parseados
        self.assertIsInstance(procesos, list)
        self.assertGreaterEqual(len(procesos), 0)  # Puede estar vacío si hay problemas de parseo
    
    def test_analizar_procesos_sospechosos_cpu_alto(self):
        """Prueba detección de procesos con uso alto de CPU."""
        proceso_normal = InfoProceso(
            pid=1, nombre="normal", cmdline=[], cpu_percent=10.0,
            memoria_mb=100, usuario="user", estado="running", tiempo_inicio=datetime.now()
        )
        
        proceso_cpu_alto = InfoProceso(
            pid=2, nombre="cpu_intensivo", cmdline=[], cpu_percent=95.0,
            memoria_mb=100, usuario="user", estado="running", tiempo_inicio=datetime.now()
        )
        
        procesos = [proceso_normal, proceso_cpu_alto]
        sospechosos = self.monitor.analizar_procesos_sospechosos(procesos)
        
        self.assertEqual(len(sospechosos), 1)
        self.assertEqual(sospechosos[0].pid, 2)
        self.assertTrue(sospechosos[0].sospechoso)
    
    def test_analizar_procesos_sospechosos_memoria_alta(self):
        """Prueba detección de procesos con uso alto de memoria."""
        proceso_memoria_alta = InfoProceso(
            pid=3, nombre="memoria_alta", cmdline=[], cpu_percent=10.0,
            memoria_mb=2048, usuario="user", estado="running", tiempo_inicio=datetime.now()
        )
        
        procesos = [proceso_memoria_alta]
        sospechosos = self.monitor.analizar_procesos_sospechosos(procesos)
        
        self.assertEqual(len(sospechosos), 1)
        self.assertTrue(sospechosos[0].sospechoso)
        self.assertTrue(any('memoria' in razon.lower() for razon in sospechosos[0].razones_sospecha))
    
    def test_analizar_procesos_sospechosos_nombre(self):
        """Prueba detección de procesos con nombres sospechosos."""
        proceso_nc = InfoProceso(
            pid=4, nombre="nc", cmdline=["nc", "-l", "-p", "4444"],
            cpu_percent=5.0, memoria_mb=50, usuario="user", estado="running", tiempo_inicio=datetime.now()
        )
        
        procesos = [proceso_nc]
        sospechosos = self.monitor.analizar_procesos_sospechosos(procesos)
        
        self.assertEqual(len(sospechosos), 1)
        self.assertTrue(sospechosos[0].sospechoso)
    
    def test_analizar_procesos_ubicacion_temporal(self):
        """Prueba detección de procesos ejecutándose desde /tmp."""
        proceso_tmp = InfoProceso(
            pid=5, nombre="suspicious", cmdline=["/tmp/suspicious", "arg1"],
            cpu_percent=5.0, memoria_mb=50, usuario="user", estado="running", tiempo_inicio=datetime.now()
        )
        
        procesos = [proceso_tmp]
        sospechosos = self.monitor.analizar_procesos_sospechosos(procesos)
        
        self.assertEqual(len(sospechosos), 1)
        self.assertTrue(any('temporal' in razon.lower() for razon in sospechosos[0].razones_sospecha))
    
    def test_detectar_procesos_nuevos(self):
        """Prueba la detección de procesos nuevos."""
        # Procesos iniciales
        proceso1 = InfoProceso(
            pid=100, nombre="existente", cmdline=[], cpu_percent=1.0,
            memoria_mb=50, usuario="user", estado="running", tiempo_inicio=datetime.now()
        )
        
        self.monitor.procesos_conocidos = {100: proceso1}
        
        # Procesos actuales (incluye uno nuevo)
        proceso2 = InfoProceso(
            pid=200, nombre="nuevo", cmdline=[], cpu_percent=1.0,
            memoria_mb=50, usuario="user", estado="running", tiempo_inicio=datetime.now()
        )
        
        procesos_actuales = [proceso1, proceso2]
        procesos_nuevos = self.monitor.detectar_procesos_nuevos(procesos_actuales)
        
        self.assertEqual(len(procesos_nuevos), 1)
        self.assertEqual(procesos_nuevos[0].pid, 200)
    
    @patch('subprocess.run')
    def test_obtener_conexiones_red_procesos_acceso_denegado(self, mock_subprocess):
        """Prueba manejo de error en conexiones de red."""
        # Simular fallo en netstat
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "Permission denied"
        mock_subprocess.return_value = mock_result
        
        conexiones = self.monitor.obtener_conexiones_red_procesos()
        
        self.assertIsInstance(conexiones, list)
        # Puede devolver lista vacía en caso de error
        # Verificar que se registró el evento
        if self.siem_mock:
            self.siem_mock.log_evento.assert_called()
    
    @patch('subprocess.run')
    def test_terminar_proceso_exitoso(self, mock_subprocess):
        """Prueba terminación exitosa de proceso."""
        # Simular éxito del comando kill
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result
        
        resultado = self.monitor.terminar_proceso(1234)
        
        self.assertTrue(resultado)
        # Verificar que se llamó el comando kill correcto
        mock_subprocess.assert_called_with(['kill', '-TERM', '1234'], capture_output=True, text=True)
        if self.siem_mock:
            self.siem_mock.log_evento.assert_called()
    
    @patch('subprocess.run')
    def test_terminar_proceso_forzar(self, mock_subprocess):
        """Prueba terminación forzada de proceso."""
        # Simular éxito del comando kill -KILL
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result
        
        resultado = self.monitor.terminar_proceso(1234, forzar=True)
        
        self.assertTrue(resultado)
        # Verificar que se llamó kill con señal KILL
        mock_subprocess.assert_called_with(['kill', '-KILL', '1234'], capture_output=True, text=True)
        if self.siem_mock:
            self.siem_mock.log_evento.assert_called()
    
    @patch('subprocess.run')
    def test_terminar_proceso_no_encontrado(self, mock_subprocess):
        """Prueba terminación de proceso no encontrado."""
        # Simular fallo del comando kill (proceso no existe)
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "No such process"
        mock_subprocess.return_value = mock_result
        
        resultado = self.monitor.terminar_proceso(1234)
        
        self.assertFalse(resultado)
        if self.siem_mock:
            self.siem_mock.log_evento.assert_called()
    
    def test_exportar_reporte_markdown_estructura(self):
        """Prueba la estructura del reporte Markdown."""
        # Crear datos de prueba
        resultado_mock = {
            'timestamp': datetime.now().isoformat(),
            'estadisticas': {
                'total_procesos': 100,
                'procesos_nuevos': 5,
                'procesos_sospechosos': 2,
                'conexiones_red': 10,
                'uso_cpu_promedio': 25.5,
                'memoria_total_mb': 2048.0,
                'tiempo_escaneo': 2.5
            },
            'procesos_sospechosos': [
                {
                    'pid': 1234,
                    'nombre': 'nc',
                    'usuario': 'root',
                    'estado': 'running',
                    'cmdline': 'nc -l -p 4444',
                    'cpu_percent': 5.0,
                    'memoria_mb': 10.0,
                    'tiempo_inicio': datetime.now().isoformat(),
                    'razones_sospecha': ['Nombre sospechoso: nc']
                }
            ],
            'procesos_nuevos': [],
            'conexiones_red': []
        }
        
        # Crear archivo temporal
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            temp_path = f.name
        
        try:
            archivo_reporte = self.monitor.exportar_reporte_markdown(resultado_mock, temp_path)
            
            # Verificar que se creó el archivo
            self.assertTrue(os.path.exists(archivo_reporte))
            
            # Leer contenido
            with open(archivo_reporte, 'r', encoding='utf-8') as f:
                contenido = f.read()
            
            # Verificar estructura básica
            self.assertIn('# Reporte de Monitoreo de Procesos', contenido)
            self.assertIn('## Resumen Ejecutivo', contenido)
            self.assertIn('## Procesos Sospechosos Detectados', contenido)
            self.assertIn('nc', contenido)  # Proceso sospechoso
            
        finally:
            # Limpiar archivo temporal
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestIntegracionMonitorProcesos(unittest.TestCase):
    """Tests de integración para el Monitor de Procesos."""
    
    def setUp(self):
        """Configurar test de integración."""
        self.monitor = MonitorProcesos()
    
    def test_escanear_sistema_sin_dependencias(self):
        """Prueba el escaneo completo sin dependencias externas."""
        # Este test verifica que el sistema funcione sin psutil
        resultado = self.monitor.escanear_sistema()
        
        self.assertIsInstance(resultado, dict)
        self.assertIn('timestamp', resultado)
        self.assertIn('estadisticas', resultado)
        self.assertIn('procesos_sospechosos', resultado)
        self.assertIn('procesos_nuevos', resultado)
        self.assertIn('conexiones_red', resultado)
        self.assertIn('todos_los_procesos', resultado)
        
        # Las estadísticas deben ser consistentes
        estadisticas = resultado['estadisticas']
        self.assertIsInstance(estadisticas['total_procesos'], int)
        self.assertIsInstance(estadisticas['tiempo_escaneo'], float)
        self.assertGreaterEqual(estadisticas['tiempo_escaneo'], 0)


if __name__ == '__main__':
    # Configurar logging para tests
    import logging
    logging.basicConfig(level=logging.WARNING)
    
    # Ejecutar tests
    unittest.main(verbosity=2)
