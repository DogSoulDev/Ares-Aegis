
"""
Generador de informes PDF usando ReportLab.
Responsable de crear informes profesionales y personalizables.
"""


from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
import datetime
from pathlib import Path




def generar_informe_pdf(resumen, ruta_pdf, usuario="Desconocido"):
    import logging
    from reportlab.platypus import Table, TableStyle, Paragraph, SimpleDocTemplate, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.units import cm
    c = canvas.Canvas(ruta_pdf, pagesize=A4)
    width, height = A4
    margen = 50
    leyendas = {
        'rootkits': 'Resultado del análisis de rootkits en el sistema. Se recomienda investigar cualquier hallazgo.',
        'procesos': 'Procesos sospechosos detectados en ejecución. Revise los procesos listados para descartar amenazas.',
        'puertos': 'Puertos abiertos detectados en el sistema. Los puertos abiertos pueden ser vectores de ataque.',
        'servicios': 'Servicios activos actualmente. Verifique que todos los servicios sean legítimos.',
        'integridad': 'Verificación de integridad de binarios críticos. Cualquier modificación puede indicar compromiso.',
        'programas': 'Listado de programas instalados. Revise programas desconocidos o no autorizados.',
    }
    try:
        # --- Portada ---
        logo_path = Path(__file__).resolve().parent.parent / "recursos" / "Ares.jpeg"
        y = height - 120
        if logo_path.exists():
            try:
                logo = ImageReader(str(logo_path))
                logo_width = 120
                logo_height = 120
                c.drawImage(logo, (width-logo_width)/2, y, width=logo_width, height=logo_height, mask='auto')
            except Exception as e:
                logging.warning(f"No se pudo cargar el logo: {e}")
        c.setFont("Helvetica-Bold", 28)
        c.setFillColor(colors.HexColor("#23272f"))
        c.drawCentredString(width/2, y-30, "Ares Aegis - Informe de Seguridad")
        c.setFont("Helvetica", 16)
        c.setFillColor(colors.HexColor("#444"))
        c.drawCentredString(width/2, y-60, f"Usuario: {usuario}")
        c.drawCentredString(width/2, y-80, f"Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
        c.setFont("Helvetica", 12)
        c.setFillColor(colors.HexColor("#3c8dbc"))
        c.drawCentredString(width/2, y-110, "Generado automáticamente por Ares Aegis")
        c.showPage()

        # --- Índice ---
        c.setFont("Helvetica-Bold", 18)
        c.setFillColor(colors.HexColor("#23272f"))
        c.drawString(margen, height-margen-10, "Índice")
        c.setFont("Helvetica", 12)
        y_indice = height-margen-40
        for i, clave in enumerate(resumen.keys(), 1):
            c.drawString(margen+10, y_indice, f"{i}. {clave.title()}")
            y_indice -= 18
        c.showPage()

        # --- Secciones detalladas ---
        styles = getSampleStyleSheet()
        style_section = ParagraphStyle('section', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=16, textColor=colors.HexColor('#3c8dbc'), spaceAfter=8)
        style_legend = ParagraphStyle('legend', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=10, textColor=colors.HexColor('#23272f'), leftIndent=10, spaceAfter=6)
        style_table_header = ParagraphStyle('table_header', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor('#23272f'), alignment=TA_CENTER)
        style_normal = styles['Normal']
        y = height - margen
        for i, (clave, valor) in enumerate(resumen.items(), 1):
            if y < 180:
                c.showPage()
                y = height - margen
            # Título de sección
            c.setFont("Helvetica-Bold", 16)
            c.setFillColor(colors.HexColor("#3c8dbc"))
            c.drawString(margen, y, f"{i}. {clave.title()}")
            y -= 22
            # Leyenda/explicación
            leyenda = leyendas.get(clave, "")
            if leyenda:
                c.setFont("Helvetica-Oblique", 10)
                c.setFillColor(colors.HexColor("#23272f"))
                c.drawString(margen+10, y, leyenda)
                y -= 16
            c.setFont("Helvetica", 10)
            c.setFillColor(colors.HexColor("#23272f"))
            # Datos tabulares o listados
            if isinstance(valor, dict) and valor:
                # Tabla para integridad
                c.setFont("Helvetica-Bold", 10)
                c.drawString(margen+10, y, "Archivo")
                c.drawString(margen+220, y, "Estado")
                y -= 14
                c.setFont("Helvetica", 10)
                for k, v in valor.items():
                    if y < 60:
                        c.showPage()
                        y = height - margen
                    c.drawString(margen+10, y, str(k))
                    c.drawString(margen+220, y, str(v))
                    y -= 12
            elif isinstance(valor, list) and valor:
                for item in valor[:30]:
                    if y < 60:
                        c.showPage()
                        y = height - margen
                    c.drawString(margen+10, y, f"- {item}")
                    y -= 12
                if len(valor) > 30:
                    c.drawString(margen+10, y, f"...y {len(valor)-30} más.")
                    y -= 12
            elif valor:
                c.drawString(margen+10, y, str(valor))
                y -= 12
            else:
                c.drawString(margen+10, y, "Sin datos relevantes para esta sección.")
                y -= 12
            y -= 18
        # Pie de página profesional
        c.setFont("Helvetica-Oblique", 9)
        c.setFillColor(colors.HexColor("#888"))
        c.drawString(margen, 30, "Generado automáticamente por Ares Aegis - https://github.com/DogSoulDev/Ares-Aegis")
        c.save()
        return ruta_pdf
    except Exception as e:
        logging.error(f"Error al generar el PDF: {e}")
        raise
