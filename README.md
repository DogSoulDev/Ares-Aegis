# 🛡️ Ares Aegis - Sistema Avanzado de Ciberseguridad

<div align="center">
  <img src="recursos/AresAegis.png" alt="Ares Aegis Logo" width="200"/>
  
  [![Versión](https://img.shields.io/badge/versión-3.0.0-blue.svg)](https://github.com/DogSoulDev/Ares-Aegis)
  [![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://python.org)
  [![Licencia](https://img.shields.io/badge/licencia-Propietaria-red.svg)](LICENSE)
  [![Estado](https://img.shields.io/badge/estado-Activo-brightgreen.svg)](https://github.com/DogSoulDev/Ares-Aegis)
</div>

## 📋 Descripción

**Ares Aegis** es un sistema avanzado de ciberseguridad desarrollado en Python que proporciona protección integral contra amenazas digitales. Combina múltiples capas de seguridad con una interfaz moderna e intuitiva para ofrecer una solución completa de protección empresarial.

### 🎯 Características Principales

- **🔍 Escaneo en Tiempo Real** - Análisis completo con progreso en vivo
- **🌐 Monitoreo de Red** - Supervisión continua del tráfico de red
- **⚙️ Análisis de Procesos** - Detección de procesos sospechosos
- **🗂️ Sistema de Cuarentena** - Aislamiento seguro de amenazas
- **📊 SIEM Integrado** - Sistema de información y gestión de eventos
- **🛡️ Protección Multicapa** - Análisis estático y dinámico
- **📈 Reportes Detallados** - Informes completos en múltiples formatos

## 🚀 Tecnologías

- **Lenguaje:** Python 3.8+
- **Interfaz:** Tkinter con componentes modernos
- **Arquitectura:** MVC (Modelo-Vista-Controlador)
- **Base de Datos:** JSON para configuración y logs
- **Análisis:** Múltiples motores de detección
- **Monitoreo:** Tiempo real con threading

## 📁 Estructura del Proyecto

```
Ares-Aegis/
├── 📄 main.py                    # Punto de entrada principal
├── 📄 requirements.txt           # Dependencias del proyecto
├── 📄 iniciar.sh                # Script de inicio rápido
├── 📁 ares_aegis/               # Código fuente principal
│   ├── 📁 controladores/        # Lógica de negocio (MVC)
│   ├── 📁 modelos/              # Modelos de datos y componentes
│   ├── 📁 vista/                # Interfaz de usuario
│   └── 📁 utilidades/           # Herramientas auxiliares
├── 📁 configuracion/            # Archivos de configuración
├── 📁 recursos/                 # Imágenes, iconos y recursos
├── 📁 cuarentena/               # Sistema de cuarentena
├── 📁 logs/                     # Archivos de registro
├── 📁 reportes/                 # Informes generados
└── 📁 tests/                    # Pruebas unitarias
```

## 🔧 Instalación

### Requisitos del Sistema

- **Sistema Operativo:** Linux (Ubuntu/Debian recomendado)
- **Python:** 3.8 o superior
- **Memoria RAM:** Mínimo 4GB, recomendado 8GB
- **Espacio en Disco:** 2GB libres
- **Permisos:** Acceso root para funciones avanzadas

### Instalación Rápida

1. **Clonar el repositorio:**
```bash
git clone https://github.com/DogSoulDev/Ares-Aegis.git
cd Ares-Aegis
```

2. **Instalar dependencias:**
```bash
pip3 install -r requirements.txt
```

3. **Configurar permisos:**
```bash
chmod +x iniciar.sh
sudo chmod +x main.py
```

4. **Ejecutar el sistema:**
```bash
sudo python3 main.py
```

## 🎮 Uso del Sistema

### Interfaz Principal

El sistema cuenta con una interfaz moderna dividida en secciones principales:

#### 🏠 Panel Principal
- **Estado del Sistema** - Monitoreo en tiempo real
- **Escaneo Rápido** - Análisis inmediato
- **Actividad Reciente** - Eventos del sistema
- **Alertas** - Notificaciones de seguridad

#### 🔍 Centro de Escaneo
- **Escaneo Rápido** - Análisis de ubicaciones críticas (2-5 min)
- **Escaneo Completo** - Análisis exhaustivo del sistema (15-45 min)
- **Escaneo Personalizado** - Análisis de directorios específicos
- **Progreso en Tiempo Real** - Visualización del proceso archivo por archivo

#### 🛡️ Monitoreo
- **Red** - Conexiones activas y tráfico
- **Procesos** - Supervisión de procesos del sistema
- **Eventos SIEM** - Registro completo de actividades
- **Estadísticas** - Métricas del sistema en tiempo real

#### 🗂️ Cuarentena
- **Gestión de Archivos** - Aislar y gestionar amenazas
- **Restauración** - Recuperar archivos seguros
- **Análisis Detallado** - Información completa de cada archivo

### Comandos Principales

```bash
# Inicio normal
sudo python3 main.py

# Inicio rápido con script
./iniciar.sh

# Modo de prueba
python3 -m pytest tests/

# Verificación del sistema
python3 verificar_proyecto.py
```

## 🔐 Características de Seguridad

### Análisis Multicapa
- **Análisis Estático** - Detección de patrones conocidos
- **Análisis Dinámico** - Comportamiento en tiempo real
- **Análisis Heurístico** - Detección de amenazas desconocidas
- **Base de Datos CVE** - Vulnerabilidades conocidas

### Protección en Tiempo Real
- **Monitor de Archivos (FIM)** - Integridad de archivos críticos
- **Monitor de Red** - Tráfico y conexiones sospechosas
- **Monitor de Procesos** - Comportamiento anómalo
- **Sistema de Cuarentena** - Aislamiento automático

### SIEM Integrado
- **Registro de Eventos** - Auditoría completa
- **Correlación** - Análisis de patrones
- **Alertas** - Notificaciones inmediatas
- **Reportes** - Informes detallados

## 📊 Tipos de Escaneo

| Tipo | Duración | Cobertura | Uso Recomendado |
|------|----------|-----------|-----------------|
| **Rápido** | 2-5 min | Ubicaciones críticas | Verificación diaria |
| **Completo** | 15-45 min | Sistema completo | Análisis semanal |
| **Personalizado** | Variable | Directorios específicos | Análisis dirigido |

## 🛠️ Configuración Avanzada

### Archivos de Configuración

- `configuracion/firmas.txt` - Firmas de malware personalizadas
- `configuracion/notificaciones.json` - Configuración de alertas
- `recursos/reglas_respuesta.json` - Reglas de respuesta automática

### Personalización

El sistema permite personalizar:
- **Umbrales de detección** - Sensibilidad del análisis
- **Reglas de cuarentena** - Criterios de aislamiento
- **Notificaciones** - Tipos y frecuencia de alertas
- **Informes** - Formato y contenido de reportes

## 📈 Monitoreo y Reportes

### Métricas del Sistema
- Archivos analizados
- Amenazas detectadas
- Tiempo de respuesta
- Uso de recursos

### Formatos de Exportación
- **HTML** - Reportes web interactivos
- **JSON** - Datos estructurados
- **TXT** - Texto plano para análisis

## 🔍 Solución de Problemas

### Problemas Comunes

**Error de permisos:**
```bash
sudo chmod +x main.py
sudo python3 main.py
```

**Dependencias faltantes:**
```bash
pip3 install -r requirements.txt --upgrade
```

**Problemas de interfaz:**
```bash
sudo apt-get install python3-tk
```

### Logs del Sistema

Los registros se almacenan en:
- `/var/log/ares_aegis/ares_aegis.log` - Log principal
- `logs/` - Logs de módulos específicos
- `/var/log/ares_aegis/eventos_siem.json` - Eventos SIEM

## 👥 Contribución

Este es un proyecto propietario desarrollado por **DogSoulDev**. 

### Contacto
- **Desarrollador:** DogSoulDev
- **GitHub:** [https://github.com/DogSoulDev](https://github.com/DogSoulDev)
- **Proyecto:** [https://github.com/DogSoulDev/Ares-Aegis](https://github.com/DogSoulDev/Ares-Aegis)

## 📄 Licencia

```
Copyright (c) 2025 DogSoulDev (https://github.com/DogSoulDev)
Todos los derechos reservados.

Este código es propietario y confidencial. La copia, distribución 
o modificación no autorizada está estrictamente prohibida.
```

## 🔮 Roadmap

### Versión 3.1.0 (Próximamente)
- [ ] Integración con bases de datos externas
- [ ] API REST para integración
- [ ] Dashboard web
- [ ] Análisis de machine learning

### Versión 3.2.0 (Futuro)
- [ ] Soporte para Windows
- [ ] Análisis de contenedores
- [ ] Integración cloud
- [ ] Mobile app de monitoreo

---

<div align="center">
  <img src="recursos/aresIcon.png" alt="Ares Icon" width="64"/>
  
  **Ares Aegis v3.0.0** - Protección Digital Avanzada
  
  Desarrollado con ❤️ por [DogSoulDev](https://github.com/DogSoulDev)
</div>
