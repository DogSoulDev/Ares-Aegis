#!/usr/bin/env python3
"""
Script de verificación final y configuración de Ares Aegis
Valida que todos los componentes estén correctamente instalados y configurados
"""

import sys
import os
import subprocess
import sqlite3
from pathlib import Path
import json

class VerificadorSistema:
    def __init__(self):
        self.errores = []
        self.advertencias = []
        self.base_dir = Path(__file__).parent
        
    def verificar_python(self):
        """Verificar versión de Python"""
        print("🐍 Verificando Python...")
        version = sys.version_info
        if version.major == 3 and version.minor >= 9:
            print(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")
        else:
            self.errores.append(f"Python 3.9+ requerido, encontrado {version.major}.{version.minor}")
            
    def verificar_dependencias_python(self):
        """Verificar dependencias de Python"""
        print("📦 Verificando dependencias Python...")
        dependencias = [
            'PySide6',
            'asyncio',
            'sqlite3',
            'aiofiles',
            'plyer'
        ]
        
        for dep in dependencias:
            try:
                __import__(dep)
                print(f"   ✅ {dep}")
            except ImportError:
                self.errores.append(f"Dependencia faltante: {dep}")
                print(f"   ❌ {dep}")
                
    def verificar_clamav(self):
        """Verificar instalación de ClamAV"""
        print("🛡️ Verificando ClamAV...")
        try:
            result = subprocess.run(['clamscan', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"   ✅ {result.stdout.strip()}")
            else:
                self.advertencias.append("ClamAV no responde correctamente")
        except FileNotFoundError:
            self.advertencias.append("ClamAV no está instalado")
            
    def verificar_estructura_archivos(self):
        """Verificar estructura de archivos del proyecto"""
        print("📁 Verificando estructura de archivos...")
        archivos_criticos = [
            "antivirus_kali/main.py",
            "antivirus_kali/launcher.py",
            "antivirus_kali/interfaz/ventana_principal.py",
            "antivirus_kali/interfaz/panel_mini_siem.py",
            "antivirus_kali/mini_siem/controlador_siem.py",
            "antivirus_kali/mini_siem/recolector_logs.py",
            "antivirus_kali/mini_siem/almacenamiento.py",
            "antivirus_kali/mini_siem/motor_correlacion.py",
            "antivirus_kali/controladores/controlador_mini_siem.py"
        ]
        
        for archivo in archivos_criticos:
            ruta = self.base_dir / archivo
            if ruta.exists():
                print(f"   ✅ {archivo}")
            else:
                self.errores.append(f"Archivo faltante: {archivo}")
                print(f"   ❌ {archivo}")
                
    def verificar_permisos_logs(self):
        """Verificar acceso a logs del sistema"""
        print("📋 Verificando acceso a logs...")
        logs_sistema = [
            "/var/log/auth.log",
            "/var/log/syslog",
            "/var/log/dpkg.log"
        ]
        
        accesibles = 0
        for log in logs_sistema:
            if os.path.exists(log) and os.access(log, os.R_OK):
                print(f"   ✅ {log}")
                accesibles += 1
            else:
                print(f"   ⚠️  {log} (sin acceso)")
                
        if accesibles == 0:
            self.advertencias.append("Sin acceso a logs del sistema - Mini-SIEM limitado")
        elif accesibles < len(logs_sistema):
            self.advertencias.append(f"Acceso parcial a logs ({accesibles}/{len(logs_sistema)})")
            
    def verificar_base_datos(self):
        """Verificar que SQLite funciona correctamente"""
        print("💾 Verificando base de datos...")
        try:
            db_path = self.base_dir / "test_siem.db"
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Crear tabla de prueba
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_table (
                    id INTEGER PRIMARY KEY,
                    timestamp TEXT,
                    data TEXT
                )
            """)
            
            # Insertar datos de prueba
            cursor.execute("INSERT INTO test_table (timestamp, data) VALUES (?, ?)",
                         ("2024-01-01", "test"))
            conn.commit()
            
            # Verificar lectura
            cursor.execute("SELECT COUNT(*) FROM test_table")
            count = cursor.fetchone()[0]
            
            conn.close()
            db_path.unlink()  # Limpiar archivo de prueba
            
            print(f"   ✅ SQLite funcional (test: {count} registros)")
            
        except Exception as e:
            self.errores.append(f"Error en base de datos: {e}")
            print(f"   ❌ Error SQLite: {e}")
            
    def verificar_importaciones(self):
        """Verificar que todos los módulos se pueden importar"""
        print("🔧 Verificando importaciones del proyecto...")
        
        modulos_test = [
            "antivirus_kali.mini_siem.motor_correlacion",
            "antivirus_kali.mini_siem.almacenamiento", 
            "antivirus_kali.mini_siem.recolector_logs",
            "antivirus_kali.controladores.controlador_mini_siem"
        ]
        
        # Agregar al path
        sys.path.insert(0, str(self.base_dir))
        
        for modulo in modulos_test:
            try:
                __import__(modulo)
                print(f"   ✅ {modulo}")
            except Exception as e:
                self.errores.append(f"Error importando {modulo}: {e}")
                print(f"   ❌ {modulo}: {e}")
                
    def crear_configuracion_inicial(self):
        """Crear archivos de configuración inicial"""
        print("⚙️ Creando configuración inicial...")
        
        config_dir = self.base_dir / "antivirus_kali" / "configuraciones"
        config_dir.mkdir(exist_ok=True)
        
        # Configuración del Mini-SIEM
        siem_config = {
            "database": {
                "path": "siem_events.db",
                "retention_days": 30,
                "batch_size": 100
            },
            "collection": {
                "poll_interval": 1,
                "sources": [
                    "/var/log/auth.log",
                    "/var/log/syslog", 
                    "/var/log/dpkg.log"
                ]
            },
            "notifications": {
                "desktop": True,
                "terminal": True,
                "log_file": True
            }
        }
        
        config_file = config_dir / "siem_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(siem_config, f, indent=2, ensure_ascii=False)
            
        print(f"   ✅ Configuración creada: {config_file}")
        
        # Crear directorio de datos
        data_dir = self.base_dir / "antivirus_kali" / "data"
        data_dir.mkdir(exist_ok=True)
        print(f"   ✅ Directorio de datos: {data_dir}")
        
    def generar_script_inicio(self):
        """Generar script de inicio conveniente"""
        print("🚀 Generando script de inicio...")
        
        script_content = f"""#!/bin/bash
# Script de inicio para Ares Aegis
cd "{self.base_dir}"

# Activar entorno virtual si existe
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    echo "✅ Entorno virtual activado"
fi

# Verificar dependencias críticas
echo "🔍 Verificando sistema..."
python3 verificar_sistema.py --quick

if [ $? -eq 0 ]; then
    echo "🚀 Iniciando Ares Aegis..."
    python3 antivirus_kali/launcher.py
else
    echo "❌ Error en verificación del sistema"
    exit 1
fi
"""
        
        script_path = self.base_dir / "iniciar_ares_aegis.sh"
        with open(script_path, 'w') as f:
            f.write(script_content)
            
        # Hacer ejecutable
        os.chmod(script_path, 0o755)
        print(f"   ✅ Script creado: {script_path}")
        
    def ejecutar_verificacion_completa(self):
        """Ejecutar verificación completa del sistema"""
        print("=" * 60)
        print("🛡️  VERIFICACIÓN DEL SISTEMA ARES AEGIS  🛡️")
        print("=" * 60)
        print()
        
        self.verificar_python()
        print()
        
        self.verificar_dependencias_python()
        print()
        
        self.verificar_clamav()
        print()
        
        self.verificar_estructura_archivos()
        print()
        
        self.verificar_permisos_logs()
        print()
        
        self.verificar_base_datos()
        print()
        
        self.verificar_importaciones()
        print()
        
        self.crear_configuracion_inicial()
        print()
        
        self.generar_script_inicio()
        print()
        
        # Resumen final
        print("=" * 60)
        print("📊 RESUMEN DE VERIFICACIÓN")
        print("=" * 60)
        
        if not self.errores and not self.advertencias:
            print("🎉 ¡PERFECTO! Sistema completamente funcional")
            print()
            print("🚀 Para iniciar Ares Aegis:")
            print("   ./iniciar_ares_aegis.sh")
            print("   O directamente: python3 antivirus_kali/launcher.py")
            return True
            
        if self.errores:
            print(f"❌ ERRORES CRÍTICOS ({len(self.errores)}):")
            for error in self.errores:
                print(f"   • {error}")
            print()
            
        if self.advertencias:
            print(f"⚠️  ADVERTENCIAS ({len(self.advertencias)}):")
            for advertencia in self.advertencias:
                print(f"   • {advertencia}")
            print()
            
        if self.errores:
            print("🔧 SOLUCIÓN RECOMENDADA:")
            print("   1. Instalar dependencias faltantes:")
            print("      pip install -r requirements.txt")
            print("   2. Instalar ClamAV si no está disponible:")
            print("      sudo apt install clamav clamav-daemon")
            print("   3. Re-ejecutar verificación:")
            print("      python3 verificar_sistema.py")
            return False
        else:
            print("✅ Sistema funcional con advertencias menores")
            print("🚀 Puede proceder con el inicio del sistema")
            return True

def main():
    """Función principal"""
    verificador = VerificadorSistema()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        # Verificación rápida para script de inicio
        verificador.verificar_python()
        verificador.verificar_dependencias_python()
        verificador.verificar_estructura_archivos()
        
        if verificador.errores:
            print("❌ Errores críticos encontrados")
            sys.exit(1)
        else:
            print("✅ Verificación rápida exitosa")
            sys.exit(0)
    else:
        # Verificación completa
        exito = verificador.ejecutar_verificacion_completa()
        sys.exit(0 if exito else 1)

if __name__ == "__main__":
    main()
