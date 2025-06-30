#!/bin/bash
# Script de instalación automática completa para Ares Aegis
# Instala todas las dependencias y configura el sistema
# Versión optimizada con mejor manejo de errores

set -e  # Salir si hay errores

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Función para logging
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_step() {
    echo -e "${PURPLE}🔧 $1${NC}"
}

# Banner de instalación
echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════╗"
echo "║              🛡️  ARES AEGIS  🛡️               ║"
echo "║           Instalación Automática              ║"
echo "║                                               ║"
echo "║  Sistema de Seguridad Avanzado para Linux     ║"
echo "╚═══════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# Verificar privilegios
if [ "$EUID" -eq 0 ]; then
    log_error "No ejecute este script como root. Use su usuario normal."
    exit 1
fi

# Verificar directorio correcto
if [ ! -f "antivirus_kali/main.py" ]; then
    log_error "Ejecute este script desde el directorio raíz de Ares-Aegis"
    exit 1
fi

# Detectar distribución
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$ID
else
    log_warning "No se pudo detectar la distribución. Asumiendo Debian/Ubuntu"
    DISTRO="ubuntu"
fi

log_info "Distribución detectada: $DISTRO"
log_info "Usuario actual: $USER"
echo ""

# Paso 1: Actualizar sistema
log_step "Paso 1: Actualizando sistema..."
if command -v apt >/dev/null 2>&1; then
    sudo apt update
    log_success "Sistema actualizado"
elif command -v pacman >/dev/null 2>&1; then
    sudo pacman -Sy
    log_success "Sistema actualizado (Arch)"
else
    log_warning "Gestor de paquetes no reconocido. Continuando..."
fi

echo ""

# Paso 2: Instalar dependencias del sistema
log_step "Paso 2: Instalando dependencias del sistema..."

install_packages() {
    local packages="$1"
    local package_manager="$2"
    
    case $package_manager in
        "apt")
            sudo apt install -y $packages
            ;;
        "pacman")
            sudo pacman -S --noconfirm $packages
            ;;
        "dnf")
            sudo dnf install -y $packages
            ;;
        *)
            log_error "Gestor de paquetes $package_manager no soportado"
            return 1
            ;;
    esac
}

# Paquetes básicos requeridos
if command -v apt >/dev/null 2>&1; then
    PACKAGES="python3-pip python3-dev python3-venv clamav clamav-daemon rkhunter chkrootkit"
    install_packages "$PACKAGES" "apt"
elif command -v pacman >/dev/null 2>&1; then
    PACKAGES="python-pip python clamav rkhunter chkrootkit"
    install_packages "$PACKAGES" "pacman"
elif command -v dnf >/dev/null 2>&1; then
    PACKAGES="python3-pip python3-devel python3-virtualenv clamav clamav-update rkhunter chkrootkit"
    install_packages "$PACKAGES" "dnf"
else
    log_error "No se encontró un gestor de paquetes compatible"
    exit 1
fi

log_success "Dependencias del sistema instaladas"
echo ""

# Paso 3: Crear entorno virtual
log_step "Paso 3: Configurando entorno virtual Python..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    log_success "Entorno virtual creado"
else
    log_info "Entorno virtual ya existe"
fi

# Activar entorno virtual
source .venv/bin/activate
log_success "Entorno virtual activado"
echo ""

# Paso 4: Instalar dependencias Python
log_step "Paso 4: Instalando dependencias Python..."
pip install --upgrade pip
pip install -r requirements.txt || {
    log_warning "requirements.txt no encontrado, instalando paquetes básicos..."
    pip install PySide6 aiofiles plyer psutil python-dateutil sqlite3
}
log_success "Dependencias Python instaladas"
echo ""

# Paso 5: Configurar ClamAV
log_step "Paso 5: Configurando ClamAV..."
sudo systemctl stop clamav-freshclam 2>/dev/null || true

# Actualizar definiciones de virus
if sudo freshclam; then
    log_success "Definiciones de ClamAV actualizadas"
else
    log_warning "Error actualizando ClamAV, continuando..."
fi

# Habilitar servicios de ClamAV
sudo systemctl start clamav-freshclam 2>/dev/null || log_warning "No se pudo iniciar clamav-freshclam"
sudo systemctl enable clamav-freshclam 2>/dev/null || log_warning "No se pudo habilitar clamav-freshclam"
sudo systemctl start clamav-daemon 2>/dev/null || log_warning "No se pudo iniciar clamav-daemon"
sudo systemctl enable clamav-daemon 2>/dev/null || log_warning "No se pudo habilitar clamav-daemon"

log_success "ClamAV configurado"
echo ""

