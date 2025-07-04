#!/bin/bash

# 🛡️ Ares Aegis - Script de Inicio Rápido
# Autor: DogSoulDev
# Versión: 2.0.0

echo "🛡️  Iniciando Ares Aegis - Sistema Antivirus y SIEM"
echo "===================================================="

# Verificar que estamos en el directorio correcto
if [ ! -f "main.py" ]; then
    echo "❌ Error: No se encuentra main.py"
    echo "💡 Ejecuta este script desde el directorio del proyecto"
    exit 1
fi

# Verificar Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 no está instalado"
    echo "💡 Instala Python 3: sudo apt install python3"
    exit 1
fi

# Verificar privilegios de root
if [ "$EUID" -ne 0 ]; then
    echo "🚨 Este programa requiere privilegios de administrador"
    echo "💡 Ejecutando con sudo..."
    exec sudo "$0" "$@"
fi

# Mostrar información del sistema
echo "🔧 Verificando sistema..."
echo "📍 Directorio: $(pwd)"
echo "🐍 Python: $(python3 --version)"
echo "👤 Usuario: $(whoami)"
echo "🖥️  Sistema: $(uname -s) $(uname -r)"

# Verificar estructura del proyecto
echo "🔍 Verificando estructura del proyecto..."
required_dirs=("ares_aegis" "ares_aegis/modelos" "ares_aegis/vista" "ares_aegis/controladores" "configuracion" "logs")
for dir in "${required_dirs[@]}"; do
    if [ ! -d "$dir" ]; then
        echo "❌ Error: Directorio faltante: $dir"
        exit 1
    fi
done

required_files=("main.py" "ares_aegis/controladores/controlador_principal.py" "configuracion/firmas.txt")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Error: Archivo faltante: $file"
        exit 1
    fi
done

echo "✅ Estructura del proyecto verificada"

# Crear directorios si no existen
mkdir -p logs
mkdir -p cuarentena

# Ejecutar test opcional
if [ "$1" = "--test" ] || [ "$1" = "-t" ]; then
    echo "🧪 Ejecutando pruebas del sistema..."
    python3 test_sistema_completo.py
    if [ $? -eq 0 ]; then
        echo "✅ Todas las pruebas pasaron"
    else
        echo "❌ Algunas pruebas fallaron"
        read -p "¿Continuar de todos modos? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
fi

# Mostrar banner
echo ""
echo "🎌 ════════════════════════════════════════════════ 🎌"
echo "    🛡️  ARES AEGIS - SISTEMA ANTIVIRUS Y SIEM     "
echo "    📊 Protección completa con estética japonesa   "
echo "    🔰 Versión 2.0.0 - DogSoulDev                  "
echo "🎌 ════════════════════════════════════════════════ 🎌"
echo ""

# Verificar display para GUI
if [ -z "$DISPLAY" ]; then
    echo "⚠️  Advertencia: No se detectó entorno gráfico (DISPLAY no configurado)"
    echo "💡 La interfaz gráfica podría no funcionar correctamente"
    read -p "¿Continuar de todos modos? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Limpiar logs antiguos (opcional)
if [ "$1" = "--clean" ] || [ "$1" = "-c" ]; then
    echo "🧹 Limpiando logs antiguos..."
    rm -f ares_aegis.log logs/eventos_siem.json
    echo "✅ Logs limpiados"
fi

echo "🚀 Iniciando Ares Aegis..."
echo "💡 Para cerrar el programa usa Ctrl+C"
echo ""

# Ejecutar el programa principal
python3 main.py

# Mostrar mensaje de cierre
echo ""
echo "🔒 Ares Aegis finalizado"
echo "🙏 ¡Gracias por usar Ares Aegis!"
