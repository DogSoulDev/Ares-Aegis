

"""
Generador de informes PDF profesional para Ares Aegis.
Incluye branding, icono, portada, estructura clara y secciones ordenadas.
"""


# Mejoras visuales y experiencia única para el informe PDF de Ares Aegis
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, Flowable
)

import datetime
import logging
import os
import io
import qrcode
from reportlab.graphics.shapes import Line

ICON_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "recursos", "iconos", "aresIcon.png")


# Utilidad para iconos de estado en tablas
def estado_icono(estado):
    if "Íntegro" in estado:
        return "🟢"
    if "Modificado" in estado:
        return "🔴"
    if "No encontrado" in estado:
        return "⚠️"
    return "🟡"

class CircularImage(Flowable):
    """Dibuja una imagen circular (para el icono de portada)."""
    def __init__(self, img_path, size=90):
        super().__init__()
        self.img_path = img_path
        self.size = size
    def draw(self):
        c = self.canv
        c.saveState()
        # Crear un path circular y usarlo como máscara de recorte
        from reportlab.pdfgen import pathobject
        p = c.beginPath()
        p.circle(self.size/2, self.size/2, self.size/2)
        c.clipPath(p, stroke=0, fill=1)
        c.drawImage(self.img_path, 0, 0, width=self.size, height=self.size, mask='auto')
        c.restoreState()
    def wrap(self, aW, aH):
        return self.size, self.size

def generar_qr_code(data, size=80):
    qr = qrcode.QRCode(box_size=2, border=1)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#222", back_color="white")
    buf = io.BytesIO()
    img.save(buf, "PNG")
    buf.seek(0)
    return Image(buf, width=size, height=size)

