#!/usr/bin/env python3
"""
Pruebas unitarias para el Monitor de Red
Tests para src/modelos/monitor_red.py

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

from modelos.monitor_red import MonitorRed, ConexionRed, PuertoAbierto


class TestConexionRed(unittest.TestCase):
    """Tests para la clase ConexionRed."""
    
    def setUp(self):
        """Configurar datos de prueba."""
        self.conexion = ConexionRed(
            protocolo="TCP",
            direccion_local="192.168.1.100",
            puerto_local=22,
            direccion_remota="192.168.1.200",
            puerto_remoto=54321,
            estado="ESTABLISHED",
            proceso="sshd"
        )
    
    def test_inicializacion_conexion(self):
        """Prueba la inicialización correcta de ConexionRed."""
        self.assertEqual(self.conexion.protocolo, "TCP")
        self.assertEqual(self.conexion.direccion_local, "192.168.1.100")
        self.assertEqual(self.conexion.puerto_local, 22)
        self.assertEqual(self.conexion.direccion_remota, "192.168.1.200")
        self.assertEqual(self.conexion.puerto_remoto, 54321)
        self.assertEqual(self.conexion.estado, "ESTABLISHED")
        self.assertEqual(self.conexion.proceso, "sshd")
        self.assertFalse(self.conexion.sospechosa)
        self.assertEqual(len(self.conexion.razones_sospecha), 0)
    
    def test_marcar_como_sospechosa(self):
        """Prueba marcar conexión como sospechosa."""
        razon = "Puerto sospechoso"
        self.conexion.marcar_como_sospechosa(razon)
        
        self.assertTrue(self.conexion.sospechosa)
        self.assertIn(razon, self.conexion.razones_sospecha)
    
    def test_to_dict(self):
        """Prueba la conversión a diccionario."""
        self.conexion.marcar_como_sospechosa("Test reason")
        dict_conexion = self.conexion.to_dict()
        
        self.assertIsInstance(dict_conexion, dict)
        self.assertEqual(dict_conexion['protocolo'], "TCP")
        self.assertEqual(dict_conexion['puerto_local'], 22)
        self.assertTrue(dict_conexion['sospechosa'])


class TestPuertoAbierto(unittest.TestCase):
    """Tests para la clase PuertoAbierto."""
    
    def setUp(self):
        """Configurar datos de prueba."""
        self.puerto = PuertoAbierto(
            puerto=80,
            protocolo="TCP",
            servicio="HTTP",
            proceso="apache2",
            direccion="0.0.0.0"
        )
    
    def test_inicializacion_puerto(self):
        """Prueba la inicialización correcta de PuertoAbierto."""
        self.assertEqual(self.puerto.puerto, 80)
        self.assertEqual(self.puerto.protocolo, "TCP")
        self.assertEqual(self.puerto.servicio, "HTTP")
        self.assertEqual(self.puerto.proceso, "apache2")
        self.assertEqual(self.puerto.direccion, "0.0.0.0")
        self.assertFalse(self.puerto.sospechoso)
    
    def test_marcar_como_sospechoso(self):
        """Prueba marcar puerto como sospechoso."""
        razon = "Puerto en lista de malware"
        self.puerto.marcar_como_sospechoso(razon)
        
        self.assertTrue(self.puerto.sospechoso)
        self.assertIn(razon, self.puerto.razones_sospecha)


class TestMonitorRed(unittest.TestCase):
    """Tests para la clase MonitorRed."""
    
    def setUp(self):
        """Configurar monitor de prueba."""
        self.siem_mock = Mock()
        self.monitor = MonitorRed(self.siem_mock)
    
    def test_inicializacion_monitor(self):
        """Prueba la inicialización del monitor."""
        self.assertIsInstance(self.monitor.puertos_sospechosos, list)
        self.assertIsInstance(self.monitor.rangos_ip_privadas, list)
        self.assertIsInstance(self.monitor.servicios_conocidos, dict)
        self.assertEqual(self.monitor.siem, self.siem_mock)
    
    def test_cargar_puertos_sospechosos(self):
        """Prueba la carga de puertos sospechosos."""
        puertos = self.monitor._cargar_puertos_sospechosos()
        
        self.assertIsInstance(puertos, list)
        self.assertGreater(len(puertos), 0)
        self.assertIn(1337, puertos)
        self.assertIn(31337, puertos)
        self.assertIn(4444, puertos)
    
    def test_cargar_servicios_conocidos(self):
        """Prueba la carga de servicios conocidos."""
        servicios = self.monitor._cargar_servicios_conocidos()
        
        self.assertIsInstance(servicios, dict)
        self.assertEqual(servicios[80], 'HTTP')
        self.assertEqual(servicios[443], 'HTTPS')
        self.assertEqual(servicios[22], 'SSH')
    
    def test_es_ip_privada_verdadero(self):
        """Prueba detección de IPs privadas."""
        ips_privadas = [
            "192.168.1.1",
            "10.0.0.1",
            "172.16.0.1",
            "127.0.0.1"
        ]
        
        for ip in ips_privadas:
            with self.subTest(ip=ip):
                self.assertTrue(self.monitor._es_ip_privada(ip))
    
    def test_es_ip_privada_falso(self):
        """Prueba detección de IPs públicas."""
        ips_publicas = [
            "8.8.8.8",
            "1.1.1.1",
            "208.67.222.222"
        ]
        
        for ip in ips_publicas:
            with self.subTest(ip=ip):
                self.assertFalse(self.monitor._es_ip_privada(ip))
    
    def test_es_ip_privada_ip_invalida(self):
        """Prueba manejo de IPs inválidas."""
        ips_invalidas = [
            "256.256.256.256",
            "invalid.ip",
            "192.168.1"
        ]
        
        for ip in ips_invalidas:
            with self.subTest(ip=ip):
                self.assertFalse(self.monitor._es_ip_privada(ip))
    
    def test_parsear_netstat_tcp(self):
        """Prueba el parseo de salida netstat TCP."""
        salida_netstat = """Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      1234/sshd
