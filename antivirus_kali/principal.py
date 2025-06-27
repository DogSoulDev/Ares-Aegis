"""
Punto de entrada principal de la aplicación Ares Aegis.
Inicializa controladores y lanza la interfaz principal.
"""

import sys
from PySide6.QtWidgets import QApplication
from antivirus_kali.interfaz.ventana_principal import VentanaPrincipal
from antivirus_kali.controladores.controlador_integridad import ControladorIntegridad
from antivirus_kali.controladores.controlador_red import ControladorRed
from antivirus_kali.controladores.controlador_privilegios import ControladorPrivilegios
from antivirus_kali.controladores.controlador_iocs import ControladorIOCs
from antivirus_kali.controladores.controlador_modo_seguro import ControladorModoSeguro
from antivirus_kali.controladores.controlador_escaneo_sistema import ControladorEscaneoSistema


if __name__ == "__main__":
    import os
    import traceback
    try:
        app = QApplication(sys.argv)
        # Comprobación de privilegios root
        es_root = False
        try:
            es_root = (os.geteuid() == 0)
        except AttributeError:
            es_root = False
        if not es_root:
            from PySide6.QtWidgets import QMessageBox, QInputDialog, QLineEdit
            import subprocess
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("Permisos insuficientes")
            msg.setText("Ares Aegis necesita permisos de administrador para todas sus funciones.\n\nOpciones:\n- Continuar en modo limitado (menos protección)\n- Reintentar como administrador (root)\n- Salir")
            btn_salir = msg.addButton("Salir", QMessageBox.ButtonRole.RejectRole)
            btn_continuar = msg.addButton("Continuar en modo limitado", QMessageBox.ButtonRole.AcceptRole)
            btn_loguear_root = msg.addButton("Loguearte como root", QMessageBox.ButtonRole.DestructiveRole)
            msg.exec()
            if msg.clickedButton() == btn_salir:
                sys.exit(0)
            elif msg.clickedButton() == btn_loguear_root:
                import shutil
                pkexec_path = shutil.which("pkexec")
                if pkexec_path:
                    try:
                        aviso = QMessageBox()
                        aviso.setIcon(QMessageBox.Icon.Information)
                        aviso.setWindowTitle("Logueo como root requerido")
                        aviso.setText(
                            "Para acceder a todas las funciones de Ares Aegis, se abrirá un diálogo de autenticación.\n\nIntroduce tu contraseña de root o administrador cuando se te solicite.\n\nEsto es seguro y estándar en Linux.")
                        aviso.setStandardButtons(QMessageBox.StandardButton.Ok)
                        if aviso.exec() == QMessageBox.StandardButton.Ok:
                            import os
                            wrapper_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ares-aegis-wrapper.sh")
                            if not os.path.exists(wrapper_path):
                                QMessageBox.critical(None, "Error de privilegios", "No se encontró el wrapper de seguridad para elevación de privilegios.\n\nPor favor, reinstala o contacta con soporte.")
                                sys.exit(1)
                            import stat
                            os.chmod(wrapper_path, os.stat(wrapper_path).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
                            cmd = ["pkexec", wrapper_path]
                            subprocess.Popen(cmd)
                            sys.exit(0)
                    except Exception as e:
                        QMessageBox.critical(None, "Error de privilegios", f"No se pudo elevar privilegios automáticamente con pkexec.\n\nPuedes ejecutar manualmente en terminal:\nsudo python3 /usr/bin/ares-aegis\n\nError técnico: {e}")
                        sys.exit(1)
                else:
                    QMessageBox.critical(None, "Permisos de administrador requeridos",
                        "No se encontró 'pkexec' en tu sistema.\n\nPara usar todas las funciones de Ares Aegis, ejecuta manualmente en terminal:\n\n<b>sudo python3 /usr/bin/ares-aegis</b>\n\nO instala 'pkexec' con:\n<b>sudo apt install policykit-1</b>\n\nLuego vuelve a iniciar Ares Aegis.")
                    os.environ['ARES_AEGIS_LIMITADO'] = '1'
                    sys.exit(0)
            else:
                QMessageBox.information(None, "Modo limitado", "Continuarás en modo limitado. Algunas funciones avanzadas estarán desactivadas.")
                os.environ['ARES_AEGIS_LIMITADO'] = '1'
        rutas_herramientas = [
            "/bin/ls", "/bin/bash", "/usr/bin/apt", "/usr/bin/nmap", "/usr/bin/wireshark", "/usr/bin/python3", "/usr/bin/ufw"
        ]
        referencia_hashes = {}
        controladores = {
            'escaneo_sistema': ControladorEscaneoSistema(),
            'integridad': ControladorIntegridad(rutas_herramientas, referencia_hashes),
            'red': ControladorRed("192.168.1.0/24"),
            'privilegios': ControladorPrivilegios(),
            'iocs': ControladorIOCs("https://feodotracker.abuse.ch/downloads/ipblocklist.txt"),
            'modo_seguro': ControladorModoSeguro(),
        }
        ventana = VentanaPrincipal(controladores)
        ventana.show()
        sys.exit(app.exec())
    except Exception as e:
        # Loguear error en archivo visible para el wrapper
        with open("/tmp/ares_aegis_python_error.log", "w") as f:
            f.write("[Ares-Aegis Python Error] " + str(e) + "\n")
            f.write(traceback.format_exc())
        # Mostrar error en terminal si es posible
        print("[Ares-Aegis] Error crítico al iniciar la aplicación. Revisa /tmp/ares_aegis_python_error.log", file=sys.stderr)
        sys.exit(1)
