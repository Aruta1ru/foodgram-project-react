from fpdf import FPDF


def pdf_create(products):
    pdf = FPDF()
    pdf.add_font('DejaVu', '', 'DejaVuSerifCondensed.ttf', uni=True)
    pdf.set_font('DejaVu', '', 14)
    pdf.add_page()
    pdf.cell(200, 10, txt="Продуктовый помощник", ln=1, align="C")
    pdf.cell(200, 10, txt='', ln=1)
    pdf.cell(200, 10, txt="Список продуктов для покупки:", ln=1, align="C")
    pdf.cell(200, 10, txt='', ln=1)
    pdf.cell(200, 10, txt='', ln=1)
    for product in products:
        name = product['name']
        amount = product['amount']
        measurement_unit = product['measurement_unit']
        pdf.cell(0, 10, txt=f'{name} - {amount} {measurement_unit}', ln=1)
    #pdf.output('media/shopping_cart.pdf')
    return pdf
