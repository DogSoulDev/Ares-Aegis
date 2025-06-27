# Ares Aegis - Antivirus para Kali Linux

Ares Aegis es un antivirus moderno, minimalista y robusto para sistemas Linux (Kali), diseñado para ser profesional, escalable y fácil de mantener. El proyecto sigue los más altos estándares de calidad de software, priorizando la claridad, la modularidad y la seguridad. Toda decisión de arquitectura, librerías y estilo de código está documentada para que cualquier desarrollador pueda entender y contribuir fácilmente.

---

## Justificación de la Arquitectura, Librerías y Buenas Prácticas

### ¿Por qué estas librerías?
- **Yara:** Estándar profesional para detección de malware por patrones.
- **Psutil:** Monitorización multiplataforma de procesos, CPU, RAM y red.
- **Hashlib:** Hashing seguro (MD5, SHA-256) para integridad y firmas.
- **Subprocess:** Ejecución de herramientas externas y comandos de Kali.
- **Requests:** Librería robusta y popular para comunicaciones HTTP.
- **Pyinotify:** Monitorización de eventos del sistema de archivos en tiempo real.
- **Scapy:** Análisis y manipulación avanzada de tráfico de red.
- **SQLite:** Motor de base de datos local, rápido y sin dependencias externas.
- **ReportLab:** Generación de informes PDF profesionales y personalizables.
- **PySide6/PyQtGraph:** GUI moderna, minimalista y de alto rendimiento.

### ¿Por qué arquitectura modular y patrón MVC?
- **Separación de responsabilidades:** Cada módulo tiene una función clara (modelo, vista, controlador).
- **Escalabilidad:** Permite añadir nuevas funcionalidades sin romper el sistema.
- **Mantenibilidad:** Facilita localizar y corregir errores o mejorar módulos de forma aislada.
- **Colaboración:** Varios desarrolladores pueden trabajar en paralelo en diferentes capas.
- **Reutilización:** Componentes y lógica pueden ser reutilizados o adaptados en otros proyectos.

### ¿Por qué SOLID, DRY y buenas prácticas?
- **SOLID:** Garantiza que el código sea fácil de mantener, extender y refactorizar.
- **DRY:** Evita duplicidad, centralizando lógica y utilidades comunes.
- **PEP8 y Clean Code:**
  - Código legible y autoexplicativo.
  - Funciones y clases pequeñas, con una única responsabilidad.
  - Nombres descriptivos y consistentes.
  - Documentación clara en cada módulo, clase y función.
  - Manejo robusto de errores y validación de entradas.
  - Uso de comentarios solo para explicar el "por qué" de decisiones complejas.
  - Uso de entornos virtuales y requirements.txt para gestión de dependencias.

### Clean Code en Ares Aegis
- Todo el código sigue los principios de Clean Code:
  - Simplicidad y claridad ante todo.
  - Código fácil de leer, entender y modificar.
  - Separación de lógica y presentación.
  - Refactorización continua para evitar duplicidad y mejorar la estructura.
  - Documentación y comentarios solo donde aportan valor real.

---

**Nombre del programa:** Ares Aegis

## Librerías Base
- **Yara**: Detección de malware por patrones (reglas estándar de la industria).
- **Psutil**: Monitorización de procesos, CPU, memoria y red (multiplataforma).
- **Hashlib**: Cálculo de hashes (MD5, SHA-256, etc.) para integridad y firmas.
- **Subprocess**: Ejecución de comandos externos y herramientas de Kali.
- **Requests**: Comunicaciones HTTP (actualizaciones de firmas, etc.).

## Librerías Avanzadas y Funcionalidades
- **Pyinotify**: Monitorización de eventos del sistema de archivos en tiempo real.
- **auditd** (vía subprocess): Auditoría avanzada de seguridad.
- **Scapy**: Análisis y manipulación de tráfico de red.
- **SQLite (sqlite3)**: Base de datos local para firmas, logs y métricas.
- **ReportLab**: Generación de informes PDF profesionales.
- **PySide6**: Interfaz gráfica de usuario moderna y minimalista.
- **PyQtGraph**: Visualización de datos y gráficos en la GUI.

## Principios y Buenas Prácticas
- **MVC (Modelo-Vista-Controlador)**: Separación clara entre lógica, interfaz y controladores.
- **Clean Code**: Código legible, funciones pequeñas, nombres descriptivos, manejo de errores y documentación.
- **DRY**: Reutilización de código mediante funciones y clases genéricas.
- **SOLID**: Arquitectura robusta, escalable y fácil de mantener.
- **PEP8**: Estilo de código Python.
- **Arquitectura Modular**: Cada componente visual, funcional o de estilo se implementa en un archivo independiente para facilitar la escalabilidad y el mantenimiento.
- **Estilo Minimalista Japonés**: Inspiración en la estética japonesa: limpio, sencillo, cómodo y visualmente agradable. Uso de colores suaves, tipografía clara y espacios amplios.