# Paso 6: Configurar permisos para Mini-SIEM
log_step "Paso 6: Configurando permisos para Mini-SIEM..."
sudo usermod -a -G adm,systemd-journal $USER 2>/dev/null || {
    log_warning "No se pudieron agregar grupos adm,systemd-journal"
}

# Verificar si el usuario puede leer logs
if [ -r /var/log/auth.log ] || [ -r /var/log/secure ]; then
    log_success "Acceso a logs del sistema verificado"
else
    log_warning "Acceso limitado a logs del sistema - algunas funciones del SIEM pueden estar restringidas"
fi
echo ""

# Paso 7: Crear directorios necesarios
log_step "Paso 7: Creando estructura de directorios..."
mkdir -p antivirus_kali/data
mkdir -p antivirus_kali/configuraciones
mkdir -p antivirus_kali/recursos/iconos
mkdir -p antivirus_kali/informes
mkdir -p logs
mkdir -p reports

log_success "Directorios creados"
echo ""

# Paso 8: Configurar archivos de configuración
log_step "Paso 8: Configurando archivos del sistema..."

# Crear configuración básica si no existe
if [ ! -f "antivirus_kali/configuraciones/siem_config.json" ]; then
    cat > antivirus_kali/configuraciones/siem_config.json << EOF
{
    "log_sources": [
        "/var/log/auth.log",
        "/var/log/syslog",
        "/var/log/security"
    ],
    "correlation_rules": [],
    "alert_thresholds": {
        "failed_logins": 5,
        "suspicious_commands": 3
    },
    "retention_days": 30
}
EOF
    log_success "Configuración SIEM creada"
fi

echo ""

# Paso 9: Verificar herramientas de seguridad opcionales
log_step "Paso 9: Verificando herramientas de seguridad..."

check_tool() {
    if command -v $1 >/dev/null 2>&1; then
        log_success "$1 disponible"
    else
        log_warning "$1 no está instalado - funcionalidad limitada"
    fi
}

check_tool "nmap"
check_tool "wireshark"
check_tool "netstat"
check_tool "ss"
check_tool "iptables"

echo ""

# Paso 10: Hacer ejecutables los scripts
log_step "Paso 10: Configurando permisos de archivos..."
chmod +x iniciar_ares_aegis.sh 2>/dev/null || log_warning "iniciar_ares_aegis.sh no encontrado"
chmod +x verificacion_rapida.py
chmod +x verificar_sistema.py 2>/dev/null || log_warning "verificar_sistema.py no encontrado"
chmod +x test_ci.sh 2>/dev/null || log_warning "test_ci.sh no encontrado"

log_success "Permisos configurados"
echo ""

# Paso 11: Verificación final
log_step "Paso 11: Verificando instalación..."

# Verificar imports de Python
if python3 -c "import antivirus_kali; print('Módulos importados correctamente')" 2>/dev/null; then
    log_success "Módulos Python verificados"
else
    log_warning "Algunos módulos Python pueden tener problemas"
fi

# Verificar script de verificación rápida
if python3 verificacion_rapida.py --silencioso 2>/dev/null; then
    log_success "Script de verificación rápida funcional"
else
    log_warning "Script de verificación rápida puede tener problemas"
fi

echo ""

# Resumen final
echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                ✅ INSTALACIÓN COMPLETADA                 ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

log_info "🚀 Para iniciar Ares Aegis:"
echo "   ./iniciar_ares_aegis.sh"
echo ""

log_info "� Verificación rápida del sistema:"
echo "   ./verificacion_rapida.py"
echo ""

log_info "🔍 Verificación completa:"
echo "   ./verificacion_rapida.py --completo"
echo ""

log_info "📚 Documentación:"
echo "   README_COMPLETO.md"
echo ""

log_info "📊 Análisis de calidad del código:"
echo "   ANALISIS_CALIDAD_CODIGO.md"
echo ""

log_warning "IMPORTANTE: Reinicie su sesión para aplicar permisos de grupo"
echo "   - Cierre sesión y vuelva a iniciar"
echo "   - O ejecute: newgrp adm"
echo ""

log_success "🎉 ¡Ares Aegis está listo para usar!"
echo ""

# Mostrar estado de servicios críticos
log_info "Estado de servicios:"
systemctl is-active clamav-daemon 2>/dev/null && echo "   ✅ ClamAV daemon activo" || echo "   ⚠️  ClamAV daemon inactivo"
systemctl is-active clamav-freshclam 2>/dev/null && echo "   ✅ ClamAV actualizador activo" || echo "   ⚠️  ClamAV actualizador inactivo"

echo ""
log_info "Instalación completada en: $(date)"
