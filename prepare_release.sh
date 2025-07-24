#!/bin/bash
# prepare_release.sh - Script para preparar Ares Aegis para distribución

set -e

echo "🛡️ PREPARANDO ARES AEGIS PARA DISTRIBUCIÓN"
echo "============================================"

# Verificar que estamos en Kali Linux
if [ ! -f "/etc/os-release" ] || ! grep -q "kali" /etc/os-release; then
    echo "⚠️ Advertencia: Este script está optimizado para Kali Linux"
fi

# Función para mostrar progreso
mostrar_progreso() {
    echo "📋 $1..."
}

# 1. Limpiar archivos temporales y de desarrollo
mostrar_progreso "Limpiando archivos temporales"
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -type f -delete 2>/dev/null || true
find . -name "*.pyo" -type f -delete 2>/dev/null || true
find . -name "*.tmp" -type f -delete 2>/dev/null || true
find . -name "*.temp" -type f -delete 2>/dev/null || true
find . -name "*.backup" -type f -delete 2>/dev/null || true
find . -name "*~" -type f -delete 2>/dev/null || true

# 2. Verificar archivos esenciales
mostrar_progreso "Verificando archivos esenciales"
archivos_esenciales=(
    "main.py"
    "ares_aegis/__init__.py" 
    "recursos/AresAegis.png"
    "recursos/aresIcon.png"
    "debian/control"
    "debian/postinst"
    "debian/postrm"
)

for archivo in "${archivos_esenciales[@]}"; do
    if [ ! -f "$archivo" ]; then
        echo "❌ Error: Archivo esencial faltante: $archivo"
        exit 1
    fi
done

echo "✅ Todos los archivos esenciales presentes"

# 3. Verificar permisos de iconos
mostrar_progreso "Verificando recursos"
if [ -f "recursos/AresAegis.png" ]; then
    echo "✅ Icono principal encontrado: recursos/AresAegis.png"
else
    echo "❌ Error: Icono principal no encontrado"
    exit 1
fi

if [ -f "recursos/aresIcon.png" ]; then
    echo "✅ Icono secundario encontrado: recursos/aresIcon.png"
else
    echo "❌ Error: Icono secundario no encontrado"
    exit 1
fi

# 4. Verificar configuración Debian
mostrar_progreso "Verificando configuración del paquete Debian"
if grep -q "DogSoulDev https://github.com/DogSoulDev/Ares-Aegis" debian/control; then
    echo "✅ Información de mantenedor correcta"
else
    echo "❌ Error: Información de mantenedor incorrecta en debian/control"
    exit 1
fi

# 5. Hacer ejecutables los scripts necesarios
mostrar_progreso "Configurando permisos de scripts"
chmod +x main.py
chmod +x debian/postinst
chmod +x debian/postrm
chmod +x build_deb.sh

# 6. Verificar que el programa principal funciona
mostrar_progreso "Verificando funcionalidad principal"
python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from ares_aegis.utils.ayuda_logging import configurar_logging_completo
    from ares_aegis.vista.interfaz_principal import InterfazPrincipalAresAegis
    print('✅ Importaciones principales exitosas')
except ImportError as e:
    print(f'❌ Error de importación: {e}')
    sys.exit(1)
"

# 7. Mostrar estadísticas del proyecto
mostrar_progreso "Generando estadísticas del proyecto"
echo ""
echo "📊 ESTADÍSTICAS DEL PROYECTO:"
echo "=============================="
echo "📁 Archivos Python: $(find . -name "*.py" | wc -l)"
echo "📁 Archivos de configuración: $(find configuracion -name "*.json" 2>/dev/null | wc -l || echo 0)"
echo "📁 Wordlists: $(find data -name "*.txt" 2>/dev/null | wc -l || echo 0)"
echo "📁 Recursos: $(find recursos -type f 2>/dev/null | wc -l || echo 0)"
echo "📦 Tamaño total: $(du -sh . 2>/dev/null | cut -f1 || echo "N/A")"

# 8. Verificar dependencias del sistema
mostrar_progreso "Verificando dependencias del sistema"
dependencias=("python3" "python3-tk")
for dep in "${dependencias[@]}"; do
    if dpkg -l | grep -q "^ii.*$dep"; then
        echo "✅ $dep instalado"
    else
        echo "⚠️ $dep no encontrado (será instalado por el paquete .deb)"
    fi
done

echo ""
echo "🎉 ¡PREPARACIÓN COMPLETADA EXITOSAMENTE!"
echo "========================================"
echo ""
echo "📋 SIGUIENTE PASO:"
echo "   ./build_deb.sh  # Para construir el paquete .deb"
echo ""
echo "🚀 CARACTERÍSTICAS PREPARADAS:"
echo "   ✅ Verificación automática de permisos root"
echo "   ✅ Iconos y recursos incluidos"
echo "   ✅ Script de lanzamiento para Kali Linux"
echo "   ✅ Entrada de menú de aplicaciones"
echo "   ✅ Instalación/desinstalación limpia"
echo "   ✅ Compatibilidad completa con Kali Linux"
echo ""
echo "🔐 PERMISOS:"
echo "   • El programa solicitará automáticamente permisos root"
echo "   • Funcionalidad completa con sudo/pkexec"
echo "   • Modo limitado sin permisos (con advertencia)"
echo ""
echo "📦 INSTALACIÓN:"
echo "   sudo dpkg -i ares-aegis_4.0.0_all.deb"
echo "   sudo apt-get install -f  # Si hay dependencias faltantes"
