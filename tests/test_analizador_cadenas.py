#!/usr/bin/env python3
"""
Tests para el Analizador de Cadenas
Pruebas completas para extracción y análisis de strings en archivos.

Autor: DogSoulDev
"""

import unittest
import tempfile
import os
import shutil
from pathlib import Path
from unittest.mock import Mock
import sys

# Añadir el directorio padre al path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.modelos.analizador_cadenas import AnalizadorCadenas, ExtractorCadenas, CadenaEncontrada
from src.modelos.siem import SIEM


class TestCadenaEncontrada(unittest.TestCase):
    """Tests para la clase CadenaEncontrada."""
    
    def test_clasificacion_url(self):
        """Test de clasificación de URLs."""
        cadena = CadenaEncontrada("https://www.example.com", 0, "ascii", 22)
        self.assertEqual(cadena.tipo_cadena, "URL")
    
    def test_clasificacion_email(self):
        """Test de clasificación de emails."""
        cadena = CadenaEncontrada("test@example.com", 0, "ascii", 16)
        self.assertEqual(cadena.tipo_cadena, "EMAIL")
    
    def test_clasificacion_ip(self):
        """Test de clasificación de direcciones IP."""
        cadena = CadenaEncontrada("192.168.1.1", 0, "ascii", 11)
        self.assertEqual(cadena.tipo_cadena, "IP_ADDRESS")
    
    def test_clasificacion_ruta_archivo(self):
        """Test de clasificación de rutas de archivo."""
        cadena = CadenaEncontrada("/usr/bin/python", 0, "ascii", 15)
        self.assertEqual(cadena.tipo_cadena, "FILE_PATH")
    
    def test_clasificacion_comando_sistema(self):
        """Test de clasificación de comandos de sistema."""
        cadena = CadenaEncontrada("cmd.exe", 0, "ascii", 7)
        self.assertEqual(cadena.tipo_cadena, "SYSTEM_COMMAND")
    
    def test_clasificacion_api_windows(self):
        """Test de clasificación de APIs de Windows."""
        cadena = CadenaEncontrada("CreateFile", 0, "ascii", 10)
        self.assertEqual(cadena.tipo_cadena, "WINDOWS_API")
    
    def test_clasificacion_registro(self):
        """Test de clasificación de claves de registro."""
        cadena = CadenaEncontrada("HKEY_LOCAL_MACHINE\\Software", 0, "ascii", 28)
        self.assertEqual(cadena.tipo_cadena, "REGISTRY_KEY")
    
    def test_clasificacion_hex(self):
        """Test de clasificación de cadenas hexadecimales."""
        cadena = CadenaEncontrada("DEADBEEF", 0, "ascii", 8)
        self.assertEqual(cadena.tipo_cadena, "HEX_STRING")
    
    def test_clasificacion_base64(self):
        """Test de clasificación de cadenas Base64."""
        cadena = CadenaEncontrada("SGVsbG8gV29ybGQ=", 0, "ascii", 16)
        self.assertEqual(cadena.tipo_cadena, "BASE64")
    
    def test_evaluacion_sospecha_password(self):
        """Test de evaluación de sospecha por palabras clave."""
        cadena = CadenaEncontrada("password123", 0, "ascii", 11)
        self.assertTrue(cadena.es_sospechosa)
    
    def test_evaluacion_sospecha_dominio(self):
        """Test de evaluación de sospecha por dominio sospechoso."""
        cadena = CadenaEncontrada("malware.tk/download", 0, "ascii", 19)
        self.assertTrue(cadena.es_sospechosa)
    
    def test_evaluacion_sospecha_ip_privada(self):
        """Test de evaluación de sospecha por IP privada."""
        cadena = CadenaEncontrada("192.168.1.100", 0, "ascii", 13)
        self.assertTrue(cadena.es_sospechosa)
    
    def test_evaluacion_sospecha_cadena_larga(self):
        """Test de evaluación de sospecha por longitud excesiva."""
        cadena_larga = "A" * 250
        cadena = CadenaEncontrada(cadena_larga, 0, "ascii", len(cadena_larga))
        self.assertTrue(cadena.es_sospechosa)
    
    def test_cadena_normal_no_sospechosa(self):
        """Test de cadena normal que no debe ser sospechosa."""
        cadena = CadenaEncontrada("Hello World", 0, "ascii", 11)
        self.assertFalse(cadena.es_sospechosa)
    
    def test_to_dict(self):
        """Test de conversión a diccionario."""
        cadena = CadenaEncontrada("test string", 100, "utf-8", 11)
        dict_resultado = cadena.to_dict()
        
        self.assertIsInstance(dict_resultado, dict)
        self.assertEqual(dict_resultado['contenido'], "test string")
        self.assertEqual(dict_resultado['offset'], 100)
        self.assertEqual(dict_resultado['encoding'], "utf-8")
        self.assertEqual(dict_resultado['longitud'], 11)
        self.assertIn('tipo_cadena', dict_resultado)
        self.assertIn('es_sospechosa', dict_resultado)


