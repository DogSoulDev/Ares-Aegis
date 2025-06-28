# ARES AEGIS - SISTEMA DE SEGURIDAD AVANZADO CON MINI-SIEM

## 🛡️ DESCRIPCIÓN GENERAL

Ares Aegis es un sistema de seguridad avanzado diseñado específicamente para Kali Linux que combina:
- **Antivirus multicapa** con motores ClamAV, YARA y análisis de hashes
- **Mini-SIEM integrado** para correlación de eventos y detección de amenazas
- **Interfaz moderna** desarrollada con PySide6/Qt
- **Monitoreo en tiempo real** del sistema y red
- **Arquitectura MVC** para máxima escalabilidad

## 🚀 CARACTERÍSTICAS PRINCIPALES

### Antivirus
- ✅ Escaneo en tiempo real y bajo demanda
- ✅ Motor ClamAV integrado
- ✅ Detección con reglas YARA personalizadas
- ✅ Análisis de hashes MD5/SHA256
- ✅ Cuarentena automática de amenazas
- ✅ Actualizaciones automáticas de firmas

### Mini-SIEM
- 🔍 **Recolección de logs en tiempo real** desde journalctl, auth.log, syslog
- 📊 **Motor de correlación** con reglas de umbral y secuenciales
- 🚨 **Sistema de alertas** con notificaciones desktop y terminal
- 📈 **Dashboard interactivo** con estadísticas y métricas
- 🔧 **Reglas personalizables** para detección de amenazas específicas
- 💾 **Base de datos SQLite** optimizada para rendimiento

### Interfaz de Usuario
- 🎨 **Diseño moderno y profesional** en español
- 📱 **Navegación intuitiva** con paneles especializados
- ⚡ **Actualizaciones en tiempo real** de estado y eventos
- 📋 **Exportación de informes** en múltiples formatos
- 🔧 **Configuración avanzada** accesible

## 📁 ESTRUCTURA DEL PROYECTO

```
Ares-Aegis/
├── antivirus_kali/
│   ├── main.py                    # Punto de entrada principal
│   ├── launcher.py                # Script de inicialización avanzado
│   ├── config.py                  # Configuración global
│   │
│   ├── controladores/             # Controladores MVC
│   │   ├── controlador_mini_siem.py    # Integración Mini-SIEM
│   │   ├── controlador_escaneo_sistema.py
│   │   ├── controlador_integridad.py
│   │   └── ...
│   │
│   ├── interfaz/                  # Interfaz de usuario Qt
│   │   ├── ventana_principal.py        # Ventana principal moderna
│   │   ├── panel_mini_siem.py          # Panel completo Mini-SIEM
│   │   ├── panel_escaneo.py
│   │   └── ...
│   │
│   ├── mini_siem/                 # Sistema Mini-SIEM
│   │   ├── controlador_siem.py         # Controlador principal
│   │   ├── recolector_logs.py          # Recolección de eventos
│   │   ├── almacenamiento.py           # Base de datos SQLite
│   │   ├── motor_correlacion.py        # Engine de correlación
│   │   └── __init__.py
│   │
│   ├── core/                      # Motores del antivirus
│   │   ├── scan_engine.py
│   │   ├── clamav_engine.py
│   │   ├── yara_engine.py
│   │   └── ...
│   │
│   └── recursos/                  # Recursos del sistema
│       ├── iconos/
│       ├── reglas_yara/
│       └── configuraciones/
│
├── test_sistema_completo.py       # Script de pruebas
├── README.md                      # Este archivo
└── requirements.txt               # Dependencias Python
```

## 🔧 INSTALACIÓN Y CONFIGURACIÓN

### Requisitos del Sistema
- **Sistema Operativo**: Kali Linux (recomendado) o Ubuntu/Debian
- **Python**: 3.9 o superior
- **Memoria RAM**: Mínimo 4GB, recomendado 8GB
- **Espacio en disco**: 2GB libres
- **Permisos**: Acceso a logs del sistema para Mini-SIEM

### Instalación Rápida

```bash
# Clonar el repositorio
git clone https://github.com/DogSoulDev/Ares-Aegis.git
cd Ares-Aegis

# Instalar dependencias del sistema
sudo apt update
sudo apt install python3-pip clamav clamav-daemon python3-dev

# Crear entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# Instalar dependencias Python
pip install -r requirements.txt

# Actualizar base de datos ClamAV
sudo freshclam

# Ejecutar sistema
python3 antivirus_kali/launcher.py
```

### Configuración Avanzada

#### 1. Permisos para Mini-SIEM
```bash
# Agregar usuario al grupo de logs
sudo usermod -a -G adm $USER

# Configurar acceso a journalctl
sudo usermod -a -G systemd-journal $USER

# Reiniciar sesión para aplicar cambios
```

