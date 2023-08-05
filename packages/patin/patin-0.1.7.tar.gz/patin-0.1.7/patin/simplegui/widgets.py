from PyQt4 import QtGui

class Boton(QtGui.QPushButton):

    def __init__(self, parent):
        QtGui.QPushButton.__init__(self, parent)
        self.setText("H")

class Ventana(QtGui.QMainWindow):

    def __init__(self):
        QtGui.QMainWindow.__init__(self)

class Lista(QtGui.QListWidget):

    def __init__(self, parent, elementos=[]):
        QtGui.QListWidget.__init__(self, parent)
        self.definir_elementos(elementos)

    def definir_elementos(self, elementos):
        for e in elementos:
            self.addItem(str(e))
