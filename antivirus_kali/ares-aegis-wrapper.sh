#!/bin/bash

# Wrapper mínimo: solo delega en el lanzador Python que gestiona privilegios y entorno
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
cd "$SCRIPT_DIR"

# Usar .venv si existe
if [ -x "../.venv/bin/python" ]; then
    ../.venv/bin/python launcher_priv.py "$@"
else
    python3 launcher_priv.py "$@"
fi
