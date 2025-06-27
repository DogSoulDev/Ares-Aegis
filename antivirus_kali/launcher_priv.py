#!/usr/bin/env python3
"""
Lanzador gráfico para Ares Aegis: permite elegir modo usuario o administrador (root) de forma segura.
Muestra un diálogo Qt antes de cargar la app principal.
"""

import os
import sys
import subprocess
from PySide6.QtWidgets import QApplication, QMessageBox, QPushButton

# Asegurar que el directorio raíz del proyecto está en sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

def main():
    app = QApplication(sys.argv)
    msg = QMessageBox()
    msg.setWindowTitle("Ares Aegis - Selección de modo de inicio")
    msg.setText("¿Desea ejecutar Ares Aegis con privilegios de administrador (root) para acceso completo?\n\n- Modo usuario: Funciones avanzadas deshabilitadas.\n- Modo administrador: Acceso completo, requiere contraseña de root.")
    modo_usuario = msg.addButton("Modo usuario", QMessageBox.ButtonRole.AcceptRole)
    modo_admin = msg.addButton("Modo administrador (root)", QMessageBox.ButtonRole.DestructiveRole)
    msg.setDefaultButton(modo_usuario)
    msg.setIcon(QMessageBox.Icon.Question)
    msg.exec()
    if msg.clickedButton() == modo_admin:
        # Relanzar con pkexec
        python_exec = sys.executable
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "principal.py")
        # Heredar entorno gráfico
        env = os.environ.copy()
        env_vars = [
            f"DISPLAY={env.get('DISPLAY','')}\n",
            f"XAUTHORITY={env.get('XAUTHORITY','')}\n",
            f"PYTHONPATH={env.get('PYTHONPATH','')}\n"
        ]
        # Usar .venv si existe
        venv_py = os.path.abspath(os.path.join(os.path.dirname(script_path), '../.venv/bin/python'))
        if os.path.exists(venv_py):
            python_exec = venv_py
        cmd = [
            "pkexec", "env",
            f"DISPLAY={env.get('DISPLAY','')}",
            f"XAUTHORITY={env.get('XAUTHORITY','')}",
            f"PYTHONPATH={env.get('PYTHONPATH','')}",
            python_exec, script_path
        ]
        try:
            subprocess.run(cmd, check=True)
        except Exception as e:
            QMessageBox.critical(None, "Ares Aegis - Error de privilegios", f"No se pudo iniciar como root.\n\n{e}")
        sys.exit(0)
    else:
        # Lanzar en modo usuario (limitado)
        os.environ["ARES_AEGIS_LIMITADO"] = "1"
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "principal.py")
        # Usar .venv si existe
        venv_py = os.path.abspath(os.path.join(os.path.dirname(script_path), '../.venv/bin/python'))
        if os.path.exists(venv_py):
            python_exec = venv_py
        else:
            python_exec = sys.executable
        os.execvpe(python_exec, [python_exec, script_path], os.environ)

if __name__ == "__main__":
    main()
