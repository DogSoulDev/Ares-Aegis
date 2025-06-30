#!/usr/bin/env python3
"""
Tests para el Escaneador de Vulnerabilidades
Pruebas completas para detección de vulnerabilidades en software instalado.

Autor: DogSoulDev
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import subprocess
import json
import sys
import os

# Añadir el directorio padre al path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.modelos.escaneador_vulnerabilidades import (
    EscaneadorVulnerabilidades, DetectorSoftware, BaseDatosVulnerabilidades, VulnerabilidadDetectada
)
from src.modelos.siem import SIEM


class TestVulnerabilidadDetectada(unittest.TestCase):
    """Tests para la clase VulnerabilidadDetectada."""
    
    def test_inicializacion_vulnerabilidad(self):
        """Test de inicialización de vulnerabilidad."""
        vuln = VulnerabilidadDetectada(
            cve_id="CVE-2021-44228",
            software="apache2",
            version="2.4.41",
            descripcion="Log4j vulnerability",
            severidad="critica"
        )
        
        self.assertEqual(vuln.cve_id, "CVE-2021-44228")
        self.assertEqual(vuln.software, "apache2")
        self.assertEqual(vuln.version, "2.4.41")
        self.assertEqual(vuln.severidad, "CRITICA")  # Debe normalizarse a mayúsculas
        self.assertGreater(vuln.puntuacion_cvss, 0)
        self.assertIsInstance(vuln.recomendaciones, list)
        self.assertGreater(len(vuln.recomendaciones), 0)
    
    def test_calculo_puntuacion_cvss(self):
        """Test de cálculo de puntuación CVSS."""
        vuln_critica = VulnerabilidadDetectada("CVE-1", "test", "1.0", "desc", "CRITICA")
        vuln_alta = VulnerabilidadDetectada("CVE-2", "test", "1.0", "desc", "ALTA")
        vuln_media = VulnerabilidadDetectada("CVE-3", "test", "1.0", "desc", "MEDIA")
        vuln_baja = VulnerabilidadDetectada("CVE-4", "test", "1.0", "desc", "BAJA")
        
        self.assertGreater(vuln_critica.puntuacion_cvss, vuln_alta.puntuacion_cvss)
        self.assertGreater(vuln_alta.puntuacion_cvss, vuln_media.puntuacion_cvss)
        self.assertGreater(vuln_media.puntuacion_cvss, vuln_baja.puntuacion_cvss)
    
    def test_recomendaciones_severidad_critica(self):
        """Test de recomendaciones para vulnerabilidades críticas."""
        vuln = VulnerabilidadDetectada("CVE-1", "test", "1.0", "desc", "CRITICA")
        
        # Vulnerabilidades críticas deben tener recomendaciones adicionales
        self.assertGreater(len(vuln.recomendaciones), 3)
        self.assertTrue(any("deshabilitar" in rec.lower() for rec in vuln.recomendaciones))
    
    def test_to_dict(self):
        """Test de conversión a diccionario."""
        vuln = VulnerabilidadDetectada("CVE-1", "test", "1.0", "desc", "ALTA")
        dict_resultado = vuln.to_dict()
        
        self.assertIsInstance(dict_resultado, dict)
        self.assertEqual(dict_resultado['cve_id'], "CVE-1")
        self.assertEqual(dict_resultado['software'], "test")
        self.assertEqual(dict_resultado['severidad'], "ALTA")
        self.assertIn('puntuacion_cvss', dict_resultado)
        self.assertIn('recomendaciones', dict_resultado)


class TestDetectorSoftware(unittest.TestCase):
    """Tests para la clase DetectorSoftware."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        self.detector = DetectorSoftware()
    
    @patch('subprocess.run')
    def test_detectar_dpkg_exitoso(self, mock_run):
        """Test de detección exitosa con dpkg."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Status=Not/Inst/Conf-files/Unpacked/halF-conf/Half-inst/trig-aWait/Trig-pend\n"
                   "|/ Err?=(none)/Reinst-required (Status,Err: uppercase=bad)\n"
                   "||/ Name           Version      Architecture Description\n"
                   "+++-==============-============-============-================================\n"
                   "ii  apache2        2.4.41-4     amd64        Apache HTTP Server\n"
                   "ii  nginx          1.18.0-6     amd64        small, powerful web server\n"
        )
        
        software = self.detector._detectar_dpkg()
        
        self.assertGreater(len(software), 0)
        nombres = [s['nombre'] for s in software]
        self.assertIn('apache2', nombres)
        self.assertIn('nginx', nombres)
        
        # Verificar estructura
        for soft in software:
            self.assertIn('nombre', soft)
            self.assertIn('version', soft)
            self.assertIn('tipo', soft)
            self.assertEqual(soft['tipo'], 'package')
    
    @patch('subprocess.run')
    def test_detectar_dpkg_fallo(self, mock_run):
        """Test de manejo de fallo en dpkg."""
        mock_run.side_effect = subprocess.CalledProcessError(1, 'dpkg')
        
        software = self.detector._detectar_dpkg()
        self.assertEqual(len(software), 0)
    
    @patch('subprocess.run')
    def test_detectar_pip_exitoso(self, mock_run):
        """Test de detección exitosa con pip."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout='[{"name": "requests", "version": "2.25.1"}, {"name": "numpy", "version": "1.21.0"}]'
        )
        
        software = self.detector._detectar_pip()
        
        self.assertGreater(len(software), 0)
        nombres = [s['nombre'] for s in software]
        self.assertIn('python-requests', nombres)
        self.assertIn('python-numpy', nombres)
        
        # Verificar tipo
        for soft in software:
            self.assertEqual(soft['tipo'], 'python_package')
    
    @patch('subprocess.run')
    def test_detectar_npm_exitoso(self, mock_run):
        """Test de detección exitosa con npm."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout='{"dependencies": {"express": {"version": "4.17.1"}, "lodash": {"version": "4.17.21"}}}'
        )
        
        software = self.detector._detectar_npm()
        
        self.assertGreater(len(software), 0)
        nombres = [s['nombre'] for s in software]
        self.assertIn('node-express', nombres)
        self.assertIn('node-lodash', nombres)
    
    @patch('subprocess.run')
    def test_detectar_binarios_comunes(self, mock_run):
        """Test de detección de binarios comunes."""
        def side_effect(*args, **kwargs):
            comando = args[0]
            if 'apache2' in comando:
                return Mock(returncode=0, stdout="Server version: Apache/2.4.41")
            elif 'nginx' in comando:
                return Mock(returncode=0, stderr="nginx version: nginx/1.18.0")
            else:
                return Mock(returncode=1, stdout="", stderr="")
        
        mock_run.side_effect = side_effect
        
        software = self.detector._detectar_binarios_comunes()
        
        nombres = [s['nombre'] for s in software]
        self.assertIn('apache2', nombres)
        self.assertIn('nginx', nombres)
    
    def test_extraer_version(self):
        """Test de extracción de versión de output."""
        casos_test = [
            ("Apache/2.4.41 (Ubuntu)", "2.4.41"),
            ("nginx version: nginx/1.18.0", "1.18.0"),
            ("Python 3.8.10", "3.8.10"),
            ("version 1.2.3", "1.2.3"),
            ("v2.1.0", "2.1.0"),
        ]
        
        for output, version_esperada in casos_test:
            version_extraida = self.detector._extraer_version(output)
            self.assertEqual(version_extraida, version_esperada)
    
    def test_detectar_todo_el_software_sin_duplicados(self):
        """Test de detección completa sin duplicados."""
        with patch.object(self.detector, '_detectar_dpkg') as mock_dpkg, \
             patch.object(self.detector, '_detectar_pip') as mock_pip:
            
            # Simular software duplicado
            mock_dpkg.return_value = [
                {'nombre': 'python3', 'version': '3.8.10', 'tipo': 'package', 'descripcion': ''}
            ]
            mock_pip.return_value = [
                {'nombre': 'python3', 'version': '3.8.10', 'tipo': 'python_package', 'descripcion': ''}
            ]
            
            software = self.detector.detectar_todo_el_software()
            
            # Solo debe aparecer una vez
            nombres_versiones = [(s['nombre'], s['version']) for s in software]
            self.assertEqual(len(nombres_versiones), len(set(nombres_versiones)))


class TestBaseDatosVulnerabilidades(unittest.TestCase):
    """Tests para la clase BaseDatosVulnerabilidades."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        self.base_datos = BaseDatosVulnerabilidades()
    
    def test_cargar_vulnerabilidades_estaticas(self):
        """Test de carga de vulnerabilidades estáticas."""
        vulnerabilidades = self.base_datos.vulnerabilidades
        
        self.assertIsInstance(vulnerabilidades, dict)
        self.assertIn('apache2', vulnerabilidades)
        self.assertIn('nginx', vulnerabilidades)
        
        # Verificar estructura de vulnerabilidades
        apache_vulns = vulnerabilidades['apache2']
        self.assertGreater(len(apache_vulns), 0)
        
        for vuln in apache_vulns:
            self.assertIn('cve_id', vuln)
            self.assertIn('versiones_afectadas', vuln)
            self.assertIn('descripcion', vuln)
            self.assertIn('severidad', vuln)
    
    def test_buscar_vulnerabilidades_encontradas(self):
        """Test de búsqueda exitosa de vulnerabilidades."""
        vulnerabilidades = self.base_datos.buscar_vulnerabilidades('apache2', '2.4.49')
        
        self.assertGreater(len(vulnerabilidades), 0)
        
        # Verificar que todas las vulnerabilidades tienen CVE
        for vuln in vulnerabilidades:
            self.assertTrue(vuln['cve_id'].startswith('CVE-'))
    
    def test_buscar_vulnerabilidades_no_encontradas(self):
        """Test de búsqueda sin vulnerabilidades."""
        vulnerabilidades = self.base_datos.buscar_vulnerabilidades('software_inexistente', '1.0.0')
        
        self.assertEqual(len(vulnerabilidades), 0)
    
    def test_convertir_version_a_numero(self):
        """Test de conversión de versión a tupla numérica."""
        casos_test = [
            ("2.4.41", (2, 4, 41)),
            ("1.18.0", (1, 18, 0)),
            ("3.8", (3, 8)),
            ("1.0.0-beta", (1, 0, 0)),
        ]
        
        for version_str, version_tuple in casos_test:
            resultado = self.base_datos._convertir_version_a_numero(version_str)
            self.assertEqual(resultado, version_tuple)
    
    def test_coincide_patron_version(self):
        """Test de coincidencia de patrones de versión."""
        version = (2, 4, 41)
        
        # Test de patrones
        self.assertTrue(self.base_datos._coincide_patron_version(version, "< 2.4.52"))
        self.assertFalse(self.base_datos._coincide_patron_version(version, "< 2.4.40"))
        self.assertTrue(self.base_datos._coincide_patron_version(version, "2.4.41"))
        self.assertFalse(self.base_datos._coincide_patron_version(version, "2.4.42"))
    
    def test_version_vulnerable(self):
        """Test de determinación de versión vulnerable."""
        # Versión vulnerable
        self.assertTrue(
            self.base_datos._version_vulnerable("2.4.49", ["2.4.49", "2.4.50"])
        )
        
        # Versión no vulnerable
        self.assertFalse(
            self.base_datos._version_vulnerable("2.4.52", ["< 2.4.52"])
        )
        
        # Versión vulnerable por patrón
        self.assertTrue(
            self.base_datos._version_vulnerable("2.4.41", ["< 2.4.52"])
        )


