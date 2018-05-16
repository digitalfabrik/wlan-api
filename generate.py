import csv
from io import BytesIO
from reportlab.lib.pagesizes import letter, A5
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak, Image, ListFlowable, ListItem, Spacer, Table, TableStyle, Frame
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle, ListStyle
from reportlab.graphics.shapes import Drawing
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch
from reportlab.lib.colors import black
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm, cm
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.fonts import addMapping
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.lib.enums import TA_RIGHT

from QRFlowable import QRFlowable

class VoucherPrint:

    def __init__(self, buffer, vouchers):
        self.buffer = buffer
        self.vouchers = vouchers
        self.pagesize = A5
        self.width, self.height = self.pagesize

    @staticmethod
    def _header_footer(canvas, doc):
        canvas.saveState()
        styles = getSampleStyleSheet()
        canvas.setFont("DejaVu Sans", 7)

        im = Image('TaT_DF_LOGO.png')
        im._restrictSize(1000 * mm, 30 * mm)
        im.drawOn(canvas, doc.leftMargin, doc.height - 20 * mm)

        # Footer
        canvas.drawRightString(doc.width + doc.rightMargin, 5 * mm,
                               'Falls Probleme auftreten, schreiben Sie eine E-Mail an wifi@tuerantuer.de')

        # Release the canvas
        canvas.restoreState()

    def print_users(self):
        pdfmetrics.registerFont(TTFont("DejaVu Sans", "DejaVuSans.ttf"))
        pdfmetrics.registerFont(
            TTFont("DejaVu Sans Bold", "DejaVuSans-Bold.ttf"))
        addMapping('DejaVu Sans', 0, 0, 'DejaVu Sans')
        addMapping('DejaVu Sans', 1, 0, 'DejaVu Sans Bold')

        buffer = self.buffer
        doc = SimpleDocTemplate(buffer,
                                rightMargin=15 * mm,
                                leftMargin=15 * mm,
                                topMargin=0 * mm,
                                bottomMargin=15 * mm,
                                pagesize=self.pagesize)

        # Our container for 'Flowable' objects
        elements = []

        # A large collection of style sheets pre-made for us
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(
            name='Text',
            fontName='DejaVu Sans',
            fontSize=8,
        ))
        styles.add(ListStyle(
            'list_default',
            bulletType='bullet',
            start='circle',
            leftIndent=10,
            bulletOffsetY=0,
            bulletFontSize=7
        ))

        for i, voucher in enumerate(vouchers):
            qrcode = QRFlowable(voucher)
            elements.append(qrcode)

            elements.append(Spacer(0, 5 * mm))
            table = Table([('Voucher Code', voucher)],
                          colWidths=55 * mm, rowHeights=10 * mm)
            table.setStyle(TableStyle(
                [
                    ('INNERGRID', (0, 0), (-1, -1), 0.5 * mm, black),
                    ('FONT', (0, 0), (-1, -1), 'DejaVu Sans Bold'),
                    ('BOX', (0, 0), (-1, -1), 0.5 * mm, black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]
            ))
            elements.append(table)
            elements.append(Spacer(0, 10 * mm))

            elements.append(ListFlowable(
                [
                    ListItem(Paragraph(
                        'Verbinden Sie sich mit dem WLAN-Netzwerk (z.B. "net2otto", "net2wind"...)', styles['Text']), value='circle'),
                    ListItem(Paragraph(
                        'Öffnen Sie ihren Webbrowser (Firefox, Chrome, Internet Explorer...)', styles['Text']), value='circle'),
                    ListItem(
                        Paragraph('Öffnen Sie eine beliebige Website', styles['Text']), value='circle'),
                    ListItem(
                        Paragraph('Die folgende Seite wird angezeigt:', styles['Text']), value='circle')
                ],
                style=styles['list_default']
            ))

            elements.append(Spacer(0, 2 * mm))
            im = Image('example.png')
            im._restrictSize(50 * mm, 50 * mm)
            elements.append(im)
            elements.append(Spacer(0, 2 * mm))

            elements.append(ListFlowable(
                [
                    ListItem(Paragraph(
                        'Geben Sie ihren persönlichen Voucher Code ein (Groß-/Kleinschreibung ist wichtig)', styles['Text']), value='circle'),
                    ListItem(Paragraph('Klicken Sie auf "Submit"',
                                       styles['Text']), value='circle'),
                    ListItem(Paragraph(
                        'Die Internetverbindung funktioniert jetzt.', styles['Text']), value='circle')
                ],
                style=styles['list_default']
            ))

            elements.append(Spacer(0, 10 * mm))
            elements.append(Paragraph('''
                <b>Geben Sie den Voucher Code nicht weiter! Sie können das Internet 
                nicht mehr normal Nutzen, falls jemand anderes Ihren Voucher Code kennt!</b>
            ''', styles["Text"]))
            elements.append(Spacer(0,  5 * mm))
            elements.append(Paragraph('''
                Sie können den Voucher Code für mehrere Geräte benutzen, allerdings nur für
                maximal ein Gerät gleichzeitig.
            ''', styles["Text"]))
            elements.append(Spacer(0,  5 * mm))
            elements.append(Paragraph('''
                <b>Erinnern Sie sich immer daran</b>, dass der Internetverkehr vom
                Internetanbieter protokolliert wird. Sie sind verantwortlich für jeglichen
                Missbrauch. Verstöße werden nach deutschem Gesetz verfolgt.
            ''', styles["Text"]))
            elements.append(PageBreak())

        doc.build(elements, onFirstPage=self._header_footer,
                  onLaterPages=self._header_footer)


if __name__ == '__main__':
    rollName = 'vouchers_tatdf_roll20'
    vouchers = []
    with open(rollName + '.csv', newline='') as rollFile:
        roll = csv.reader(rollFile, delimiter=';', quotechar='"')
        vouchers = list(filter(lambda voucher: not voucher[0].startswith('#'), roll))
        vouchers = [voucher[0].strip() for voucher in vouchers]

    buffer = BytesIO()

    report = VoucherPrint(buffer, vouchers)
    pdf = report.print_users()
    buffer.seek(0)

    with open(rollName + '.pdf', 'wb') as f:
        f.write(buffer.read())