tcp        0      0 127.0.0.1:3306          0.0.0.0:*               LISTEN      5678/mysqld
tcp        0      0 192.168.1.100:45678     192.168.1.200:80        ESTABLISHED 9999/firefox"""
        
        conexiones = self.monitor._parsear_netstat(salida_netstat)
        
        self.assertEqual(len(conexiones), 3)
        
        # Verificar conexión SSH
        ssh_conn = conexiones[0]
        self.assertEqual(ssh_conn.protocolo, "TCP")
        self.assertEqual(ssh_conn.puerto_local, 22)
        self.assertEqual(ssh_conn.estado, "LISTEN")
    
    def test_parsear_ss_tcp(self):
        """Prueba el parseo de salida ss TCP."""
        salida_ss = """State    Recv-Q   Send-Q     Local Address:Port       Peer Address:Port
LISTEN   0        128              0.0.0.0:22                  0.0.0.0:*
LISTEN   0        80             127.0.0.1:3306                0.0.0.0:*
ESTAB    0        0          192.168.1.100:45678       192.168.1.200:80"""
        
        conexiones = self.monitor._parsear_ss(salida_ss)
        
        self.assertEqual(len(conexiones), 3)
        
        # Verificar que se parsearon correctamente
        ssh_conn = next((c for c in conexiones if c.puerto_local == 22), None)
        self.assertIsNotNone(ssh_conn)
        self.assertEqual(ssh_conn.protocolo, "TCP")
    
    def test_verificar_puerto_tcp_cerrado(self):
        """Prueba verificación de puerto TCP cerrado."""
        # Puerto que debería estar cerrado
        resultado = self.monitor._verificar_puerto_tcp(65432, timeout=0.1)
        self.assertFalse(resultado)
    
    @patch('subprocess.run')
    def test_obtener_conexiones_activas_netstat_exitoso(self, mock_run):
        """Prueba obtener conexiones con netstat exitoso."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "tcp 0 0 0.0.0.0:22 0.0.0.0:* LISTEN"
        mock_run.return_value = mock_result
        
        conexiones = self.monitor.obtener_conexiones_activas()
        
        self.assertIsInstance(conexiones, list)
        mock_run.assert_called_with(['netstat', '-tuln'], capture_output=True, text=True, timeout=30)
    
    @patch('subprocess.run')
    def test_obtener_conexiones_activas_netstat_falla_ss_exitoso(self, mock_run):
        """Prueba fallback a ss cuando netstat falla."""
        # Primera llamada (netstat) falla, segunda (ss) exitosa
        mock_run.side_effect = [
            Mock(returncode=1, stdout=""),  # netstat falla
            Mock(returncode=0, stdout="tcp LISTEN 0.0.0.0:22")  # ss exitoso
        ]
        
        conexiones = self.monitor.obtener_conexiones_activas()
        
        self.assertIsInstance(conexiones, list)
        self.assertEqual(mock_run.call_count, 2)
    
    def test_analizar_conexiones_sospechosas_puerto(self):
        """Prueba análisis de conexiones con puertos sospechosos."""
        conexion_normal = ConexionRed("TCP", "192.168.1.1", 22, "", 0, "LISTEN")
        conexion_sospechosa = ConexionRed("TCP", "192.168.1.1", 1337, "", 0, "LISTEN")
        
        conexiones = [conexion_normal, conexion_sospechosa]
        sospechosas = self.monitor.analizar_conexiones_sospechosas(conexiones)
        
        self.assertEqual(len(sospechosas), 1)
        self.assertEqual(sospechosas[0].puerto_local, 1337)
        self.assertTrue(sospechosas[0].sospechosa)
    
    def test_analizar_conexiones_sospechosas_ip_externa(self):
        """Prueba análisis de conexiones a IPs externas."""
        conexion_interna = ConexionRed("TCP", "192.168.1.1", 22, "192.168.1.2", 54321, "ESTABLISHED")
        conexion_externa = ConexionRed("TCP", "192.168.1.1", 80, "8.8.8.8", 12345, "ESTABLISHED")
        
        conexiones = [conexion_interna, conexion_externa]
        sospechosas = self.monitor.analizar_conexiones_sospechosas(conexiones)
        
        self.assertEqual(len(sospechosas), 1)
        self.assertEqual(sospechosas[0].direccion_remota, "8.8.8.8")
    
    def test_analizar_puertos_sospechosos_lista_malware(self):
        """Prueba análisis de puertos en lista de malware."""
        puerto_normal = PuertoAbierto(80, "TCP", "HTTP")
        puerto_sospechoso = PuertoAbierto(31337, "TCP", "Desconocido")
        
        puertos = [puerto_normal, puerto_sospechoso]
        sospechosos = self.monitor.analizar_puertos_sospechosos(puertos)
        
        self.assertEqual(len(sospechosos), 1)
        self.assertEqual(sospechosos[0].puerto, 31337)
    
    def test_analizar_puertos_sospechosos_puerto_alto(self):
        """Prueba análisis de puertos muy altos."""
        puerto_alto = PuertoAbierto(60000, "TCP", "Desconocido")
        
        puertos = [puerto_alto]
        sospechosos = self.monitor.analizar_puertos_sospechosos(puertos)
        
        self.assertEqual(len(sospechosos), 1)
        self.assertTrue(any('muy alto' in razon.lower() for razon in sospechosos[0].razones_sospecha))
    
    @patch('subprocess.run')
    def test_escanear_red_local_nmap_exitoso(self, mock_run):
        """Prueba escaneo de red local con nmap."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = """Nmap scan report for 192.168.1.1
