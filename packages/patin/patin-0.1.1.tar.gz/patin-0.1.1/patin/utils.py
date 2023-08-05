import os

def reemplazar_plantilla(archivo_origen, archivo_destino, busca, reemplaza):
    # Lee la plantilla
    origen = open(archivo_origen, "rt")
    contenido = origen.read()
    origen.close()

    # Reemplaza y graba
    destino = open(archivo_destino, "wt")
    contenido = contenido.replace(busca, reemplaza)
    destino.write(contenido)
    destino.close()
    
def obtener_contenido_del_archivo(nombre_del_archivo):
    archivo = open(nombre_del_archivo, "rt")
    contenido = archivo.read()
    archivo.close()
    return contenido

def guardar_contenido_en_el_archivo(nombre_del_archivo, contenido):
    archivo = open(nombre_del_archivo, "wt")
    archivo.write(contenido)
    archivo.close()

def obtener_ruta(ruta_relativa):
    "Obtiene una ruta absoluta a partir de una ruta relativa a este archivo."
    este_directorio = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(este_directorio, ruta_relativa)

