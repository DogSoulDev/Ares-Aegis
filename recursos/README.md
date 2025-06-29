# Ares Aegis - Recursos Gráficos

Este directorio contiene los recursos gráficos oficiales para la aplicación Ares Aegis.

## 🖼️ Archivos Disponibles

### ✅ aresIcon.png
- **Propósito:** Icono principal de la aplicación y ejecutable
- **Formato:** PNG 
- **Estado:** ✅ **DISPONIBLE**
- **Uso:** 
  - Icono de la ventana principal de la aplicación
  - Icono del ejecutable en el sistema operativo
  - Icono del paquete .deb para distribución
  - Barra de tareas del sistema
- **Ubicación en distribución:** `/usr/share/ares_aegis/recursos/aresIcon.png`

### ✅ AresAegis.png
- **Propósito:** Imagen principal de marca/logo del programa
- **Formato:** PNG
- **Estado:** ✅ **DISPONIBLE**
- **Uso:** 
  - Imagen de branding en el menú principal
  - Logo prominente en la interfaz gráfica
  - Elemento visual de identificación del programa
  - Imagen de referencia para documentación
- **Ubicación en distribución:** `/usr/share/ares_aegis/recursos/AresAegis.png`

## 🔧 Notas Técnicas

### Compatibilidad con tkinter
**IMPORTANTE:** tkinter.PhotoImage solo soporta nativamente los formatos GIF, PPM/PGM. 

Para usar las imágenes PNG en la interfaz sin librerías externas, se recomienda convertirlas a formatos compatibles:

### Conversión para uso en tkinter:
```bash
# Convertir icono principal
convert aresIcon.png aresIcon.ppm

# Convertir imagen de marca
convert AresAegis.png AresAegis.ppm
```

### Alternativas de conversión:
```bash
# Usando herramientas online si no tienes ImageMagick:
# 1. Subir PNG a convertidor online PNG → PPM
# 2. Descargar archivo .ppm
# 3. Colocar en el directorio recursos/
```

## 📋 Estado de Recursos

| Archivo | Estado | Formato | Propósito |
|---------|--------|---------|-----------|
| `aresIcon.png` | ✅ Disponible | PNG | Icono de aplicación |
| `AresAegis.png` | ✅ Disponible | PNG | Imagen principal de marca |
| `aresIcon.ppm` | ⏳ Pendiente | PPM | Icono para tkinter |
| `AresAegis.ppm` | ⏳ Pendiente | PPM | Marca para tkinter |

## 🚀 Para Desarrollo

La aplicación está configurada para:
1. **Intentar cargar primero** los formatos PPM (compatibles con tkinter)
2. **Mostrar mensajes informativos** si las imágenes PPM no están disponibles
3. **Continuar funcionando normalmente** sin las imágenes (modo fallback)

## 📦 Para Distribución

En el paquete .deb final, las imágenes se ubicarán en:
- `/usr/share/ares_aegis/recursos/aresIcon.png` - Icono oficial
- `/usr/share/ares_aegis/recursos/AresAegis.png` - Imagen de marca
- `/usr/share/applications/ares-aegis.desktop` - Archivo de aplicación que referencia el icono
