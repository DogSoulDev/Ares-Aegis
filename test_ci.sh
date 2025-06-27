#!/bin/bash
# Script de test y linting para integración continua de Ares Aegis

set -e

# Activar entorno virtual si existe
if [ -f antivirus_kali/.venv/bin/activate ]; then
    source antivirus_kali/.venv/bin/activate
fi

# Instalar dependencias si es necesario
pip install --upgrade pip
pip install -r antivirus_kali/requirements.txt

# Linting (puedes añadir flake8, black, etc.)
if command -v flake8 >/dev/null 2>&1; then
    echo "Ejecutando flake8..."
    flake8 antivirus_kali/ || true
fi

# Tests
pytest -v antivirus_kali/tests/
