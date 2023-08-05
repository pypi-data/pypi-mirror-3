# -*- encoding: utf-8 -*-
import os
import sys
import json
import ws
import codecs
import pyactiveresource

from optparse import OptionParser

class Configuracion:
    """Representa todos los parametros de configuración del
    programa.

    La configuración se genera automáticamente si no existe
    cuando se lanza el programa por primera vez.
    """

    def __init__(self):
        self.path = os.path.expanduser('~/.lissues')

        if not os.path.exists(self.path):
            self._crear_configuracion_inicial(self.path)

        self._cargar_configuracion(self.path)


    def _crear_configuracion_inicial(self, path):
        archivo = open(path, "wt")
        base_config = {
                        'url': 'http://192.168.1.108:8080/redmine',
                        'user': 'hugoruscitti',
                        'password': '123456',
                        'current_project': '????',
                      }
        json.dump(base_config, archivo)
        archivo.close()
        print "Creando el archivo de configuración '%s'..." %(path)

    def _cargar_configuracion(self, path):
        archivo = open(path, "rt")
        self.parametros = json.load(archivo)
        archivo.close()

def procesar_argumentos():
    """Analiza y procesa los argumentos para que sean mas sencillo leerlos.

    El resultado es esta función es un objeto al que se le puede consultar
    directamente el comando que se ha invocado, por ejemplo:
    
        >>> resultado = procesar_argumentos()
        >>> print resultado.proyectos
    """
    analizador = OptionParser()

    analizador.add_option("-p", "--projects", dest="proyectos",
        action="store_true", default=False,
        help="Muestra el listado de todos los proyectos en redmine.")
    
    analizador.add_option("-i", "--issues", dest="issues",
        action="store_true", default=False,
        help="Lista todos los issues del proyecto indicado por current_project.")
    
    analizador.add_option("-e", "--edit", dest="editar",
        action="store_true", default=False,
        help="Abre un editor para cambiar parametros de configuracion.")

    analizador.add_option("-c", "--crear", dest="crear",
        action="store_true", default=False,
        help="Permite crear un nuevo issue dentro del proyecto actual.")

    analizador.add_option("-b", "--batch", dest="batch",
        action="store_true", default=False,
        help="Realiza una importacion masiva desde un archivo csv.")

    (opciones, argumentos) = analizador.parse_args()
    return opciones

def issues(configuracion):
    """Emite un listado de todos los bugs del proyecto 'current_project'."""

    if configuracion.parametros['current_project'] == '????':
        print "Cuidado, tienes que configurar 'current_project' para indicar el proyecto, "
        print "usá el comando 'li -p' antes de continuar."
        return

    url = configuracion.parametros['url']
    user = configuracion.parametros['user']
    password = configuracion.parametros['password']
    project = configuracion.parametros['current_project']
    ws.listar_issues(url, user, password, project)

def projects(configuracion):
    """Emite un listado de todos los proyectos conocidos."""
    url = configuracion.parametros['url']
    user = configuracion.parametros['user']
    password = configuracion.parametros['password']
    project = configuracion.parametros['current_project']
    ws.listar_proyectos(url, user, password, project)

def editar(configuracion):
    """Invoca al editor de sistema para que se pueda configurar la aplicación."""
    os.system("editor %s" %configuracion.path)

def crear(configuracion):
    """Comando que se invoca al crear un bug."""
    url = configuracion.parametros['url']
    user = configuracion.parametros['user']
    password = configuracion.parametros['password']
    project = configuracion.parametros['current_project']

    if len(sys.argv) != 4:
        print "ERROR, número inválido de argumentos."
        print "tienes que indicar el asunto y la descripción del issue. Por ejemplo:"
        print '   li -c "se ven ids repetidos" "en la pantalla de acceso ..."'
    else:
        ws.crear_issue(url, user, password, project, sys.argv[2], sys.argv[3])

def es_archivo_csv_correcto(archivo):
    """Analiza si un archivo csv cumple teniendo solo dos columnas.
    
    Retorna True si el archivo es correcto o False si tiene errores.
    """
    sin_errores = True

    tmp = codecs.open(archivo, 'rt')

    for (index, linea) in enumerate(tmp.readlines()):
        if not ';' in linea:
            print "Error: la linea %d no tiene como separador el caracter ;" %(index +1)
        elif linea.count(';') != 1:
            print "Error: existe mas de un separador en la linea %d" %(index +1)

    tmp.close()
    return sin_errores

def importar_batch(configuracion):
    """Comando que se invoca junto a un archivo de texto cvs para importar muchos issues juntos."""
    url = configuracion.parametros['url']
    user = configuracion.parametros['user']
    password = configuracion.parametros['password']
    project = configuracion.parametros['current_project']

    if len(sys.argv) != 3:
        print "Tienes que indicar el nombre del archivo csv."
        print 'Por ejemplo: '
        print '   li -b issues.csv'
    else:
        if os.path.exists(sys.argv[2]):
            if es_archivo_csv_correcto(sys.argv[2]):
                archivo = codecs.open(sys.argv[2], 'rt')

                for linea in archivo.readlines():
                    asunto, descripcion = tuple(linea.split(';'))
                    ws.crear_issue(url, user, password, project, asunto, descripcion)

                archivo.close()
        else:
            print "El archivo indicando no existe..."

def main():
    "Programa principal: obtiene los argumentos de consola e invoca comandos."
    configuracion = Configuracion()
    opciones = procesar_argumentos()

    try:
        if opciones.proyectos:
            projects(configuracion)
        elif opciones.issues:
            issues(configuracion)
        elif opciones.editar:
            editar(configuracion)
        elif opciones.crear:
            crear(configuracion)
        elif opciones.batch:
            importar_batch(configuracion)
        else:
            print "Tienes que indicar al menos un parámetro, o usá --help."
    except pyactiveresource.connection.Error, e:
        if "Unauthorized" in str(e):
            print "ERROR, el usuario o constraseña son inválidos."
        elif "Not Found" in str(e):
            print "ERROR, no se encuentra la ruta al proyecto, ¿Está bien configurado el nombre de proyecto?."
        else:
            print "ERROR, no se puede conectar al servidor:", e[1]

        print "use el comando `li -e` para configurar el programa."

