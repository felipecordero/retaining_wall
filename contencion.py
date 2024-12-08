import sys
#import v
from PyQt5 import QtCore, QtGui, QtWidgets
from interfaz_murocontencion2 import Ui_MainWindow
from dibujarmuro import MuroScene
from flexvigas import flexion
from math import radians as rad
from math import cos, sin
import math
from PyQt5.QtWidgets import QGraphicsRectItem as RectItem
from PyQt5.QtWidgets import QGraphicsPolygonItem as PoligonItem
from PyQt5.QtCore import QPointF
#import qdarkstyle

from PyQt5.QtGui import QPen

pen = QPen()
pen.setWidth(0)

# variables globales
font = QtGui.QFont("Consolas", 10, QtGui.QFont.Normal)
flagIgnoreTransform = QtWidgets.QGraphicsItem.GraphicsItemFlags(QtWidgets.QGraphicsItem.ItemIgnoresTransformations)


inputs = []
[inputs.append(i + "Input") for i in ["e", "hm", "hf", "hd", "l1", "l2", "beta", "d",
                                      "kh", "kv", "phi", "mu", "qsc",
                                      "rec","fc","fy"]]

outputs = []
[outputs.append(i) for i in ["wMuro", "wTierra", "mResistente", "mVolcante",
                             "eActivo", "eSismo", "roce", "ePasivo",
                             "fsPPSCDout","fsPPSCVout", "fsPPSISDout", "fsPPSISVout"]]

class MuroContencion(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self):
        super(MuroContencion, self).__init__()
        self.setupUi(self)
        # pasar la escena al view del muro
        self.muroScene = MuroScene(self)
        self.muroView.setScene(self.muroScene)
#        self.muroView.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
        # agregar a la escena los poligonos con los diagramas de carga
        self.eat = PoligonItem()
        self.eat.setPen(pen)
        self.escr = RectItem()
        self.escr.setPen(pen)
        self.esist = PoligonItem()
        self.esist.setPen(pen)
        self.fundTensionesEst = RectItem()
        self.fundTensionesEst.setPen(pen)
        self.fundTensionesSis = RectItem()
        self.fundTensionesSis.setPen(pen)
        self.pLevEst = QtWidgets.QGraphicsSimpleTextItem()
        self.pLevSis = QtWidgets.QGraphicsSimpleTextItem()
        [self.muroScene.addItem(self.__dict__[i]) for i in ["eat","escr","esist"]]
        # agregar a la escena los textos con los diagramas de carga
        self.unidades = QtWidgets.QGraphicsSimpleTextItem()
        self.unidades.setFont(font)
        self.unidades.setFlags(flagIgnoreTransform)
        self.tea = QtWidgets.QGraphicsSimpleTextItem()
        self.tea.setFont(font)
        self.tea.setFlags(flagIgnoreTransform)
        self.tesc = QtWidgets.QGraphicsSimpleTextItem()
        self.tesc.setFont(font)
        self.tesc.setFlags(flagIgnoreTransform)
        self.tesis = QtWidgets.QGraphicsSimpleTextItem()
        self.tesis.setFont(font)
        self.tesis.setFlags(flagIgnoreTransform)
        #[self.__dict__[i].scale(1,-1) for i in ["tea","tesc","tesis","unidades"]]
        [self.muroScene.addItem(self.__dict__[i]) for i in ["tea","tesc","tesis","unidades"]]
        # continuando
        self.eActivo = self.ePasivo = self.eSismo = self.eSC = 0.0
        self.bActivo = self.bPasivo = self.bSismo = self.bSC = 0.0
        self.mActivo = self.mPasivo = self.mSismo = self.mSC = 0.0
        self.fsPPSCD = self.fsPPSCV = self.fsPPSISD = self.fsPPSISV = 0.0
        self.kae = 0.0
        self.ka = 0.0
        self.omegaMuro = 0.0
        self.sPPSC1 = self.sPPSC2 = self.sPPSIS1 = self.sPPSIS2 = 0.0
        self.mMuro = self.mTierra = 0.0
        self.te = QtWidgets.QGraphicsPolygonItem()
        self.te.setPen(pen)
        self.ts = QtWidgets.QGraphicsPolygonItem()
        self.ts.setPen(pen)
        self.tetext1 = QtWidgets.QGraphicsSimpleTextItem()
        self.tetext2= QtWidgets.QGraphicsSimpleTextItem()
        self.tstext1 = QtWidgets.QGraphicsSimpleTextItem()
        self.tstext2 = QtWidgets.QGraphicsSimpleTextItem()
        self.dibujarTensiones()
        self.aBase = 0.0
        self.fRoce = 0.0
        self.mResistente = 0.0
        self.mVocante = 0.0
        self.wSCresistente = 0.0
        self.mSCresistente = 0.0
        self.bSCresistente = 0.0
        # cambiar la posicion del view del muro
        self.muroView.scale(1, -1)
        # conectar los cambios
        [self.__dict__[i].valueChanged.connect(self.dibujar_muro) for i in inputs]
        [self.__dict__[i].valueChanged.connect(self.actualizar_resultados) for i in inputs]
        #asignar la actualizacion de resultados al boton calcular
        self.actionCalcular.triggered.connect(self.dibujar_muro)
        self.actionCalcular.triggered.connect(self.actualizar_resultados)
        self.kaInput.valueChanged.connect(self.actualizarKa)

    def dibujarTensiones(self):
        self.teView.setScene(QtWidgets.QGraphicsScene())
        self.tsView.setScene(QtWidgets.QGraphicsScene())
        self.teView.scene().addItem(self.te)
        self.tsView.scene().addItem(self.ts)
        self.teView.scene().addItem(self.tetext1)
        self.teView.scene().addItem(self.tetext2)
        self.tsView.scene().addItem(self.tstext1)
        self.tsView.scene().addItem(self.tstext2)
        self.teView.scene().addItem(self.fundTensionesEst)
        self.tsView.scene().addItem(self.fundTensionesSis)
        self.teView.scene().addItem(self.pLevEst)
        self.tsView.scene().addItem(self.pLevSis)

    def actualizarKa(self):
        self.calcularEactivo()
        self.calcularEsc()
        self.calcularAs()
        self.calcularMvolcante()
        self.calcularFS()
        self.calcularTensiones()
        self.dibujarEmpujes()
        self.ajustar()

    def actualizar_resultados(self):
