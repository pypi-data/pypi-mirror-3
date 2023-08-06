import re
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.view import view_config, forbidden_view_config
from pyramid.security import remember, forget, authenticated_userid
from sapproject.models.rol import *
from sapproject.models.usuario import *
from sapproject.models.rolusuario import *

@view_config(route_name='crear_rol_json', renderer='json')
def crear_rol_json(request):
    """
    Nos permite traer los parametros que fueron cargados por el usuario
    y guardarlos en la base de datos.
    @param request: objeto que encapsula la peticion del cliente
    @return: True si la accion se realizo correctamente
    """ 
    nombre        = request.params['nombre']
    descripcion   = request.params['descripcion']
    #guardamos en la BD
    model         = Rol(nombre, descripcion)
    DBSession.add(model)

    return {'success' : True}

@view_config(route_name='modificar_rol_json', renderer='json')
def modificar_rol_json(request):
    """
    Nos permite traer los parametros que fueron modificados por el usuario
    y guardar los cambios en la base de datos.
    @param request: objeto que encapsula la peticion del cliente
    @return: True si la accion se realizo correctamente
    """ 
    id            = request.params['id']
    nombre        = request.params['nombre']
    descripcion   = request.params['descripcion']   
    # se modifica en la BD
    model         = Rol(nombre, descripcion)
    model.id      = id
    DBSession.merge(model)   
    return {'success' : True}

@view_config(route_name='consultar_rol_json', renderer='json')
def consultar_rol_json(request):
    """
    Nos permite traer los parametros de consulta(el filtro y el valor) y mostrar
    los roles que cumplen con la condicion del filtro.
    @param request: objeto que encapsula la peticion del cliente
    @return: si la accion se realizo correctamente
    """ 
    usuarios = None
    if 'filtro' in request.params:
        filtro    = request.params['filtro']
        valor     = request.params['valor']
        sentencia = 'SELECT * from Rol WHERE {0}=\'{1}\''.format(filtro,valor)
        roles  = DBSession.query(Rol).from_statement(sentencia).all()
    else:
        roles = DBSession.query(Rol).all()
    
    data = []
    for rol in roles:
        item = {}
        item['id'] = rol.id
        item['nombre'] = rol.nombre
        item['descripcion'] = rol.descripcion
        data.append(item)
    return {'success':True, 'data':data, 'total':len(data)}

@view_config(route_name='eliminar_rol_json', renderer='json')
def eliminar_rol_json(request):
    """
    Nos permite traer el id del rol a eliminar, eliminar las dependendcias
    del mismo con respecto a otras tablas y eliminar el registro de la base de datos.
    @param request: objeto que encapsula la peticion del cliente
    @return: True si la accion se realizo correctamente y False en caso contrario
    """ 

    id      = request.params['id']
    rol = DBSession.query(Rol).filter_by(id=id).first()
    if rol is None:
        return {'success':False}
    DBSession.delete(rol)
    return {'success' : True}

@view_config(route_name='consulta_asignar_roles_json', renderer='json')
def consulta_asignar_roles_json(request):
    """
    Nos permite traer todos los roles asignados y asignables a un usuario
    @param request: objeto que encapsula la peticion del cliente
    @return: True si la accion se realizo correctamente, la lista de roles asignados al usuario y la lista de roles asignables al usuario
    """
    def process_rol_list(list):
        """
        Serializa una lista de con los datos de los roles para enviarla al cliente
        @param list: lista de objectos Permiso obtenidas desde la BD
        @return: result lista procesada de roles
        """
        result = []
        for rol in list:
            item = [None,None,None,None]
            item[0] = rol.id
            item[1] = rol.nombre
            item[2] = rol.descripcion
            result.append(item)
        return result
    
    id_usuario = request.params['id']
    # Obtenemos la lista de roles que fueron asignados al usuario
    # Roles es de tipo RolUsuario[] por tanto es necesario extraer el 'rol' de la relacion
    roles_asignados = [x.rol for x in DBSession.query(Usuario).filter_by(id=id_usuario).first().roles]
    # Obtenemos la lista de roles que no fueron asignados al usuario
    roles_asignables = DBSession.query(Rol).from_statement('select * from Rol where id not in (select idrol from RolUsuario where idusuario=\'{0}\')'.format(id_usuario)).all()
    
    asignados  = process_rol_list(roles_asignados)
    asignables = process_rol_list(roles_asignables)

    return {'success':True, 'asignados':asignados, 'asignables':asignables}

@view_config(route_name='asignar_desasignar_rol_json', renderer='json')
def asignar_desasignar_rol_json(request):
    """
    Nos permite asignar/desasignar roles a un usuario
    @param request: objeto que encapsula la peticion del cliente
    @return: True si la accion se realizo correctamente
    """
    received   = eval(request.params['data'])
    # id del usuario a asignar/desasignar roles
    id_usuario = received['id_usuario']
    # ids de roles asignados
    data   = received['data']

    # obtenemos el usuario desde la BD
    usuario = DBSession.query(Usuario).filter_by(id=id_usuario).first()
    # eliminamos sus roles asignados anteriormente
    DBSession.query(RolUsuario).filter_by(idusuario=id_usuario).delete(synchronize_session=False)
    # actualizamos el usuario
    DBSession.refresh(usuario);
    # creamos una nueva lista de roles asignados
    for id_rol in data:
        usuario.roles.append(RolUsuario(id_rol, id_usuario))
    # guardamos los cambios
    DBSession.merge(usuario)
    
    return {'success':True}

@view_config(route_name='consulta_rol_x_usuario_json', renderer='json')
def consulta_rol_x_usuario_json(request):
    """
    Nos permite obtener la lista detallada de roles asignados a un usuario
    @param request: objeto que encapsula la peticion del cliente
    @return: True si la accion se realizo correctamente
    """
    id_usuario = request.params['id_usuario']
    usuario    = DBSession.query(Usuario).filter_by(id=id_usuario).first()
    data = []
    for rol in usuario.roles:
        item = {}
        item['id'] = rol.rol.id
        item['nombre'] = rol.rol.nombre
        item['descripcion'] = rol.rol.descripcion
        data.append(item)
    return {'success':True, 'data':data, 'total':len(data)}

