from PyQt4 import QtGui

def cuidado(mensaje):
    QtGui.QMessageBox.warning(None, "Cuidado", mensaje)

def ingresar(titulo, texto):
    texto, ok = QtGui.QInputDialog.getText(None, titulo, texto)
    return texto