## Estructura del Proyecto

```
antivirus_kali/
├── .venv/                         # Entorno virtual
├── main.py                        # Punto de entrada de la aplicación GUI (Controlador principal)
├── config.py                      # Configuración global
├── core/
│   ├── __init__.py
│   ├── scan_engine.py             # Lógica principal de escaneo (Modelo)
│   ├── signature_manager.py       # Gestión de firmas (Yara, Hashlib) (Modelo)
│   ├── system_monitor.py          # Monitoreo de procesos, red, archivos (Psutil, Pyinotify) (Modelo)
│   └── database.py                # Interacción con SQLite (Modelo - aplicando DIP)
├── gui/
│   ├── __init__.py
│   ├── main_window.py             # Ventana principal (Vista, minimalista y modular)
│   ├── style.py                   # Colores y estilos globales (QSS)
│   ├── scan_panel.py              # Panel de escaneo principal
│   ├── scan_options_panel.py      # Opciones avanzadas de escaneo (carpetas, YARA, profundo)
│   ├── results_viewer.py          # Visualización de resultados (Vista)
│   ├── system_monitor_panel.py    # Monitorización de CPU, RAM y procesos
│   ├── network_monitor_panel.py   # Monitorización de red y conexiones
│   ├── report_viewer.py           # Visor de informes PDF (Vista)
│   └── settings_panel.py          # Panel de configuración (Vista)
├── controllers/
│   ├── __init__.py
│   └── main_controller.py         # Conecta GUI con lógica (Controlador)
├── reports/
│   ├── __init__.py
│   ├── pdf_generator.py           # Generación de PDF (ReportLab) (Modelo/Servicio)
│   └── templates/                 # Plantillas para informes
├── utils/
│   ├── __init__.py
│   ├── helpers.py                 # Funciones auxiliares genéricas
│   └── logger.py                  # Configuración de logging
└── resources/
    └── icons/                     # Aquí va el icono principal (ares_aegis.png)
```

## Gestión de Componentes y Estilos

Cada panel está implementado en un archivo independiente para máxima escalabilidad y mantenibilidad.
- Cada componente visual (ventana principal, paneles, visores, etc.) se implementa en un archivo independiente dentro de `gui/`.
- Los colores y estilos globales se definen en `gui/style.py` usando QSS (Qt Style Sheets) y una paleta inspirada en el minimalismo japonés.
- Para modificar la apariencia, solo edita `style.py` y se reflejará en toda la aplicación.

## Funcionalidades Profesionales y Paneles

- **Escaneo de Amenazas:** Escaneo rápido, completo y personalizado de archivos y carpetas.
- **Opciones Avanzadas de Escaneo:** Selección de carpetas, uso de reglas YARA, escaneo profundo.
- **Resultados:** Visualización clara de amenazas detectadas y estado del sistema.
- **Monitor del Sistema:** Uso de CPU, RAM y procesos activos en tiempo real.
- **Monitor de Red:** Visualización de conexiones activas y tráfico sospechoso (Scapy).
- **Informes PDF:** Generación y visualización de informes profesionales (ReportLab).
- **Configuración:** Opciones de actualización, escaneo al inicio y preferencias del usuario.

## Icono de la Aplicación

Coloca el icono principal en `antivirus_kali/resources/icons/ares_aegis.png` (o .svg). Este icono se usará en la GUI y para el paquete .deb.

Cuando el proyecto esté finalizado, este icono será referenciado en el archivo `.desktop` y en el empaquetado para Kali Linux.

## Instalación y Entorno

1. **Clona el repositorio:**
   ```bash
   git clone https://github.com/DogSoulDev/Ares-Aegis.git
   cd Ares-Aegis/antivirus_kali
   ```
2. **Crea el entorno virtual:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. **Instala las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

## Principios de Desarrollo
- **Modelo:** Toda la lógica de negocio y datos (detección, análisis, base de datos, firmas, monitorización).
- **Vista:** Interfaz gráfica con PySide6, visualización de resultados y configuración.
- **Controlador:** Conecta la GUI con la lógica del modelo y gestiona la interacción.

## Consejos de Seguridad y Rendimiento
- Usa multithreading/multiprocessing para tareas pesadas.
- Implementa análisis incremental y monitorización en tiempo real.
- Aplica hardening de código y validación de entradas.
- Asegura las actualizaciones y la integridad de las firmas.

## Créditos y Licencia
Trabajo universitario desarrollado por DogSoulDev.

---

> ¡Que no te fallen las bases de tu antivirus! Cumple con la industria y destaca con una arquitectura profesional y moderna.
