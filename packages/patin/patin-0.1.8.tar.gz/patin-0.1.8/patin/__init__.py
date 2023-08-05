# -*- encoding: utf-8 -*-
import simplegui
from PyQt4 import QtCore
from PyQt4 import QtGui
import os
import utils
import syntax
import patin_version
from ui import recursos_rc
from simplegui.console import console_widget
import programas

class Ventana(simplegui.Base):
    programa_actual = None

    def __init__(self):
        simplegui.Base.__init__(self, utils.obtener_ruta("ui/untitled.ui"))
        self.view.manual.setUrl(QtCore.QUrl(utils.obtener_ruta("documentacion/index.html")))
        self.cargar_programa(utils.obtener_ruta("mis_programas/holamundo.py"))

        if not os.path.exists(utils.obtener_ruta("documentacion/index.html")):
            simplegui.mensajes.cuidado("No se encuentra la documentacion de patin, por favor ejecuta el comando 'make docs' desde consola para resolver este problema.") 

        # Administra la vista de programas
        self.programas = programas.Programas(self, self.view.programas)

        # Administra la vista de manual
        self.c = controlador.Controlador()
        self.c.definir_ventana(self)
        frame = self.view.manual.page().mainFrame()
        senal = QtCore.SIGNAL("javaScriptWindowObjectCleared()")
        frame.connect(frame, senal, self.vincular_javascript) 
        # ^^^ llevar a otro archivo ^^^

        self.avisar(u"Bienvenido a patín versión: " + patin_version.VERSION)
        self.view.closeEvent = self.cerrar_aplicacion
        self.view.editor.setTabStopWidth(20)

    def vincular_javascript(self):
        self.view.manual.page().mainFrame().addToJavaScriptWindowObject("c", self.c)

    def cargar_consola(self):
        """Toma el codigo del editor, lo ejecuta y muestra la consola interactiva."""

        variables = {'patin': self}
        consola = console_widget.ConsoleWidget(variables, None)
        self.view.consola = consola

        codigo = self.view.editor.document().toPlainText()
        self.view.resultado.hide()

        if 'pilas.iniciar' in codigo:
            codigo = codigo.replace('pilas.iniciar()', """pilas.iniciar(usar_motor='qtsugargl', ancho=640, alto=302, pantalla_completa=True)\npatin.reemplazar(patin.view.resultado, pilas.mundo.motor.widget, 1, 0, 1, 2)\npatin.view.consola.ventana = pilas.mundo.motor.widget\n
            """)
            # solo muesta la ventana de resultado si usa pilas.
            consola.execute(str(codigo))
            self.view.consola.ventana.setMinimumWidth(640)
            self.view.consola.ventana.setMaximumWidth(640)
            self.view.consola.ventana.setMinimumHeight(302)
            self.view.consola.ventana.setMaximumHeight(302)

            self.view.resultado.show()
        else:
            consola.execute(str(codigo))

        self.reemplazar(self.view.interprete, consola, 2, 0, 1, 2)

    def on_terminar__clicked(self):
        self.mostrar_editor()

    def mostrar_editor(self):
        """Muestra el editor para modificar un programa."""
        self.view.stack.setCurrentIndex(0)
        self.view.editor.setFocus()

    def on_ejecutar__clicked(self):
        """Intenta ejecutar el código del editor.

        Este método se llama cuando se pulsa al botón ejecutar. A partir
        de ese momento se trata de ir al modo ejecución, cambiando
        la pestaña actual y mostrando un intérprete interactivo.
        """
        self.guardar_programa()

        # TODO: evaluar el codigo de alguna manera para encontrar
        #       errores antes de ejecutar

        self.mostrar_consola_interactiva()
        self.avisar("Ejecutando el programa")

    def cerrar_aplicacion(self, evento):
        self.programas.terminar()

    def mostrar_consola_interactiva(self):
        self.cargar_consola()
        self.view.consola.setFocus()

        self.view.stack.setCurrentIndex(1)

    def _ejecutar(self, contenido):
        exec(str(contenido))

    def _cargar_programas(self):
        self.view.programas.setUrl(QtCore.QUrl(self.programas.obtener_url()))

    def on_tabWidget__currentChanged(self):
        if self.view.tabWidget.currentIndex() == 1:
            self._cargar_programas()

    '''
    def on_programas__linkClicked(self, param):
        self.avisar("AAAAAAAAAAAAA")

    def on_programas__urlChanged(self, param):
        """Se ejecuta cuando se seleccionar un programa de la lista.

        Los programas se almacenan en el directorio 'programas', asi
        que este metodo se encarga de conocer el link en donde se ha
        pulsado y simplemente lo carga en el panel de la izquierda.
        """

        path = str(param.toString())

        if '#' in path:
            indice = path.index('#')
            elemento = path[indice + 1:]

            if elemento == 'crear':
                nombre = simplegui.mensajes.ingresar("Creando...", u"¿Cómo se llamará el programa?")
                nombre = str(nombre)

                if nombre:
                    self.crear_programa(nombre)
                    self.cargar_programa(utils.obtener_ruta("mis_programas/" + nombre))
                    self.mostrar_editor()
                    self.avisar("Creando el programa {0}".format(nombre))
            
                self._cargar_programas()

            else:
                self.cargar_programa(utils.obtener_ruta("mis_programas/" + elemento))
                self.mostrar_editor()
                self.avisar("Cargando el programa '{0}'".format(elemento))
    '''

    def crear_programa(self, nombre):
        archivo = open(utils.obtener_ruta("mis_programas/" + nombre), "wt")
        archivo.close()

    def on_tipografia__currentIndexChanged(self, indice):
        """Cambia el tamaño de la tipografia."""
        tamanos = {
                    0: 11,
                    1: 15,
                    2: 20,
                  }

        font = self.view.editor.font()
        font.setPointSize(tamanos[indice])
        self.view.editor.setFont(font)
        self.view.consola.setFont(font)

    def cargar_programa(self, nombre):
        """Carga el código de un programa dentro del editor."""

        nombre = str(nombre)
        self.programa_actual = nombre
        base =  utils.obtener_ruta("mis_programas")
        path = os.path.join(base, nombre)
        contenido = utils.obtener_contenido_del_archivo(path)
        self.view.editor.setPlainText(contenido)

        # Se aplica el coloreado de sintaxis
        syntax.PythonHighlighter(self.view.editor.document())

    def crear_un_nuevo_programa(self):
        nombre = simplegui.mensajes.ingresar("Creando...", u"¿Cómo se llamará el programa?")
        nombre = str(nombre)

        if nombre:
            self.crear_programa(nombre)
            self.cargar_programa(utils.obtener_ruta("mis_programas/" + nombre))
            self.mostrar_editor()
            self.avisar("Creando el programa {0}".format(nombre))
    
            self._cargar_programas()
            self.mostrar_programas()

    def mostrar_programas(self):
        self.view.tabWidget.setCurrentIndex(1)

    def guardar_programa(self):
        "Guarda en disco el programa actual."
        path = os.path.join(utils.obtener_ruta("mis_programas"), self.programa_actual)
        contenido = self.view.editor.document().toPlainText()
        utils.guardar_contenido_en_el_archivo(path, contenido)


    def avisar(self, mensaje):
        "Muestra un mensaje en la barra de esta de la ventana."
        self.view.statusbar.showMessage(mensaje)

    def crear_programa_temporal(self, programa):
        self.cargar_programa('temporal')
        self.view.editor.setPlainText(programa)

        
def iniciar():
    simplegui.iniciar()
    ventana = Ventana()
    simplegui.ejecutar()
