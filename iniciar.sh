#!/bin/bash
# Script de Inicio Optimizado - Ares Aegis
# Ejecuta el antivirus con verificaciones automáticas

echo "🛡️  ARES AEGIS - ANTIVIRUS AVANZADO"
echo "=================================="

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python3 no está instalado"
    exit 1
fi

# Verificar privilegios
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  Ejecutando sin privilegios root"
    echo "   Algunas funciones estarán limitadas"
    echo "   Para funcionalidad completa: sudo $0"
fi

# Activar entorno virtual si existe
if [ -d ".venv" ]; then
    echo "🐍 Activando entorno virtual..."
    source .venv/bin/activate
fi

# Verificar estructura básica
if [ ! -f "main.py" ]; then
    echo "❌ Error: main.py no encontrado"
    exit 1
fi

# Ejecutar aplicación
echo "✅ Iniciando Ares Aegis..."
python3 main.py
