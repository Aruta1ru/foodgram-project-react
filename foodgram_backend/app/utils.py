import os
from io import BytesIO

from django.conf import settings
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

FONT_PATH = os.path.join(settings.BASE_DIR, 'DejaVuSerifCondensed.ttf')


def pdf_create(products):
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    pdfmetrics.registerFont(TTFont('DejaVuSerifCondensed', FONT_PATH))
    p.setFont('DejaVuSerifCondensed', 16)
    p.drawString(200, 800, "Продуктовый помощник")
    p.drawString(180, 700, "Список продуктов для покупки")
    coord_y = 600
    for product in products:
        name = product['name']
        amount = product['amount']
        measurement_unit = product['measurement_unit']
        p.drawString(50, coord_y, f'{name} - {amount} {measurement_unit}')
        coord_y -= 40
    p.showPage()
    p.save()
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
