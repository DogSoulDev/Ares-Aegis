#!/bin/bash
# Script de limpieza y optimización para Ares Aegis
# Elimina archivos temporales, cache y optimiza el proyecto

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════╗"
echo "║              🛡️  ARES AEGIS  🛡️               ║"
echo "║            Limpieza del Proyecto              ║"
echo "╚═══════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# Verificar directorio correcto
if [ ! -f "antivirus_kali/main.py" ]; then
    echo -e "${RED}❌ Ejecute este script desde el directorio raíz de Ares-Aegis${NC}"
    exit 1
fi

# Contar archivos antes de la limpieza
archivos_antes=$(find . -type f | wc -l)
tamaño_antes=$(du -sh . | cut -f1)

log_info "Estado inicial:"
echo "   • Archivos: $archivos_antes"
echo "   • Tamaño: $tamaño_antes"
echo ""

# 1. Limpiar archivos Python compilados
log_info "Limpiando archivos Python compilados..."
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.egg-info" -type d -exec rm -rf {} + 2>/dev/null || true
log_success "Archivos Python compilados eliminados"

# 2. Limpiar archivos de logs temporales
log_info "Limpiando logs temporales..."
find . -name "*.log" -size +10M -delete 2>/dev/null || true
find . -name "*.log.*" -delete 2>/dev/null || true
find . -name "debug.log" -delete 2>/dev/null || true
log_success "Logs temporales limpiados"

# 3. Limpiar archivos de backup
log_info "Limpiando archivos de backup..."
find . -name "*~" -delete 2>/dev/null || true
find . -name "*.bak" -delete 2>/dev/null || true
find . -name "*.orig" -delete 2>/dev/null || true
find . -name "*.swp" -delete 2>/dev/null || true
find . -name "*.swo" -delete 2>/dev/null || true
find . -name ".*.swp" -delete 2>/dev/null || true
log_success "Archivos de backup eliminados"

# 4. Limpiar archivos del sistema
log_info "Limpiando archivos del sistema..."
find . -name ".DS_Store" -delete 2>/dev/null || true
find . -name "Thumbs.db" -delete 2>/dev/null || true
find . -name "desktop.ini" -delete 2>/dev/null || true
log_success "Archivos del sistema eliminados"

# 5. Limpiar directorios de desarrollo
log_info "Limpiando directorios de desarrollo..."
find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name ".mypy_cache" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name ".coverage" -delete 2>/dev/null || true
find . -name "htmlcov" -type d -exec rm -rf {} + 2>/dev/null || true
log_success "Directorios de desarrollo limpiados"

# 6. Limpiar archivos temporales de Ares Aegis
log_info "Limpiando archivos temporales de Ares Aegis..."
find . -name "ares_aegis_*.tmp" -delete 2>/dev/null || true
find . -name "test_*.tmp" -delete 2>/dev/null || true
find . -name "*.pid" -delete 2>/dev/null || true

# Limpiar archivos de escaneo temporales
if [ -d "antivirus_kali/data" ]; then
    find antivirus_kali/data -name "temp_*" -delete 2>/dev/null || true
    find antivirus_kali/data -name "scan_*.tmp" -delete 2>/dev/null || true
fi

log_success "Archivos temporales de Ares Aegis eliminados"

# 7. Limpiar informes antiguos (mantener últimos 10)
if [ -d "antivirus_kali/informes" ]; then
    log_info "Limpiando informes antiguos..."
    cd antivirus_kali/informes
    ls -t *.pdf 2>/dev/null | tail -n +11 | xargs rm -f 2>/dev/null || true
    cd - >/dev/null
    log_success "Informes antiguos limpiados"
fi

# 8. Limpiar logs antiguos (mantener últimos 7 días)
if [ -d "logs" ]; then
    log_info "Limpiando logs antiguos..."
    find logs -name "*.log" -mtime +7 -delete 2>/dev/null || true
    log_success "Logs antiguos limpiados"
fi

# 9. Optimizar base de datos SQLite
log_info "Optimizando bases de datos..."
if [ -f "antivirus_kali/data/ares_aegis.db" ]; then
    sqlite3 antivirus_kali/data/ares_aegis.db "VACUUM;" 2>/dev/null || log_warning "No se pudo optimizar la base de datos"
    log_success "Base de datos optimizada"
fi

# 10. Limpiar archivos de configuración temporales
log_info "Limpiando configuraciones temporales..."
find . -name "*.conf.bak" -delete 2>/dev/null || true
find . -name "config_*.tmp" -delete 2>/dev/null || true
log_success "Configuraciones temporales limpiadas"

# 11. Verificar y reparar permisos
log_info "Verificando permisos de archivos..."
find . -type f -name "*.sh" -exec chmod +x {} \; 2>/dev/null || true
find . -type f -name "*.py" -path "*/bin/*" -exec chmod +x {} \; 2>/dev/null || true
chmod +x verificacion_rapida.py 2>/dev/null || true
log_success "Permisos verificados"

# 12. Crear archivo .gitignore optimizado si no existe
if [ ! -f ".gitignore" ]; then
    log_info "Creando .gitignore optimizado..."
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt
.coverage
htmlcov/
.pytest_cache/
.mypy_cache/

# Ares Aegis específicos
*.log
*.tmp
*.pid
antivirus_kali/data/*.db-journal
antivirus_kali/data/temp_*
logs/*.log.*
reports/temp_*

# Sistema
.DS_Store
Thumbs.db
desktop.ini
*~
*.bak
*.orig
*.swp
*.swo

# IDE
.vscode/
.idea/
*.sublime-*

# Archivos sensibles
*.key
*.pem
config_local.py
.env
EOF
    log_success ".gitignore creado"
fi

echo ""

# Estadísticas finales
archivos_despues=$(find . -type f | wc -l)
tamaño_despues=$(du -sh . | cut -f1)
archivos_eliminados=$((archivos_antes - archivos_despues))

echo -e "${GREEN}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    🎉 LIMPIEZA COMPLETADA                  ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

log_success "Resumen de limpieza:"
echo "   • Archivos eliminados: $archivos_eliminados"
echo "   • Archivos restantes: $archivos_despues"
echo "   • Tamaño anterior: $tamaño_antes"
echo "   • Tamaño actual: $tamaño_despues"
echo ""

log_info "El proyecto ha sido optimizado y está listo para distribución"
echo ""

# Sugerir siguientes pasos
log_info "Siguientes pasos recomendados:"
echo "   • Ejecutar tests: ./test_ci.sh"
echo "   • Verificar sistema: ./verificacion_rapida.py"
echo "   • Crear backup: tar -czf ares-aegis-backup-$(date +%Y%m%d).tar.gz ."
echo ""
