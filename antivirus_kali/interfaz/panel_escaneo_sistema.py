"""
Panel visual de Ares Aegis para el escaneo del sistema operativo, carpetas y programas instalados.
Estilo minimalista japonés, limpio y diferente.
Incluye docstrings y comentarios para máxima claridad y mantenibilidad.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget, QApplication
from PySide6.QtCore import Qt


class PanelEscaneoSistema(QWidget):
    def __init__(self, controlador):
        """
        Inicializa el panel de escaneo avanzado del sistema.
        controlador: instancia de ControladorEscaneoSistema
        """
        super().__init__()
        self.controlador = controlador
        self.setWindowTitle("Ares Aegis - Escaneo Avanzado del Sistema (Principal)")
        self.setStyleSheet("background: #fff; font-family: 'Inter', 'Noto Sans', 'Segoe UI', Arial, sans-serif; color: #23272f; border-radius: 12px;")
        layout = QVBoxLayout()
        self.advertencia_label = QLabel("")
        self.advertencia_label.setStyleSheet("color: #b00; font-weight: 600; font-size: 14px; font-family: 'Inter', 'Noto Sans', 'Segoe UI', Arial, sans-serif;")
        self.advertencia_label.setWordWrap(True)
        self.resultados = QListWidget()
        layout.addWidget(QLabel("Ares Aegis: Escaneo avanzado del sistema operativo y programas instalados. Prioridad máxima de seguridad.\n"))
        layout.addWidget(self.advertencia_label)
        layout.addWidget(self.resultados)
        self.setLayout(layout)
        # Hashes de referencia de ejemplo, solo se usan si el usuario lo solicita
        self.base_hashes = {"/bin/ls": "HASH_DE_REFERENCIA"}
        self.ultimo_resumen = None

    def mostrar_resumen(self):
        self.resultados.clear()
        self.advertencia_label.setText("")
        self.resultados.addItem("Pulsa el botón para analizar el sistema. No se realiza ningún análisis ni escaneo hasta que el usuario lo solicite.")
        # Solo ejecuta análisis si el usuario pulsa el botón correspondiente
        # El análisis real se ejecuta bajo demanda

    def analizar_rootkits(self):
        self.resultados.clear()
        self.resultados.addItem("⏳ Analizando rootkits... Por favor, espera.")
        QApplication.processEvents()
        # No hay botones que deshabilitar
        try:
            rootkits = self.controlador.escanear_rootkits()
            self.resultados.clear()
            self.resultados.addItem("Análisis de rootkits:")
            for r in rootkits:
                self.resultados.addItem(r)
        finally:
            pass

    def analizar_procesos(self):
        self.resultados.clear()
        self.resultados.addItem("⏳ Analizando procesos... Por favor, espera.")
        QApplication.processEvents()
        # No hay botones que deshabilitar
        try:
            procesos = self.controlador.escanear_procesos()
            self.resultados.clear()
            self.resultados.addItem("Procesos sospechosos:")
            for p in procesos:
                self.resultados.addItem(p)
        finally:
            pass

    def analizar_puertos(self):
        self.resultados.clear()
        self.resultados.addItem("⏳ Analizando puertos abiertos... Por favor, espera.")
        QApplication.processEvents()
        # No hay botones que deshabilitar
        try:
            puertos = self.controlador.escanear_puertos()
            self.resultados.clear()
            self.resultados.addItem("Puertos abiertos:")
            for p in puertos:
                self.resultados.addItem(p)
        finally:
            pass

    def analizar_servicios(self):
        self.resultados.clear()
        self.resultados.addItem("⏳ Analizando servicios activos... Por favor, espera.")
        QApplication.processEvents()
        # No hay botones que deshabilitar
        try:
            servicios = self.controlador.escanear_servicios()
            self.resultados.clear()
            self.resultados.addItem("Servicios activos:")
            for s in servicios:
                self.resultados.addItem(s)
        finally:
            pass

    def analizar_integridad(self):
        self.resultados.clear()
        self.resultados.addItem("⏳ Verificando integridad de binarios... Por favor, espera.")
        QApplication.processEvents()
        # No hay botones que deshabilitar
        try:
            integridad = self.controlador.escanear_integridad(self.base_hashes)
            self.resultados.clear()
            self.resultados.addItem("Verificación de integridad de binarios críticos:")
            if integridad:
                for archivo, estado in integridad.items():
                    self.resultados.addItem(f"{archivo}: {estado}")
            else:
                self.resultados.addItem("Todos los binarios críticos están íntegros.")
        finally:
            pass

    def listar_programas(self):
        self.resultados.clear()
        self.resultados.addItem("⏳ Listando programas instalados... Por favor, espera.")
        QApplication.processEvents()
        # No hay botones que deshabilitar
        try:
            programas = self.controlador.obtener_programas()
            self.resultados.clear()
            self.resultados.addItem("Programas instalados:")
            for prog in programas[:100]:
                self.resultados.addItem(prog)
            if len(programas) > 100:
                self.resultados.addItem(f"...y {len(programas)-100} más.")
        finally:
            pass

    def exportar_informe(self):
        self.resultados.clear()
        self.resultados.addItem("⏳ Exportando informe PDF profesional... Por favor, espera.")
        QApplication.processEvents()
        # No hay botones que deshabilitar
        try:
            if not self.ultimo_resumen:
                self.mostrar_resumen()
            # Se puede obtener el usuario real si se desea
            import getpass
            usuario = getpass.getuser()
            ruta = self.controlador.exportar_informe(self.ultimo_resumen, usuario=usuario)
            self.resultados.addItem(f"Informe PDF exportado a: {ruta}")
        finally:
            pass
