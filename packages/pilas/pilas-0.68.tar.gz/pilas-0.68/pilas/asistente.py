# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'asistente.ui'
#
# Created: Tue Feb 21 03:46:28 2012
#      by: PyQt4 UI code generator 4.8.5
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
import sys
import utils

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Dialog(object):

    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(500, 271)
        self.gridLayout_2 = QtGui.QGridLayout(Dialog)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.graphicsView = QtGui.QGraphicsView(Dialog)
        self.graphicsView.setObjectName(_fromUtf8("graphicsView"))
        self.gridLayout_2.addWidget(self.graphicsView, 0, 0, 1, 1)
        self.groupBox = QtGui.QGroupBox(Dialog)
        self.groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Opciones", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setText(QtGui.QApplication.translate("Dialog", "Aceleración:", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.comboBox = QtGui.QComboBox(self.groupBox)
        self.comboBox.setObjectName(_fromUtf8("comboBox"))
        self.comboBox.addItem(_fromUtf8(""))
        self.comboBox.setItemText(0, QtGui.QApplication.translate("Dialog", "Usar aceleración OpenGL", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox.addItem(_fromUtf8(""))
        self.comboBox.setItemText(1, QtGui.QApplication.translate("Dialog", "Sin aceleración", None, QtGui.QApplication.UnicodeUTF8))
        self.gridLayout.addWidget(self.comboBox, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "Pantalla completa:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.comboBox_2 = QtGui.QComboBox(self.groupBox)
        self.comboBox_2.setObjectName(_fromUtf8("comboBox_2"))
        self.comboBox_2.addItem(_fromUtf8(""))
        self.comboBox_2.setItemText(0, QtGui.QApplication.translate("Dialog", "Deshabilitar", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_2.addItem(_fromUtf8(""))
        self.comboBox_2.setItemText(1, QtGui.QApplication.translate("Dialog", "Habilitar", None, QtGui.QApplication.UnicodeUTF8))
        self.gridLayout.addWidget(self.comboBox_2, 1, 1, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox, 1, 0, 1, 1)
        self.line = QtGui.QFrame(Dialog)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.gridLayout_2.addWidget(self.line, 2, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))

        self.gridLayout_2.addWidget(self.buttonBox, 3, 0, 1, 1)
        self.label.setBuddy(self.comboBox)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), self.acepta)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        self.ha_aceptado = False

    def retranslateUi(self, Dialog):
        pass

    def acepta(self):
        self.ha_aceptado = True

    def obtener_seleccion(self):
        motor = ['qtgl', 'qt']
        modo = [False, True]

        i = self.comboBox.currentIndex()
        j = self.comboBox_2.currentIndex()

        return (motor[i], modo[j])

    def mostrar_imagen(self, ruta):
        escena = QtGui.QGraphicsScene()
        self.graphicsView.setScene(escena)
        pixmap = QtGui.QGraphicsPixmapItem(QtGui.QPixmap(ruta))
        escena.addItem(pixmap)


app = None

def salir():
    import sys
    sys.exit(0)

def ejecutar(imagen, titulo):
    global app

    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    Dialog.setWindowTitle(titulo)
    ui = Ui_Dialog()
    ui.setupUi(Dialog)

    if imagen:
        ruta_a_imagen = utils.obtener_ruta_al_recurso(imagen)
        ui.mostrar_imagen(ruta_a_imagen)

    Dialog.show()
    app.exec_()
    if not ui.ha_aceptado:
        salir()
    return ui.obtener_seleccion()
