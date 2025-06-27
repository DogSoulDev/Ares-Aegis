#!/bin/bash
# Wrapper seguro para lanzar Ares Aegis con privilegios root usando pkexec
# Garantiza privacidad: no envía datos fuera, solo ejecuta localmente

# Este script debe tener permisos de ejecución: chmod +x ares-aegis-wrapper.sh
# No modifica variables globales del sistema ni almacena contraseñas.

# Ruta absoluta al directorio de instalación (ajustar si se instala en otro sitio)
INSTALL_DIR="$(dirname "$(readlink -f "$0")")"
PROJECT_ROOT="$(dirname "$INSTALL_DIR")"
export PYTHONPATH="$INSTALL_DIR:$PROJECT_ROOT"



# Heredar entorno gráfico para Qt y dar acceso temporal a root
ORIG_USER=${SUDO_USER:-$USER}
if [ -z "$DISPLAY" ]; then
    # Intentar detectar el DISPLAY real del usuario
    USER_DISPLAY=$(w | grep -m1 $ORIG_USER | grep -oP '\(:[0-9]+\)' | head -1 | tr -d '()')
    if [ -n "$USER_DISPLAY" ]; then
        export DISPLAY="$USER_DISPLAY"
    else
        export DISPLAY=":0"
    fi
fi
if [ -z "$XAUTHORITY" ]; then
    export XAUTHORITY="/home/$ORIG_USER/.Xauthority"
fi

# Comprobar si root tiene acceso al X server
if ! xauth list "$DISPLAY" | grep -q "$ORIG_USER" && command -v xhost >/dev/null 2>&1; then
    xhost +SI:localuser:root >/dev/null 2>&1
    XHOST_ADDED=1
else
    XHOST_ADDED=0
fi

# Verificar acceso X11 antes de continuar
if ! xauth list "$DISPLAY" | grep -q "$ORIG_USER" && [ "$XHOST_ADDED" = "0" ]; then
    MSG="\nERROR: No hay autorización X11 para root en $DISPLAY.\n\nEjecuta en tu terminal de usuario:\n\n  xhost +SI:localuser:root\n\ny luego vuelve a lanzar el programa.\n\nEsto es necesario para que la interfaz gráfica funcione como root."
    if command -v zenity >/dev/null 2>&1; then
        zenity --error --title="Ares Aegis - Error de entorno gráfico" --text="$MSG"
    elif command -v kdialog >/dev/null 2>&1; then
        kdialog --error "$MSG" "Ares Aegis - Error de entorno gráfico"
    elif command -v xmessage >/dev/null 2>&1; then
        xmessage "$MSG"
    else
        echo "$MSG" >&2
    fi
    exit 1
fi

# Log de errores para depuración
LOGFILE="/tmp/ares_aegis_wrapper.log"
ERRFILE="/tmp/ares_aegis_python_error.log"
echo "[Ares-Aegis Wrapper] Lanzando desde $INSTALL_DIR como $(whoami) con DISPLAY=$DISPLAY XAUTHORITY=$XAUTHORITY" > "$LOGFILE"


# Si existe un entorno virtual, usar su Python y entorno
if [ -x "$PROJECT_ROOT/.venv/bin/python" ]; then
    VENV_PY="$PROJECT_ROOT/.venv/bin/python"
    VENV_BIN="$PROJECT_ROOT/.venv/bin"
    export PATH="$VENV_BIN:$PATH"
    "$VENV_PY" "$INSTALL_DIR/principal.py" "$@" 2> "$ERRFILE"
    STATUS=$?
else
    python3 "$INSTALL_DIR/principal.py" "$@" 2> "$ERRFILE"
    STATUS=$?
fi

# Restaurar seguridad del X server
if [ "$XHOST_ADDED" = "1" ]; then
    xhost -SI:localuser:root >/dev/null 2>&1
fi

# Si hubo error, mostrarlo en zenity/kdialog/xmessage si están disponibles
if [ $STATUS -ne 0 ]; then
    MSG="Ares Aegis no pudo iniciarse correctamente.\n\nRevisa el log de error en $ERRFILE.\n\n$(head -20 "$ERRFILE")"
    if command -v zenity >/dev/null 2>&1; then
        zenity --error --title="Ares Aegis - Error de inicio" --text="$MSG"
    elif command -v kdialog >/dev/null 2>&1; then
        kdialog --error "$MSG" "Ares Aegis - Error de inicio"
    elif command -v xmessage >/dev/null 2>&1; then
        xmessage "$MSG"
    else
        echo "$MSG" >&2
    fi
    exit $STATUS
fi
