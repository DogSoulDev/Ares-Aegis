#!/usr/bin/env python3
"""
Ares Aegis v4.0 - Instalador Simple para Kali Linux
Instalador Python que no requiere dependencias externas
"""

import os
import sys
import shutil
import subprocess
import tempfile
import base64
import gzip
from pathlib import Path

# Colores para terminal
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

def mostrar_banner():
    """Mostrar banner de inicio"""
    os.system('clear' if os.name == 'posix' else 'cls')
    print(f"{Colors.PURPLE}")
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                    🛡️  ARES AEGIS v4.0 🛡️                    ║")
    print("║              Sistema de Ciberseguridad Avanzado              ║")
    print("║                    Para Kali Linux                          ║")
    print("║                                                              ║")
    print("║                  👨‍💻 Por: DogSoulDev                          ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print(f"{Colors.NC}")
    print()

def log_info(mensaje):
    print(f"{Colors.CYAN}[INFO]{Colors.NC} {mensaje}")

def log_exito(mensaje):
    print(f"{Colors.GREEN}[✓]{Colors.NC} {mensaje}")

def log_error(mensaje):
    print(f"{Colors.RED}[✗]{Colors.NC} {mensaje}")

def log_advertencia(mensaje):
    print(f"{Colors.YELLOW}[⚠]{Colors.NC} {mensaje}")

def verificar_root():
    """Verificar permisos de root"""
    if os.geteuid() != 0:
        log_error("Este instalador requiere permisos de root")
        print("Por favor ejecuta: sudo python3 installer.py")
        sys.exit(1)
    log_exito("Permisos de root verificados")

def verificar_kali():
    """Verificar que estamos en Kali Linux"""
    try:
        with open('/etc/os-release', 'r') as f:
            contenido = f.read()
        if 'kali' in contenido.lower() or 'debian' in contenido.lower():
            log_exito("Sistema Kali/Debian detectado")
        else:
            log_advertencia("Este instalador está optimizado para Kali Linux")
            respuesta = input("¿Deseas continuar de todas formas? (s/N): ")
            if respuesta.lower() != 's':
                print("Instalación cancelada")
                sys.exit(0)
    except FileNotFoundError:
        log_advertencia("No se pudo detectar el sistema operativo")

def instalar_dependencias():
    """Instalar dependencias necesarias"""
    log_info("Verificando dependencias del sistema...")
    
    dependencias = ["python3", "python3-tk"]
    
    try:
        # Verificar qué dependencias faltan
        resultado = subprocess.run(['dpkg', '-l'], capture_output=True, text=True)
        instalados = resultado.stdout
        
        faltan = []
        for dep in dependencias:
            if f" {dep} " not in instalados:
                faltan.append(dep)
        
        if faltan:
            log_info(f"Instalando dependencias faltantes: {', '.join(faltan)}")
            subprocess.run(['apt-get', 'update'], check=True)
            subprocess.run(['apt-get', 'install', '-y'] + faltan, check=True)
        
        log_exito("Todas las dependencias están disponibles")
        
    except subprocess.CalledProcessError as e:
        log_error(f"Error instalando dependencias: {e}")
        sys.exit(1)

def crear_directorios():
    """Crear estructura de directorios"""
    log_info("Creando estructura de directorios...")
    
    directorios = [
        "/opt/ares-aegis",
        "/usr/share/applications",
        "/usr/share/pixmaps",
        "/usr/bin"
    ]
    
    for directorio in directorios:
        Path(directorio).mkdir(parents=True, exist_ok=True)
    
    log_exito("Directorios creados")

def copiar_archivos():
    """Copiar archivos del proyecto"""
    log_info("Copiando archivos de Ares Aegis...")
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists('main.py') or not os.path.exists('ares_aegis'):
        log_error("No se encontraron los archivos del proyecto")
        log_error("Asegúrate de ejecutar este script desde la carpeta de Ares Aegis")
        sys.exit(1)
    
    # Copiar archivos principales
    try:
        shutil.copy2('main.py', '/opt/ares-aegis/')
        shutil.copytree('ares_aegis', '/opt/ares-aegis/ares_aegis', dirs_exist_ok=True)
        
        # Copiar recursos si existen
        for carpeta in ['recursos', 'configuracion', 'data']:
            if os.path.exists(carpeta):
                shutil.copytree(carpeta, f'/opt/ares-aegis/{carpeta}', dirs_exist_ok=True)
        
        # Crear carpetas que pueden no existir
        for carpeta in ['cuarentena', 'reportes']:
            Path(f'/opt/ares-aegis/{carpeta}').mkdir(exist_ok=True)
        
        log_exito("Archivos copiados exitosamente")
        
    except Exception as e:
        log_error(f"Error copiando archivos: {e}")
        sys.exit(1)

def configurar_permisos():
    """Configurar permisos correctos"""
    log_info("Configurando permisos...")
    
    # Cambiar propietario
    subprocess.run(['chown', '-R', 'root:root', '/opt/ares-aegis'])
    
    # Permisos de directorios
    subprocess.run(['chmod', '-R', '755', '/opt/ares-aegis'])
    
    # Hacer ejecutable el main.py
    os.chmod('/opt/ares-aegis/main.py', 0o755)
    
    log_exito("Permisos configurados")

def instalar_iconos():
    """Instalar iconos del sistema"""
    log_info("Instalando iconos...")
    
    iconos = [
        ('/opt/ares-aegis/recursos/AresAegis.png', '/usr/share/pixmaps/ares-aegis.png'),
        ('/opt/ares-aegis/recursos/aresIcon.png', '/usr/share/pixmaps/ares-aegis-icon.png')
    ]
    
    for origen, destino in iconos:
        if os.path.exists(origen):
            shutil.copy2(origen, destino)
            os.chmod(destino, 0o644)
            log_exito(f"Icono instalado: {os.path.basename(destino)}")

def crear_launcher():
    """Crear script de lanzamiento"""
    log_info("Creando script de lanzamiento...")
    
    launcher_content = '''#!/bin/bash
# Ares Aegis - Launcher Script para Kali Linux

# Verificar si se está ejecutando como root
if [ "$EUID" -ne 0 ]; then
    # Intentar ejecutar con pkexec (interfaz gráfica para sudo)
    if command -v pkexec >/dev/null 2>&1; then
        exec pkexec /usr/bin/python3 /opt/ares-aegis/main.py "$@"
    # Si no hay pkexec, usar sudo
    elif command -v sudo >/dev/null 2>&1; then
        echo "🔐 Ares Aegis requiere permisos de root para funcionalidad completa"
        exec sudo /usr/bin/python3 /opt/ares-aegis/main.py "$@"
    else
        echo "❌ Error: Se requieren permisos de administrador"
        echo "Por favor ejecuta: sudo ares-aegis"
        exit 1
    fi
else
    # Ya somos root, ejecutar directamente
    exec /usr/bin/python3 /opt/ares-aegis/main.py "$@"
fi'''
    
    with open('/usr/bin/ares-aegis', 'w') as f:
        f.write(launcher_content)
    
    os.chmod('/usr/bin/ares-aegis', 0o755)
    log_exito("Launcher creado en /usr/bin/ares-aegis")

def crear_menu():
    """Crear entrada del menú de aplicaciones"""
    log_info("Creando entrada del menú de aplicaciones...")
    
    desktop_content = '''[Desktop Entry]
Version=1.0
Name=Ares Aegis
Comment=Sistema de Ciberseguridad Avanzado para Kali Linux
Comment[es]=Suite completa de herramientas de ciberseguridad y pentesting
Exec=ares-aegis
Icon=ares-aegis
Terminal=false
Type=Application
Categories=Security;Network;System;
Keywords=security;cybersecurity;pentesting;vulnerability;scanner;kali;
StartupNotify=true
StartupWMClass=Ares Aegis
MimeType=
'''
    
    with open('/usr/share/applications/ares-aegis.desktop', 'w') as f:
        f.write(desktop_content)
    
    os.chmod('/usr/share/applications/ares-aegis.desktop', 0o644)
    
    # Actualizar base de datos de aplicaciones
    try:
        subprocess.run(['update-desktop-database'], check=False)
    except:
        pass
    
    log_exito("Entrada del menú creada")

def verificar_instalacion():
    """Verificar que la instalación fue exitosa"""
    log_info("Verificando instalación...")
    
    archivos_criticos = [
        '/usr/bin/ares-aegis',
        '/opt/ares-aegis/main.py',
        '/opt/ares-aegis/ares_aegis',
        '/usr/share/applications/ares-aegis.desktop'
    ]
    
    for archivo in archivos_criticos:
        if not os.path.exists(archivo):
            log_error(f"Archivo crítico faltante: {archivo}")
            return False
    
    log_exito("Instalación verificada correctamente")
    return True

def mostrar_info_final():
    """Mostrar información de finalización"""
    print()
    print(f"{Colors.GREEN}╔══════════════════════════════════════════════════════════════╗")
    print(f"║                ✅ INSTALACIÓN COMPLETADA ✅                   ║")
    print(f"╚══════════════════════════════════════════════════════════════╝{Colors.NC}")
    print()
    print(f"{Colors.CYAN}🚀 FORMAS DE EJECUTAR ARES AEGIS:{Colors.NC}")
    print()
    print(f"   {Colors.YELLOW}1. Desde terminal:{Colors.NC}")
    print(f"      {Colors.BLUE}ares-aegis{Colors.NC}")
    print()
    print(f"   {Colors.YELLOW}2. Desde menú gráfico:{Colors.NC}")
    print(f"      {Colors.BLUE}Aplicaciones → Security → Ares Aegis{Colors.NC}")
    print()
    print(f"   {Colors.YELLOW}3. Con permisos explícitos:{Colors.NC}")
    print(f"      {Colors.BLUE}sudo ares-aegis{Colors.NC}")
    print()
    print(f"{Colors.CYAN}🔐 NOTA IMPORTANTE:{Colors.NC}")
    print("   • Ares Aegis solicitará automáticamente permisos de root")
    print("   • Para funcionalidad completa se requieren permisos de administrador")
    print("   • El programa puede ejecutarse en modo limitado sin permisos")
    print()
    print(f"{Colors.PURPLE}🛡️ Ares Aegis v4.0 - Desarrollado por DogSoulDev{Colors.NC}")
    print(f"{Colors.PURPLE}📧 GitHub: https://github.com/DogSoulDev/Ares-Aegis{Colors.NC}")
    print()

def desinstalar():
    """Desinstalar Ares Aegis"""
    print(f"{Colors.YELLOW}Desinstalando Ares Aegis...{Colors.NC}")
    
    archivos_a_eliminar = [
        '/opt/ares-aegis',
        '/usr/bin/ares-aegis',
        '/usr/share/applications/ares-aegis.desktop',
        '/usr/share/pixmaps/ares-aegis.png',
        '/usr/share/pixmaps/ares-aegis-icon.png'
    ]
    
    for archivo in archivos_a_eliminar:
        if os.path.exists(archivo):
            if os.path.isdir(archivo):
                shutil.rmtree(archivo)
            else:
                os.remove(archivo)
    
    # Actualizar base de datos de aplicaciones
    try:
        subprocess.run(['update-desktop-database'], check=False)
    except:
        pass
    
    log_exito("Ares Aegis desinstalado exitosamente")

def main():
    """Función principal"""
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--uninstall', '-u']:
            verificar_root()
            desinstalar()
            return
        elif sys.argv[1] in ['--help', '-h']:
            print("Ares Aegis v4.0 - Instalador para Kali Linux")
            print()
            print("Uso:")
            print(f"  sudo python3 {sys.argv[0]}              # Instalar Ares Aegis")
            print(f"  sudo python3 {sys.argv[0]} --uninstall  # Desinstalar Ares Aegis")
            print(f"  python3 {sys.argv[0]} --help           # Mostrar esta ayuda")
            print()
            return
    
    # Instalación principal
    mostrar_banner()
    print(f"{Colors.CYAN}Iniciando instalación de Ares Aegis v4.0...{Colors.NC}")
    print()
    
    verificar_kali()
    verificar_root()
    instalar_dependencias()
    crear_directorios()
    copiar_archivos()
    configurar_permisos()
    instalar_iconos()
    crear_launcher()
    crear_menu()
    
    if verificar_instalacion():
        mostrar_info_final()
    else:
        log_error("La instalación no se completó correctamente")
        sys.exit(1)

if __name__ == "__main__":
    main()
