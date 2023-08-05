import os
import multiprocessing
import controlador

from PyQt4 import QtGui
from PyQt4 import QtCore

import bottle
from bottle import route, run, template, static_file
import utils

HOST = 'localhost'
PORT = 9991
MODO_SILENCIOSO = True  # si debe ocultar de la pantalla todos los pedidos.


@route('/')
def index():
    programas = os.listdir(utils.obtener_ruta("mis_programas"))
    return template("programas", programas=programas)

@route('/_static/<filename>')
def server_static(filename):
    return static_file(filename, root=utils.obtener_ruta("documentacion/_static"))


def ejecutar_servidor_web():
    bottle.TEMPLATE_PATH.append(utils.obtener_ruta('plantillas'))
    run(quiet=MODO_SILENCIOSO, host=HOST, port=PORT)


class Programas:

    def __init__(self, ventana, webview_de_programas):
        self.ventana = ventana
        self.webview = webview_de_programas

        self.c = controlador.Controlador()
        self.c.definir_ventana(ventana)

        frame = self.webview.page().mainFrame()
        senal = QtCore.SIGNAL("javaScriptWindowObjectCleared()")
        frame.connect(frame, senal, self.vincular_javascript) 

        self.iniciar()

    def iniciar(self):
        """Inicia el proceso bottle en segundo plano."""

        def ejecutar():
            ejecutar_servidor_web()

        self.proceso = multiprocessing.Process(target=ejecutar)
        self.proceso.start()

    def terminar(self):
        self.proceso.terminate()

    def vincular_javascript(self):
        self.webview.page().mainFrame().addToJavaScriptWindowObject("c", self.c)

    def obtener_url(self):
        return 'http://{0}:{1}/'.format(HOST, PORT)

if __name__ == '__main__':
    ejecutar_servidor_web()
