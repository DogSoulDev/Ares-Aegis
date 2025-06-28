#!/bin/bash
# Script de inicio para Ares Aegis
cd "/home/dogsoul/Ares-Aegis"

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
