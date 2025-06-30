"""
Tests para el módulo Escaneador de Ares Aegis
Implementa pruebas unitarias para el sistema de escaneo.
"""

import unittest
import tempfile
import os
from pathlib import Path
import sys

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from modelos.siem import SIEM
from modelos.escaneador import Escaneador, ResultadoEscaneo, GestorFirmas


class TestResultadoEscaneo(unittest.TestCase):
    """Tests para la clase ResultadoEscaneo."""
    
    def test_resultado_limpio(self):
        """Test resultado de escaneo limpio."""
        resultado = ResultadoEscaneo("/test/archivo.txt", limpio=True)
        
        self.assertTrue(resultado.limpio)
        self.assertEqual(resultado.archivo, "/test/archivo.txt")
        self.assertEqual(len(resultado.amenazas), 0)
    
    def test_resultado_con_amenazas(self):
        """Test resultado de escaneo con amenazas."""
        amenazas = ["Trojan.Test", "Backdoor.Shell"]
        resultado = ResultadoEscaneo("/test/malware.exe", limpio=False, amenazas=amenazas)
        
        self.assertFalse(resultado.limpio)
        self.assertEqual(resultado.amenazas, amenazas)
        self.assertEqual(len(resultado.amenazas), 2)
    
    def test_resultado_to_markdown(self):
        """Test conversión a Markdown del resultado."""
        amenazas = ["Virus.Test"]
        resultado = ResultadoEscaneo("/test/infected.txt", limpio=False, amenazas=amenazas)
        
        markdown = resultado.to_markdown()
        
        self.assertIn("infected.txt", markdown)
        self.assertIn("AMENAZA DETECTADA", markdown)
        self.assertIn("Virus.Test", markdown)


class TestGestorFirmas(unittest.TestCase):
    """Tests para la clase GestorFirmas."""
    
    def setUp(self):
        """Configuración previa a cada test."""
        # Crear archivo temporal para firmas de prueba
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
        self.temp_file.write("# Firmas de prueba\n")
        self.temp_file.write("eval(base64_decode\n")
        self.temp_file.write("system($_GET\n")
        self.temp_file.write("HASH:d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2\n")
        self.temp_file.write("REGEX:eval\\s*\\(\\s*base64_decode\n")
        self.temp_file.close()
        
        self.temp_path = Path(self.temp_file.name)
        self.gestor = GestorFirmas(archivo_firmas=self.temp_path)
    
    def tearDown(self):
        """Limpieza posterior a cada test."""
        if self.temp_path.exists():
            self.temp_path.unlink()
    
    def test_cargar_firmas_texto(self):
        """Test carga de firmas de texto."""
        self.assertIn("eval(base64_decode", self.gestor.firmas_texto)
        self.assertIn("system($_get", self.gestor.firmas_texto)  # Debería estar en minúsculas
    
    def test_cargar_firmas_hash(self):
        """Test carga de firmas de hash."""
        self.assertIn("d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2", 
                     self.gestor.firmas_hash)
    
    def test_cargar_firmas_regex(self):
        """Test carga de firmas regex."""
        self.assertEqual(len(self.gestor.firmas_regex), 1)
        # Verificar que el patrón regex funciona
        patron = self.gestor.firmas_regex[0]
        self.assertIsNotNone(patron.search("eval(base64_decode("))


