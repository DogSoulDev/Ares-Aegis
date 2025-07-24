#!/bin/bash
# build_deb.sh - Script para construir el paquete .deb de Ares Aegis

set -e

echo "🛡️ Construyendo paquete .deb de Ares Aegis para Kali Linux"
echo "============================================================"

# Variables
PACKAGE_NAME="ares-aegis"
VERSION="4.0.0"
ARCH="all"
BUILD_DIR="build_deb"
DEB_DIR="${BUILD_DIR}/DEBIAN"

# Limpiar build anterior
if [ -d "$BUILD_DIR" ]; then
    echo "🗑️ Limpiando build anterior..."
    rm -rf "$BUILD_DIR"
fi

# Crear estructura de directorios
echo "📁 Creando estructura de directorios..."
mkdir -p "${BUILD_DIR}/opt/ares-aegis"
mkdir -p "${BUILD_DIR}/usr/share/applications"
mkdir -p "${BUILD_DIR}/usr/share/pixmaps"
mkdir -p "${BUILD_DIR}/usr/bin"
mkdir -p "${DEB_DIR}"

# Copiar archivos del proyecto
echo "📋 Copiando archivos del proyecto..."
cp -r ares_aegis "${BUILD_DIR}/opt/ares-aegis/"
cp main.py "${BUILD_DIR}/opt/ares-aegis/"
cp -r configuracion "${BUILD_DIR}/opt/ares-aegis/" 2>/dev/null || true
cp -r data "${BUILD_DIR}/opt/ares-aegis/" 2>/dev/null || true
cp -r recursos "${BUILD_DIR}/opt/ares-aegis/" 2>/dev/null || true

# Copiar iconos
echo "🎨 Copiando iconos..."
if [ -f "recursos/AresAegis.png" ]; then
    cp recursos/AresAegis.png "${BUILD_DIR}/usr/share/pixmaps/ares-aegis.png"
fi

if [ -f "recursos/aresIcon.png" ]; then
    cp recursos/aresIcon.png "${BUILD_DIR}/usr/share/pixmaps/ares-aegis-icon.png"
fi

# Crear launcher script
echo "🚀 Creando script de lanzamiento..."
cat > "${BUILD_DIR}/usr/bin/ares-aegis" << 'EOF'
#!/bin/bash
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
fi
EOF

chmod +x "${BUILD_DIR}/usr/bin/ares-aegis"

# Crear archivo .desktop
echo "🖥️ Creando entrada del menú..."
cat > "${BUILD_DIR}/usr/share/applications/ares-aegis.desktop" << 'EOF'
[Desktop Entry]
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
EOF

# Copiar archivos de control de Debian
echo "📦 Configurando metadatos del paquete..."
cp debian/control "${DEB_DIR}/"
cp debian/postinst "${DEB_DIR}/"
cp debian/postrm "${DEB_DIR}/"

# Hacer ejecutables los scripts
chmod +x "${DEB_DIR}/postinst"
chmod +x "${DEB_DIR}/postrm"

# Establecer permisos correctos
echo "🔧 Configurando permisos..."
find "${BUILD_DIR}" -type d -exec chmod 755 {} \;
find "${BUILD_DIR}" -type f -exec chmod 644 {} \;
chmod +x "${BUILD_DIR}/usr/bin/ares-aegis"
chmod +x "${BUILD_DIR}/opt/ares-aegis/main.py"

# Construir el paquete .deb
echo "🔨 Construyendo paquete .deb..."
dpkg-deb --build "$BUILD_DIR" "${PACKAGE_NAME}_${VERSION}_${ARCH}.deb"

# Verificar el paquete
echo "✅ Verificando paquete..."
dpkg-deb --info "${PACKAGE_NAME}_${VERSION}_${ARCH}.deb"
dpkg-deb --contents "${PACKAGE_NAME}_${VERSION}_${ARCH}.deb"

echo ""
echo "🎉 ¡Paquete .deb construido exitosamente!"
echo "📦 Archivo: ${PACKAGE_NAME}_${VERSION}_${ARCH}.deb"
echo ""
echo "📋 Para instalar:"
echo "   sudo dpkg -i ${PACKAGE_NAME}_${VERSION}_${ARCH}.deb"
echo "   sudo apt-get install -f  # Si hay dependencias faltantes"
echo ""
echo "🚀 Para ejecutar después de instalar:"
echo "   ares-aegis                # Desde terminal"
echo "   sudo ares-aegis           # Con permisos completos"
echo "   # O desde el menú de aplicaciones en Security"
