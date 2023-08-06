import re
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.view import view_config, forbidden_view_config
from pyramid.security import remember, forget, authenticated_userid, effective_principals
from sapproject.models.security import *
from sapproject.models.usuario import *
from sapproject.models.rol import *

@view_config(route_name='main_view', renderer='../templates/main.pt', permission='admin')
def main_view(request):
    """
    Muestra el main
    @param request: objeto que encapsula la peticion del cliente
    """     
    return {}

@view_config(route_name='home_view', renderer='../templates/index.pt')
def home_view(request):
    """
    Si la autenticacion es correcta le muestra la pantalla principal al usuario
    sino vuelve a mostrarle el login
    @param request: objeto que encapsula la peticion del cliente
    """ 
    if authenticated_userid(request):
        return HTTPFound(location=request.route_url('main_view'))
    return HTTPFound(location=request.route_url('login_view'))
    
@view_config(route_name='llenar_combo_proyecto_json', renderer='json')
def llenar_combo_proyecto(request):
    """
    Llena el combo correspondiente a los proyectos que le pertenecen a ese usuario
    mediante la relacion ProyectoUsuarioRoles
    @param request: objeto que encapsula la peticion del cliente
    @return: la cantidad de proyectos de ese Usuario y la lista de proyectos con su rol respectivo que tiene el usuario
    """ 
    userid  = authenticated_userid(request)
    usuario = DBSession.query(Usuario).filter_by(nick=userid).first()
    lista   = usuario.roles_x_proyecto
    if len(lista) == 0:
        return {'total':0, 'data':[]}
    else:
        data = []
        for rp in lista:
            item = {}
            item['idproyecto']   = rp.proyecto.id
            item['proyecto']     = rp.proyecto.nombre
            item['idrol']        = rp.rol.id
            item['rol']          = rp.rol.nombre
            item['proyecto_rol'] = '{0} ({1})'.format(rp.proyecto.nombre,rp.rol.nombre)
            data.append(item)
        return {'total':len(data), 'data':data}
