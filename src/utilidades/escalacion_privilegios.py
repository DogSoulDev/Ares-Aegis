#!/usr/bin/env python3
"""
Módulo de Escalación de Privilegios - Ares Aegis
Maneja la escalación automática de privilegios con solicitud de contraseña
"""

import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox, simpledialog
import getpass
from typing import Optional


def verificar_privilegios() -> bool:
    """Verifica si se ejecuta con privilegios de root."""
    return os.geteuid() == 0


def solicitar_password_gui() -> Optional[str]:
    """Solicita la contraseña de root usando una ventana gráfica."""
    root = tk.Tk()
    root.withdraw()  # Ocultar ventana principal
    
    # Configurar la ventana de diálogo
    root.title("Ares Aegis - Autenticación")
    
    password = simpledialog.askstring(
        "Autenticación Requerida",
        "Ares Aegis requiere privilegios de administrador.\nIngrese su contraseña de sudo:",
        show='*'
    )
    
    root.destroy()
    return password


def solicitar_password_terminal() -> Optional[str]:
    """Solicita la contraseña de root usando el terminal."""
    try:
        print("🔐 Ares Aegis requiere privilegios de administrador")
        password = getpass.getpass("Ingrese su contraseña de sudo: ")
        return password
    except KeyboardInterrupt:
        print("\n❌ Operación cancelada por el usuario")
        return None


def verificar_password_sudo(password: str) -> bool:
    """Verifica que la contraseña de sudo sea correcta."""
    try:
        # Probar la contraseña ejecutando un comando simple con sudo
        cmd = ['sudo', '-S', '-k', 'echo', 'test']
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate(input=password + '\n', timeout=10)
        
        # Si el comando se ejecutó sin error, la contraseña es correcta
        return process.returncode == 0
        
    except subprocess.TimeoutExpired:
        return False
    except Exception:
        return False


def reejecutar_con_sudo(password: str) -> bool:
    """Re-ejecuta el programa con privilegios de sudo."""
    try:
        # Obtener el comando completo actual
        script_path = os.path.abspath(sys.argv[0])
        args = sys.argv[1:] if len(sys.argv) > 1 else []
        
        # Comando sudo con los argumentos originales
        cmd = ['sudo', '-S'] + [sys.executable, script_path] + args
        
        # Ejecutar con la contraseña proporcionada
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            text=True
        )
        
        # Enviar la contraseña
        process.communicate(input=password + '\n')
        
        # Salir del proceso actual
        sys.exit(process.returncode)
        
    except Exception as e:
        print(f"❌ Error al re-ejecutar con sudo: {e}")
        return False


def escalacion_automatica_privilegios() -> bool:
    """
    Maneja la escalación automática de privilegios.
    
    Returns:
        bool: True si se obtuvieron privilegios de root, False en caso contrario
    """
    # Si ya tenemos privilegios de root, no hacer nada
    if verificar_privilegios():
        print("✅ Privilegios de administrador confirmados")
        return True
    
    print("⚠️  Se requieren privilegios de administrador para Ares Aegis")
    
    # Intentar obtener la contraseña
    password = None
    
    # Primero intentar con GUI si está disponible
    try:
        password = solicitar_password_gui()
    except Exception:
        # Si falla la GUI, usar terminal
        password = solicitar_password_terminal()
    
    if not password:
        print("❌ No se proporcionó contraseña. Saliendo...")
        return False
    
    # Verificar que la contraseña sea correcta
    print("🔍 Verificando credenciales...")
    if not verificar_password_sudo(password):
        print("❌ Contraseña incorrecta")
        return False
    
    print("✅ Credenciales verificadas. Re-ejecutando con privilegios...")
    
    # Re-ejecutar el programa con sudo
    reejecutar_con_sudo(password)
    
    # Esta línea no debería ejecutarse nunca
    return False


def modo_limitado_disponible() -> bool:
    """
    Verifica si el modo limitado está disponible.
    En modo limitado, algunas funciones no estarán disponibles.
    """
    return True


def mostrar_advertencia_modo_limitado():
    """Muestra advertencia sobre las limitaciones del modo sin privilegios."""
    print("\n" + "⚠️ " * 20)
    print("ADVERTENCIA: Ejecutando en MODO LIMITADO")
    print("=" * 60)
    print("Las siguientes funciones NO estarán disponibles:")
    print("• Escaneo de archivos del sistema")
    print("• Monitoreo de procesos críticos")
    print("• Análisis de logs del sistema")
    print("• Acceso a directorios protegidos")
    print("• Cuarentena de archivos del sistema")
    print("")
    print("Para funcionalidad completa, ejecute:")
    print("   sudo python3 main.py")
    print("=" * 60)
    print("")


def gestionar_privilegios_inicial() -> str:
    """
    Gestiona los privilegios al inicio del programa.
    
    Returns:
        str: 'root' si tiene privilegios completos, 'limitado' si modo limitado
    """
    if verificar_privilegios():
        return 'root'
    
    # Intentar escalación automática
    if escalacion_automatica_privilegios():
        return 'root'
    
    # Preguntar si continuar en modo limitado
    continuar = input("¿Desea continuar en modo limitado? (s/N): ").lower().strip()
    
    if continuar in ['s', 'si', 'sí', 'y', 'yes']:
        mostrar_advertencia_modo_limitado()
        return 'limitado'
    else:
        print("❌ Programa cancelado por el usuario")
        sys.exit(1)


if __name__ == "__main__":
    # Test del módulo
    print("🔐 Testing módulo de escalación de privilegios...")
    modo = gestionar_privilegios_inicial()
    print(f"✅ Modo obtenido: {modo}")
