
"""
Módulo para el escaneo del sistema operativo, carpetas y programas instalados.
Permite comparar con la base de datos de referencia de Kali Linux.
Refactorizado para usar pathlib y mayor robustez.
"""
from pathlib import Path
import subprocess
import hashlib

class EscaneoSistema:
    def __init__(self, rutas_directorios=None):
        """
        Inicializa el escaneo del sistema.
        rutas_directorios: lista de rutas a analizar (por defecto, binarios principales de Linux)
        """
        self.rutas_directorios = rutas_directorios or ["/bin", "/usr/bin", "/sbin", "/usr/sbin"]

    def obtener_programas_instalados(self):
        try:
            salida = subprocess.check_output(['dpkg-query', '-W', '-f', '${Package}\n'], text=True)
            return salida.splitlines()
        except Exception as e:
            return [f"Error: {e}"]

    def escanear_rootkits(self):
        try:
            salida = subprocess.check_output(['chkrootkit'], text=True)
            return salida.splitlines()
        except Exception:
            return ["No se pudo ejecutar chkrootkit. Instale el paquete para análisis de rootkits."]

    def escanear_procesos_sospechosos(self):
        try:
            salida = subprocess.check_output(['ps', 'aux'], text=True)
            procesos = [linea for linea in salida.splitlines() if 'suspicious' in linea.lower() or 'malware' in linea.lower()]
            return procesos if procesos else ["Sin procesos sospechosos detectados."]
        except Exception:
            return ["No se pudo analizar los procesos."]

    def escanear_puertos_abiertos(self):
        try:
            salida = subprocess.check_output(['ss', '-tuln'], text=True)
            return salida.splitlines()
        except Exception:
            return ["No se pudo obtener la lista de puertos abiertos."]

    def escanear_servicios_activos(self):
        try:
            salida = subprocess.check_output(['systemctl', 'list-units', '--type=service', '--state=running'], text=True)
            return salida.splitlines()
        except Exception:
            return ["No se pudo obtener la lista de servicios activos."]

    def escanear_integridad_binarios(self, base_hashes):
        diferencias = {}
        for archivo, hash_ref in base_hashes.items():
            hash_actual = self.calcular_hash_archivo(archivo)
            if hash_actual is None:
                diferencias[archivo] = 'No encontrado'
            elif hash_actual != hash_ref:
                diferencias[archivo] = 'Modificado'
        return diferencias

    def calcular_hash_archivo(self, ruta, algoritmo='sha256'):
        """
        Calcula el hash de un archivo usando pathlib para mayor robustez.
        """
        try:
            hash_func = hashlib.new(algoritmo)
            ruta_path = Path(ruta)
            with ruta_path.open('rb') as f:
                for bloque in iter(lambda: f.read(4096), b''):
                    hash_func.update(bloque)
            return hash_func.hexdigest()
        except Exception:
            return None

    def obtener_resumen(self, base_hashes):
        # Solo ejecuta análisis bajo demanda, nunca automáticamente
        resumen = {}
        resumen['rootkits'] = self.escanear_rootkits()
        resumen['procesos'] = self.escanear_procesos_sospechosos()
        resumen['puertos'] = self.escanear_puertos_abiertos()
        resumen['servicios'] = self.escanear_servicios_activos()
        resumen['integridad'] = self.escanear_integridad_binarios(base_hashes)
        resumen['programas'] = self.obtener_programas_instalados()
        return resumen

    def exportar_informe(self, resumen, ruta="/tmp/informe_ares_aegis.pdf", usuario="Desconocido"):
        try:
            from antivirus_kali.informes.generador_pdf import generar_informe_pdf
            ruta_pdf = ruta if ruta.endswith('.pdf') else ruta + '.pdf'
            result = generar_informe_pdf(resumen, ruta_pdf, usuario=usuario)
            return result
        except Exception as e:
            return f"Error al exportar informe PDF: {e}"
