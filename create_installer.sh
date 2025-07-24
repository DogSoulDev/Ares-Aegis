#!/bin/bash
# create_installer.sh - Crear instalador autocontenido para Ares Aegis

set -e

echo "🚀 Creando instalador autocontenido de Ares Aegis v4.0"
echo "======================================================"

# Variables
INSTALLER_NAME="ares-aegis-installer.run"
TEMP_DIR="installer_temp"
TAR_FILE="ares-aegis-data.tar.gz"

# Limpiar archivos anteriores
if [ -f "$INSTALLER_NAME" ]; then
    echo "🗑️ Eliminando instalador anterior..."
    rm -f "$INSTALLER_NAME"
fi

if [ -d "$TEMP_DIR" ]; then
    rm -rf "$TEMP_DIR"
fi

# Crear directorio temporal
echo "📁 Preparando archivos para el instalador..."
mkdir -p "$TEMP_DIR"

# Copiar archivos esenciales
echo "📋 Copiando archivos del proyecto..."
cp -r ares_aegis "$TEMP_DIR/"
cp main.py "$TEMP_DIR/"
cp -r recursos "$TEMP_DIR/" 2>/dev/null || true
cp -r configuracion "$TEMP_DIR/" 2>/dev/null || true
cp -r data "$TEMP_DIR/" 2>/dev/null || true
mkdir -p "$TEMP_DIR/cuarentena"
mkdir -p "$TEMP_DIR/reportes"

# Limpiar archivos innecesarios del temp
echo "🧹 Limpiando archivos temporales..."
find "$TEMP_DIR" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find "$TEMP_DIR" -name "*.pyc" -type f -delete 2>/dev/null || true
find "$TEMP_DIR" -name "*.tmp" -type f -delete 2>/dev/null || true

# Crear archivo tar comprimido
echo "📦 Comprimiendo archivos..."
tar -czf "$TAR_FILE" -C "$TEMP_DIR" .

# Leer el template del instalador
echo "🔧 Creando instalador autocontenido..."
if [ ! -f "ares-aegis-installer.run" ]; then
    echo "❌ Error: No se encuentra el template del instalador"
    exit 1
fi

# Crear el instalador final
cp ares-aegis-installer.run "${INSTALLER_NAME}.tmp"
echo "" >> "${INSTALLER_NAME}.tmp"
cat "$TAR_FILE" >> "${INSTALLER_NAME}.tmp"
mv "${INSTALLER_NAME}.tmp" "$INSTALLER_NAME"

# Hacer ejecutable
chmod +x "$INSTALLER_NAME"

# Limpiar archivos temporales
rm -rf "$TEMP_DIR"
rm -f "$TAR_FILE"

# Verificar el instalador creado
echo "✅ Verificando instalador creado..."
if [ -f "$INSTALLER_NAME" ]; then
    TAMAÑO=$(du -h "$INSTALLER_NAME" | cut -f1)
    echo "📊 Instalador creado: $INSTALLER_NAME ($TAMAÑO)"
else
    echo "❌ Error: No se pudo crear el instalador"
    exit 1
fi

echo ""
echo "🎉 ¡INSTALADOR AUTOCONTENIDO CREADO EXITOSAMENTE!"
echo "=================================================="
echo ""
echo "📁 Archivo generado: $INSTALLER_NAME"
echo "📊 Tamaño: $TAMAÑO"
echo ""
echo "🚀 INSTRUCCIONES PARA EL USUARIO:"
echo ""
echo "1. Transferir el archivo a Kali Linux:"
echo "   scp $INSTALLER_NAME user@kali-ip:~/"
echo ""
echo "2. En Kali Linux, hacer ejecutable e instalar:"
echo "   chmod +x $INSTALLER_NAME"
echo "   sudo ./$INSTALLER_NAME"
echo ""
echo "3. Para desinstalar (si es necesario):"
echo "   sudo ./$INSTALLER_NAME --uninstall"
echo ""
echo "4. Ejecutar Ares Aegis:"
echo "   ares-aegis"
echo "   # O desde Aplicaciones → Security → Ares Aegis"
echo ""
echo "✨ ¡LISTO! Solo necesitas transferir 1 archivo a Kali Linux"