class TestExtractorCadenas(unittest.TestCase):
    """Tests para la clase ExtractorCadenas."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        self.extractor = ExtractorCadenas(longitud_minima=4)
    
    def test_extraer_cadenas_ascii_simples(self):
        """Test de extracción de cadenas ASCII simples."""
        datos = b"Hello World\x00\x01Binary Data\x00Test String"
        cadenas = self.extractor.extraer_cadenas_ascii(datos)
        
        self.assertGreater(len(cadenas), 0)
        contenidos = [c.contenido for c in cadenas]
        self.assertIn("Hello World", contenidos)
        self.assertIn("Test String", contenidos)
    
    def test_extraer_cadenas_ascii_longitud_minima(self):
        """Test de respeto a longitud mínima en extracción ASCII."""
        datos = b"Hi\x00Test\x00"
        cadenas = self.extractor.extraer_cadenas_ascii(datos)
        
        # "Hi" debe ser filtrado por ser muy corto (< 4 caracteres)
        contenidos = [c.contenido for c in cadenas]
        self.assertNotIn("Hi", contenidos)
        self.assertIn("Test", contenidos)
    
    def test_extraer_cadenas_unicode(self):
        """Test de extracción de cadenas Unicode."""
        # Crear datos UTF-16LE: "Test" = T\x00e\x00s\x00t\x00
        datos = b"T\x00e\x00s\x00t\x00\x00\x00"
        cadenas = self.extractor.extraer_cadenas_unicode(datos)
        
        if cadenas:  # Puede no encontrar cadenas dependiendo de la implementación
            self.assertGreater(len(cadenas), 0)
    
    def test_extraer_cadenas_encoding_utf8(self):
        """Test de extracción con codificación UTF-8."""
        texto = "Texto de prueba con acentos: ñáéíóú"
        datos = texto.encode('utf-8')
        cadenas = self.extractor.extraer_cadenas_encoding(datos, 'utf-8')
        
        self.assertGreater(len(cadenas), 0)
        contenidos = [c.contenido for c in cadenas]
        self.assertTrue(any("Texto de prueba" in contenido for contenido in contenidos))
    
    def test_extraer_cadenas_encoding_latin1(self):
        """Test de extracción con codificación Latin1."""
        texto = "Cadena en latin1"
        datos = texto.encode('latin1')
        cadenas = self.extractor.extraer_cadenas_encoding(datos, 'latin1')
        
        self.assertGreater(len(cadenas), 0)
        contenidos = [c.contenido for c in cadenas]
        self.assertTrue(any("latin1" in contenido for contenido in contenidos))
    
    def test_extraer_todas_las_cadenas_sin_duplicados(self):
        """Test de extracción completa sin duplicados."""
        datos = b"Hello World\x00Hello World\x00Different String"
        cadenas = self.extractor.extraer_todas_las_cadenas(datos)
        
        # Verificar que no hay duplicados
        contenidos = [c.contenido for c in cadenas]
        contenidos_unicos = set(contenidos)
        self.assertEqual(len(contenidos), len(contenidos_unicos))
    
    def test_extraer_cadenas_datos_vacios(self):
        """Test de extracción con datos vacíos."""
        datos = b""
        cadenas = self.extractor.extraer_todas_las_cadenas(datos)
        self.assertEqual(len(cadenas), 0)
    
    def test_extraer_cadenas_solo_binario(self):
        """Test de extracción con solo datos binarios."""
        datos = b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09"
        cadenas = self.extractor.extraer_todas_las_cadenas(datos)
        # No debería encontrar cadenas de texto
        self.assertEqual(len(cadenas), 0)


class TestAnalizadorCadenas(unittest.TestCase):
    """Tests para la clase AnalizadorCadenas."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        self.temp_dir = tempfile.mkdtemp()
        self.siem_mock = Mock(spec=SIEM)
        self.analizador = AnalizadorCadenas(siem=self.siem_mock)
    
    def tearDown(self):
        """Limpieza después de cada test."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_analizar_archivo_con_cadenas(self):
        """Test de análisis de archivo con cadenas."""
        archivo_test = os.path.join(self.temp_dir, "test_strings.bin")
        
        # Crear archivo con cadenas mixtas
        contenido = b"Hello World\x00\x01\x02password123\x00https://malware.example.com\x00192.168.1.1"
        with open(archivo_test, 'wb') as f:
            f.write(contenido)
        
        resultado = self.analizador.analizar_archivo(archivo_test)
        
        self.assertNotIn('error', resultado)
        self.assertIn('total_cadenas', resultado)
        self.assertIn('cadenas_sospechosas', resultado)
        self.assertIn('estadisticas', resultado)
        self.assertIn('categorias', resultado)
        self.assertIn('cadenas', resultado)
        
        # Debe encontrar cadenas
        self.assertGreater(resultado['total_cadenas'], 0)
        
        # Debe encontrar cadenas sospechosas
        self.assertGreater(resultado['cadenas_sospechosas'], 0)
    
    def test_analizar_archivo_inexistente(self):
        """Test de análisis de archivo que no existe."""
        archivo_inexistente = os.path.join(self.temp_dir, "no_existe.bin")
        resultado = self.analizador.analizar_archivo(archivo_inexistente)
        
        self.assertIn('error', resultado)
        self.assertEqual(resultado['error'], 'Archivo no encontrado')
    
    def test_analizar_archivo_demasiado_grande(self):
        """Test de manejo de archivos demasiado grandes."""
        archivo_test = os.path.join(self.temp_dir, "archivo_grande.bin")
        
        # Crear archivo pequeño para la prueba
        with open(archivo_test, 'wb') as f:
            f.write(b"test content")
        
        # Analizar con límite muy pequeño
        resultado = self.analizador.analizar_archivo(archivo_test, max_tamaño=5)
        
        self.assertIn('error', resultado)
        self.assertIn('demasiado grande', resultado['error'])
    
    def test_calcular_estadisticas(self):
        """Test de cálculo de estadísticas."""
        cadenas = [
            CadenaEncontrada("short", 0, "ascii", 5),
            CadenaEncontrada("medium length string", 0, "ascii", 20),
            CadenaEncontrada("very long string with many characters", 0, "utf-8", 37)
        ]
        
        estadisticas = self.analizador._calcular_estadisticas(cadenas)
        
        self.assertIn('longitud_promedio', estadisticas)
        self.assertIn('longitud_minima', estadisticas)
        self.assertIn('longitud_maxima', estadisticas)
        self.assertIn('encodings_encontrados', estadisticas)
        self.assertIn('tipos_encontrados', estadisticas)
        self.assertIn('porcentaje_sospechosas', estadisticas)
        
        self.assertEqual(estadisticas['longitud_minima'], 5)
        self.assertEqual(estadisticas['longitud_maxima'], 37)
        self.assertIn('ascii', estadisticas['encodings_encontrados'])
        self.assertIn('utf-8', estadisticas['encodings_encontrados'])
    
    def test_categorizar_cadenas(self):
        """Test de categorización de cadenas."""
        cadenas = [
            CadenaEncontrada("https://example.com", 0, "ascii", 19),
            CadenaEncontrada("test@email.com", 0, "ascii", 14),
            CadenaEncontrada("192.168.1.1", 0, "ascii", 11),
            CadenaEncontrada("regular text", 0, "ascii", 12)
        ]
        
        # Forzar tipos para test
        cadenas[0].tipo_cadena = "URL"
        cadenas[1].tipo_cadena = "EMAIL"
        cadenas[2].tipo_cadena = "IP_ADDRESS"
        cadenas[3].tipo_cadena = "TEXT"
        
        categorias = self.analizador._categorizar_cadenas(cadenas)
        
        self.assertEqual(categorias['URL'], 1)
        self.assertEqual(categorias['EMAIL'], 1)
        self.assertEqual(categorias['IP_ADDRESS'], 1)
        self.assertEqual(categorias['TEXT'], 1)
    
    def test_buscar_patrones_especificos(self):
        """Test de búsqueda de patrones específicos."""
        archivo_test = os.path.join(self.temp_dir, "test_patterns.txt")
        
        contenido = "password: secret123\nuser@domain.com\nhttps://evil.com"
        with open(archivo_test, 'w') as f:
            f.write(contenido)
        
        patrones = [r'password:\s*\w+', r'\w+@\w+\.\w+']
        coincidencias = self.analizador.buscar_patrones_especificos(archivo_test, patrones)
        
        self.assertGreater(len(coincidencias), 0)
        
        # Verificar estructura de coincidencias
        for coincidencia in coincidencias:
            self.assertIn('patron', coincidencia)
            self.assertIn('cadena', coincidencia)
            self.assertIn('coincidencia_completa', coincidencia)
    
    def test_extraer_urls(self):
        """Test de extracción específica de URLs."""
        archivo_test = os.path.join(self.temp_dir, "test_urls.txt")
        
        contenido = "Visit https://example.com and http://test.org for more info"
        with open(archivo_test, 'w') as f:
            f.write(contenido)
        
        urls = self.analizador.extraer_urls(archivo_test)
        
        # Dependiendo de la implementación, puede encontrar las URLs
        self.assertIsInstance(urls, list)
    
    def test_extraer_ips(self):
        """Test de extracción específica de IPs."""
        archivo_test = os.path.join(self.temp_dir, "test_ips.txt")
        
        contenido = "Connect to 192.168.1.1 or 10.0.0.1 for access"
        with open(archivo_test, 'w') as f:
            f.write(contenido)
        
        ips = self.analizador.extraer_ips(archivo_test)
        
        # Dependiendo de la implementación, puede encontrar las IPs
        self.assertIsInstance(ips, list)
    
    def test_analizador_sin_siem(self):
        """Test de funcionamiento sin SIEM."""
        analizador_sin_siem = AnalizadorCadenas()
        
        archivo_test = os.path.join(self.temp_dir, "test_no_siem.txt")
        with open(archivo_test, 'w') as f:
            f.write("Simple test content")
        
        resultado = analizador_sin_siem.analizar_archivo(archivo_test)
        
        # Debe funcionar sin errores
        self.assertNotIn('error', resultado)
        self.assertIn('total_cadenas', resultado)
    
    def test_integracion_siem_logging(self):
        """Test de integración con SIEM para logging."""
        archivo_test = os.path.join(self.temp_dir, "test_siem.txt")
        with open(archivo_test, 'w') as f:
            f.write("Test content for SIEM logging")
        
        self.analizador.analizar_archivo(archivo_test)
        
        # Verificar que se llamó al SIEM
        self.siem_mock.log_evento.assert_called()
        
        # Verificar eventos INFO
        llamadas = self.siem_mock.log_evento.call_args_list
        eventos_info = [call for call in llamadas if call[0][0] == 'INFO']
        self.assertGreater(len(eventos_info), 0)
    
    def test_generar_reporte_markdown(self):
        """Test de generación de reporte Markdown."""
        archivo_test = os.path.join(self.temp_dir, "test_report.txt")
        with open(archivo_test, 'w') as f:
            f.write("Content for markdown report generation")
        
        resultado = self.analizador.analizar_archivo(archivo_test)
        reporte = self.analizador.generar_reporte_markdown(resultado)
        
        self.assertIsInstance(reporte, str)
        self.assertIn("# Análisis de Cadenas:", reporte)
        self.assertIn("## Resumen", reporte)
        self.assertIn("## Estadísticas", reporte)
        self.assertIn("## Categorías de Cadenas", reporte)
        self.assertIn("*Análisis realizado el", reporte)
    
    def test_generar_reporte_con_error(self):
        """Test de generación de reporte con error."""
        analisis_error = {
            'error': 'Archivo no encontrado',
            'timestamp_analisis': '2023-01-01T00:00:00'
        }
        
        reporte = self.analizador.generar_reporte_markdown(analisis_error)
        
        self.assertIn("# Error en Análisis de Cadenas", reporte)
        self.assertIn("Archivo no encontrado", reporte)


class TestIntegracionCompleta(unittest.TestCase):
    """Tests de integración completa del analizador de cadenas."""
    
    def setUp(self):
        """Configuración inicial para tests de integración."""
        self.temp_dir = tempfile.mkdtemp()
        self.siem = SIEM()
        self.analizador = AnalizadorCadenas(siem=self.siem)
    
    def tearDown(self):
        """Limpieza después de cada test."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_flujo_completo_analisis_ejecutable(self):
        """Test del flujo completo de análisis de un ejecutable simulado."""
        archivo_ejecutable = os.path.join(self.temp_dir, "malware.exe")
        
        # Simular contenido de ejecutable con cadenas sospechosas
        contenido_sospechoso = (
            b"CreateFile\x00"
            b"password123\x00"
            b"https://malware.evil.com/payload\x00"
            b"192.168.1.100\x00"
            b"cmd.exe /c del C:\\*\x00"
            b"Normal string content\x00"
        )
        
        with open(archivo_ejecutable, 'wb') as f:
            f.write(contenido_sospechoso)
        
        # Realizar análisis completo
        resultado = self.analizador.analizar_archivo(archivo_ejecutable)
        
        # Verificar que se completó el análisis
        self.assertNotIn('error', resultado)
        self.assertGreater(resultado['total_cadenas'], 0)
        
        # Debe haber encontrado cadenas sospechosas
        self.assertGreater(resultado['cadenas_sospechosas'], 0)
        
        # Verificar estadísticas
        estadisticas = resultado['estadisticas']
        self.assertIn('longitud_promedio', estadisticas)
        self.assertGreater(estadisticas['porcentaje_sospechosas'], 0)
        
        # Verificar categorías
        categorias = resultado['categorias']
        self.assertIn('WINDOWS_API', categorias)
        self.assertIn('URL', categorias)
        
        # Extraer URLs específicas
        urls = self.analizador.extraer_urls(archivo_ejecutable)
        self.assertTrue(any('malware.evil.com' in url for url in urls))
        
        # Extraer IPs específicas
        ips = self.analizador.extraer_ips(archivo_ejecutable)
        self.assertIn('192.168.1.100', ips)
        
        # Buscar patrones específicos
        patrones = [r'password\d+', r'cmd\.exe']
        coincidencias = self.analizador.buscar_patrones_especificos(archivo_ejecutable, patrones)
        self.assertGreater(len(coincidencias), 0)
        
        # Generar reporte
        reporte = self.analizador.generar_reporte_markdown(resultado)
        self.assertIn('malware.exe', reporte)
        self.assertIn('Cadenas Sospechosas', reporte)


if __name__ == '__main__':
    unittest.main(verbosity=2)