##        self.wMuroOut.setText(str(self.muroScene.wMuro))
##        self.wTierraOut.setText(str(self.muroScene.wTierra))
        self.calcularKaeKa()
        self.calcularEactivo()
        self.calcularEsismo()
        self.calcularEsc()
        self.calcularMresistenteyRoce()
        self.calcularMvolcante()
        self.muroScene.cotas()
        self.calcularTensiones()
        self.calcularPasivo()
        self.calcularAs()
        self.calcularFS()
        self.dibujarEmpujes()
        self.ajustar()


    def dibujar_muro(self):
        [globals().__setitem__(i.strip("Input"), self.__dict__[i].value()) for i in inputs]
        MuroScene.dibujarmuro(self.muroScene, e, hm, hf, hd, l1, l2, beta, self.dInput.value())

    def ajustar(self):
        self.muroScene.setSceneRect(self.muroScene.itemsBoundingRect())
        self.muroView.fitInView(self.muroScene.sceneRect(), QtCore.Qt.KeepAspectRatio)
        #self.muroScene.brushTierra.setMatrix(self.muroView.matrix().inverted()[0].scale(0.001,0.001))
        self.teView.setSceneRect(self.teView.scene().itemsBoundingRect())
        self.tsView.setSceneRect(self.tsView.scene().itemsBoundingRect())
        self.teView.fitInView(self.teView.sceneRect(), QtCore.Qt.KeepAspectRatio)
        self.tsView.fitInView(self.tsView.sceneRect(), QtCore.Qt.KeepAspectRatio)

    def resizeEvent(self, event):
        self.ajustar()
        self.update()

    def calcularEactivo(self):
        ka = self.kaInput.value()
        d = self.dInput.value()
        h = self.hmInput.value() + self.hfInput.value()
        self.eActivo = 0.5 * ka * d * h ** 2
        self.bActivo = h / 3
        self.mActivo = self.eActivo * self.bActivo
        self.eActivoOut.setText(str(self.eActivo))

    def calcularEsismo(self):
        kae = self.kae
        d = self.dInput.value()
        h = self.muroScene.hEmpujes
        kv = self.kvInput.value()
        pae = 0.5 * kae * d * h ** 2 * (1 - kv)
        self.eSismo = pae - self.eActivo
        self.bSismo = 2 / 3 * h
        self.mSismo = self.eSismo * self.bSismo
        self.eSismoOut.setText(str(self.eSismo))

    def calcularEsc(self):
        ka = self.kaInput.value()
        h = self.muroScene.hEmpujes
        qsc = self.qscInput.value()
        self.eSC = ka * qsc * h
        self.bSC = h * 0.5
        self.mSC = self.eSC * self.bSC
        self.eScOut.setText(str(self.mSC))

    def calcularMresistenteyRoce(self):
        self.mMuro = self.muroScene.wMuro * self.muroScene.centroideMuro
        self.mTierra = self.muroScene.wTierra * self.muroScene.centroideTierra
        self.wSCresistente = self.qscInput.value() * self.muroScene.l2
        self.bSCresistente = self.muroScene.l1 + self.muroScene.e + self.muroScene.l2
        self.mSCresistente = self.wSCresistente * (self.bSCresistente - self.aBase / 2)
        self.mResistente = self.mMuro + self.mTierra + self.mSCresistente
        self.mResistenteOut.setText(str(self.mResistente))
        mu = self.muInput.value()
        n = self.muroScene.wMuro + self.muroScene.wTierra + self.wSCresistente
        self.fRoce = mu * n
        self.roceOut.setText(str(self.fRoce))

    def calcularMvolcante(self):
        m1 = self.mActivo + self.mSismo
        m2 = self.mActivo + self.mSC
        self.mVocante = max(m1,m2)
        self.mVocanteOut.setText(str(self.mVocante))

    def calcularFS(self):
        self.fsPPSCD = (self.fRoce + self.ePasivoEst) / (self.eActivo + self.eSC)
        self.fsPPSCV = self.mResistente / (self.mActivo + self.mSC)
        self.fsPPSISD = (self.fRoce + self.ePasivoSis - self.muInput.value() * self.wSCresistente)\
                         / (self.eActivo + self.eSismo)
        self.fsPPSISV = (self.mResistente - self.mSCresistente) / (self.mActivo + self.mSismo)
        output(self.fsPPSCD,self.fsPPSCDout)
        output(self.fsPPSCV,self.fsPPSCVout)
        output(self.fsPPSISD,self.fsPPSISDout)
        output(self.fsPPSISV,self.fsPPSISVout)

    def calcularTensiones(self):
        escala = 0.025*self.muroScene.sceneRect().width()
        self.aBase =  self.muroScene.l1 + self.muroScene.l2 + self.muroScene.e
        self.omegaMuro = self.aBase ** 2 / 6
        levanteEst = 0.0
        levanteSis = 0.0
        nPPSC = self.muroScene.wMuro + self.muroScene.wTierra + self.wSCresistente
        nPPSIS = self.muroScene.wMuro + self.muroScene.wTierra
        mPPSC = self.mActivo + self.mSC + \
                - self.muroScene.wMuro * (self.muroScene.centroideMuro - self.aBase / 2) + \
                - self.muroScene.wTierra * (self.muroScene.centroideTierra - self.aBase / 2)
        mPPSIS = self.mActivo + self.mSismo + \
                 - self.muroScene.wMuro * (self.muroScene.centroideMuro - self.aBase / 2) + \
                 - self.muroScene.wTierra * (self.muroScene.centroideTierra - self.aBase / 2)
        # calculo de las tensiones minimas:
        if mPPSC / nPPSC > self.aBase / 6:
            self.sPPSC1 = 2 / 3 * nPPSC / ((self.aBase / 2 - mPPSC / nPPSC) * self.aBase)
            self.sPPSC2 = 0.0
            levanteEst = 3 * mPPSC / nPPSC - self.aBase / 2
        else:
            self.sPPSC1 = nPPSC / self.aBase + mPPSC / self.omegaMuro
            self.sPPSC2 = nPPSC / self.aBase - mPPSC / self.omegaMuro

        if mPPSIS / nPPSIS > self.aBase / 6:
            self.sPPSIS1 = 2 / 3 * nPPSIS / ((self.aBase / 2 - mPPSIS / nPPSIS) * self.aBase)
            self.sPPSIS2 = 0.0
            levanteSis = 3 * mPPSIS / nPPSIS - self.aBase / 2
        else:
            self.sPPSIS1 = nPPSIS / self.aBase + mPPSIS / self.omegaMuro
            self.sPPSIS2 = nPPSIS / self.aBase - mPPSIS / self.omegaMuro
        # poligono para tensiones estaticas
        p1 = QtCore.QPointF(0.0, 0.0)
        p2 = QtCore.QPointF(0.0, self.sPPSC1)
        p3 = QtCore.QPointF((self.aBase - levanteEst) * 10, self.sPPSC2)
        p4 = QtCore.QPointF((self.aBase - levanteEst) * 10, 0.0)
        self.te.setPolygon(QtGui.QPolygonF([p1, p2, p3, p4]))
        # poligono para tensiones sismicas
        p1 = QtCore.QPointF(0.0, 0.0)
        p2 = QtCore.QPointF(0.0, self.sPPSIS1)
        p3 = QtCore.QPointF((self.aBase - levanteSis) * 10, self.sPPSIS2)
        p4 = QtCore.QPointF((self.aBase - levanteSis)* 10, 0.0)
        self.ts.setPolygon(QtGui.QPolygonF([p1, p2, p3, p4]))
        # agregar los textos con los valores de las tensiones
        self.tetext1.setText(str(round(self.sPPSC1,2)))
        self.tetext1.setPos(0.0, 0.0)
        self.tetext1.setScale(escala)
        self.tetext2.setText(str(round(self.sPPSC2,2)))
        self.tetext2.setPos((self.aBase - levanteEst) * 10, 0.0)
        self.tetext2.setScale(escala)
        # agregar los textos con los valores de las tensiones
        self.tstext1.setText(str(round(self.sPPSIS1,2)))
        self.tstext1.setPos(0.0, 0.0)
        self.tstext1.setScale(escala)
        self.tstext2.setText(str(round(self.sPPSIS2,2)))
        self.tstext2.setPos((self.aBase - levanteSis) * 10, 0.0)
        self.tstext2.setScale(escala)
        # agregar rectÃƒÆ’Ã‚Â¡ngulos simbolizando las fundaciones
        self.fundTensionesEst.setRect(0.0, - self.muroScene.hf * 10, self.aBase * 10, self.muroScene.hf * 10)
        self.fundTensionesSis.setRect(0.0, - self.muroScene.hf * 10, self.aBase * 10, self.muroScene.hf * 10)
        brush = QtGui.QBrush()
        brush.setColor(QtCore.Qt.gray)
        brush.setStyle(QtCore.Qt.SolidPattern)
        self.fundTensionesEst.setBrush(brush)
        self.fundTensionesSis.setBrush(brush)
        self.pLevEst.setText("% Lev = " + str(round(levanteEst / self.aBase * 100, 2) ) + "%")
        self.pLevSis.setText("% Lev = " + str(round(levanteSis / self.aBase * 100, 2) ) + "%")
        self.pLevEst.setScale(escala)
        self.pLevSis.setScale(escala)
        self.pLevEst.setPos(0.0, self.sPPSC1)
        self.pLevSis.setPos(0.0, self.sPPSIS1)

    # def wheelEvent(self, event):
        # factor = pow(1.2, event.delta() / 240.0)
        # if self.muroView.underMouse():
            # self.muroView.scale(factor, factor)
        # if self.teView.underMouse():
            # self.teView.scale(factor, factor)
        # brush = self.muroScene.brushTierra
        # matrix = self.muroView.matrix().inverted()[0]
        # brush.setMatrix(matrix)
        # self.muroScene.rectTierra.setBrush(brush)
        # event.accept()

    def calcularAs(self):
        hm = self.hmInput.value()
        ka = self.kaInput.value()
        sc = self.qscInput.value()
        d = self.dInput.value()
        mSC = ka * sc * hm * hm / 2
        mEa = ka * d * hm * hm / 2 * hm / 3
