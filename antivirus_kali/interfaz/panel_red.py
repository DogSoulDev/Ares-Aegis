"""
Panel visual de Ares Aegis para mostrar el análisis de red y honeypots.
Estilo minimalista japonés, limpio y diferente.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget
from PySide6.QtCore import Qt


class PanelRed(QWidget):
    def __init__(self, controlador):
        """
        Inicializa el panel de análisis de red y honeypots.
        controlador: instancia de ControladorRed
        """
        super().__init__()
        self.controlador = controlador
        self.setWindowTitle("Ares Aegis - Análisis de Red y Honeypots")
        self.setStyleSheet("background: #fff; font-family: 'Inter', 'Noto Sans', 'Segoe UI', Arial, sans-serif; color: #23272f; border-radius: 12px;")
        layout = QVBoxLayout()
        self.resultados = QListWidget()
        self.boton_analizar = QPushButton("Analizar Red y Honeypots")
        self.boton_analizar.setStyleSheet("padding: 12px 28px; font-size: 16px; border-radius: 8px; background: #3c8dbc; color: #fff; font-weight: 600; border: none; margin-top: 10px; margin-bottom: 8px;")
        self.boton_analizar.clicked.connect(self.analizar)
        self.label_info = QLabel(
            "Ares Aegis: Este panel analiza la red local y detecta posibles honeypots o dispositivos anómalos.\n"
            "- Si ejecutas como root, el análisis es más profundo.\n"
            "- Se detectan MACs genéricas, puertos inusuales y dispositivos con comportamiento sospechoso.\n"
            "Recomendación: Si ves dispositivos sospechosos, revisa su procedencia y limita su acceso a la red.")
        self.label_info.setStyleSheet("color: #28353B; font-size: 15px; font-weight: 500; margin-bottom: 10px; font-family: 'Inter', 'Noto Sans', 'Segoe UI', Arial, sans-serif;")
        self.advertencia_label = QLabel("")
        self.advertencia_label.setStyleSheet("color: #b00; font-weight: 600; font-size: 14px; font-family: 'Inter', 'Noto Sans', 'Segoe UI', Arial, sans-serif;")
        layout.addWidget(self.label_info)
        layout.addWidget(self.resultados)
        layout.addWidget(self.advertencia_label)
        layout.addWidget(self.boton_analizar)
        self.setLayout(layout)
        self.ultimo_resultado = None  # Guarda el último análisis para exportación o consulta

    def analizar(self):
        """
        Ejecuta el análisis de red y honeypots, mostrando resultados y advertencias.
        Guarda el último resultado para exportación o consulta posterior.
        """
        from PySide6.QtWidgets import QApplication
        self.resultados.clear()
        self.advertencia_label.setText("")
        self.resultados.addItem("⏳ Analizando red... Por favor, espera.")
        QApplication.processEvents()
        self.boton_analizar.setEnabled(False)
        try:
            # Validación previa de dependencias
            try:
                import scapy
            except ImportError:
                self.advertencia_label.setText("⚠️ Scapy no está instalado. El análisis será básico. Instala 'scapy' para mejores resultados.")
            sospechosos, advertencias, explicaciones = self.controlador.analizar_red()
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
            # Guardar último resultado para exportación o consulta
            self.ultimo_resultado = {
                'sospechosos': sospechosos,
                'advertencias': advertencias,
                'explicaciones': explicaciones
            }
        except Exception as e:
            self.advertencia_label.setText(f"Error al analizar la red: {e}")
            self.resultados.addItem("No se pudo analizar la red.")
        finally:
            self.boton_analizar.setEnabled(True)
