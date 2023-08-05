from PyQt4 import QtGui
from PyQt4 import QtCore

class Controlador(QtCore.QObject):
    """Representa el objeto que se expone para charlar con javascript."""

    def _nombre(self):
        return "unodostres"

    @QtCore.pyqtSlot(result=str)
    def saludar(self):
        return "hola mundo!!!"

    @QtCore.pyqtSlot(str, result=str)
    def cargar_programa(self, programa):
        self.ventana.cargar_programa(programa)
        return ""

    @QtCore.pyqtSlot(str)
    def crear_programa_temporal(self, programa):
        programa = str(programa)
        self.ventana.crear_programa_temporal(programa)

    @QtCore.pyqtSlot()
    def crear_un_nuevo_programa(self):
        self.ventana.crear_un_nuevo_programa()

    def definir_ventana(self, ventana):
        self.ventana = ventana

    nombre = QtCore.pyqtProperty(str, fget=_nombre)