##        mEs = kh * d * hf * hm * hm / 2 + kh * d * hm * hm / 2 * 2 / 3 * hm
        mEs = self.mSismo
        mu = 1.5 * max(mSC + mEa, mEs + mEa)
        h = self.eInput.value() * 100
        b = 1.0 * 100
        rec = self.recInput.value()
        fc = self.fcInput.value()
        fy = self.fyInput.value()
        pu = 0.0
        a = str(flexion(h,b,rec,fc,fy,mu,pu)[0])
        self.asOut.setText(a)
        self.muOut.setText(str(mu))

    def calcularKaeKa(self):
        phi = rad(self.phiInput.value())
        theta = 0.0
        beta = rad(self.betaInput.value())
        kh = self.khInput.value()
        kv = self.kvInput.value()
        ten = math.atan(kh / (1 - kv))
        delta = phi / 2
        # calculo de Kae
        a = (cos(phi - theta - ten)) ** 2
        b = cos(ten) * (cos(theta) ** 2) * cos(delta + theta + ten)
        c = sin(delta + phi)*sin(phi - beta - ten)
        d = cos(delta + theta + ten) * cos(beta - theta)
        self.kae = a / (b * ( 1 + (c / d) ** 0.5) ** 2 )
        self.kaeOut.setText(str(self.kae))
        # calculo de Ka
        ten = 0.0
        a = (cos(phi - theta - ten)) ** 2
        b = cos(ten) * (cos(theta) ** 2) * cos(delta + theta + ten)
        c = sin(delta + phi)*sin(phi - beta - ten)
        d = cos(delta + theta + ten) * cos(beta - theta)
        self.ka = a / (b * ( 1 + (c / d) ** 0.5) ** 2 )
        self.kaInput.setValue(self.ka)

    def calcularPasivo(self):
        #fijar algunos valores
        self.hdInput.setMaximum(self.aBase)
        # parametros generales
        a = self.hdInput.value()
        phi = rad(self.phiInput.value())
        c  = a * math.tan(rad(45.0) + phi / 2)
        kp = (math.tan(rad(45.0) + phi / 2)) ** 2
        l = self.aBase
        # empuje estÃƒÆ’Ã‚Â¡tico
        a = self.sPPSC1
        b = self.sPPSC2
        s2 = 0.0
        if b < 0.0:
            s2 = a - c * (a + b) / l
        else:
            s2 = b +(l - c) / l * (a - b)
        sPasivo = c * (a + s2) / 2
        self.ePasivoEst = kp * sPasivo
        self.ePasivoEOut.setText(str(self.ePasivoEst))
        self.cOut.setText(str(c))
        # empuje sismico
        a = self.sPPSIS1
        b = self.sPPSIS2
        s2 = 0.0
        if b < 0.0:
            s2 = a - c * (a + b) / l
        else:
            s2 = b +(l - c) / l * (a - b)
        sPasivo = c * (a + s2) / 2
        self.ePasivoSis = kp * sPasivo
        self.ePasivoSOut.setText(str(self.ePasivoSis))
        self.kpOut.setValue(kp)
        self.muroScene.rectDiente.setRect(c, -hd, e, hd)

    def dibujarEmpujes(self):
        # escala = 0.002*self.muroScene.sceneRect().width()
        escala = 1
        # d = self.aBase + 0.75
        d = self.aBase
        h = self.muroScene.hf + self.muroScene.hm
        # empuje activo
        b = self.dInput.value()*self.kaInput.value()* h
        p1 = QPointF(d, 0.0)
        p2 = QPointF(d + b, 0.0)
        p3 = QPointF(d, h)
        self.eat.setPolygon(QtGui.QPolygonF([p1, p2, p3]))
        # agregar los textos
        self.tea.setText("qAct = " + str(round(b,2)))
        self.tea.setPos(d, 0.0)
        # self.tea.setScale(escala)
        # empuje sc
        d = d + max(b , self.tea.boundingRect().width()*escala) + 0.1
        d = 0
        b = self.eSC / h
        self.escr.setRect(d, 0.0, b, h)
        # agregar los textos
        self.tesc.setText("qSC = " + str(round(b,2)))
        d = 0
        self.tesc.setPos(d, 0.0)
        # self.tesc.setScale(escala)
        # empuje sismo:
        # d = d + b + 0.5
        d = d + b
        b = self.eSismo / h
        p1 = QPointF(d, 0.0)
        p2 = QPointF(d + b, h)
        p3 = QPointF(d, h)
        self.esist.setPolygon(QtGui.QPolygonF([p1, p2, p3]))
        # agregar los textos
        self.tesis.setText("qSis = " + str(round(b,2)))
        alto = self.tesis.boundingRect().height()*escala
        alto = 0
        d= 0
        self.tesis.setPos(d, h + alto)
        # self.tesis.setScale(escala)
        # texto con las unidades globales
        self.unidades.setText("[ton/m2]")
        self.unidades.setPos(self.aBase, h + alto)
        # self.unidades.setScale(escala)
        self.muroView.fitInView(self.muroView.sceneRect(), QtCore.Qt.KeepAspectRatio)

def output(texto,label):
    label.setText(str(texto))

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
#    dark_stylesheet = qdarkstyle.load_stylesheet_pyqt()
#    app.setStyleSheet(dark_stylesheet)
    ppal = MuroContencion()
    ppal.show()
    # calcular una vez todo:
    ppal.dibujar_muro()
    ppal.actualizar_resultados()
    ppal.actualizar_resultados()
    ppal.muroScene.brushTierra.setTransform(ppal.muroView.transform().inverted()[0])
    ppal.muroScene.rectTierra.setBrush(ppal.muroScene.brushTierra)
    ppal.muroView.fitInView(ppal.muroView.sceneRect(), QtCore.Qt.KeepAspectRatio)
    sys.exit(app.exec_())

