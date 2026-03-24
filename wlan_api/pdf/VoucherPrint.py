from reportlab.lib.pagesizes import A5
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak, Image, ListFlowable, ListItem, Spacer, Table, TableStyle
from wlan_api.pdf.QRFlowable import QRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle, ListStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import black
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.fonts import addMapping
from reportlab.lib.enums import TA_RIGHT


class VoucherPrint:

    def __init__(self, buffer, vouchers, validity_days):
        self.buffer = buffer
        self.vouchers = vouchers
        self.validity_days = validity_days
        self.pagesize = A5
        self.width, self.height = self.pagesize

        pdfmetrics.registerFont(
            TTFont("DejaVu Sans", "assets/fonts/DejaVuSans.ttf"))
        pdfmetrics.registerFont(
            TTFont("DejaVu Sans Bold", "assets/fonts/DejaVuSans-Bold.ttf"))
        addMapping('DejaVu Sans', 0, 0, 'DejaVu Sans')
        addMapping('DejaVu Sans', 1, 0, 'DejaVu Sans Bold')

        self.styles = getSampleStyleSheet()
        self.styles.add(ParagraphStyle(
            name='Text',
            fontName='DejaVu Sans',
            fontSize=8,
        ))
        self.styles.add(ParagraphStyle(
            name='Voucher_Subtitle',
            fontName='DejaVu Sans',
            fontSize=5,
            alignment=TA_RIGHT
        ))
        self.styles.add(ListStyle(
            'list_default',
            bulletType='bullet',
            start='circle',
            leftIndent=10,
            bulletOffsetY=0,
            bulletFontSize=7
        ))

    @staticmethod
    def _header_footer(canvas, doc):
        canvas.saveState()
        styles = getSampleStyleSheet()
        canvas.setFont("DejaVu Sans", 7)

        im = Image('assets/images/TaT-Logo.png')
        im._restrictSize(1000 * mm, 15 * mm)
        im.drawOn(canvas, doc.leftMargin + 5 * mm, doc.height - 20 * mm)

        # Footer
        canvas.drawRightString(doc.width + doc.rightMargin, 10 * mm,
                               'Falls Probleme auftreten, schreiben Sie eine E-Mail an wifi@tuerantuer.org')

        # Release the canvas
        canvas.restoreState()

    def print_table(self, elements, voucher):
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

    def print_vouchers(self):
        buffer = self.buffer
        styles = self.styles

        doc = SimpleDocTemplate(buffer,
                                rightMargin=15 * mm,
                                leftMargin=15 * mm,
                                topMargin=0 * mm,
                                bottomMargin=15 * mm,
                                pagesize=self.pagesize)

        # Our container for 'Flowable' objects
        elements = []

        for i, voucher in enumerate(self.vouchers):
            elements.append(Spacer(0, 10 * mm))
            elements.append(QRFlowable(voucher))

            self.print_table(elements, voucher)
            elements.append(Spacer(0, 10 * mm))

            elements.append(Paragraph('<b>So verbinden Sie sich mit dem Internet:</b>', styles["Text"]))
            elements.append(Spacer(0, 3 * mm))
            elements.append(ListFlowable(
                [
                    ListItem(Paragraph(
                        'Mit WLAN verbinden (z.B. "net2otto", "net2wind")', styles['Text']), value='circle'),
                    ListItem(Paragraph(
                        'Browser öffnen und eine beliebige Website aufrufen', styles['Text']), value='circle'),
                    ListItem(Paragraph(
                        'Voucher Code eingeben (Groß-/Kleinschreibung beachten) und auf „Submit" klicken', styles['Text']), value='circle'),
                ],
                style=styles['list_default']
            ))

            elements.append(Spacer(0, 5 * mm))
            elements.append(Paragraph(f'<b>Gültigkeit:</b> Dieser Voucher ist <b>{self.validity_days}</b> Tage gültig ab der ersten Nutzung.', styles["Text"]))
            elements.append(Spacer(0, 3 * mm))
            elements.append(Paragraph('<b>Sicherheit:</b> Voucher Code nicht weitergeben – sonst kann jemand anderes Ihr Internet nutzen.', styles["Text"]))
            elements.append(Spacer(0, 3 * mm))
            elements.append(Paragraph('<b>Mehrere Geräte:</b> Der Code funktioniert auf mehreren Geräten, aber immer nur einem gleichzeitig.', styles["Text"]))
            elements.append(Spacer(0, 3 * mm))
            elements.append(Paragraph('<b>Android 10+:</b> Zufällige MAC-Adresse für dieses WLAN ausschalten, sonst kann es beim Wiederverbinden mehrere Stunden dauern, bis das Internet wieder funktioniert.', styles["Text"]))
            elements.append(Spacer(0, 3 * mm))
            elements.append(Paragraph('<b>Rechtliches:</b> Der Internetverkehr wird protokolliert. Sie sind verantwortlich für die Nutzung.', styles["Text"]))
            elements.append(PageBreak())

        doc.build(elements, onFirstPage=self._header_footer,
                  onLaterPages=self._header_footer)
