"""
Panel visual de Ares Aegis para mostrar el análisis de red y honeypots.
Estilo minimalista japonés, limpio y diferente.
"""


from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget, QApplication
from PySide6.QtCore import Qt, QThread, Signal, QObject



class PanelRed(QWidget):
    class Worker(QObject):
        finished = Signal()
        result = Signal(object)
        error = Signal(Exception)
        log = Signal(str, str)
        def __init__(self, fn, *args, **kwargs):
            super().__init__()
            self.fn = fn
            self.args = args
            self.kwargs = kwargs
        def run(self):
            try:
                self.log.emit("Iniciando análisis de red...", "info")
                result = self.fn(*self.args, **self.kwargs)
                self.result.emit(result)
            except Exception as e:
                self.error.emit(e)
            finally:
                self.finished.emit()

    def __init__(self, controlador, panel_consola=None):
        """
        Inicializa el panel de análisis de red y honeypots.
        controlador: instancia de ControladorRed
        panel_consola: PanelConsola para logs globales
        """
        super().__init__()
        self.controlador = controlador
        self.panel_consola = panel_consola
        self.setWindowTitle("Ares Aegis - Análisis de Red y Honeypots")
        self.setStyleSheet('''
            QWidget { background: #fff; font-family: 'Inter', 'Noto Sans', 'Segoe UI', Arial, sans-serif; color: #23272f; border-radius: 12px; }
            QLabel { font-size: 15px; }
            QListWidget { background: #f7f8fa; color: #23272f; font-size: 15px; border-radius: 8px; padding: 8px; border: 1px solid #e0e0e0; selection-background-color: #e3f2fd; selection-color: #23272f; }
            QListWidget::item { padding: 10px 12px; border-radius: 7px; margin-bottom: 2px; }
            QListWidget::item:selected { background: #c3e6ff; color: #23272f; font-weight: 700; border-left: 5px solid #2563eb; }
            QListWidget::item:hover { background: #e0e7ef; }
            QPushButton { background: #e0e7ef; color: #23272f; border-radius: 8px; font-size: 15px; padding: 7px 18px; font-weight: 600; border: 1px solid #cfd8dc; }
            QPushButton:hover { background: #dbeafe; color: #1e293b; }
            QPushButton:focus { outline: 2px solid #2563eb; }
            QPushButton#exportar { background: #3c8dbc; color: #fff; border-radius: 8px; font-size: 15px; padding: 7px 18px; font-weight: 600; border: 1px solid #2563eb; }
            QPushButton#exportar:hover { background: #2563eb; color: #fff; }
        ''')
        layout = QVBoxLayout()
        self.resultados = QListWidget()
        self.boton_analizar = QPushButton("Analizar Red y Honeypots")
        self.boton_analizar.setStyleSheet("padding: 12px 28px; font-size: 16px; border-radius: 8px; background: #3c8dbc; color: #fff; font-weight: 600; border: none; margin-top: 10px; margin-bottom: 8px;")
        self.boton_analizar.clicked.connect(self.analizar_threaded)
        # Detectar modo limitado
        import os
        self.modo_limitado = os.environ.get('ARES_AEGIS_LIMITADO') == '1'
        self.advertencia_label = QLabel("")
        self.advertencia_label.setStyleSheet("color: #b00; font-weight: 600; font-size: 14px; font-family: 'Inter', 'Noto Sans', 'Segoe UI', Arial, sans-serif;")
        if self.modo_limitado:
            self.boton_analizar.setEnabled(False)
            self.advertencia_label.setText("⚠️ Modo limitado: Ejecuta como root para análisis de red completo.")
        self.label_info = QLabel(
            "Ares Aegis: Este panel analiza la red local y detecta posibles honeypots o dispositivos anómalos.\n"
            "- Si ejecutas como root, el análisis es más profundo.\n"
            "- Se detectan MACs genéricas, puertos inusuales y dispositivos con comportamiento sospechoso.\n"
            "Recomendación: Si ves dispositivos sospechosos, revisa su procedencia y limita su acceso a la red.")
        self.label_info.setStyleSheet("font-size: 16px; font-weight: 800; color: #2563eb; margin-bottom: 8px; letter-spacing:0.5px;")
        self.label_info.setAccessibleName("Título red")
        self.advertencia_label.setAccessibleName("Advertencia red")
        self.resultados.setAccessibleName("Resultados red")
        self.boton_analizar.setObjectName("exportar")
        self.boton_analizar.setToolTip("Analizar red y honeypots.")
        layout.addWidget(self.label_info)
        layout.addWidget(self.resultados)
        layout.addWidget(self.advertencia_label)
        layout.addWidget(self.boton_analizar)
        self.setLayout(layout)
        self.ultimo_resultado = None  # Guarda el último análisis para exportación o consulta

    def log(self, mensaje, nivel="info"):
        if self.panel_consola:
            self.panel_consola.log(mensaje, nivel)

    def run_in_thread(self, fn, on_result, on_error=None, log_msg=None):
        thread = QThread()
        worker = self.Worker(fn)
        worker.moveToThread(thread)
        worker.result.connect(on_result)
        if on_error:
            worker.error.connect(on_error)
        worker.log.connect(self.log)
        thread.started.connect(worker.run)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.start()
        if log_msg:
            self.log(log_msg, "info")
        return thread

    def analizar_threaded(self):
        self.run_in_thread(self._analizar, self._on_analizar)

    def _analizar(self):
        QApplication.processEvents()
        # Validación previa de dependencias
        try:
            import scapy
        except ImportError:
            self.log("Scapy no está instalado. El análisis será básico. Instala 'scapy' para mejores resultados.", "warning")
        sospechosos, advertencias, explicaciones = self.controlador.analizar_red()
        return (sospechosos, advertencias, explicaciones)

    def _on_analizar(self, result):
        sospechosos, advertencias, explicaciones = result
        self.resultados.clear()
        # Feedback visual minimalista y didáctico
        if advertencias:
            advertencia_texto = "\n".join(advertencias)
            if any("root" in adv.lower() for adv in advertencias):
                self.advertencia_label.setStyleSheet("color: #b00; font-weight: bold; font-size: 13px; background: #fffbe6; border: 1px solid #e0b000; padding: 4px; border-radius: 6px;")
                self.advertencia_label.setText("⚠️ <b>Permiso insuficiente:</b> Ejecuta como <b>root</b> para un análisis completo.\n" + advertencia_texto)
            elif any("scapy" in adv.lower() for adv in advertencias):
                self.advertencia_label.setStyleSheet("color: #b00; font-weight: bold; font-size: 13px; background: #fffbe6; border: 1px solid #e0b000; padding: 4px; border-radius: 6px;")
                self.advertencia_label.setText("⚠️ <b>Error con Scapy:</b> No se pudo usar el motor avanzado de red.\n" + advertencia_texto)
            elif any("arp" in adv.lower() for adv in advertencias):
                self.advertencia_label.setStyleSheet("color: #b00; font-weight: bold; font-size: 13px; background: #fffbe6; border: 1px solid #e0b000; padding: 4px; border-radius: 6px;")
                self.advertencia_label.setText("⚠️ <b>Comando 'arp' no disponible:</b> Instala el paquete <b>net-tools</b> para análisis básico de red.\n" + advertencia_texto)
            else:
                self.advertencia_label.setStyleSheet("color: #b00; font-weight: bold; font-size: 13px;")
                self.advertencia_label.setText(advertencia_texto)
        else:
            self.advertencia_label.setText("")
        if not sospechosos:
            self.resultados.addItem("🟢 No se detectaron dispositivos sospechosos en la red.")
        else:
            self.resultados.addItem("🔴 Dispositivos sospechosos detectados:")
            for disp in sospechosos:
                self.resultados.addItem(f"IP: {disp.get('ip','')} | MAC: {disp.get('mac','')}")
            for exp in explicaciones:
                self.resultados.addItem(f"⚠️ {exp}")
        self.ultimo_resultado = {
            'sospechosos': sospechosos,
            'advertencias': advertencias,
            'explicaciones': explicaciones
        }
        self.boton_analizar.setEnabled(True)
        self.log("Análisis de red completado", "info")
