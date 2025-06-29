# Ares Aegis - Recursos Gráficos

Este directorio contiene los recursos gráficos necesarios para la aplicación Ares Aegis.

## Archivos Requeridos

### aresIcon.png
- **Propósito:** Icono principal de la aplicación
- **Formato:** PNG (recomendado 64x64 píxeles o mayor)
- **Uso:** Se muestra en la barra de tareas del sistema operativo y como icono de la ventana
- **Ubicación en distribución:** `/usr/share/ares_aegis/recursos/aresIcon.png`

### Ares.jpeg
- **Propósito:** Imagen de marca/logo para la interfaz
- **Formato:** JPEG
- **Uso:** Se muestra prominentemente en el menú principal como elemento de branding
- **Ubicación en distribución:** `/usr/share/ares_aegis/recursos/Ares.jpeg`

## Notas Técnicas

**IMPORTANTE:** tkinter.PhotoImage solo soporta nativamente los formatos GIF, PPM/PGM. 
Para usar PNG y JPEG sin librerías externas, las imágenes deben ser convertidas a formatos compatibles:

### Conversión de PNG a PPM:
```bash
convert aresIcon.png aresIcon.ppm
```

### Conversión de JPEG a PPM:
```bash
convert Ares.jpeg Ares.ppm
```

## Alternativas para Desarrollo

Si no tienes las imágenes disponibles, la aplicación mostrará mensajes de placeholder y registrará advertencias en el log, pero seguirá funcionando normalmente.