def generar_informe_pdf(resumen, ruta_pdf="/tmp/informe_ares_aegis.pdf", usuario="Desconocido", branding="Ares Aegis", icono_path=ICON_PATH):
    """
    Genera un informe PDF profesional, visualmente único y memorable.
    """
    try:
        doc = SimpleDocTemplate(ruta_pdf, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=60, bottomMargin=40)
        elementos = []
        estilos = getSampleStyleSheet()
        estilo_titulo = estilos['Title']
        estilo_titulo.fontName = 'Helvetica-Bold'
        estilo_titulo.fontSize = 32
        estilo_titulo.textColor = colors.HexColor('#1a1a1a')
        estilo_subtitulo = estilos['Heading2']
        estilo_subtitulo.fontName = 'Helvetica-Bold'
        estilo_subtitulo.fontSize = 16
        estilo_subtitulo.textColor = colors.HexColor('#444')
        estilo_normal = estilos['BodyText']
        estilo_normal.fontName = 'Helvetica'
        estilo_normal.fontSize = 11
        estilo_normal.leading = 16
        estilo_normal.textColor = colors.HexColor('#222')
        estilo_pie = ParagraphStyle('Pie', fontSize=8, textColor=colors.HexColor('#888'), alignment=1)
        estilo_seccion = ParagraphStyle('Seccion', fontSize=15, fontName='Helvetica-Bold', textColor=colors.HexColor('#b00'), spaceAfter=8)
        estilo_tabla_header = ParagraphStyle('TablaHeader', fontSize=11, fontName='Helvetica-Bold', textColor=colors.HexColor('#fff'), alignment=1)

        # Portada visual única
        portada_bg = colors.HexColor('#f6f6f6')
        elementos.append(Spacer(1, 30))
        if os.path.exists(icono_path):
            elementos.append(CircularImage(icono_path, size=110))
        elementos.append(Spacer(1, 18))
        elementos.append(Paragraph(f"<b>{branding}</b>", estilo_titulo))
        elementos.append(Spacer(1, 8))
        elementos.append(Paragraph("Antivirus modular para Kali Linux", estilo_subtitulo))
        elementos.append(Spacer(1, 8))
        elementos.append(Paragraph(f"<b>Informe generado:</b> {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}", estilo_normal))
        elementos.append(Paragraph(f"<b>Usuario:</b> {usuario}", estilo_normal))
        elementos.append(Spacer(1, 18))
        elementos.append(Paragraph("<i>“La seguridad no es un producto, es un proceso continuo.”</i>", estilo_normal))
        elementos.append(Spacer(1, 18))
        # Panel visual de riesgo global
        elementos.append(Paragraph("Nivel de riesgo global del sistema:", estilo_subtitulo))
        elementos.append(gauge_riesgo_global(resumen))
        elementos.append(Spacer(1, 18))
        # Resumen ejecutivo automático
        resumen_exec, recomendaciones = resumen_ejecutivo(resumen)
        elementos.append(Paragraph("<b>Resumen Ejecutivo:</b>", estilo_subtitulo))
        elementos.append(Paragraph(resumen_exec, estilo_normal))
        elementos.append(Spacer(1, 8))
        elementos.append(Paragraph("<b>Recomendaciones:</b>", estilo_subtitulo))
        for rec in recomendaciones:
            elementos.append(Paragraph(f"- {rec}", estilo_normal))
        elementos.append(Spacer(1, 18))
        # QR de restauración rápida
        elementos.append(Paragraph("¿Necesitas restaurar tu sistema? Escanea este QR para obtener scripts de restauración y ayuda offline:", estilo_normal))
        elementos.append(generar_qr_code("https://github.com/DogSoulDev/Ares-Aegis/wiki/Restauracion", size=70))
        elementos.append(Spacer(1, 8))
        # QR de feedback anónimo
        elementos.append(Paragraph("¿Quieres ayudarnos a mejorar? Escanea este QR para enviar feedback anónimo:", estilo_normal))
        elementos.append(generar_qr_code("https://github.com/DogSoulDev/Ares-Aegis/issues/new?template=feedback.md", size=70))
        elementos.append(Spacer(1, 18))
        elementos.append(Paragraph("Este informe presenta los resultados del análisis de seguridad realizado por Ares Aegis. Todos los datos están organizados para facilitar su interpretación por cualquier usuario, técnico o auditor.", estilo_normal))
        elementos.append(PageBreak())

        def pie_de_pagina(canvas, doc):
            canvas.saveState()
            pie = f"{branding} | {datetime.datetime.now().strftime('%d/%m/%Y')} | Página {doc.page} | 'La seguridad es arte y disciplina.'"
            canvas.setFont('Helvetica', 8)
            canvas.setFillColor(colors.HexColor('#888'))
            canvas.drawCentredString(A4[0]/2, 20, pie)
            canvas.restoreState()

        doc.build(elementos, onFirstPage=pie_de_pagina, onLaterPages=pie_de_pagina)
        return ruta_pdf
    except Exception as e:
        logging.error(f"Error global al generar informe PDF: {e}", exc_info=True)
        return f"Error global al generar informe PDF: {e}"
def resumen_ejecutivo(resumen):
    """Genera un resumen ejecutivo y recomendaciones automáticas a partir del análisis."""
    problemas = []
    recomendaciones = []
    if resumen.get('rootkits'):
        problemas.append("Se detectaron posibles rootkits en el sistema.")
        recomendaciones.append("Ejecuta un análisis forense y considera reinstalar el sistema si no reconoces los rootkits.")
    if resumen.get('procesos'):
        problemas.append("Procesos sospechosos detectados.")
        recomendaciones.append("Revisa los procesos listados y detén los que no reconozcas.")
    if resumen.get('puertos'):
        problemas.append("Existen puertos abiertos que pueden suponer un riesgo.")
        recomendaciones.append("Cierra los puertos no utilizados y revisa la configuración del firewall.")
    if resumen.get('servicios'):
        recomendaciones.append("Verifica que los servicios activos sean necesarios y estén actualizados.")
    if resumen.get('integridad') and any('Modificado' in v for v in resumen['integridad'].values()):
        problemas.append("Algunos binarios críticos han sido modificados.")
        recomendaciones.append("Restaura los binarios modificados usando los scripts de restauración o reinstala los paquetes afectados.")
    if resumen.get('integridad') and any('No encontrado' in v for v in resumen['integridad'].values()):
        problemas.append("No se pudo verificar la integridad de algunos binarios.")
        recomendaciones.append("Asegúrate de que todos los binarios críticos estén presentes y sin alteraciones.")
    if not problemas:
        resumen_exec = "No se detectaron amenazas ni anomalías relevantes. El sistema parece estar seguro y en buen estado."
        recomendaciones.append("Mantén el sistema actualizado y realiza análisis periódicos.")
    else:
        resumen_exec = " ".join(problemas)
    return resumen_exec, recomendaciones

