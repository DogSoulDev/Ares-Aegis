---

## 📁 Estructura del Proyecto

```text
Ares-Aegis/
│
├── antivirus_kali/                # Código principal del antivirus
│   ├── controladores/             # Lógica de control (MVC)
│   ├── interfaz/                  # Interfaz gráfica (paneles, ventanas, estilos)
│   ├── nucleo/                    # Núcleo de análisis, escaneo, integridad, red, IOCs
│   ├── reports/                   # Generador profesional de informes PDF
│   ├── recursos/                  # Recursos gráficos (iconos, imágenes)
│   ├── tests/                     # Tests unitarios de todos los módulos y paneles
│   ├── utils/                     # Utilidades y helpers reutilizables
│   ├── requirements.txt           # Dependencias principales
│   ├── principal.py               # Entry point de la aplicación
│   └── ...                        # Otros módulos y configuraciones
│
├── README.md                      # Documentación principal y guía de uso
├── CREDITOS.md                    # Créditos de autoría y edición
└── ...                            # Archivos de configuración y licencia
```

**Descripción de carpetas clave:**
- `controladores/`: Controladores para cada panel y función (escaneo, integridad, red, IOCs, modo seguro, etc).
- `interfaz/`: Paneles visuales, ventana principal, estilos y visores.
- `nucleo/`: Lógica de análisis, escaneo, integridad, red, gestión de IOCs, modo seguro, etc.
- `reports/`: Generador de informes PDF visuales y profesionales.
- `recursos/`: Iconos, imágenes y recursos gráficos.
- `tests/`: Tests unitarios exhaustivos para todos los componentes principales.
- `utils/`: Helpers y utilidades comunes (logger, helpers, etc).

---
# Ares Aegis - Antivirus para Kali Linux

Ares Aegis es un antivirus moderno, minimalista y robusto para sistemas Linux (Kali), diseñado para ser profesional, escalable y fácil de mantener. El proyecto sigue los más altos estándares de calidad de software, priorizando la claridad, la modularidad y la seguridad. Toda decisión de arquitectura, librerías y estilo de código está documentada para que cualquier desarrollador pueda entender y contribuir fácilmente.

---

## Justificación de la Arquitectura, Librerías y Buenas Prácticas


# Ares Aegis

Antivirus modular, visual, automatizado y profesional para Kali Linux.

---

## Características principales

- **Escaneo avanzado** de rootkits, procesos, puertos, servicios, integridad de binarios y programas instalados.
- **Generación de informes PDF profesionales y visuales**:
  - Portada con branding, icono circular y QR de soporte y feedback.
  - Panel visual de riesgo global (gauge).
  - Resumen ejecutivo automático y recomendaciones personalizadas.
  - Tablas visuales con iconos y colores para cada sección.
  - QR de restauración rápida y feedback anónimo.
  - Pie de página motivacional y paginación.
- **Experiencia 100% automatizada**: el usuario solo elige la opción, el sistema analiza, interpreta y presenta todo de forma clara y visual.
- **No requiere APIs externas ni registros**: toda la lógica y análisis es local y privado.
- **Interfaz gráfica minimalista y moderna** (PySide6), con paneles para cada área de seguridad.
- **Código limpio, modular y profesional**: sin archivos duplicados ni rutas obsoletas.
- **Test unitarios exhaustivos**: todos los componentes principales están cubiertos y validados.
- **Validación continua**: todos los tests pasan correctamente (pytest), garantizando robustez y calidad.

---

## Instalación

1. Clona el repositorio y entra en la carpeta:
   ```bash
   git clone https://github.com/DogSoulDev/Ares-Aegis.git
   cd Ares-Aegis
   ```
2. Crea y activa el entorno virtual:
   ```bash
   python3 -m venv antivirus_kali/.venv
   source antivirus_kali/.venv/bin/activate
   ```
3. Instala las dependencias:
   ```bash
   pip install --upgrade pip
   pip install -r antivirus_kali/requirements.txt
   pip install qrcode[pil]
   ```
4. Ejecuta la aplicación:
   ```bash
   python3 antivirus_kali/principal.py
   ```

---

## Uso

- Navega por los paneles para escanear el sistema, verificar integridad, analizar red, gestionar IOCs y más.
- Exporta el informe PDF profesional desde el panel de escaneo avanzado.
- Escanea los QR del informe para restaurar el sistema o enviar feedback anónimo.

---

## Buenas prácticas y principios

- **Privacidad y autonomía**: todo el análisis es local, sin enviar datos fuera.
- **Visual y didáctico**: cada informe y panel está diseñado para ser claro, visual y fácil de interpretar.
- **Automatización total**: el usuario no necesita conocimientos técnicos ni realizar pasos complejos.
- **Código profesional y mantenible**: estructura limpia, modular y sin duplicidades.
- **Cobertura de tests**: cada módulo y panel cuenta con tests unitarios robustos.
- **Documentación y créditos**: autoría y edición documentada en `CREDITOS.md`.

---

## Estado del sistema (junio 2025)

- **Validación completa:** Todos los tests unitarios pasan correctamente (`pytest`).
- **Sin errores de importación, sintaxis ni ejecución.**
- **Estructura limpia y profesional, lista para distribución y uso real.**
- **Automatización y experiencia visual únicas.**

---

## Créditos

Desarrollado por DogSoulDev y colaboradores. Edición y refuerzo profesional con ayuda de GPT-4.1.

¿Ideas, sugerencias o problemas? Escanea el QR de feedback en tu informe o abre un issue en GitHub.

---

Ares Aegis: Seguridad, arte y disciplina para tu sistema Kali Linux.
Desarrollado por DogSoulDev. Inspirado en la filosofía de software libre y la cultura japonesa del detalle.

---

## 📄 Licencia

[MIT](LICENSE)
