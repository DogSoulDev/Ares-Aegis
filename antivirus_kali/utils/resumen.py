"""
Utilidades para resumen ejecutivo, feedback visual y exportación profesional en Ares Aegis.
Incluye funciones para terminal (colores, iconos) y para PDF/Markdown.
"""
import datetime
import os

# ANSI para terminal
ANSI = {
    'reset': '\033[0m',
    'red': '\033[91m',
    'yellow': '\033[93m',
    'green': '\033[92m',
    'blue': '\033[94m',
    'bold': '\033[1m',
}

ICONS = {
    'ok': '🟢',
    'warn': '🟡',
    'fail': '🔴',
    'info': 'ℹ️',
    'arrow': '➜',
    'star': '★',
    'danger': '⚠️',
}

def colorize(text, color):
    return f"{ANSI.get(color, '')}{text}{ANSI['reset']}"

def resumen_ejecutivo(data, recomendaciones=None, formato='terminal'):
    """
    Genera un resumen ejecutivo visual y claro para terminal, PDF o Markdown.
    data: dict con resultados de análisis.
    recomendaciones: lista de strings.
    formato: 'terminal', 'markdown' o 'pdf'.
    """
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    out = []
    if formato == 'terminal':
        out.append(colorize(f"\n{ICONS['star']} RESUMEN EJECUTIVO ARES AEGIS {ICONS['star']}", 'bold'))
        out.append(colorize(f"Fecha: {now}", 'blue'))
        for k, v in data.items():
            if isinstance(v, list):
                icon = ICONS['fail'] if v else ICONS['ok']
                out.append(f"{icon} {k.title()}: {len(v)} detectados")
            elif isinstance(v, dict):
                out.append(f"{ICONS['info']} {k.title()}: {len(v)} elementos")
            else:
                out.append(f"{ICONS['info']} {k.title()}: {v}")
        if recomendaciones:
            out.append(colorize(f"\n{ICONS['arrow']} RECOMENDACIONES:", 'yellow'))
            for rec in recomendaciones:
                out.append(f"  - {rec}")
    elif formato == 'markdown':
        out.append(f"# {ICONS['star']} Resumen Ejecutivo Ares Aegis\n")
        out.append(f"**Fecha:** {now}\n")
        for k, v in data.items():
            if isinstance(v, list):
                icon = ICONS['fail'] if v else ICONS['ok']
                out.append(f"- {icon} **{k.title()}:** {len(v)} detectados")
            elif isinstance(v, dict):
                out.append(f"- {ICONS['info']} **{k.title()}:** {len(v)} elementos")
            else:
                out.append(f"- {ICONS['info']} **{k.title()}:** {v}")
        if recomendaciones:
            out.append(f"\n## {ICONS['arrow']} Recomendaciones\n")
            for rec in recomendaciones:
                out.append(f"- {rec}")
    # Para PDF, se delega a generador_pdf
    return '\n'.join(out)

def exportar_markdown(data, recomendaciones=None, ruta=None):
    md = resumen_ejecutivo(data, recomendaciones, formato='markdown')
    if not ruta:
        ruta = f"informe_ares_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.md"
    with open(ruta, 'w', encoding='utf-8') as f:
        f.write(md)
    return os.path.abspath(ruta)

def exportar_txt(data, recomendaciones=None, ruta=None):
    txt = resumen_ejecutivo(data, recomendaciones, formato='terminal')
    if not ruta:
        ruta = f"informe_ares_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    with open(ruta, 'w', encoding='utf-8') as f:
        f.write(txt)
    return os.path.abspath(ruta)

def feedback_visual_terminal(msg, tipo='info'):
    color = 'green' if tipo == 'ok' else 'yellow' if tipo == 'warn' else 'red' if tipo == 'fail' else 'blue'
    icon = ICONS.get(tipo, ICONS['info'])
    return colorize(f"{icon} {msg}", color)