def gauge_riesgo_global(resumen):
    """Dibuja un gauge visual del nivel de riesgo global del sistema."""
    from reportlab.graphics.shapes import Drawing, String, Circle, Line
    # Cálculo simple: cada problema suma puntos de riesgo
    riesgo = 0
    if resumen.get('rootkits'):
        riesgo += 3
    if resumen.get('procesos'):
        riesgo += 2
    if resumen.get('puertos'):
        riesgo += 1
    if resumen.get('integridad') and any('Modificado' in v for v in resumen['integridad'].values()):
        riesgo += 3
    if resumen.get('integridad') and any('No encontrado' in v for v in resumen['integridad'].values()):
        riesgo += 1
    if riesgo == 0:
        color = colors.HexColor('#27ae60')
        label = "Seguro"
    elif riesgo <= 2:
        color = colors.HexColor('#f1c40f')
        label = "Precaución"
    elif riesgo <= 4:
        color = colors.HexColor('#e67e22')
        label = "Riesgo Moderado"
    else:
        color = colors.HexColor('#c0392b')
        label = "Alto Riesgo"
    d = Drawing(200, 80)
    # Gauge simple: círculo y aguja
    d.add(Circle(100, 40, 35, fillColor=colors.HexColor('#f6f6f6'), strokeColor=color, strokeWidth=4))
    # Aguja
    import math
    angle = 180 - (riesgo / 7.0) * 180  # 0 seguro, 7 máximo riesgo
    x2 = 100 + 30 * math.cos(math.radians(angle))
    y2 = 40 + 30 * math.sin(math.radians(angle))
    d.add(Line(100, 40, x2, y2, strokeColor=color, strokeWidth=4))
    d.add(String(100, 10, label, fontName='Helvetica-Bold', fontSize=13, fillColor=color, textAnchor='middle'))
    d.add(String(100, 70, "RIESGO GLOBAL", fontName='Helvetica', fontSize=9, fillColor=colors.HexColor('#888'), textAnchor='middle'))
    d.add(String(100, 40, "", fontName='Helvetica', fontSize=1, fillColor=color))
    return d

    # Secciones visuales y ordenadas
    def seccion(titulo, color=colors.HexColor('#b00')):
        elementos.append(Spacer(1, 12))
        elementos.append(Paragraph(f"<b>{titulo}</b>", ParagraphStyle('Seccion', parent=estilo_seccion, textColor=color)))
        elementos.append(Spacer(1, 6))

    # Rootkits
    seccion("Análisis de Rootkits", color=colors.HexColor('#b00'))
    rootkits = resumen.get('rootkits', [])
    if rootkits:
        for r in rootkits:
            elementos.append(Paragraph(f"<font color='#b00'>⛔</font> {r}", estilo_normal))
    else:
        elementos.append(Paragraph("<font color='#0a0'>✔ No se detectaron rootkits.</font>", estilo_normal))

    # Procesos sospechosos
    seccion("Procesos Sospechosos", color=colors.HexColor('#e67e22'))
    procesos = resumen.get('procesos', [])
    if procesos:
        for p in procesos:
            elementos.append(Paragraph(f"<font color='#e67e22'>⚠️</font> {p}", estilo_normal))
    else:
        elementos.append(Paragraph("<font color='#0a0'>✔ No se detectaron procesos sospechosos.</font>", estilo_normal))

    # Puertos abiertos
    seccion("Puertos Abiertos", color=colors.HexColor('#2980b9'))
    puertos = resumen.get('puertos', [])
    if puertos:
        data = [[Paragraph(f"<font color='#2980b9'>🔓</font> {p}", estilo_normal)] for p in puertos]
        tabla = Table(data, colWidths=[450])
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#eaf6fb')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#222')),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#eaf6fb')]),
        ]))
        elementos.append(tabla)
    else:
        elementos.append(Paragraph("<font color='#0a0'>✔ No se detectaron puertos abiertos.</font>", estilo_normal))

    # Servicios activos
    seccion("Servicios Activos", color=colors.HexColor('#16a085'))
    servicios = resumen.get('servicios', [])
    if servicios:
        data = [[Paragraph(f"<font color='#16a085'>⚙️</font> {s}", estilo_normal)] for s in servicios]
        tabla = Table(data, colWidths=[450])
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#eafaf7')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#222')),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#eafaf7')]),
        ]))
        elementos.append(tabla)
    else:
        elementos.append(Paragraph("<font color='#0a0'>✔ No se detectaron servicios activos.</font>", estilo_normal))

    # Integridad de binarios
    seccion("Integridad de Binarios Críticos", color=colors.HexColor('#8e44ad'))
    integridad = resumen.get('integridad', {})
    if integridad:
        data = [[Paragraph(str(archivo), estilo_normal), Paragraph(f"<font color='#8e44ad'>{estado_icono(estado)}</font> {estado}", estilo_normal)] for archivo, estado in integridad.items()]
        tabla = Table([[Paragraph("Archivo", estilo_tabla_header), Paragraph("Estado", estilo_tabla_header)]] + data, colWidths=[300, 150])
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8e44ad')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#fff')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#222')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f6f6f6')]),
        ]))
        elementos.append(tabla)
    else:
        elementos.append(Paragraph("<font color='#0a0'>✔ Todos los binarios críticos están íntegros.</font>", estilo_normal))

    # Programas instalados
    seccion("Programas Instalados", color=colors.HexColor('#34495e'))
    programas = resumen.get('programas', [])
    if programas:
        elementos.append(Paragraph(f"Total de programas instalados: <b>{len(programas)}</b>", estilo_normal))
        for prog in programas[:30]:
            elementos.append(Paragraph(f"<font color='#34495e'>📦</font> {prog}", estilo_normal))
        if len(programas) > 30:
            elementos.append(Paragraph(f"...y {len(programas)-30} más.", estilo_pie))
    else:
        elementos.append(Paragraph("No se detectaron programas instalados.", estilo_normal))

    # Pie de página visual y motivacional
    def pie_de_pagina(canvas, doc):
        canvas.saveState()
        pie = f"{branding} | {datetime.datetime.now().strftime('%d/%m/%Y')} | Página {doc.page} | 'La seguridad es arte y disciplina.'"
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor('#888'))
        canvas.drawCentredString(A4[0]/2, 20, pie)
        canvas.restoreState()



    try:
        try:
            doc.build(elementos, onFirstPage=pie_de_pagina, onLaterPages=pie_de_pagina)
            return ruta_pdf
        except Exception as e:
            logging.error(f"Error al generar informe PDF: {e}", exc_info=True)
            return f"Error al generar informe PDF: {e}"
    except Exception as fatal:
        logging.error(f"Fallo inesperado en generar_informe_pdf: {fatal}", exc_info=True)
        return f"Error fatal al generar informe PDF: {fatal}"
