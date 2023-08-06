import re
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.view import view_config, forbidden_view_config
from pyramid.security import remember, forget, authenticated_userid
from sapproject.models.usuario import *

@view_config(route_name='login_view', renderer='../templates/login.pt')
@forbidden_view_config(renderer='../templates/login.pt')
def login_view(request):
    """
    Muestra el login
    @param request: objeto que encapsula la peticion del cliente
    """   
    return {}

@view_config(route_name='login_check_json', renderer='json')
def login_check_json(request):
    """
    Trae los parametros ingreasados en el login y verifica que los datos ingresados en el login concuerden con algun 
    usuario registrado en el sistema
    @param request: objeto que encapsula la peticion del cliente
    @return: Retorna False si no fue encontrado ningun usuario con ese nick y ese password y True en caso contrario
             y un mensaje para el usuario
    """ 
    # Extraemos los datos ingresados desde la interfaz
    user_name     = request.params['name']
    user_password = request.params['password']
    # Ejecutamos en la base de datos 'SELECT * from usuarios where name == user_name and password == user_password'
    usuario = DBSession.query(Usuario).filter_by(nick=user_name,password=user_password).first()

    if usuario is None:
        # No existe el usuario user_name con password user_password
        return {'success' : False, 'message' : 'Login failed'}
    # Existe el usuario user_name con password user_password
    # Se generan encabezados de autenticacion para el usuario
    headers = remember(request, user_password)
    request._response_headerlist_set(headers) 
    # Se genera una respuesta para el usuario
    return {'success' : True, 'message' : 'Login successful'}
      
@view_config(route_name='logout_view')
def logout_view(request):
    """
    Devuelve la URL raiz
    @param request: objeto que encapsula la peticion del cliente
    """ 
    headers = forget(request)
    return HTTPFound(location=request.route_url('home_view'),headers=headers)
