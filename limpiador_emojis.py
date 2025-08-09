#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Limpiador Profesional de Emojis y Símbolos no ASCII

Este script elimina de forma segura todos los emojis y otros símbolos
problemáticos del código fuente para garantizar la compatibilidad
y prevenir errores de codificación.
"""

import os
import re

def eliminar_emojis(contenido):
    """
    Elimina emojis y otros símbolos Unicode problemáticos de una cadena de texto.
    """
    # Expresión regular para detectar la mayoría de los emojis y símbolos
    regex_emoji = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticonos
        "\U0001F300-\U0001F5FF"  # símbolos y pictogramas
        "\U0001F680-\U0001F6FF"  # transporte y símbolos misceláneos
        "\U0001F700-\U0001F77F"  # alquimia
        "\U0001F780-\U0001F7FF"  # símbolos geométricos extendidos
        "\U0001F800-\U0001F8FF"  # suplemento de flechas
        "\U0001F900-\U0001F9FF"  # suplemento de pictogramas
        "\U0001FA00-\U0001FA6F"  # ajedrez y otros símbolos
        "\U0001FA70-\U0001FAFF"  # símbolos y pictogramas extendidos
        "\U00002702-\U000027B0"  # dingbats
        "\U000024C2-\U0001F251" 
        "]+",
        flags=re.UNICODE,
    )
    
    # Diccionario de reemplazos manuales para símbolos comunes
    reemplazos = {
        '✅': '[OK]',
        '❌': '[ERROR]',
        '🔧': '[TOOL]',
        '🛡️': '[SHIELD]',
        '🔄': '[REFRESH]',
        '🧹': '[CLEAN]',
        '🏛️': '[SYSTEM]',
        '📱': '[VIEW]',
        '🎯': '[TARGET]',
        '📊': '[STATS]',
        '🖼️': '[ICON]',
        '🔐': '[LOCK]'
    }

    # Primero, aplicar reemplazos manuales
    for emoji, texto in reemplazos.items():
        contenido = contenido.replace(emoji, texto)

    # Luego, eliminar cualquier emoji restante con la regex
    contenido_limpio = regex_emoji.sub('', contenido)
    
    return contenido_limpio

def limpiar_archivos_proyecto():
    """
    Recorre todos los archivos .py del proyecto y elimina los emojis.
    """
    directorio_proyecto = "."
    archivos_python = []
    exclusiones = ["__pycache__", "respaldo_", "installer_temp", ".git"]
    
    for root, dirs, files in os.walk(directorio_proyecto):
        dirs[:] = [d for d in dirs if d not in exclusiones]
        for file in files:
            if file.endswith('.py') and not file.startswith('limpiador_'):
                archivos_python.append(os.path.join(root, file))

    print(f"Analizando {len(archivos_python)} archivos Python para limpieza de emojis...")
    print("-" * 60)
    
    total_modificados = 0
    for archivo_path in archivos_python:
        try:
            with open(archivo_path, 'r', encoding='utf-8') as f:
                contenido_original = f.read()
            
            contenido_limpio = eliminar_emojis(contenido_original)
            
            if contenido_limpio != contenido_original:
                with open(archivo_path, 'w', encoding='utf-8') as f:
                    f.write(contenido_limpio)
                print(f"✓ [LIMPIADO] {archivo_path}")
                total_modificados += 1
        except Exception as e:
            print(f"✗ [ERROR] No se pudo procesar {archivo_path}: {e}")

    print("-" * 60)
    print(f"Limpieza completada. Se modificaron {total_modificados} archivos.")
    print("=" * 60)

if __name__ == "__main__":
    print("LIMPIADOR PROFESIONAL DE EMOJIS Y SÍMBOLOS")
    print("=" * 60)
    limpiar_archivos_proyecto()
    print("El proyecto está ahora libre de emojis para prevenir errores de codificación.")
