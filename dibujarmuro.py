from math import tan, radians

from PyQt5.QtWidgets import QGraphicsRectItem as RectItem
from PyQt5.QtWidgets import QGraphicsPolygonItem as PoligonItem
from PyQt5.QtWidgets import QGraphicsLineItem as LineItem
from PyQt5.QtWidgets import QGraphicsScene as Scene
from PyQt5.QtCore import QRectF
from PyQt5 import QtGui,QtCore, QtWidgets
from PyQt5.QtGui import QPen

pen = QPen()
pen.setWidth(0)
font = QtGui.QFont("Consolas", 10, QtGui.QFont.Normal)
flagIgnoreTransform = QtWidgets.QGraphicsItem.GraphicsItemFlags(QtWidgets.QGraphicsItem.ItemIgnoresTransformations)
#import verificar


class MuroView(QtWidgets.QGraphicsView):
    def __init__(self, parent=None):
        QtWidgets.QGraphicsView.__init__(self, parent)
        
    def wheelEvent(self, event):
#        super(PlantasView, self).wheelEvent(event)
        factor = pow(1.2, event.angleDelta().y() / 240.0)
        self.scale(factor, factor)
        event.accept()
    
    def showEvent(self, event):
        super(MuroView, self).showEvent(event)
        self.fitInView(self.sceneRect(), QtCore.Qt.KeepAspectRatio)

# atributos de la clase MuroScene:

rectangulos = ["rectMuro", "rectFund", "rectDiente"]
atributos_clase_muro = ["lineaTierra", "hEmpujes", "eActivo", "eSC", "eSismo", "areaMuro", "centroideMuro",
                        "wMuro", "areaTierra", "centroideTierra", "wTierra"]


class MuroScene(Scene):
#    verificar.verificar()
    def __init__(self, parent=None):
        Scene.__init__(self, parent)
        # iniciar las variables:
        for i in atributos_clase_muro:
            self.__dict__[i] = None
        # crear los rectangulos que representan el muro
        for i in rectangulos:
            self.__dict__[i] = RectItem()
            self.__dict__[i].setPen(pen)
            self.addItem(self.__dict__[i])
        self.rectTierra = PoligonItem()
        self.rectTierra.setPen(pen)
        self.lineaTierra = LineItem()
        self.lineaTierra.setPen(pen)
        self.addItem(self.lineaTierra)
        self.brush = QtGui.QBrush()
        self.brush.setColor(QtCore.Qt.gray)
        self.brush.setStyle(QtCore.Qt.SolidPattern)
        self.brushTierra = QtGui.QBrush()
        self.brushTierra.setColor(QtCore.Qt.green)
        self.brushTierra.setStyle(QtCore.Qt.DiagCrossPattern)
        self.rectTierra.setBrush(self.brushTierra)
        self.addItem(self.rectTierra)
        self.e = self.hm = self.hf =self.hd = self.l1 = self.l2 = self.l2 = \
        self.beta = self.dTierra = 0.0
        self.cotae = LineItem()
        self.cotae.setPen(pen)
        self.cotahm = LineItem()
        self.cotahm.setPen(pen)
        self.cotahf = LineItem()
        self.cotahf.setPen(pen)
        self.cotahd = LineItem()
        self.cotahd.setPen(pen)
        self.cotal1 = LineItem()
        self.cotal1.setPen(pen)
        self.cotal2 = LineItem()
        self.cotal2.setPen(pen)
        self.cotabeta = LineItem()
        self.cotabeta.setPen(pen)
        items = ["e", "hf", "hd", "l1", "l2", "beta", "hm"]
        [self.addItem(self.__dict__["cota" + i]) for i in items]
        #textos de las cotas
        self.cotaet = QtWidgets.QGraphicsSimpleTextItem()
        self.cotaet.setFont(font)
        self.cotaet.setFlags(flagIgnoreTransform)
        self.cotahmt = QtWidgets.QGraphicsSimpleTextItem()
        self.cotahmt.setFont(font)
        self.cotahmt.setFlags(flagIgnoreTransform)
        self.cotahft = QtWidgets.QGraphicsSimpleTextItem()
        self.cotahft.setFont(font)
        self.cotahft.setFlags(flagIgnoreTransform)
        self.cotahdt = QtWidgets.QGraphicsSimpleTextItem()
        self.cotahdt.setFont(font)
        self.cotahdt.setFlags(flagIgnoreTransform)
        self.cotal1t = QtWidgets.QGraphicsSimpleTextItem()
        self.cotal1t.setFont(font)
        self.cotal1t.setFlags(flagIgnoreTransform)
        self.cotal2t = QtWidgets.QGraphicsSimpleTextItem()
        self.cotal2t.setFont(font)
        self.cotal2t.setFlags(flagIgnoreTransform)
        self.cotabetat = QtWidgets.QGraphicsSimpleTextItem()
        self.cotabetat.setFont(font)
        self.cotabetat.setFlags(flagIgnoreTransform)
