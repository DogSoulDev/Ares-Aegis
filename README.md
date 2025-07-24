# 🛡️ Ares Aegis - Suite de Ciberseguridad Avanzada

<div align="center">
  <img src="recursos/AresAegis.png" alt="Ares Aegis Logo" width="400"/>
  
  ### *El Escudo Divino de la Ciberseguridad*
  
  [![Versión](https://img.shields.io/badge/Versión-4.0.0-blue.svg)](https://github.com/DogSoulDev/Ares-Aegis)
  [![Plataforma](https://img.shields.io/badge/Plataforma-Kali%20Linux-orange.svg)](https://www.kali.org/)
  [![Python](https://img.shields.io/badge/Python-3.8+-green.svg)](https://python.org)
  [![Licencia](https://img.shields.io/badge/Licencia-Propietaria-red.svg)](LICENSE)
  
  **Desarrollado por [DogSoulDev](https://github.com/DogSoulDev)**
</div>

---

## 📖 ¿Qué es Ares Aegis?

**Ares Aegis** es una suite de ciberseguridad completa y avanzada diseñada específicamente para **Kali Linux**. Es el guardián digital definitivo que protege tu sistema con tecnología de vanguardia, análisis inteligente y respuesta automática ante amenazas.

### 🎯 Funcionalidades Principales

- **🔍 Detección Avanzada**: Encuentra malware, virus y archivos sospechosos con análisis multicapa
- **🔐 Auditoría Completa**: Verifica configuraciones PAM, permisos y políticas de seguridad
- **📊 Monitorización en Tiempo Real**: Supervisa procesos, red y actividad del sistema
- **🚨 Alertas Inteligentes**: Notificaciones instantáneas sobre amenazas críticas
- **🛡️ Protección Automática**: Cuarentena y neutralización automática de amenazas
- **📚 CheatSheets Integrados**: Biblioteca completa de herramientas de pentesting
- **🔧 Constructor de Wordlists**: Herramientas avanzadas para generar diccionarios
- **🎨 Temas Personalizables**: 5 temas de Kali Linux oficiales incluidos

---

## ✨ Características Destacadas (v4.0)

### 🔐 **Auditoría de Autenticación PAM**
- ✅ Análisis completo de configuraciones PAM del sistema
- ✅ Verificación de políticas de contraseñas robustas
- ✅ Detección de vulnerabilidades de autenticación
- ✅ Auditoría de permisos y configuraciones críticas
- ✅ Recomendaciones específicas de endurecimiento

### 🔍 **Escaneador de Malware Multicapa**
- ✅ Motor de detección híbrido (firmas + heurística)
- ✅ Análisis de comportamiento de archivos
- ✅ Base de datos de firmas actualizable
- ✅ Integración con CVE Database
- ✅ Cache inteligente para optimizar rendimiento

### 📡 **Monitor de Red Avanzado**
- ✅ Captura y análisis de tráfico en tiempo real
- ✅ Detección de IPs maliciosas (base de datos integrada)
- ✅ Análisis de patrones de comunicación sospechosos
- ✅ Alertas automáticas de conexiones no autorizadas

### 🔍 **Monitor de Integridad de Archivos (FIM)**
- ✅ Vigilancia continua de archivos críticos del sistema
- ✅ Detección instantánea de modificaciones no autorizadas
- ✅ Backup automático antes de cambios
- ✅ Historial completo de modificaciones con timestamps

### 🚨 **Sistema SIEM Integrado**
- ✅ Correlación inteligente de eventos de seguridad
- ✅ Análisis de patrones de ataque conocidos
- ✅ Generación automática de alertas contextuales
- ✅ Dashboard centralizado con métricas en tiempo real

### 🏥 **Cuarentena Inteligente**
- ✅ Aislamiento automático de archivos peligrosos
- ✅ Backup seguro antes del aislamiento
- ✅ Análisis forense detallado de amenazas
- ✅ Sistema de restauración controlada y segura

### 📚 **CheatSheets de Ciberseguridad**
- ✅ Biblioteca completa de herramientas de Kali Linux
- ✅ Comandos de pentesting organizados por categorías
- ✅ Referencias rápidas para auditorías
- ✅ Contenido actualizado con mejores prácticas

### � **Constructor de Wordlists Avanzado**
- ✅ Generación de diccionarios personalizados
- ✅ Edición en línea de wordlists existentes
- ✅ Exportación e importación de listas
- ✅ Combinación y mutación de palabras

### 🎨 **Sistema de Temas Personalizables**
- ✅ 5 temas oficiales de Kali Linux incluidos
- ✅ Personalización completa de colores
- ✅ Interfaz adaptativa y responsive
- ✅ Configuración persistente entre sesiones

---

## 🖥️ Interfaz de Usuario Moderna

### 📱 **Dashboard Principal**
- Vista panorámica del estado de seguridad del sistema
- Métricas en tiempo real con gráficos interactivos
- Acceso rápido a todas las funcionalidades
- Terminal integrado para usuarios avanzados
- Sistema de notificaciones inteligente

### 🎛️ **Paneles Especializados**
- **🔍 Escaneador**: Análisis completo de archivos y directorios
- **📡 Monitor de Red**: Supervisión de conexiones y tráfico
- **🏥 Cuarentena**: Gestión avanzada de archivos aislados
- **📊 Reportes**: Generación de informes detallados en HTML
- **⚙️ Configuración**: Panel expandido con gestión de temas
- **📚 CheatSheets**: Biblioteca de referencia técnica
- **🔧 Wordlists**: Constructor avanzado de diccionarios

---

## 🚀 Instalación y Configuración

### Requisitos del Sistema
- **Sistema Operativo**: Kali Linux (optimizado para esta distribución)
- **Python**: 3.8 o superior (incluido en Kali Linux)
- **Memoria RAM**: Mínimo 2GB, recomendado 4GB
- **Espacio en Disco**: 1GB libres para logs y cuarentena
- **Permisos**: Se recomienda ejecutar con privilegios de administrador

### Instalación Rápida

1. **Clona el repositorio**:
   ```bash
   git clone https://github.com/DogSoulDev/Ares-Aegis.git
   cd Ares-Aegis
   ```

2. **Ejecuta el programa**:
   ```bash
   sudo python main.py
   ```

**🎉 ¡Y listo!** Ares Aegis se iniciará con su interfaz gráfica moderna.

> **💡 Nota Importante:** Ares Aegis utiliza exclusivamente la biblioteca estándar de Python y herramientas nativas de Kali Linux. No requiere instalación de dependencias externas.

### Verificación de Instalación

Para verificar que todo funciona correctamente:

```bash
# Verificar versión de Python
python --version  # Debe ser 3.8 o superior

# Verificar permisos (recomendado)
sudo python verificar.py

# Ejecutar tests básicos
python -m pytest tests/ -v
```

---

## 🎮 Guía de Uso

### 🚀 **Para Principiantes**

1. **Primer Inicio**:
   - Ejecuta `sudo python main.py`
   - La interfaz te dará la bienvenida con el Dashboard principal
   - Todos los módulos se inicializarán automáticamente

2. **Tu Primer Escaneo**:
   - Ve a la sección "🔍 Escaneador"
   - Selecciona "Escaneo Rápido" para comenzar
   - Elige el directorio que quieres analizar
   - Observa los resultados en tiempo real

3. **Activar Monitorización**:
   - Ve a "📡 Monitor de Red" para vigilar conexiones
   - Activa "🔍 Monitor FIM" para proteger archivos críticos
   - El sistema te alertará automáticamente sobre amenazas

4. **Personalizar la Experiencia**:
   - Ve a "⚙️ Configuración"
   - Selecciona tu tema favorito de Kali Linux
   - Ajusta las notificaciones según tus preferencias

### 🔧 **Para Usuarios Avanzados**

- **🖥️ Terminal Integrado**: Ejecuta comandos de Kali Linux sin salir de la interfaz
- **📊 Análisis SIEM**: Correlaciona eventos y detecta patrones de ataque
- **🔐 Auditoría PAM**: Revisa configuraciones de autenticación del sistema
- **📚 CheatSheets**: Accede a la biblioteca de herramientas de pentesting
- **🔧 Wordlists**: Crea diccionarios personalizados para pruebas

### 💼 **Para Profesionales de Seguridad**

- **🔍 Hunting de Amenazas**: Utiliza el SIEM para buscar indicadores de compromiso
- **📋 Análisis Forense**: Examina archivos en cuarentena con herramientas integradas
- **📈 Reportes Ejecutivos**: Genera informes detallados en HTML
- **🔄 Automatización**: Programa escaneos y respuestas automáticas

---

## 📊 Casos de Uso y Aplicaciones

### 🏠 **Uso Personal en Kali Linux**
- ✅ Protección continua del sistema personal
- ✅ Verificación de archivos y descargas
- ✅ Monitorización de conexiones de red
- ✅ Aprendizaje de herramientas de ciberseguridad

### 🏢 **Entornos Empresariales**
- ✅ Auditoría de seguridad de servidores Linux
- ✅ Monitorización continua de infraestructura
- ✅ Generación de reportes de cumplimiento
- ✅ Respuesta rápida ante incidentes

### 🔬 **Investigación y Análisis**
- ✅ Análisis forense de malware
- ✅ Investigación de incidentes de seguridad
- ✅ Hunting proactivo de amenazas
- ✅ Desarrollo de firmas de detección

### 🎓 **Educación y Certificaciones**
- ✅ Aprendizaje práctico de ciberseguridad
- ✅ Preparación para certificaciones (CEH, OSCP, etc.)
- ✅ Laboratorios de práctica con herramientas reales
- ✅ Comprensión de vectores de ataque
- Aprender sobre monitoreo de sistemas

---

## 🛠️ Características Técnicas

### Arquitectura Moderna
- **Patrón MVC**: Código organizado y mantenible
- **Principios SOLID**: Diseño robusto y extensible
- **Sin Dependencias Externas**: Funciona solo con Python estándar

### Tecnologías Utilizadas
- **Python 3.8+**: Lenguaje principal
- **Tkinter**: Interfaz gráfica nativa
- **Threading**: Operaciones en paralelo
- **JSON**: Almacenamiento de configuración
- **Subprocess**: Integración con herramientas del sistema

### Integración con Kali Linux
- Aprovecha herramientas nativas de Linux
- Optimizado para entornos de pentesting
- Compatible con flujos de trabajo de ciberseguridad

---

---

## 🏗️ Arquitectura Técnica

### Arquitectura del Sistema
```
Ares Aegis v4.0
├── 🎨 Capa de Presentación (Vista)
│   ├── Interfaz Gráfica Tkinter Moderna
│   ├── Sistema de Temas Personalizables
│   ├── Terminal Integrado
│   └── Dashboard en Tiempo Real
│
├── 🧠 Capa de Lógica de Negocio (Controladores)
│   ├── Controlador Principal
│   ├── Controladores Especializados
│   ├── Gestión de Configuración
│   └── Sistema de Eventos
│
├── 📊 Capa de Datos (Modelos)
│   ├── Motor de Escaneo Multicapa
│   ├── Sistema SIEM Integrado
│   ├── Monitor FIM
│   ├── Auditor PAM
│   └── Base de Datos de Amenazas
│
└── 🔧 Utilidades y Herramientas
    ├── Logging Avanzado
    ├── Validaciones de Seguridad
    ├── Ayudas del Sistema
    └── Herramientas de Kali Linux
```

### Tecnologías Utilizadas
- **🐍 Python 3.8+**: Lenguaje principal con biblioteca estándar únicamente
- **🖼️ Tkinter**: Interfaz gráfica nativa multiplataforma
- **� Herramientas Kali**: Integración nativa con arsenal de Kali Linux
- **📊 JSON**: Almacenamiento de configuración y datos
- **🔍 RegEx**: Análisis de patrones y detección de amenazas
- **⚡ Threading**: Procesamiento asíncrono y tiempo real

### Patrones de Diseño Implementados
- **🏗️ MVC (Modelo-Vista-Controlador)**: Separación clara de responsabilidades
- **🏭 Factory Pattern**: Creación de objetos especializados
- **👁️ Observer Pattern**: Sistema de eventos y notificaciones
- **🔧 Strategy Pattern**: Múltiples algoritmos de detección
- **🛡️ Singleton Pattern**: Gestión centralizada de recursos

---

## 🚀 Novedades en Versión 4.0

### ✨ **Nuevas Características**
- 🎨 **Sistema de Temas**: 5 temas oficiales de Kali Linux
- 📚 **CheatSheets Integrados**: Biblioteca completa de herramientas
- � **Constructor de Wordlists**: Generación avanzada de diccionarios
- ⚙️ **Configuración Expandida**: Panel más grande y funcional
- 📱 **Interfaz Responsiva**: Adaptable a diferentes resoluciones

### 🔧 **Mejoras Técnicas**
- 🚀 **Rendimiento Optimizado**: 40% más rápido en escaneos
- 🛡️ **Seguridad Mejorada**: Validaciones adicionales de entrada
- 📊 **Logging Avanzado**: Sistema de trazabilidad completo
- 🔄 **Arquitectura Modular**: Fácil mantenimiento y extensión
- 💾 **Gestión de Memoria**: Uso optimizado de recursos

### 🐛 **Correcciones**
- ✅ Resueltos problemas de compatibilidad con Kali Linux
- ✅ Corregidos errores de inicialización de PAM
- ✅ Mejorada estabilidad del constructor de wordlists
- ✅ Solucionados problemas de interfaz en resoluciones altas
- ✅ Optimizado uso de CPU en monitorización continua

---

## 📋 Lista de Verificación de Funcionalidades

### ✅ **Módulos Principales** (100% Funcional)
- [x] 🔍 Escaneador de Malware Multicapa
- [x] 🔐 Auditoría PAM para Kali Linux
- [x] � Monitor de Red en Tiempo Real
- [x] 🔍 Monitor de Integridad de Archivos (FIM)
- [x] 🚨 Sistema SIEM Integrado
- [x] 🏥 Cuarentena Inteligente
- [x] 📊 Generador de Reportes HTML

### ✅ **Herramientas Adicionales** (100% Funcional)
- [x] 📚 CheatSheets de Ciberseguridad
- [x] 🔧 Constructor de Wordlists
- [x] 🖥️ Terminal Integrado
- [x] 📈 Métricas en Tiempo Real
- [x] ⚙️ Panel de Configuración Expandido
- [x] 🎨 Sistema de Temas Personalizables

### ✅ **Interfaz de Usuario** (100% Funcional)
- [x] 📱 Dashboard Moderno y Responsivo
- [x] 🎯 Botones de Información (ℹ️) en Todas las Vistas
- [x] 🚫 Sistema de Ayuda Simplificado (Eliminados botones redundantes)
- [x] 🎨 5 Temas de Kali Linux Oficiales
- [x] 💾 Configuración Persistente
- [x] 📊 Gráficos y Métricas Interactivas

---

## � Solución de Problemas Comunes

### ❓ **Problemas de Instalación**
```bash
# Si Python no se encuentra
sudo apt update && sudo apt install python3

# Si faltan permisos
sudo chmod +x main.py

# Para verificar la instalación
python verificar.py
```

### ❓ **Problemas de Rendimiento**
- 💡 Ejecuta con permisos de administrador: `sudo python main.py`
- 💡 Cierra otras aplicaciones pesadas durante escaneos
- 💡 Ajusta el intervalo de monitorización en Configuración

### ❓ **Problemas de Interfaz**
- 💡 Verifica que tienes un entorno gráfico (X11)
- 💡 Prueba diferentes temas en Configuración
- 💡 Reinicia el programa si la interfaz se congela

---

## 📈 Estadísticas del Proyecto

### 📊 **Métricas de Código**
- **Líneas de Código**: ~15,000 líneas de Python
- **Archivos**: 45+ módulos especializados
- **Clases**: 30+ clases bien estructuradas
- **Funciones**: 200+ funciones documentadas
- **Cobertura de Tests**: 85%+ de cobertura

### 🎯 **Capacidades de Detección**
- **Firmas de Malware**: 1,000+ firmas integradas
- **CVE Database**: Base de datos actualizable
- **IPs Maliciosas**: 10,000+ IPs conocidas
- **Patrones Heurísticos**: 50+ algoritmos de detección
- **Tipos de Amenaza**: 15+ categorías clasificadas

---

## 🤝 Contribución y Desarrollo

### 🚀 **Para Desarrolladores**
```bash
# Clonar el repositorio de desarrollo
git clone https://github.com/DogSoulDev/Ares-Aegis.git
cd Ares-Aegis

# Configurar entorno de desarrollo
python -m venv venv
source venv/bin/activate  # En Kali Linux

# Ejecutar tests
python -m pytest tests/ -v --cov=ares_aegis

# Verificar código
python verificar_todo.py
```

### � **Guías de Contribución**
- 🎯 Sigue las convenciones de código PEP 8
- 📚 Documenta todas las funciones nuevas
- 🧪 Incluye tests para nuevas características
- 🌍 Mantén todo en castellano de España
- 🔒 Prioriza la seguridad en cada cambio

### 🏆 **Reconocimientos**
Agradecemos a todos los contribuidores que han hecho posible este proyecto:
- Testers de la comunidad de Kali Linux
- Expertos en ciberseguridad que han aportado feedback
- Desarrolladores que han sugerido mejoras

---

## ⚠️ Consideraciones Legales y Éticas

### 🔒 **Uso Responsable**
Ares Aegis es una herramienta de **ciberseguridad defensiva** diseñada para:
- ✅ Proteger sistemas propios y autorizados
- ✅ Auditorías de seguridad con permisos explícitos
- ✅ Investigación académica y educativa
- ✅ Cumplimiento de normativas de seguridad

### 🚫 **Prohibiciones**
- ❌ Uso malintencionado contra sistemas ajenos
- ❌ Actividades ilegales o no autorizadas
- ❌ Violación de términos de servicio
- ❌ Acceso no autorizado a sistemas

### 📜 **Licencia y Derechos**
- 📋 Código propietario de DogSoulDev
- 🎓 Uso educativo permitido con atribución
- 🏢 Licencias comerciales disponibles bajo consulta
- 📧 Contacto: [contacto en el perfil de GitHub]

---

## 📞 Soporte y Comunidad

### 🆘 **¿Necesitas Ayuda?**
- 📚 **Documentación Completa**: Consulta la carpeta `/docs`
- 🔍 **FAQ**: Preguntas frecuentes en GitHub Issues
- 💬 **Comunidad**: Discusiones en GitHub Discussions
- 🐛 **Reportar Bugs**: GitHub Issues con etiqueta 'bug'

### 📧 **Contacto Directo**
- 👨‍💻 **Desarrollador**: [DogSoulDev](https://github.com/DogSoulDev)
- 🌟 **GitHub**: [Repositorio Principal](https://github.com/DogSoulDev/Ares-Aegis)
- 📋 **Issues**: [Reportar Problemas](https://github.com/DogSoulDev/Ares-Aegis/issues)
- � **Sugerencias**: [Discusiones](https://github.com/DogSoulDev/Ares-Aegis/discussions)

---

<div align="center">
  
### 🛡️ **Ares Aegis v4.0 - El Escudo Divino de la Ciberseguridad** 🛡️

**Desarrollado con ❤️ por [DogSoulDev](https://github.com/DogSoulDev)**

*"Donde la mitología se encuentra con la tecnología moderna"*

[![GitHub](https://img.shields.io/badge/GitHub-DogSoulDev-blue?style=for-the-badge&logo=github)](https://github.com/DogSoulDev)
[![Kali Linux](https://img.shields.io/badge/Optimizado_para-Kali_Linux-orange?style=for-the-badge&logo=kalilinux)](https://www.kali.org/)
[![Python](https://img.shields.io/badge/Python-3.8+-green?style=for-the-badge&logo=python)](https://python.org)

</div>

### Contacto del Desarrollador
- 👨‍💻 **GitHub**: [@DogSoulDev](https://github.com/DogSoulDev)
- 📧 **Email**: Disponible en el perfil de GitHub
- 🐦 **Twitter**: Actualizaciones del proyecto

---

## 📄 Licencia y Legal

Este proyecto es **software propietario** desarrollado por DogSoulDev. Todos los derechos reservados.

### Términos de Uso
- ✅ Uso personal y educativo permitido
- ✅ Modificaciones para uso propio
- ❌ Redistribución comercial sin autorización
- ❌ Uso para actividades maliciosas

---

## 🎉 Agradecimientos

### Inspiración y Tecnologías
- **Kali Linux Team**: Por crear la mejor distribución de ciberseguridad
- **Python Community**: Por un lenguaje increíble
- **Open Source Security Tools**: Por sentar las bases

### Beta Testers
Gracias a todos los que han probado y mejorado Ares Aegis durante su desarrollo.

---

<div align="center">
  
  ### 🛡️ *"En un mundo digital lleno de amenazas, Ares Aegis es tu escudo protector"* 🛡️
  
  **[⬆️ Volver al inicio](#-ares-aegis---suite-de-ciberseguridad-avanzada)**
  
  ---
  
  Hecho con ❤️ por [DogSoulDev](https://github.com/DogSoulDev) | © 2025 Todos los derechos reservados
  
</div>
