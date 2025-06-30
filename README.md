# Ares Aegis

## 🛡️ Antivirus Avanzado para Kali Linux

Sistema de seguridad integral desarrollado en Python con arquitectura MVC y principios Clean Code.

### 🚀 Características Principales

- **Motor de Escaneo Interno**: Análisis basado en patrones y heurística
- **Integración ClamAV**: Compatibilidad con motor externo
- **Sistema SIEM**: Registro centralizado de eventos de seguridad
- **File Integrity Monitoring**: Monitoreo de integridad de archivos críticos
- **Cuarentena Inteligente**: Aislamiento automático de amenazas
- **Monitoreo de Red**: Detección de conexiones y puertos sospechosos
- **Interfaz Gráfica**: GUI moderna con estética japonesa

### 📋 Requisitos Técnicos

- **Sistema Operativo**: Kali Linux o distribución basada en Debian
- **Python**: Versión 3.8 o superior
- **Dependencias**: Solo módulos estándar de Python (tkinter, logging, os, sys)
- **Privilegios**: Root para funcionalidad completa

### ⚡ Instalación Rápida

```bash
# Clonar repositorio
git clone https://github.com/DogSoulDev/Ares-Aegis.git
cd Ares-Aegis

# Instalar dependencias
pip3 install -r requirements.txt

# Ejecutar aplicación
sudo python3 main.py
```

### 🏗️ Arquitectura del Proyecto

```
Ares-Aegis/
├── main.py                 # Punto de entrada principal
├── requirements.txt        # Dependencias Python
├── README.md              # Documentación técnica
├── MANUAL.md              # Manual de usuario completo
│
├── src/                   # Código fuente principal
│   ├── modelos/           # Lógica de negocio (MVC)
│   ├── vista/             # Interfaz gráfica (MVC)
│   └── controladores/     # Controladores (MVC)
│
├── config/                # Configuraciones
│   └── firmas/           # Base de datos de firmas
│
├── recursos/              # Recursos gráficos
│   ├── AresAegis.png     # Logo principal
│   └── aresIcon.png      # Icono aplicación
│
└── tests/                 # Tests unitarios
```

### 🎨 Principios de Desarrollo

- **Arquitectura**: MVC (Modelo-Vista-Controlador)
- **Metodología**: TDD (Test-Driven Development)
- **Estándares**: Clean Code y principios SOLID
- **Diseño**: Estética japonesa minimalista
- **Localización**: 100% en español

### 🔧 Componentes Técnicos

#### Modelos (`src/modelos/`)
- `siem.py`: Sistema de gestión de eventos e información
- `escaneador.py`: Motor interno de análisis de archivos
- `fim.py`: Monitoreo de integridad de archivos
- `cuarentena.py`: Sistema de cuarentena de archivos
- `integracion_externa.py`: Integración con ClamAV
- `monitor_red.py`: Monitoreo de conexiones de red

#### Vista (`src/vista/`)
- `interfaz_principal_gui.py`: Interfaz gráfica principal con tkinter

#### Controladores (`src/controladores/`)
- `controlador_principal.py`: Coordinador principal de la aplicación

### 🎯 Funcionalidades Core

1. **Detección de Amenazas**
   - Análisis de archivos y directorios
   - Detección de malware, rootkits y scripts maliciosos
   - Integración con bases de datos externas

2. **Monitoreo en Tiempo Real**
   - File Integrity Monitoring (FIM)
   - Monitoreo de procesos del sistema
   - Análisis de conexiones de red

3. **Gestión de Seguridad**
   - Cuarentena automática de amenazas
   - Sistema SIEM para auditoría
   - Reportes exportables en Markdown

4. **Interfaz de Usuario**
   - Diseño japonés con colores matcha, sakura y bamboo
   - Layout optimizado con grid tkinter
   - Manejo inteligente de imágenes y recursos

### 🛠️ Herramientas de Desarrollo

```bash
# Ejecutar tests
python3 -m pytest tests/

# Verificar calidad de código
python3 -m flake8 src/

# Generar documentación
python3 -m pydoc src.modelos.siem
```

### 📊 Configuración Avanzada

#### Variables de Entorno
```bash
export ARES_LOG_LEVEL=DEBUG
export ARES_QUARANTINE_DIR=/var/quarantine
```

#### Integración ClamAV
```bash
sudo apt install clamav clamav-daemon
sudo freshclam
```

### 🚨 Solución de Problemas

#### Error de Privilegios
```bash
sudo python3 main.py
```

#### Error de Módulos
```bash
pip3 install -r requirements.txt --force-reinstall
```

#### Error de Interfaz Gráfica
```bash
export DISPLAY=:0
xhost +local:
```

### 📈 Estado del Proyecto

- **Versión**: 2.0.0
- **Estado**: Producción estable
- **Cobertura de Tests**: Implementada
- **Documentación**: Completa (README.md + MANUAL.md)
- **Arquitectura**: MVC consolidada

### 🤝 Contribución

Este proyecto sigue los estándares de Clean Code y SOLID. Para contribuir:

1. Fork del repositorio
2. Crear branch feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a branch (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

### 📝 Licencia

Proyecto Open Source - Ver documentación completa en `MANUAL.md`

### 👨‍💻 Autor

**DogSoulDev** - Desarrollo y mantenimiento

---

Para instrucciones detalladas de uso, consultar `MANUAL.md`
