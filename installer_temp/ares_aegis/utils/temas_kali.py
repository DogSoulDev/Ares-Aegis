#!/usr/bin/env python3
"""
Temas de Kali Linux para Ares Aegis
Definiciones de colores oficiales de Kali Linux y variantes
"""

# Tema por defecto - Kali Linux Original
TEMA_KALI_ORIGINAL = {
    'nombre': 'Kali Original',
    'bg_principal': '#0D1117',
    'bg_secundario': '#21262D',
    'bg_terciario': '#30363D',
    'texto_principal': '#F0F6FC',
    'texto_secundario': '#8B949E',
    'acento_primario': '#00FF41',  # Verde Kali clásico
    'acento_secundario': '#367BF0',
    'error': '#F85149',
    'warning': '#D29922',
    'success': '#2DA44E',
    'borde': '#30363D'
}

# Tema Dragon - Inspirado en Kali Dragon
TEMA_DRAGON = {
    'nombre': 'Dragon',
    'bg_principal': '#1A0B0B',
    'bg_secundario': '#2D1B1B',
    'bg_terciario': '#3D2B2B',
    'texto_principal': '#FFFFFF',
    'texto_secundario': '#CCCCCC',
    'acento_primario': '#FF0040',  # Rojo dragon
    'acento_secundario': '#FF6B35',
    'error': '#FF0040',
    'warning': '#FFB347',
    'success': '#32CD32',
    'borde': '#3D2B2B'
}

# Tema Purple - Inspirado en herramientas de pentesting
TEMA_PURPLE = {
    'nombre': 'Purple Haze',
    'bg_principal': '#0F0518',
    'bg_secundario': '#1F0F33',
    'bg_terciario': '#2F1A4D',
    'texto_principal': '#E6E6FA',
    'texto_secundario': '#C8A2C8',
    'acento_primario': '#9D4EDD',  # Púrpura vibrante
    'acento_secundario': '#7209B7',
    'error': '#FF006E',
    'warning': '#FB8500',
    'success': '#06FFA5',
    'borde': '#2F1A4D'
}

# Tema Blue Steel - Azules profesionales
TEMA_BLUE_STEEL = {
    'nombre': 'Blue Steel',
    'bg_principal': '#0A0F1C',
    'bg_secundario': '#1A2332',
    'bg_terciario': '#2A3747',
    'texto_principal': '#E1E8F0',
    'texto_secundario': '#A8B2C1',
    'acento_primario': '#00D9FF',  # Cian brillante
    'acento_secundario': '#0080FF',
    'error': '#FF4757',
    'warning': '#FFA502',
    'success': '#2ED573',
    'borde': '#2A3747'
}

# Tema Matrix - Verde Matrix clásico
TEMA_MATRIX = {
    'nombre': 'Matrix',
    'bg_principal': '#000000',
    'bg_secundario': '#001100',
    'bg_terciario': '#002200',
    'texto_principal': '#00FF00',
    'texto_secundario': '#00CC00',
    'acento_primario': '#00FF41',  # Verde Matrix
    'acento_secundario': '#39FF14',
    'error': '#FF0000',
    'warning': '#FFFF00',
    'success': '#00FF00',
    'borde': '#002200'
}

# Mapa de todos los temas disponibles
TEMAS_DISPONIBLES = {
    'kali_original': TEMA_KALI_ORIGINAL,
    'dragon': TEMA_DRAGON,
    'purple': TEMA_PURPLE,
    'blue_steel': TEMA_BLUE_STEEL,
    'matrix': TEMA_MATRIX
}

def obtener_tema(nombre_tema='kali_original'):
    """Obtiene un tema por nombre"""
    return TEMAS_DISPONIBLES.get(nombre_tema, TEMA_KALI_ORIGINAL)

def obtener_lista_temas():
    """Obtiene lista de nombres de temas disponibles"""
    return list(TEMAS_DISPONIBLES.keys())

def aplicar_tema_a_widget(widget, tema, tipo_widget='frame'):
    """Aplica un tema a un widget específico"""
    try:
        if tipo_widget == 'frame':
            widget.configure(bg=tema['bg_secundario'])
        elif tipo_widget == 'label':
            widget.configure(
                bg=tema['bg_secundario'],
                fg=tema['texto_principal']
            )
        elif tipo_widget == 'button':
            widget.configure(
                bg=tema['acento_primario'],
                fg=tema['bg_principal'],
                activebackground=tema['acento_secundario']
            )
        elif tipo_widget == 'entry':
            widget.configure(
                bg=tema['bg_terciario'],
                fg=tema['texto_principal'],
                insertbackground=tema['texto_principal']
            )
        elif tipo_widget == 'text':
            widget.configure(
                bg=tema['bg_terciario'],
                fg=tema['texto_principal'],
                insertbackground=tema['texto_principal']
            )
        elif tipo_widget == 'listbox':
            widget.configure(
                bg=tema['bg_terciario'],
                fg=tema['texto_principal'],
                selectbackground=tema['acento_primario']
            )
    except Exception:
        pass  # Ignorar errores si el widget no soporta cierta configuración