class TestEscaneadorVulnerabilidades(unittest.TestCase):
    """Tests para la clase EscaneadorVulnerabilidades."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        self.siem_mock = Mock(spec=SIEM)
        self.escaneador = EscaneadorVulnerabilidades(siem=self.siem_mock)
    
    def test_inicializacion(self):
        """Test de inicialización del escaneador."""
        self.assertIsInstance(self.escaneador.detector_software, DetectorSoftware)
        self.assertIsInstance(self.escaneador.base_datos, BaseDatosVulnerabilidades)
        self.assertEqual(self.escaneador.siem, self.siem_mock)
    
    @patch.object(DetectorSoftware, 'detectar_todo_el_software')
    def test_escanear_sistema_completo(self, mock_detectar):
        """Test de escaneo completo del sistema."""
        # Simular software instalado
        mock_detectar.return_value = [
            {'nombre': 'apache2', 'version': '2.4.49', 'tipo': 'package', 'descripcion': ''},
            {'nombre': 'nginx', 'version': '1.18.0', 'tipo': 'package', 'descripcion': ''},
            {'nombre': 'software_seguro', 'version': '1.0.0', 'tipo': 'package', 'descripcion': ''}
        ]
        
        resultado = self.escaneador.escanear_sistema_completo()
        
        # Verificar estructura del resultado
        self.assertIn('timestamp_escaneo', resultado)
        self.assertIn('tiempo_escaneo_segundos', resultado)
        self.assertIn('total_software', resultado)
        self.assertIn('software_vulnerable', resultado)
        self.assertIn('total_vulnerabilidades', resultado)
        self.assertIn('estadisticas', resultado)
        self.assertIn('vulnerabilidades', resultado)
        
        # Verificar números
        self.assertEqual(resultado['total_software'], 3)
        self.assertGreater(resultado['total_vulnerabilidades'], 0)
        self.assertGreater(resultado['software_vulnerable'], 0)
        
        # Verificar logging SIEM
        self.siem_mock.log_evento.assert_called()
    
    @patch.object(DetectorSoftware, 'detectar_todo_el_software')
    def test_escanear_software_especifico(self, mock_detectar):
        """Test de escaneo de software específico."""
        mock_detectar.return_value = [
            {'nombre': 'apache2', 'version': '2.4.49', 'tipo': 'package', 'descripcion': ''},
            {'nombre': 'nginx', 'version': '1.18.0', 'tipo': 'package', 'descripcion': ''}
        ]
        
        resultado = self.escaneador.escanear_software_especifico('apache')
        
        self.assertIn('software_buscado', resultado)
        self.assertIn('software_encontrado', resultado)
        self.assertIn('vulnerabilidades', resultado)
        self.assertEqual(resultado['software_buscado'], 'apache')
        
        # Debe encontrar apache2
        nombres = [s['nombre'] for s in resultado['software_encontrado']]
        self.assertIn('apache2', nombres)
    
    def test_calcular_estadisticas_sin_vulnerabilidades(self):
        """Test de cálculo de estadísticas sin vulnerabilidades."""
        software = [{'nombre': 'test', 'version': '1.0'}]
        vulnerabilidades = []
        
        estadisticas = self.escaneador._calcular_estadisticas(software, vulnerabilidades)
        
        self.assertEqual(estadisticas['por_severidad'], {})
        self.assertIsNone(estadisticas['software_mas_vulnerable'])
        self.assertEqual(estadisticas['puntuacion_riesgo_promedio'], 0.0)
        self.assertEqual(estadisticas['porcentaje_software_vulnerable'], 0.0)
    
    def test_calcular_estadisticas_con_vulnerabilidades(self):
        """Test de cálculo de estadísticas con vulnerabilidades."""
        software = [
            {'nombre': 'apache2', 'version': '2.4.49'},
            {'nombre': 'nginx', 'version': '1.18.0'}
        ]
        
        vulnerabilidades = [
            VulnerabilidadDetectada('CVE-1', 'apache2', '2.4.49', 'desc1', 'CRITICA'),
            VulnerabilidadDetectada('CVE-2', 'apache2', '2.4.49', 'desc2', 'ALTA'),
            VulnerabilidadDetectada('CVE-3', 'nginx', '1.18.0', 'desc3', 'MEDIA'),
        ]
        
        estadisticas = self.escaneador._calcular_estadisticas(software, vulnerabilidades)
        
        # Verificar severidades
        self.assertEqual(estadisticas['por_severidad']['CRITICA'], 1)
        self.assertEqual(estadisticas['por_severidad']['ALTA'], 1)
        self.assertEqual(estadisticas['por_severidad']['MEDIA'], 1)
        
        # Verificar software más vulnerable
        self.assertEqual(estadisticas['software_mas_vulnerable'][0], 'apache2')
        self.assertEqual(estadisticas['software_mas_vulnerable'][1], 2)
        
        # Verificar puntuación promedio
        self.assertGreater(estadisticas['puntuacion_riesgo_promedio'], 0)
        
        # Verificar porcentaje vulnerable
        self.assertEqual(estadisticas['porcentaje_software_vulnerable'], 100.0)
    
    def test_escaneador_sin_siem(self):
        """Test de funcionamiento sin SIEM."""
        escaneador_sin_siem = EscaneadorVulnerabilidades()
        
        # Debe inicializarse sin errores
        self.assertIsNone(escaneador_sin_siem.siem)
        self.assertIsInstance(escaneador_sin_siem.detector_software, DetectorSoftware)
    
    def test_generar_reporte_markdown(self):
        """Test de generación de reporte Markdown."""
        resultado_escaneo = {
            'timestamp_escaneo': '2023-01-01T00:00:00',
            'tiempo_escaneo_segundos': 5.5,
            'total_software': 10,
            'software_vulnerable': 3,
            'total_vulnerabilidades': 5,
            'estadisticas': {
                'por_severidad': {'CRITICA': 1, 'ALTA': 2, 'MEDIA': 2},
                'software_mas_vulnerable': ('apache2', 3),
                'puntuacion_riesgo_promedio': 7.2,
                'porcentaje_software_vulnerable': 30.0
            },
            'vulnerabilidades': [
                {
                    'cve_id': 'CVE-2021-44228',
                    'software': 'apache2',
                    'version': '2.4.49',
                    'severidad': 'CRITICA',
                    'puntuacion_cvss': 9.5,
                    'descripcion': 'Test vulnerability',
                    'recomendaciones': ['Update software', 'Apply patches']
                }
            ]
        }
        
        reporte = self.escaneador.generar_reporte_markdown(resultado_escaneo)
        
        self.assertIsInstance(reporte, str)
        self.assertIn("# Reporte de Escaneo de Vulnerabilidades", reporte)
        self.assertIn("## Resumen Ejecutivo", reporte)
        self.assertIn("## Distribución por Severidad", reporte)
        self.assertIn("🔴 **CRITICA:** 1", reporte)
        self.assertIn("CVE-2021-44228", reporte)
        self.assertIn("apache2", reporte)


class TestIntegracionCompleta(unittest.TestCase):
    """Tests de integración completa del escaneador."""
    
    def setUp(self):
        """Configuración inicial para tests de integración."""
        self.siem = SIEM()
        self.escaneador = EscaneadorVulnerabilidades(siem=self.siem)
    
    @patch('subprocess.run')
    def test_flujo_completo_deteccion_vulnerabilidades(self, mock_run):
        """Test del flujo completo de detección de vulnerabilidades."""
        # Simular output de dpkg con software vulnerable
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Status=Not/Inst/Conf-files/Unpacked/halF-conf/Half-inst/trig-aWait/Trig-pend\n"
                   "|/ Err?=(none)/Reinst-required (Status,Err: uppercase=bad)\n"
                   "||/ Name           Version      Architecture Description\n"
                   "+++-==============-============-============-================================\n"
                   "ii  apache2        2.4.49-1     amd64        Apache HTTP Server\n"
                   "ii  nginx          1.18.0-6     amd64        nginx web server\n"
                   "ii  openssh-client 7.9p1-10     amd64        OpenSSH client\n"
        )
        
        # Realizar escaneo completo
        resultado = self.escaneador.escanear_sistema_completo()
        
        # Verificar que se detectó software
        self.assertGreater(resultado['total_software'], 0)
        
        # Verificar que se encontraron vulnerabilidades
        self.assertGreater(resultado['total_vulnerabilidades'], 0)
        
        # Verificar que apache2 2.4.49 tiene vulnerabilidades conocidas
        software_vulnerable = resultado['software_con_vulnerabilidades']
        nombres_vulnerables = [s['nombre'] for s in software_vulnerable]
        self.assertIn('apache2', nombres_vulnerables)
        
        # Verificar estructura de vulnerabilidades
        vulnerabilidades = resultado['vulnerabilidades']
        for vuln in vulnerabilidades:
            self.assertIn('cve_id', vuln)
            self.assertIn('software', vuln)
            self.assertIn('severidad', vuln)
            self.assertTrue(vuln['cve_id'].startswith('CVE-'))
        
        # Generar reporte
        reporte = self.escaneador.generar_reporte_markdown(resultado)
        self.assertIn('apache2', reporte)
        self.assertIn('CVE-', reporte)
        
        # Verificar escaneo específico
        resultado_apache = self.escaneador.escanear_software_especifico('apache')
        self.assertGreater(len(resultado_apache['vulnerabilidades']), 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