class TestEscaneador(unittest.TestCase):
    """Tests para la clase Escaneador."""
    
    def setUp(self):
        """Configuración previa a cada test."""
        # Crear SIEM temporal
        self.temp_siem_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.temp_siem_file.close()
        self.siem = SIEM(archivo_eventos=Path(self.temp_siem_file.name))
        
        # Crear gestor de firmas temporal
        self.temp_firmas_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
        self.temp_firmas_file.write("malware\n")
        self.temp_firmas_file.write("backdoor\n")
        self.temp_firmas_file.write("HASH:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855\n")  # Hash de archivo vacío
        self.temp_firmas_file.close()
        
        gestor_firmas = GestorFirmas(archivo_firmas=Path(self.temp_firmas_file.name))
        self.escaneador = Escaneador(self.siem, gestor_firmas)
    
    def tearDown(self):
        """Limpieza posterior a cada test."""
        # Limpiar archivos temporales
        for temp_file in [self.temp_siem_file.name, self.temp_firmas_file.name]:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_inicializacion_escaneador(self):
        """Test inicialización del escaneador."""
        self.assertIsInstance(self.escaneador, Escaneador)
        self.assertEqual(self.escaneador.siem, self.siem)
        self.assertIsNotNone(self.escaneador.gestor_firmas)
    
    def test_escanear_archivo_inexistente(self):
        """Test escaneo de archivo que no existe."""
        with self.assertRaises(FileNotFoundError):
            self.escaneador.escanear_archivo("/archivo/inexistente.txt")
    
    def test_escanear_archivo_limpio(self):
        """Test escaneo de archivo limpio."""
        # Crear archivo temporal limpio
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write("Este es un archivo limpio sin contenido malicioso.")
            temp_path = temp_file.name
        
        try:
            resultado = self.escaneador.escanear_archivo(temp_path)
            
            self.assertTrue(resultado.limpio)
            self.assertEqual(len(resultado.amenazas), 0)
            self.assertEqual(resultado.archivo, temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_escanear_archivo_con_amenaza_texto(self):
        """Test escaneo de archivo con amenaza de texto."""
        # Crear archivo temporal con contenido malicioso
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write("Este archivo contiene malware y backdoor.")
            temp_path = temp_file.name
        
        try:
            resultado = self.escaneador.escanear_archivo(temp_path)
            
            self.assertFalse(resultado.limpio)
            self.assertGreater(len(resultado.amenazas), 0)
            # Debería detectar tanto "malware" como "backdoor"
            amenazas_texto = ' '.join(resultado.amenazas).lower()
            self.assertIn("malware", amenazas_texto)
            self.assertIn("backdoor", amenazas_texto)
        finally:
            os.unlink(temp_path)
    
    def test_escanear_archivo_vacio_hash_conocido(self):
        """Test escaneo de archivo vacío con hash conocido."""
        # Crear archivo vacío (hash conocido en las firmas)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            # No escribir nada, dejar vacío
            temp_path = temp_file.name
        
        try:
            resultado = self.escaneador.escanear_archivo(temp_path)
            
            # Debería detectar el hash malicioso
            self.assertFalse(resultado.limpio)
            amenazas_texto = ' '.join(resultado.amenazas).lower()
            self.assertIn("hash", amenazas_texto)
        finally:
            os.unlink(temp_path)
    
    def test_escanear_directorio_inexistente(self):
        """Test escaneo de directorio que no existe."""
        with self.assertRaises(NotADirectoryError):
            self.escaneador.escanear_directorio("/directorio/inexistente")
    
    def test_escanear_directorio_vacio(self):
        """Test escaneo de directorio vacío."""
        with tempfile.TemporaryDirectory() as temp_dir:
            resultado = self.escaneador.escanear_directorio(temp_dir)
            
            self.assertEqual(resultado['archivos_escaneados'], 0)
            self.assertEqual(resultado['amenazas_encontradas'], 0)
            self.assertEqual(resultado['directorio'], temp_dir)
    
    def test_escanear_directorio_con_archivos(self):
        """Test escaneo de directorio con archivos."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Crear algunos archivos de prueba
            archivo_limpio = os.path.join(temp_dir, "limpio.txt")
            with open(archivo_limpio, 'w') as f:
                f.write("Archivo limpio sin amenazas.")
            
            archivo_malicioso = os.path.join(temp_dir, "malicioso.txt")
            with open(archivo_malicioso, 'w') as f:
                f.write("Este archivo contiene malware.")
            
            resultado = self.escaneador.escanear_directorio(temp_dir)
            
            self.assertEqual(resultado['archivos_escaneados'], 2)
            self.assertGreaterEqual(resultado['amenazas_encontradas'], 1)  # Al menos el archivo malicioso
            self.assertGreaterEqual(resultado['archivos_infectados'], 1)
    
    def test_generar_reporte_markdown_limpio(self):
        """Test generación de reporte Markdown para directorio limpio."""
        with tempfile.TemporaryDirectory() as temp_dir:
            resultado = self.escaneador.escanear_directorio(temp_dir)
            markdown = self.escaneador.generar_reporte_markdown(resultado)
            
            self.assertIn("# Reporte de Escaneo de Directorio", markdown)
            self.assertIn("DIRECTORIO LIMPIO", markdown)
            self.assertIn("No se encontraron amenazas", markdown)
    
    def test_generar_reporte_markdown_con_amenazas(self):
        """Test generación de reporte Markdown para directorio con amenazas."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Crear archivo malicioso
            archivo_malicioso = os.path.join(temp_dir, "malware.txt")
            with open(archivo_malicioso, 'w') as f:
                f.write("Este archivo contiene malware y backdoor.")
            
            resultado = self.escaneador.escanear_directorio(temp_dir)
            markdown = self.escaneador.generar_reporte_markdown(resultado)
            
            self.assertIn("# Reporte de Escaneo de Directorio", markdown)
            self.assertIn("AMENAZAS DETECTADAS", markdown)
            self.assertIn("malware.txt", markdown)


if __name__ == '__main__':
    unittest.main()
