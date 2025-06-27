# Cómo compilar el paquete .deb de Ares Aegis

1. Instala las herramientas necesarias:
   ```bash
   sudo apt update
   sudo apt install build-essential devscripts debhelper dh-python python3-all
   ```

2. Desde la raíz del proyecto, ejecuta:
   ```bash
   cd antivirus_kali
   debuild -us -uc
   ```

3. El archivo .deb generado estará en el directorio superior (`../ares-aegis_*.deb`).

4. Para instalarlo:
   ```bash
   sudo dpkg -i ../ares-aegis_*.deb
   sudo apt-get install -f  # Para resolver dependencias si es necesario
   ```

5. El lanzador gráfico aparecerá en el menú de aplicaciones como "Ares Aegis".

---

- El wrapper y el lanzador .desktop garantizan privilegios y entorno automáticamente.
- Si necesitas probar en Docker:
   ```bash
   docker build -t ares-aegis .
   docker run -it --rm --env DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix ares-aegis
   ```

- Para pruebas gráficas, ejecuta en un entorno con X11 o usa X11 forwarding.
