from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from sqlalchemy import engine_from_config
from models.base import DBSession
from models.usuario import groupfinder
from models.rol import *
from views import *

def main(global_config, **settings):
    """ Metodo que define todas las rutas del sistema"""
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    authentication_policy = AuthTktAuthenticationPolicy('sosecret', callback=groupfinder)
    authorization_policy  = ACLAuthorizationPolicy()
    config = Configurator(settings=settings, root_factory='sapproject.models.security.rootFactory.RootFactory')
    config.set_authentication_policy(authentication_policy)
    config.set_authorization_policy(authorization_policy)
    config.add_static_view('static', 'static', cache_max_age=3600)
    # MAIN.PY
    config.add_route('home_view', '/')
    config.add_route('main_view', '/main')
    config.add_route('llenar_combo_proyecto_json', '/llenar_combo_proyecto')    
    # LOGIN.PY
    config.add_route('login_view', '/login')
    config.add_route('logout_view', '/logout')
    config.add_route('login_check_json','/login_check')
    # PERMISO.PY
    config.add_route('crear_permiso_json', '/crear_permiso')
    config.add_route('eliminar_permiso_json', '/eliminar_permiso')
    config.add_route('modificar_permiso_json', '/modificar_permiso')
    config.add_route('consulta_acciones_json', '/consulta_acciones')
    config.add_route('consultar_permiso_json', '/consultar_permiso')
    config.add_route('consulta_asignar_permisos_json', '/consulta_asignar_permisos')
    config.add_route('asignar_desasignar_permiso_json', '/asignar_desasignar_permiso')
    config.add_route('consulta_permiso_x_rol_json', '/consulta_permiso_x_rol')
    # USUARIO.PY
    config.add_route('crear_usuario_json', '/crear_usuario')
    config.add_route('eliminar_usuario_json', '/eliminar_usuario')
    config.add_route('modificar_usuario_json', '/modificar_usuario')    
    config.add_route('consultar_usuario_json', '/consultar_usuario')
    config.add_route('consultar_usuario_completo_json', '/consultar_usuario_completo')
    config.add_route('consulta_asignar_usuarios_json', '/consulta_asignar_usuarios')
    #PROYECTO.PY
    config.add_route('crear_proyecto_json', '/crear_proyecto')
    config.add_route('eliminar_proyecto_json', '/eliminar_proyecto')
    config.add_route('modificar_proyecto_json', '/modificar_proyecto')
    config.add_route('consultar_proyecto_json', '/consultar_proyecto')    
    config.add_route('asignar_usuario_rol_proyecto_json', 'asignar_usuario_rol_proyecto')
    config.add_route('desasignar_usuario_rol_proyecto_json', 'desasignar_usuario_rol_proyecto')
    #ROL.PY
    config.add_route('crear_rol_json', '/crear_rol')
    config.add_route('consultar_rol_json', '/consultar_rol')
    config.add_route('eliminar_rol_json', '/eliminar_rol')    
    config.add_route('modificar_rol_json', '/modificar_rol')
    config.add_route('consulta_asignar_roles_json', '/consulta_asignar_roles')
    config.add_route('asignar_desasignar_rol_json', '/asignar_desasignar_rol')
    config.add_route('consulta_rol_x_usuario_json','/consulta_rol_x_usuario')
    # ATRIBUTO.PY
    config.add_route('crear_atributo_json', '/crear_atributo')
    config.add_route('eliminar_atributo_json', '/eliminar_atributo')
    config.add_route('modificar_atributo_json', '/modificar_atributo')    
    config.add_route('consultar_atributo_json', '/consultar_atributo')
    config.add_route('consulta_asignar_atributos', '/consulta_asignar_atributos')
    config.add_route('asignar_desasignar_atributo', '/asignar_desasignar_atributo')
    config.add_route('consulta_atributo_x_tipoitem_json','/consulta_atributo_x_tipoitem')
    # TIPOITEM.PY
    config.add_route('crear_tipoitem_json', '/crear_tipoitem')
    config.add_route('eliminar_tipoitem_json', '/eliminar_tipoitem')
    config.add_route('modificar_tipoitem_json', '/modificar_tipoitem')
    config.add_route('consultar_tipoitem_json', '/consultar_tipoitem')
    config.add_route('consultar_tipoitem_fase_json','/consultar_tipoitem_fase')
    # FASE.PY
    config.add_route('crear_fase_json', '/crear_fase')
    config.add_route('eliminar_fase_json', '/eliminar_fase')
    config.add_route('modificar_fase_json', '/modificar_fase')
    config.add_route('consultar_fase_json', '/consultar_fase')
    config.add_route('consultar_fase_proyecto_json', '/consultar_fase_proyecto')
    # ITEM.PY
    config.add_route('crear_item_json', '/crear_item')
    config.add_route('consultar_item_json', '/consultar_item')
    config.add_route('eliminar_item_json', '/eliminar_item')
    config.add_route('modificar_item_json', '/modificar_item')
    config.add_route('consultar_campos_crear_item_json', '/consultar_campos_crear_item')
    config.add_route('consultar_campos_modificar_item_json', '/consultar_campos_modificar_item')
    config.scan()
    return config.make_wsgi_app() 