#### 2. Configuración de ClamAV
```bash
# Editar configuración
sudo nano /etc/clamav/clamd.conf

# Habilitar escaneo en tiempo real
sudo systemctl enable clamav-daemon
sudo systemctl start clamav-daemon
```

## 🎯 USO DEL SISTEMA

### Inicio Rápido

1. **Ejecutar el sistema**:
   ```bash
   python3 antivirus_kali/launcher.py
   ```

2. **Navegar por la interfaz**:
   - **Escaneo**: Realizar análisis de archivos y sistema
   - **Resultados**: Ver detecciones y amenazas encontradas
   - **Mini-SIEM**: Monitorear eventos de seguridad en tiempo real
   - **Configuración**: Ajustar parámetros del sistema
   - **Historial**: Revisar actividad pasada

### Mini-SIEM: Guía de Uso

#### Panel de Control
- **Iniciar/Detener monitoreo**: Control del estado del SIEM
- **Configurar notificaciones**: Desktop, terminal, logs
- **Ajustar intervalos**: Frecuencia de recolección

#### Dashboard
- **Eventos en tiempo real**: Stream de actividad del sistema
- **Estadísticas**: Métricas de eventos procesados y alertas
- **Gráficos**: Visualización de tendencias de seguridad

#### Alertas
- **SSH Brute Force**: Detección de ataques de fuerza bruta
- **Escalada de privilegios**: Monitoreo de uso de sudo
- **Instalación masiva**: Control de paquetes instalados
- **Actividad de red sospechosa**: Análisis de conexiones

#### Configuración de Reglas

```python
# Ejemplo: Regla personalizada de umbral
{
    "nombre": "multiple_failed_logins",
    "descripcion": "Múltiples fallos de login desde misma IP",
    "tipo": "umbral",
    "severidad": "HIGH",
    "umbral": 3,
    "ventana_tiempo": 180,
    "campo_agrupacion": "source.ip",
    "filtros": {
        "event.category": "authentication",
        "action": "failed"
    }
}
```

## 🔍 ARQUITECTURA TÉCNICA

### Componentes del Mini-SIEM

#### 1. Recolector de Logs (`recolector_logs.py`)
- **Fuentes**: journalctl, auth.log, syslog, dpkg.log, kern.log
- **Normalización**: Conversión a formato ECS (Elastic Common Schema)
- **Procesamiento asíncrono**: Alto rendimiento con asyncio
- **Filtrado inteligente**: Eventos relevantes para seguridad

#### 2. Motor de Correlación (`motor_correlacion.py`)
- **Reglas de umbral**: Detección basada en frecuencia de eventos
- **Reglas secuenciales**: Análisis de patrones de comportamiento
- **Ventanas deslizantes**: Análisis temporal de eventos
- **Callbacks personalizables**: Integración con sistemas externos

#### 3. Almacenamiento (`almacenamiento.py`)
- **Base de datos SQLite**: Optimizada para escritura masiva
- **Índices especializados**: Búsquedas rápidas por timestamp y categoría
- **Procesamiento por lotes**: Mejora el rendimiento
- **Retención configurable**: Gestión automática del espacio

#### 4. Sistema de Alertas
- **Notificaciones desktop**: Usando plyer
- **Output terminal**: Logs estructurados
- **Integración Qt**: Alertas en interfaz
- **Webhooks**: Posibilidad de integración externa

### Flujo de Datos

```
Logs del Sistema → Recolector → Normalización → Motor Correlación → Alertas
                                      ↓
                            Base de Datos ← Dashboard ← Interfaz Qt
```

## 📊 RENDIMIENTO Y OPTIMIZACIÓN

### Métricas de Rendimiento
- **Procesamiento**: >1000 eventos/segundo
- **Memoria**: <500MB en uso normal
- **Latencia**: <100ms para alertas críticas
- **Base de datos**: Compresión automática de datos antiguos

### Configuraciones de Optimización

```python
# En almacenamiento.py
BATCH_SIZE = 100          # Tamaño de lote para inserciones
FLUSH_INTERVAL = 5        # Segundos entre flush automático
INDEX_MAINTENANCE = 3600  # Mantenimiento de índices (segundos)

# En recolector_logs.py
POLL_INTERVAL = 1         # Intervalo de polling (segundos)
MAX_LINE_LENGTH = 8192    # Longitud máxima de línea de log
BUFFER_SIZE = 10000       # Tamaño del buffer de eventos
```

## 🚨 DETECCIÓN DE AMENAZAS

### Reglas Predefinidas

1. **SSH Brute Force**
   - Umbral: 5 fallos en 5 minutos
   - Severidad: HIGH
   - Agrupación: IP origen

