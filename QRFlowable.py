from reportlab.platypus import Flowable
from reportlab.graphics.barcode import qr
from reportlab.graphics import renderPDF
from reportlab.graphics.shapes import Drawing
from reportlab.lib.units import mm


class QRFlowable(Flowable):
    def __init__(self, qr_value):
        Flowable.__init__(self)
        self.width = 40 * mm
        self.height = 40 * mm
        self.hAlign = 'RIGHT'
        self.qr_value = qr_value

    def draw(self):
        qr_code = qr.QrCodeWidget(self.qr_value)
        bounds = qr_code.getBounds()
        qr_width = bounds[2] - bounds[0]
        qr_height = bounds[3] - bounds[1]

        d = Drawing(self.width, self.height, transform=[
                    self.width/qr_width, 0, 0, self.height/qr_height, 0, 0])
        d.add(qr_code)
        renderPDF.draw(d, self.canv, 0, 0)
