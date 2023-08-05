# -*- encoding: utf-8 -*-

from pyactiveresource.activeresource import ActiveResource

class Issue(ActiveResource):
    _site = None
    _user = None
    _password = None

class Projects(ActiveResource):
    _site = None
    _user = None
    _password = None

def listar_proyectos(url, user, password, current_project):
    Projects._site = url
    Projects._user = user
    Projects._password = password

    proyectos = Projects.find()                                                      
    nombres_de_proyectos = [p.name for p in proyectos]

    for nombre in nombres_de_proyectos:
        if nombre == current_project:
            print "*", nombre
        else:
            print " ", nombre

    if current_project not in nombres_de_proyectos:
        print "CUIDADO, el nombre de proyecto configurado es incorrecto..."
        print "Ejecute el comando `li -e` para configurar la aplicación."


def obtener_id_proyecto(url, user, password, nombre_del_proyecto):
    Projects._site = url
    Projects._user = user
    Projects._password = password

    # TODO: buscar una forma mas eficiente de encontrar el id de proyecto.
    proyectos = Projects.find()
    proyecto = [p for p in proyectos if p.name == nombre_del_proyecto]
    
    if proyecto:
        return proyecto[0].id


def listar_issues(url, user, password, nombre_del_proyecto):
    Issue._site = url
    Issue._user = user
    Issue._password = password

    identificar_de_proyecto = obtener_id_proyecto(url, user, password, nombre_del_proyecto)
    issues = Issue.find(project_id=identificar_de_proyecto)
    issues = [(i.id, i.subject, i.description) for i in issues]

    for (id, asunto, description) in issues:
        print u"#{0} - {1}".format(id, asunto)

def crear_issue(url, user, password, nombre_del_proyecto, asunto, descripcion):
    Issue._site = url
    Issue._user = user
    Issue._password = password

    nuevo = Issue()
    nuevo.subject = asunto
    nuevo.description = descripcion
    nuevo.project_id = obtener_id_proyecto(url, user, password, nombre_del_proyecto)
    nuevo.save()

    print "Bug #%s: '%s' creado dentro del proyecto '%s'." %(nuevo.id, asunto, nombre_del_proyecto)