Host is up (0.001s latency).
Nmap scan report for 192.168.1.100
Host is up (0.002s latency)."""
        mock_run.return_value = mock_result
        
        dispositivos = self.monitor.escanear_red_local()
        
        self.assertIsInstance(dispositivos, list)
        self.assertGreaterEqual(len(dispositivos), 0)
    
    @patch('subprocess.run')
    def test_escanear_red_local_nmap_falla_ping_fallback(self, mock_run):
        """Prueba fallback a ping cuando nmap falla."""
        # nmap falla, ping exitoso para una IP
        mock_run.side_effect = [
            Mock(returncode=1, stdout=""),  # nmap falla
            Mock(returncode=0),  # ping exitoso
            Mock(returncode=1),  # ping falla
            Mock(returncode=1),  # ping falla
            Mock(returncode=1),  # ping falla
            Mock(returncode=1),  # ping falla
        ]
        
        with patch('socket.socket') as mock_socket:
            mock_sock = Mock()
            mock_sock.getsockname.return_value = ('192.168.1.100', 12345)
            mock_socket.return_value = mock_sock
            
            dispositivos = self.monitor.escanear_red_local()
            
            self.assertIsInstance(dispositivos, list)
    
    def test_exportar_reporte_markdown_estructura(self):
        """Prueba la estructura del reporte Markdown."""
        # Crear datos de prueba
        resultado_mock = {
            'timestamp': datetime.now().isoformat(),
            'estadisticas': {
                'total_conexiones': 10,
                'conexiones_sospechosas': 2,
                'total_puertos_abiertos': 5,
                'puertos_sospechosos': 1,
                'dispositivos_en_red': 3,
                'tiempo_escaneo': 1.5
            },
            'conexiones_activas': [],
            'conexiones_sospechosas': [
                {
                    'protocolo': 'TCP',
                    'direccion_local': '192.168.1.1',
                    'puerto_local': 1337,
                    'direccion_remota': '8.8.8.8',
                    'puerto_remoto': 4444,
                    'estado': 'ESTABLISHED',
                    'razones_sospecha': ['Puerto sospechoso: 1337']
                }
            ],
            'puertos_abiertos': [],
            'puertos_sospechosos': [
                {
                    'puerto': 31337,
                    'protocolo': 'TCP',
                    'servicio': 'Desconocido',
                    'razones_sospecha': ['Puerto en lista de malware conocido']
                }
            ],
            'dispositivos_red': [
                {'ip': '192.168.1.1', 'estado': 'activo', 'metodo_deteccion': 'nmap'}
            ]
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
            self.assertIn('# Reporte de Monitoreo de Red', contenido)
            self.assertIn('## Resumen Ejecutivo', contenido)
            self.assertIn('## Conexiones Sospechosas Detectadas', contenido)
            self.assertIn('## Puertos Sospechosos Detectados', contenido)
            self.assertIn('1337', contenido)  # Puerto sospechoso
            
        finally:
            # Limpiar archivo temporal
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestIntegracionMonitorRed(unittest.TestCase):
    """Tests de integración para el Monitor de Red."""
    
    def setUp(self):
        """Configurar test de integración."""
        self.monitor = MonitorRed()
    
    def test_escanear_sistema_red_completo(self):
        """Prueba el escaneo completo del sistema de red."""
        resultado = self.monitor.escanear_sistema_red()
        
        self.assertIsInstance(resultado, dict)
        self.assertIn('timestamp', resultado)
        self.assertIn('estadisticas', resultado)
        self.assertIn('conexiones_activas', resultado)
        self.assertIn('conexiones_sospechosas', resultado)
        self.assertIn('puertos_abiertos', resultado)
        self.assertIn('puertos_sospechosos', resultado)
        self.assertIn('dispositivos_red', resultado)
        
        # Verificar estadísticas
        estadisticas = resultado['estadisticas']
        self.assertIsInstance(estadisticas['total_conexiones'], int)
        self.assertIsInstance(estadisticas['tiempo_escaneo'], float)
        self.assertGreaterEqual(estadisticas['tiempo_escaneo'], 0)


if __name__ == '__main__':
    # Configurar logging para tests
    import logging
    logging.basicConfig(level=logging.WARNING)
    
    # Ejecutar tests
    unittest.main(verbosity=2)
