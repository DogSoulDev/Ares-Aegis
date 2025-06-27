FROM python:3.11-slim

# Instala dependencias del sistema necesarias para PySide6, scapy, yara, policykit, etc.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3-pyside6 python3-psutil python3-requests python3-pyinotify python3-scapy python3-pyqtgraph python3-reportlab python3-yara python3-qrcode policykit-1 sudo xauth dbus-x11 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copia el código fuente
COPY antivirus_kali /usr/share/ares-aegis/
WORKDIR /usr/share/ares-aegis/

# Da permisos de ejecución al wrapper
RUN chmod +x /usr/share/ares-aegis/ares-aegis-wrapper.sh

# Crea un usuario no root para pruebas de privilegios
RUN useradd -ms /bin/bash aresuser
USER aresuser

# Expone el comando por defecto (el usuario puede usar pkexec en entorno gráfico real)
CMD ["python3", "principal.py"]