#        [self.__dict__["cota"+i+"t"].scale(1,-1) for i in items]
        [self.addItem(self.__dict__["cota"+i+"t"]) for i in items]
    # Funcion que dibuja el muro y la linea que muestra la inclinacion
    # del relleno
    def dibujarmuro(self, e, hm, hf, hd, l1, l2, beta, dTierra):
        # crear el rectangulo del muro, la fundacion y el diente
        self.e = e
        self.hm = hm
        self.hf = hf
        self.hd = hd
        self.l1 = l1
        self.l2 = l2
        self.beta = beta
        self.dTierra = dTierra
        self.rectMuro.setRect(l1, hf, e, hm)
        self.rectFund.setRect(0.0, 0.0, l1 + e + l2, hf)
        self.rectDiente.setRect(l1, -hd, e, hd)
        self.rectMuro.setBrush(self.brush)
        self.rectFund.setBrush(self.brush)
        self.rectDiente.setBrush(self.brush)
        # dibujar la linea que representa el relleno tras muro
        y = l2 * tan(radians(beta))
        self.lineaTierra.setLine(l1 + e, hf + hm, l1 + e + l2, hf + hm + y)
        # poligono para dibujar la tierra
        
        p1 = QtCore.QPointF(self.l1 + self.e, self.hf)
        p2 = QtCore.QPointF(self.l1 + self.e + self.l2, self.hf)
        p3 = QtCore.QPointF(self.l1 + self.e + self.l2, self.hf + self.hm + y)
        p4 = QtCore.QPointF(self.l1 + self.e, self.hf + self.hm)
        self.rectTierra.setPolygon(QtGui.QPolygonF([p1, p2, p3, p4]))
        # actualizar calculos
        self.calcular(l1, l2, hf, hm, e, y, dTierra)
        self.hEmpujes = hm + hf

    # Funcion para calcular el area de cada parte del muro. Tambien se recalcula el area total
    # y el centroide del muro completo.
    def calcular(self, l1, l2, hf, hm, e, y, dTierra):
        for i in rectangulos:
            self.__dict__[i].__dict__["area"] = area(self.__dict__[i])
            self.__dict__[i].__dict__["centroide"] = centroide(self.__dict__[i])
        self.areaMuro, self.centroideMuro = calculo_muro(self)
        self.wMuro = 2.5 * self.areaMuro
        self.areaTierra, self.centroideTierra = calculo_tierra(l1, l2, hf, hm, e, y)
        self.wTierra = dTierra * self.areaTierra
        self.parent().wMuroOut.setText(str(self.wMuro))
        self.parent().wTierraOut.setText(str(self.wTierra))

    def cotas(self):
        # escala = 0.002*self.sceneRect().width()
        escala = 1
        # cota de la parte superior del muro de contencion
        x1 = self.l1
        y1 = self.hf + self.hm + 0.1 * self.hm
        x2 = self.l1 + self.e
        y2 = y1
        self.cotae.setLine(x1,y1,x2,y2)
        self.cotaet.setText("e=" + str(round(self.e,2)))
        # self.cotaet.setScale(escala)
        # alto = self.cotaet.boundingRect().height()*escala
        alto = 0
        self.cotaet.setPos(x1, y1 + alto)
        self.cotaet.setToolTip("Este es el espesor del muro")
        # cota del muro
        x1 = -0.1 * self.l2
        y1 = self.hf
        x2 = x1
        y2 = self.hf + self.hm
        self.cotahm.setLine(x1,y1,x2,y2)
        self.cotahmt.setText("hm=" + str(round(self.hm,2)))
        # self.cotahmt.setScale(escala)
        ancho = self.cotahmt.boundingRect().width()*escala
        ancho = 0
        self.cotahmt.setPos(x1 , self.hf + self.hm / 2)
        # cota de l2
        x1 = self.l1 + self.e
        y1 =  - self.hd - self.hf
        x2 = x1 + self.l2
        y2 = y1
        self.cotal2.setLine(x1,y1,x2,y2)
        self.cotal2t.setText("L2=" + str(round(self.l2,2)))
        # self.cotal2t.setScale(escala)
        alto = self.cotal2.boundingRect().height()*escala
        alto = 0
        self.cotal2t.setPos(self.l1 + self.e + self.l2 / 2, y1 + alto)
        # cota l1
        x1 = 0.0
        y1 =  - self.hd - self.hf
        x2 = x1 + self.l1
        y2 = y1
        self.cotal1.setLine(x1,y1,x2,y2)
        self.cotal1t.setText("L1=" + str(round(self.l1,2)))
        # self.cotal1t.setScale(escala)
        alto = self.cotal1.boundingRect().height()*escala
        alto = 0
        self.cotal1t.setPos(x1, y1 + alto)
        # cota hf
        x1 = self.l1 + self.e + self.l2 + 0.1
        y1 = 0.0
        x2 = x1
        y2 = self.hf
        self.cotahf.setLine(x1,y1,x2,y2)
        self.cotahft.setText("hf="+str(round(self.hf,2)))
        # self.cotahft.setScale(escala)
        self.cotahft.setPos(x1 + 0.15 / 2 , self.hf)
        # cota hd
        x1 = -0.1 * self.l2
        y1 = - self.hd
        x2 = x1
        y2 = 0.0
        self.cotahd.setLine(x1,y1,x2,y2)
        self.cotahdt.setText("hd=" + str(round(self.hd,2)))
        # self.cotahdt.setScale(escala)
        ancho = self.cotahdt.boundingRect().width()*escala
        ancho = 0
        self.cotahdt.setPos(x1 - ancho, 0.0)

def area(self):
    return self.rect().height() * self.rect().width()


def centroide(self):
    return self.rect().center()


def calculo_tierra(l1, l2, hf, hm, e, y):
    area1 = l2 * hm
    area2 = l2 * y * 0.5
    centro1 = QRectF(l1 + e, hf, l2, hm).center().x()
    centro2 = 2 / 3 * QRectF(l1 + e, hf + hm, l2, y).center().x()
    return area1 + area2, (area1 * centro1 + area2 * centro2) / (area1 + area2)


def calculo_muro(self):
    areatotal = 0.0
    sumatoria = 0.0
    for i in rectangulos:
        areatotal = areatotal + self.__dict__[i].area
        sumatoria = sumatoria + self.__dict__[i].area * self.__dict__[i].centroide.x()
    return areatotal, sumatoria / areatotal