2. **Escalada de Privilegios**
   - Secuencia: Login exitoso → uso de sudo
   - Ventana: 60 segundos
   - Severidad: CRITICAL

3. **Instalación Masiva de Software**
   - Umbral: 10 paquetes en 30 minutos
   - Severidad: WARNING
   - Categoría: Gestión de paquetes

4. **Escaneo de Red**
   - Umbral: 50 conexiones en 5 minutos
   - Severidad: WARNING
   - Agrupación: IP origen

### Respuesta Automática
- **Bloqueo temporal de IPs** (integración con iptables)
- **Alertas en tiempo real** al administrador
- **Registro detallado** para análisis forense
- **Integración con fail2ban** (configuración adicional)

## 🔧 CONFIGURACIÓN AVANZADA

### Variables de Entorno

```bash
# Configuración del Mini-SIEM
export SIEM_DB_PATH="/var/lib/ares-aegis/siem.db"
export SIEM_LOG_LEVEL="INFO"
export SIEM_RETENTION_DAYS="30"

# Configuración de alertas
export ALERT_DESKTOP_ENABLED="true"
export ALERT_TERMINAL_ENABLED="true"
export ALERT_WEBHOOK_URL=""

# Configuración del antivirus
export CLAMAV_DB_PATH="/var/lib/clamav"
export YARA_RULES_PATH="./recursos/reglas_yara"
```

### Archivos de Configuración

#### `config.py` - Configuración Global
```python
# Configuración del Mini-SIEM
SIEM_CONFIG = {
    'db_path': '/var/lib/ares-aegis/siem.db',
    'log_sources': [
        '/var/log/auth.log',
        '/var/log/syslog',
        '/var/log/dpkg.log'
    ],
    'retention_days': 30,
    'max_events_memory': 10000
}

# Configuración de notificaciones
NOTIFICATION_CONFIG = {
    'desktop': True,
    'terminal': True,
    'webhook_url': None
}
```

## 🐛 SOLUCIÓN DE PROBLEMAS

### Problemas Comunes

#### 1. Error de permisos en logs
```bash
# Síntoma: "Permission denied" al acceder a logs
# Solución:
sudo usermod -a -G adm,systemd-journal $USER
# Reiniciar sesión
```

#### 2. ClamAV no iniciado
```bash
# Síntoma: Error al escanear archivos
# Solución:
sudo systemctl start clamav-daemon
sudo systemctl enable clamav-daemon
```

#### 3. Base de datos SIEM corrupta
```bash
# Síntoma: Errores SQLite
# Solución:
rm /var/lib/ares-aegis/siem.db
# Reiniciar aplicación
```

#### 4. Alto uso de memoria
```bash
# Síntoma: Consumo excesivo de RAM
# Solución: Reducir configuraciones en config.py
BATCH_SIZE = 50
MAX_EVENTS_MEMORY = 5000
```

### Logs de Depuración

```bash
# Habilitar logs detallados
export SIEM_LOG_LEVEL="DEBUG"

# Ver logs en tiempo real
tail -f ares_aegis.log

# Analizar rendimiento
grep "performance" ares_aegis.log
```

## 🤝 CONTRIBUCIÓN

### Estructura para Nuevas Características

1. **Nuevos motores de antivirus**: Agregar en `core/`
2. **Nuevas reglas SIEM**: Modificar `motor_correlacion.py`
3. **Nuevos paneles UI**: Crear en `interfaz/`
4. **Nuevas fuentes de logs**: Extender `recolector_logs.py`

### Guías de Desarrollo

```python
# Ejemplo: Nueva regla de correlación
class ReglaPersonalizada(ReglaCorrelacion):
    def __init__(self, nombre: str, config: Dict):
        super().__init__(nombre, config['descripcion'], config['severidad'])
        # Inicialización específica
    
    def evaluar(self, evento: Dict) -> Optional[Alerta]:
        # Lógica de evaluación
        pass
```

## 📞 SOPORTE

- **GitHub Issues**: Para reportar bugs y solicitar características
- **Documentación**: Wiki del repositorio
- **Logs del sistema**: `ares_aegis.log` para diagnóstico

## 📋 ROADMAP

### Versión Actual (v1.0)
- ✅ Mini-SIEM completo funcional
- ✅ Interfaz moderna integrada
- ✅ Motores antivirus básicos
- ✅ Sistema de alertas

### Próximas Versiones
- 🔄 Integración con MISP (Malware Information Sharing Platform)
- 🔄 API RESTful para integración externa
- 🔄 Machine Learning para detección de anomalías
- 🔄 Soporte para múltiples nodos
- 🔄 Integración con Elasticsearch/Kibana

---

**Ares Aegis** - Protección avanzada para el ecosistema Kali Linux
Desarrollado con ❤️ para la comunidad de seguridad informática
