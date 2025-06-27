"""
Panel visual de Ares Aegis para mostrar la validación de integridad de herramientas.
Estilo minimalista japonés, limpio y diferente.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget, QApplication, QHBoxLayout
from PySide6.QtCore import Qt

class PanelIntegridad(QWidget):
    def __init__(self, controlador):
        """
        Inicializa el panel de validación de integridad de herramientas.
        controlador: instancia de ControladorIntegridad
        """
        super().__init__()
        self.controlador = controlador
        self.setWindowTitle("Ares Aegis - Integridad de Herramientas")
        self.setStyleSheet("background: #fff; font-family: 'Inter', 'Noto Sans', 'Segoe UI', Arial, sans-serif; color: #23272f; border-radius: 12px;")
        layout = QVBoxLayout()
        self.advertencia_label = QLabel("")
        self.advertencia_label.setStyleSheet("color: #b00; font-weight: 600; font-size: 14px; font-family: 'Inter', 'Noto Sans', 'Segoe UI', Arial, sans-serif;")
        self.advertencia_label.setWordWrap(True)
        self.resultados = QListWidget()
        self.boton_validar = QPushButton("Validar Integridad con Hashes Oficiales")
        self.boton_validar.setStyleSheet("padding: 12px 28px; font-size: 16px; border-radius: 8px; background: #3c8dbc; color: #fff; font-weight: 600; border: none; margin-top: 10px; margin-bottom: 8px;")
        self.boton_validar.clicked.connect(self.validar)
        # Detectar modo limitado
        import os
        self.modo_limitado = os.environ.get('ARES_AEGIS_LIMITADO') == '1'
        if self.modo_limitado:
            self.boton_validar.setEnabled(False)
            self.advertencia_label.setText("⚠️ Modo limitado: Ejecuta como root para validar integridad de herramientas.")
        self.label_info = QLabel(
            "Ares Aegis: Este panel compara los binarios críticos con los hashes oficiales de Kali Linux.\n"
            "- Íntegro: Coincide con el hash oficial.\n"
            "- Modificado: El binario ha cambiado, posible riesgo.\n"
            "- Sin referencia: No hay hash oficial, verifique manualmente.\n"
            "Recomendación: Si detecta binarios modificados, reinstale el paquete o investigue el origen.")
        self.label_info.setStyleSheet("color: #28353B; font-size: 15px; font-weight: 500; margin-bottom: 10px; font-family: 'Inter', 'Noto Sans', 'Segoe UI', Arial, sans-serif;")
        layout.addWidget(self.label_info)
        layout.addWidget(self.advertencia_label)
        layout.addWidget(self.resultados)
        layout.addWidget(self.boton_validar)
        # Botones de exportación
        export_layout = QHBoxLayout()
        self.boton_exportar_md = QPushButton("Exportar Markdown")
        self.boton_exportar_md.clicked.connect(self.exportar_informe_markdown)
        self.boton_exportar_txt = QPushButton("Exportar TXT")
        self.boton_exportar_txt.clicked.connect(self.exportar_informe_txt)
        export_layout.addWidget(self.boton_exportar_md)
        export_layout.addWidget(self.boton_exportar_txt)
        layout.addLayout(export_layout)
        self.setLayout(layout)
        self.ultimo_resultado = None  # Guarda el último resultado para exportación o consulta

    def validar(self):
        """
        Ejecuta la validación de integridad, mostrando resultados y advertencias.
        Guarda el último resultado para exportación o consulta posterior.
        """
        self.resultados.clear()
        self.advertencia_label.setText("")
        self.resultados.addItem("⏳ Validando integridad... Por favor, espera.")
        QApplication.processEvents()
        self.boton_validar.setEnabled(False)
        try:
            # Validación previa de dependencias
            try:
                import requests
            except ImportError:
                from antivirus_kali.utils.resumen import feedback_visual_terminal
                self.advertencia_label.setText(feedback_visual_terminal("El módulo 'requests' no está instalado. No se podrán descargar hashes oficiales.", tipo="warn"))
            resultados, advertencias = self.controlador.validar()
            self.resultados.clear()
            from antivirus_kali.utils.resumen import feedback_visual_terminal
            for herramienta, estado in resultados.items():
                tipo = "ok" if "Íntegro" in estado else "fail" if "Modificado" in estado else "warn" if "No encontrado" in estado else "info"
                self.resultados.addItem(feedback_visual_terminal(f"{herramienta}: {estado}", tipo=tipo))
            if advertencias:
                self.advertencia_label.setStyleSheet("color: #b00; font-weight: bold; font-size: 13px; background: #fffbe6; border: 1px solid #e0b000; padding: 4px; border-radius: 6px;")
                self.advertencia_label.setText("\n".join(advertencias))
            else:
                self.advertencia_label.setText("")
            # Guardar último resultado para exportación o consulta
            self.ultimo_resultado = {
                'resultados': resultados,
                'advertencias': advertencias
            }
        except Exception as e:
            from antivirus_kali.utils.resumen import feedback_visual_terminal
            self.advertencia_label.setText(feedback_visual_terminal(f"Error al validar integridad: {e}", tipo="fail"))
            self.resultados.addItem(feedback_visual_terminal("No se pudo validar la integridad.", tipo="fail"))
        finally:
            self.boton_validar.setEnabled(True)

    def exportar_informe_markdown(self):
        """
        Exporta el informe de integridad en formato Markdown profesional.
        """
        self.resultados.clear()
        self.advertencia_label.setText("")
        self.resultados.addItem("⏳ Exportando informe Markdown... Por favor, espera.")
        from PySide6.QtWidgets import QApplication
        QApplication.processEvents()
        try:
            if not self.ultimo_resultado or 'resultados' not in self.ultimo_resultado:
                self.advertencia_label.setText("No hay resultados de integridad para exportar. Ejecuta la validación primero.")
                self.resultados.addItem("No hay resultados de integridad para exportar.")
                return
            recomendaciones = [
                "Verifica manualmente cualquier binario modificado o no encontrado.",
                "Reinstala paquetes sospechosos desde fuentes oficiales.",
                "Mantén actualizado tu sistema y hashes de referencia."
            ]
            from antivirus_kali.utils.resumen import exportar_markdown
            ruta = exportar_markdown(self.ultimo_resultado['resultados'], recomendaciones=recomendaciones)
            self.resultados.addItem(f"Informe Markdown exportado a: {ruta}")
        except Exception as e:
            self.advertencia_label.setText(f"Error al exportar informe Markdown: {e}")
            self.resultados.addItem("No se pudo exportar el informe Markdown.")

    def exportar_informe_txt(self):
        """
        Exporta el informe de integridad en formato texto plano profesional.
        """
        self.resultados.clear()
        self.advertencia_label.setText("")
        self.resultados.addItem("⏳ Exportando informe TXT... Por favor, espera.")
        from PySide6.QtWidgets import QApplication
        QApplication.processEvents()
        try:
            if not self.ultimo_resultado or 'resultados' not in self.ultimo_resultado:
                self.advertencia_label.setText("No hay resultados de integridad para exportar. Ejecuta la validación primero.")
                self.resultados.addItem("No hay resultados de integridad para exportar.")
                return
            recomendaciones = [
                "Verifica manualmente cualquier binario modificado o no encontrado.",
                "Reinstala paquetes sospechosos desde fuentes oficiales.",
                "Mantén actualizado tu sistema y hashes de referencia."
            ]
            from antivirus_kali.utils.resumen import exportar_txt
            ruta = exportar_txt(self.ultimo_resultado['resultados'], recomendaciones=recomendaciones)
            self.resultados.addItem(f"Informe TXT exportado a: {ruta}")
        except Exception as e:
            self.advertencia_label.setText(f"Error al exportar informe TXT: {e}")
            self.resultados.addItem("No se pudo exportar el informe TXT.")
