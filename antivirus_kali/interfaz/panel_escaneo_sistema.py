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
        from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout, QSizePolicy
        from antivirus_kali.interfaz.style import BUTTON_STYLE, EXPORT_BUTTON_STYLE
        layout = QVBoxLayout()
        self.advertencia_label = QLabel("")
        self.advertencia_label.setStyleSheet("color: #b00; font-weight: 600; font-size: 14px; font-family: 'Inter', 'Noto Sans', 'Segoe UI', Arial, sans-serif;")
        self.advertencia_label.setWordWrap(True)
        self.resultados = QListWidget()
        layout.addWidget(QLabel("Ares Aegis: Escaneo avanzado del sistema operativo y programas instalados. Prioridad máxima de seguridad.\n"))
        layout.addWidget(self.advertencia_label)
        layout.addWidget(self.resultados)
        # Detectar modo limitado
        import os
        self.modo_limitado = os.environ.get('ARES_AEGIS_LIMITADO') == '1'
        # Botones de exportación (arriba, alineados y con estilo)
        export_layout = QHBoxLayout()
        self.boton_exportar_pdf = QPushButton("Exportar PDF")
        self.boton_exportar_pdf.setStyleSheet(EXPORT_BUTTON_STYLE)
        self.boton_exportar_pdf.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.boton_exportar_pdf.clicked.connect(self.exportar_informe)
        self.boton_exportar_md = QPushButton("Exportar Markdown")
        self.boton_exportar_md.setStyleSheet(EXPORT_BUTTON_STYLE)
        self.boton_exportar_md.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.boton_exportar_md.clicked.connect(self.exportar_informe_markdown)
        self.boton_exportar_txt = QPushButton("Exportar TXT")
        self.boton_exportar_txt.setStyleSheet(EXPORT_BUTTON_STYLE)
        self.boton_exportar_txt.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.boton_exportar_txt.clicked.connect(self.exportar_informe_txt)
        export_layout.addWidget(self.boton_exportar_pdf)
        export_layout.addWidget(self.boton_exportar_md)
        export_layout.addWidget(self.boton_exportar_txt)
        layout.addLayout(export_layout)
        # Botones críticos en grid profesional
        grid = QGridLayout()
        self.boton_analizar_rootkits = QPushButton("Analizar Rootkits")
        self.boton_analizar_rootkits.setStyleSheet(BUTTON_STYLE)
        self.boton_analizar_rootkits.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.boton_analizar_rootkits.clicked.connect(self.analizar_rootkits)
        self.boton_analizar_procesos = QPushButton("Analizar Procesos")
        self.boton_analizar_procesos.setStyleSheet(BUTTON_STYLE)
        self.boton_analizar_procesos.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.boton_analizar_procesos.clicked.connect(self.analizar_procesos)
        self.boton_analizar_puertos = QPushButton("Analizar Puertos")
        self.boton_analizar_puertos.setStyleSheet(BUTTON_STYLE)
        self.boton_analizar_puertos.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.boton_analizar_puertos.clicked.connect(self.analizar_puertos)
        self.boton_analizar_servicios = QPushButton("Analizar Servicios")
        self.boton_analizar_servicios.setStyleSheet(BUTTON_STYLE)
        self.boton_analizar_servicios.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.boton_analizar_servicios.clicked.connect(self.analizar_servicios)
        self.boton_analizar_integridad = QPushButton("Verificar Integridad")
        self.boton_analizar_integridad.setStyleSheet(BUTTON_STYLE)
        self.boton_analizar_integridad.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.boton_analizar_integridad.clicked.connect(self.analizar_integridad)
        self.boton_listar_programas = QPushButton("Listar Programas")
        self.boton_listar_programas.setStyleSheet(BUTTON_STYLE)
        self.boton_listar_programas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.boton_listar_programas.clicked.connect(self.listar_programas)
        # Añadir botones al grid (2 columnas, 3 filas)
        grid.addWidget(self.boton_analizar_rootkits, 0, 0)
        grid.addWidget(self.boton_analizar_procesos, 0, 1)
        grid.addWidget(self.boton_analizar_puertos, 1, 0)
        grid.addWidget(self.boton_analizar_servicios, 1, 1)
        grid.addWidget(self.boton_analizar_integridad, 2, 0)
        grid.addWidget(self.boton_listar_programas, 2, 1)
        layout.addLayout(grid)
        # Deshabilitar si modo limitado
        if self.modo_limitado:
            for btn in [self.boton_analizar_rootkits, self.boton_analizar_procesos, self.boton_analizar_puertos, self.boton_analizar_servicios, self.boton_analizar_integridad]:
                btn.setEnabled(False)
            self.advertencia_label.setText("⚠️ Modo limitado: Ejecuta como root para análisis completos y acceso a todas las funciones.")
        self.setLayout(layout)
        # Hashes de referencia de ejemplo, solo se usan si el usuario lo solicita
        self.base_hashes = {"/bin/ls": "HASH_DE_REFERENCIA"}
        self.ultimo_resumen = None
    def exportar_informe_markdown(self):
        """
        Exporta el informe en formato Markdown profesional.
        """
        self.resultados.clear()
        self.advertencia_label.setText("")
        self.resultados.addItem("⏳ Exportando informe Markdown... Por favor, espera.")
        from PySide6.QtWidgets import QApplication
        QApplication.processEvents()
        try:
            if not self.ultimo_resumen:
                self.mostrar_resumen()
            recomendaciones = [
                "Mantén tu sistema actualizado.",
                "Investiga cualquier rootkit o proceso sospechoso.",
                "Revisa los puertos abiertos y servicios activos regularmente."
            ]
            ruta = self.controlador.exportar_informe_markdown(self.ultimo_resumen, recomendaciones=recomendaciones)
            self.resultados.addItem(f"Informe Markdown exportado a: {ruta}")
        except Exception as e:
            self.advertencia_label.setText(f"Error al exportar informe Markdown: {e}")
            self.resultados.addItem("No se pudo exportar el informe Markdown.")

    def exportar_informe_txt(self):
        """
        Exporta el informe en formato texto plano profesional.
        """
        self.resultados.clear()
        self.advertencia_label.setText("")
        self.resultados.addItem("⏳ Exportando informe TXT... Por favor, espera.")
        from PySide6.QtWidgets import QApplication
        QApplication.processEvents()
        try:
            if not self.ultimo_resumen:
                self.mostrar_resumen()
            recomendaciones = [
                "Mantén tu sistema actualizado.",
                "Investiga cualquier rootkit o proceso sospechoso.",
                "Revisa los puertos abiertos y servicios activos regularmente."
            ]
            ruta = self.controlador.exportar_informe_txt(self.ultimo_resumen, recomendaciones=recomendaciones)
            self.resultados.addItem(f"Informe TXT exportado a: {ruta}")
        except Exception as e:
            self.advertencia_label.setText(f"Error al exportar informe TXT: {e}")
            self.resultados.addItem("No se pudo exportar el informe TXT.")

    def mostrar_resumen(self):
        """
        Muestra un mensaje inicial y guarda el resumen general del sistema tras el análisis.
        """
        self.resultados.clear()
        self.advertencia_label.setText("")
        try:
            self.ultimo_resumen = self.controlador.obtener_resumen(self.base_hashes)
            from antivirus_kali.utils.resumen import feedback_visual_terminal
            self.resultados.addItem(feedback_visual_terminal("Resumen general del sistema:", tipo="info"))
            for clave, valor in self.ultimo_resumen.items():
                if isinstance(valor, list):
                    self.resultados.addItem(feedback_visual_terminal(f"{clave.title()}: {len(valor)} elementos", tipo="ok" if not valor else "warn"))
                elif isinstance(valor, dict):
                    self.resultados.addItem(feedback_visual_terminal(f"{clave.title()}: {len(valor)} archivos verificados", tipo="info"))
                else:
                    self.resultados.addItem(feedback_visual_terminal(f"{clave.title()}: {valor}", tipo="info"))
        except Exception as e:
            from antivirus_kali.utils.resumen import feedback_visual_terminal
            self.advertencia_label.setText(feedback_visual_terminal(f"Error al obtener el resumen: {e}", tipo="fail"))
            self.resultados.addItem(feedback_visual_terminal("No se pudo obtener el resumen del sistema.", tipo="fail"))

    def analizar_rootkits(self):
        """
        Analiza rootkits y muestra resultados, guardando en el resumen.
        """
        self.resultados.clear()
        self.advertencia_label.setText("")
        self.resultados.addItem("⏳ Analizando rootkits... Por favor, espera.")
        QApplication.processEvents()
        try:
            rootkits = self.controlador.escanear_rootkits()
            self.resultados.clear()
            self.resultados.addItem("Análisis de rootkits:")
            for r in rootkits:
                self.resultados.addItem(r)
            if not self.ultimo_resumen:
                self.ultimo_resumen = {}
            self.ultimo_resumen['rootkits'] = rootkits
        except Exception as e:
            self.advertencia_label.setText(f"Error al analizar rootkits: {e}")
            self.resultados.addItem("No se pudo analizar rootkits.")

    def analizar_procesos(self):
        """
        Analiza procesos sospechosos y muestra resultados, guardando en el resumen.
        """
        self.resultados.clear()
        self.advertencia_label.setText("")
        self.resultados.addItem("⏳ Analizando procesos... Por favor, espera.")
        QApplication.processEvents()
        try:
            procesos = self.controlador.escanear_procesos()
            self.resultados.clear()
            self.resultados.addItem("Procesos sospechosos:")
            for p in procesos:
                self.resultados.addItem(p)
            if not self.ultimo_resumen:
                self.ultimo_resumen = {}
            self.ultimo_resumen['procesos'] = procesos
        except Exception as e:
            self.advertencia_label.setText(f"Error al analizar procesos: {e}")
            self.resultados.addItem("No se pudo analizar procesos.")

    def analizar_puertos(self):
        """
        Analiza puertos abiertos y muestra resultados, guardando en el resumen.
        """
        self.resultados.clear()
        self.advertencia_label.setText("")
        self.resultados.addItem("⏳ Analizando puertos abiertos... Por favor, espera.")
        QApplication.processEvents()
        try:
            puertos = self.controlador.escanear_puertos()
            self.resultados.clear()
            self.resultados.addItem("Puertos abiertos:")
            for p in puertos:
                self.resultados.addItem(p)
            if not self.ultimo_resumen:
                self.ultimo_resumen = {}
            self.ultimo_resumen['puertos'] = puertos
        except Exception as e:
            self.advertencia_label.setText(f"Error al analizar puertos: {e}")
            self.resultados.addItem("No se pudo analizar puertos.")

    def analizar_servicios(self):
        """
        Analiza servicios activos y muestra resultados, guardando en el resumen.
        """
        self.resultados.clear()
        self.advertencia_label.setText("")
        self.resultados.addItem("⏳ Analizando servicios activos... Por favor, espera.")
        QApplication.processEvents()
        try:
            servicios = self.controlador.escanear_servicios()
            self.resultados.clear()
            self.resultados.addItem("Servicios activos:")
            for s in servicios:
                self.resultados.addItem(s)
            if not self.ultimo_resumen:
                self.ultimo_resumen = {}
            self.ultimo_resumen['servicios'] = servicios
        except Exception as e:
            self.advertencia_label.setText(f"Error al analizar servicios: {e}")
            self.resultados.addItem("No se pudo analizar servicios.")

    def analizar_integridad(self):
        """
        Verifica la integridad de binarios y muestra resultados, guardando en el resumen.
        """
        self.resultados.clear()
        self.advertencia_label.setText("")
        self.resultados.addItem("⏳ Verificando integridad de binarios... Por favor, espera.")
        QApplication.processEvents()
        try:
            integridad = self.controlador.escanear_integridad(self.base_hashes)
            self.resultados.clear()
            self.resultados.addItem("Verificación de integridad de binarios críticos:")
            if integridad:
                for archivo, estado in integridad.items():
                    self.resultados.addItem(f"{archivo}: {estado}")
            else:
                self.resultados.addItem("Todos los binarios críticos están íntegros.")
            if not self.ultimo_resumen:
                self.ultimo_resumen = {}
            self.ultimo_resumen['integridad'] = integridad
        except Exception as e:
            self.advertencia_label.setText(f"Error al verificar integridad: {e}")
            self.resultados.addItem("No se pudo verificar la integridad.")

    def listar_programas(self):
        """
        Lista los programas instalados y muestra resultados, guardando en el resumen.
        """
        self.resultados.clear()
        self.advertencia_label.setText("")
        self.resultados.addItem("⏳ Listando programas instalados... Por favor, espera.")
        QApplication.processEvents()
        try:
            programas = self.controlador.obtener_programas()
            self.resultados.clear()
            self.resultados.addItem("Programas instalados:")
            for prog in programas[:100]:
                self.resultados.addItem(prog)
            if len(programas) > 100:
                self.resultados.addItem(f"...y {len(programas)-100} más.")
            if not self.ultimo_resumen:
                self.ultimo_resumen = {}
            self.ultimo_resumen['programas'] = programas
        except Exception as e:
            self.advertencia_label.setText(f"Error al listar programas: {e}")
            self.resultados.addItem("No se pudo listar los programas instalados.")

    def exportar_informe(self):
        """
        Exporta el informe PDF profesional con el último resumen disponible.
        """
        self.resultados.clear()
        self.advertencia_label.setText("")
        self.resultados.addItem("⏳ Exportando informe PDF profesional... Por favor, espera.")
        QApplication.processEvents()
        try:
            if not self.ultimo_resumen:
                self.mostrar_resumen()
            import getpass
            usuario = getpass.getuser()
            ruta = self.controlador.exportar_informe(self.ultimo_resumen, usuario=usuario)
            self.resultados.addItem(f"Informe PDF exportado a: {ruta}")
        except Exception as e:
            self.advertencia_label.setText(f"Error al exportar informe: {e}")
            self.resultados.addItem("No se pudo exportar el informe PDF.")
