# -*- encoding: utf-8 -*-
#
# Pin, una biblioteca para crear aplicaciones
# gráficas muy rápidamente.
#
import sys
import inspect

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import uic

import mensajes
import console

# Atrapa la señar CTRL+C
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

# hace global el estado de la aplicación.
app = None

def iniciar():
    global app
    app = QtGui.QApplication(sys.argv)

def ejecutar():
    global app
    sys.exit(app.exec_())


class Base(object):

    def __init__(self, ui, centrar=True, mostrar=True):
        self.view = uic.loadUi(ui)

        if centrar:
            self.centrar()

        if mostrar:
            self.view.show()

        self._conectar_senales_automaticamente()

    def obtener_widgets_con_nombre(self):
        """Retorna un diccionario con los nombres y referencias a los widgets.

        Por ejemplo, dado un widget:

            >>> ventana.obtener_widgets_con_nombre()
            {
                'splitter': <PyQt4.QtGui.QSplitter object at 0x90ccbfc>, 
                'centralwidget': <PyQt4.QtGui.QWidget object at 0x90cca04>,
            }

        """

        hijos = self.obtener_hijos(self.view)
        widgets = {}

        for h in hijos:
            if h.objectName():
                widgets[str(h.objectName())] = h

        return widgets

    def obtener_hijos(self, widget):
        """Obtiene los widgets hijos en forma de generador."""
        hijos = widget.children()

        for hijo in hijos:
            yield hijo
            for x in self.obtener_hijos(hijo):
                yield x

    def obtener_senales(self, widget):
        """Retorna una lista de todas las señales que entiende un widget."""
        for name in dir(widget):
            obj = getattr(widget, name)
            if inspect.isclass(obj) and issubclass(obj, QtCore.QObject):
                for name2 in dir(obj):
                    obj2 = getattr(obj, name2)

                    if isinstance(obj2, QtCore.pyqtSignal):
                        yield name, name2

    def _conectar_senales_automaticamente(self):
        """Se encarga de conectar senales a metodos usando nombres.

        Para que un metodo se conecte a una senal de un widget se
        debe escribir el nombre de metodo de una manera especial, el
        nombre de metodo debe comenzar con "on_", luego tener
        el nombre del widget y por ultimo dos guiones y el nombre
        de la senal.

        Por ejemplo, estos son algunos nombres validos::

            - on_close__clicked(self, senal):
            - on_mainWindow__destroyed(self, signal):
        """

        # recolecta todos los metodos que parezcan definir slots.
        candidatos = [metodo for metodo in dir(self) if metodo.startswith('on_')]
        widgets = self.obtener_widgets_con_nombre()

        for metodo in candidatos:
            widget, senal = metodo[3:].split("__")

            try:
                senal_obj = getattr(widgets[widget], senal)
                senal_obj.connect(getattr(self, metodo))
            except KeyError:
                print "Error, no se encuentra el widget de nombre:", widget
            except AttributeError:
                print "El widget '%s' no tiene una senal de nombre '%s'" %(widget, senal)

    def centrar(self):
        """Busca colocar la ventana principal en el centro del escritorio."""
        screen = QtGui.QDesktopWidget().screenGeometry()
        size =  self.view.geometry()
        self.view.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)

    def listar_widgets_y_senales(self):
        """Imprime en pantalla todos los widgets y sus respectivas señales."""
        widgets = self.obtener_widgets_con_nombre()

        for widget in widgets:
            print widget
            for s in self.obtener_senales(widgets[widget]):
                print "\t", s[1]


    def reemplazar(self, widget_anterior, widget_nuevo, fila=0, columna=0, filas_ocupa=1, columnas_ocupa=1):
        parent = widget_anterior.parent()
        parent.layout().addWidget(widget_nuevo, fila, columna, filas_ocupa, columnas_ocupa)
        widget_anterior.close()
