"""
Panel visual de Ares Aegis para mostrar procesos con privilegios sospechosos.
Estilo minimalista japonés, limpio y diferente.
"""


from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget, QApplication, QListWidgetItem
from PySide6.QtCore import Qt, QThread, Signal, QObject



class PanelPrivilegios(QWidget):
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
                self.log.emit("Iniciando monitoreo de privilegios...", "info")
                result = self.fn(*self.args, **self.kwargs)
                self.result.emit(result)
            except Exception as e:
                self.error.emit(e)
            finally:
                self.finished.emit()

    def __init__(self, controlador, panel_consola=None):
        super().__init__()
        self.controlador = controlador
        self.panel_consola = panel_consola
        self.setWindowTitle("Ares Aegis - Monitoreo de Privilegios y Seguridad")
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
        self.advertencia_label = QLabel("")
        self.advertencia_label.setStyleSheet("color: #b00; font-weight: 600; font-size: 14px; font-family: 'Inter', 'Noto Sans', 'Segoe UI', Arial, sans-serif;")
        self.advertencia_label.setWordWrap(True)
        self.resultados = QListWidget()
        self.boton_monitorear = QPushButton("Comprobar Privilegios y Procesos")
        self.boton_monitorear.setStyleSheet("padding: 12px 28px; font-size: 16px; border-radius: 8px; background: #3c8dbc; color: #fff; font-weight: 600; border: none; margin-top: 10px; margin-bottom: 8px;")
        self.boton_monitorear.clicked.connect(self.monitorear_threaded)
        # Detectar modo limitado
        import os
        self.modo_limitado = os.environ.get('ARES_AEGIS_LIMITADO') == '1'
        if self.modo_limitado:
            self.boton_monitorear.setEnabled(False)
            self.advertencia_label.setText("⚠️ Modo limitado: Ejecuta como root para monitoreo completo de privilegios.")
        self.label_info = QLabel("Ares Aegis: Este panel muestra si tienes permisos de administrador (root) y si hay procesos sospechosos ejecutándose con privilegios elevados.\nSi ves advertencias, revisa los procesos listados.")
        self.label_info.setStyleSheet("font-size: 16px; font-weight: 800; color: #2563eb; margin-bottom: 8px; letter-spacing:0.5px;")
        self.label_info.setAccessibleName("Título privilegios")
        self.advertencia_label.setAccessibleName("Advertencia privilegios")
        self.resultados.setAccessibleName("Resultados privilegios")
        self.boton_monitorear.setObjectName("exportar")
        self.boton_monitorear.setToolTip("Comprobar privilegios y procesos sospechosos.")
        layout.addWidget(self.label_info)
        layout.addWidget(self.advertencia_label)
        layout.addWidget(self.resultados)
        layout.addWidget(self.boton_monitorear)
        self.setLayout(layout)

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

    def monitorear_threaded(self):
        self.run_in_thread(self._monitorear, self._on_monitorear)

    def monitorear(self):
        self.monitorear_threaded()

    def monitorear_sin_thread(self):
        result = self._monitorear()
        self._on_monitorear(result)
        return result

    def _monitorear(self):
        import os
        QApplication.processEvents()
        advertencias = []
        if os.geteuid() == 0:
            root_msg = "🟢 Tienes permisos de administrador (root). Ten cuidado con los cambios."
        else:
            root_msg = "🟡 No tienes permisos de root. Algunas funciones avanzadas pueden estar limitadas."
            advertencias.append("No tienes permisos de root. El monitoreo puede ser incompleto.")
        sospechosos = self.controlador.monitorear_privilegios()
        return (root_msg, sospechosos, advertencias)

    def _on_monitorear(self, result):
        root_msg, sospechosos, advertencias = result
        self.resultados.clear()
        self.resultados.addItem(root_msg)
        if sospechosos:
            self.resultados.addItem("Procesos sospechosos con privilegios elevados:")
            for proc in sospechosos:
                item = QListWidgetItem(f"PID: {proc['pid']} | Nombre: {proc['name']} | CMD: {' '.join(proc['cmdline'])}")
                item.setBackground(Qt.GlobalColor.red)
                item.setForeground(Qt.GlobalColor.white)
                font = item.font()
                font.setBold(True)
                item.setFont(font)
                self.resultados.addItem(item)
            advertencias.append("Se detectaron procesos sospechosos ejecutándose como root. Revisa cuidadosamente.")
        else:
            self.resultados.addItem("No se detectaron procesos sospechosos ejecutándose como root.")
        if advertencias:
            self.advertencia_label.setStyleSheet("color: #b00; font-weight: bold; font-size: 13px; background: #fffbe6; border: 1px solid #e0b000; padding: 4px; border-radius: 6px;")
            self.advertencia_label.setText("\n".join(advertencias))
        else:
            self.advertencia_label.setText("")
        self.boton_monitorear.setEnabled(True)
        self.log("Monitoreo de privilegios completado", "info")
