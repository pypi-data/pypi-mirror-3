import re
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.view import view_config, forbidden_view_config
from pyramid.security import remember, forget, authenticated_userid
from sapproject.models.usuario import *
from sapproject.models.proyecto import *
from sapproject.models.proyectousuario import *

@view_config(route_name='crear_usuario_json', renderer='json')
def crear_usuario_json(request):
    """
    Nos permite traer los parametros que fueron cargados por el usuario
    y guardarlos en la base de datos.
    @param request: objeto que encapsula la peticion del cliente
    @return : True si la accion se realizo correctamente
    """     
    ci            = request.params['ci']
    nombres       = request.params['nombres']
    apellidos     = request.params['apellidos']
    fechanac      = request.params['fechanac']
    sexo          = request.params['sexo']
    nick          = request.params['nick']
    password      = request.params['password']
    email         = request.params['email']
    telefono      = request.params['telefono']
    direccion     = request.params['direccion']
    observaciones = request.params['observaciones']
    # se agrega a la BD
    model         = Usuario(ci, nombres, apellidos, nick, password, email, telefono, direccion, observaciones, sexo, fechanac)
    DBSession.add(model)
    return {'success' : True}

@view_config(route_name='modificar_usuario_json', renderer='json')
def modificar_usuario_json(request):
    """
    Nos permite traer los parametros que fueron modificados por el usuario
    y guardar los cambios en la base de datos.
    @param request: objeto que encapsula la peticion del cliente
    @return : True si la accion se realizo correctamente
    """ 
    id            = request.params['id']
    ci            = request.params['ci']
    nombres       = request.params['nombres']
    apellidos     = request.params['apellidos']
    fechanac      = request.params['fechanac']
    sexo          = request.params['sexo']
    nick          = request.params['nick']
    password      = request.params['password']
    email         = request.params['email']
    telefono      = request.params['telefono']
    direccion     = request.params['direccion']
    observaciones = request.params['observaciones']
    # se modifica en la BD
    model         = Usuario(ci, nombres, apellidos, nick, password, email, telefono, direccion, observaciones, sexo, fechanac)
    model.id      = id
    DBSession.merge(model)   
    return {'success' : True}


@view_config(route_name='consultar_usuario_json', renderer='json')
def consultar_usuario_json(request):
    """
    Nos permite traer los parametros de consulta(el filtro y el valor) y mostrar
    los usuarios que cumplen con la condicion del filtro.
    @param request: objeto que encapsula la peticion del cliente
    @return : si la accion se realizo correctamente
    """
    usuarios = None
    if 'filtro' in request.params:
        filtro    = request.params['filtro']
        valor     = request.params['valor']
        sentencia = 'SELECT * from Usuario WHERE {0}=\'{1}\''.format(filtro,valor)
        usuarios  = DBSession.query(Usuario).from_statement(sentencia).all()
    else:
        usuarios  = DBSession.query(Usuario).all()
    
    data = []
    for usuario in usuarios:
        item = {}
        item['id'] = usuario.id
        item['ci'] = usuario.ci
        item['nick'] = usuario.nick
        item['nombres'] = usuario.nombres
        item['apellidos'] = usuario.apellidos
        item['direccion'] = usuario.direccion
        item['email'] = usuario.email
        data.append(item)
    return {'success':True, 'data':data, 'total':len(data)}

@view_config(route_name='consultar_usuario_completo_json', renderer='json')
def consultar_usuario_completo_json(request):
    """
    Nos permite traer los parametros de consulta(el filtro y el valor) y mostrar los campos
    completos de los usuarios que cumplen con la condicion del filtro.
    @param request: objeto que encapsula la peticion del cliente
    @return : si la accion se realizo correctamente
    """
    usuarios = None
    if 'filtro' in request.params:
        filtro    = request.params['filtro']
        valor     = request.params['valor']
        sentencia = 'SELECT * from Usuario WHERE {0}=\'{1}\''.format(filtro,valor)
        usuarios  = DBSession.query(Usuario).from_statement(sentencia).all()
    else:
        usuarios  = DBSession.query(Usuario).all()
    
    data = []
    for usuario in usuarios:
        item = {}
        item['id'] = usuario.id
        item['ci'] = usuario.ci
        item['nombres'] = usuario.nombres
        item['apellidos'] = usuario.apellidos
        item['email'] = usuario.email
        item['telefono'] = usuario.telefono
        item['direccion'] = usuario.direccion
        item['observaciones'] = usuario.observaciones
        item['nick'] = usuario.nick
        item['password'] = usuario.password
        item['sexo'] = usuario.sexo
        item['fechanac'] = str(usuario.fechanac)
        data.append(item)
    return {'success':True, 'data':data, 'total':len(data)}

@view_config(route_name='eliminar_usuario_json', renderer='json')
def eliminar_usuario_json(request):
    """
    Nos permite traer el id del usuario a eliminar, eliminar las dependendcias
    del mismo con respecto a otras tablas y eliminar el registro de la base de datos.
    @param request: objeto que encapsula la peticion del cliente
    @return : True si la accion se realizo correctamente y False en caso contrario
    """ 
    id      = request.params['id']
    usuario = DBSession.query(Usuario).filter_by(id=id).first()
    if usuario is None:
        return {'success':False}
    
    # ANTIGUA ELIMINACION EN CASCADA
    # usuario.eliminar_dependencias()
    # DBSession.refresh(usuario)
    # DBSession.delete(usuario)
    
    try:
        DBSession.delete(usuario)
        return {'success' : True}
    except AssertionError:
        return {'success' : False}

@view_config(route_name='consulta_asignar_usuarios_json', renderer='json')
def consulta_asignar_usuarios_json(request):
    """
    Nos permite traer todos los usuarios asignados y asignables a un proyecto
    @param request: objeto que encapsula la peticion del cliente
    @return: True si la accion se realizo correctamente, la lista de permisos asignados al rol y la lista de permisos asignables al proyecto
    """
    def process_usuario_list(list):
        """
        Serializa una lista de con los datos de los usuarios para enviarla al cliente
        @param list: lista de objectos Usuario obtenidas desde la BD
        @return: result lista procesada de usuarios
        """
        result = []
        for usuario in list:
            item = [None,None,None,None]
            item[0] = usuario.id
            item[1] = usuario.nick
            item[2] = usuario.nombres
            item[3] = usuario.apellidos
            result.append(item)
        return result
    
    id_proyecto = request.params['id']
    # Obtenemos la lista de usuarios que fueron asignados al proyecto
    # Usuarios es de tipo ProyectoUsuario[] por tanto es necesario extraer el 'usuario' de la relacion
    usuarios_asignados = [x.usuario for x in DBSession.query(Proyecto).filter_by(id=id_proyecto).first().usuarios]
    # Obtenemos la lista de usuarios que no fueron asignados al proyecto
    usuarios_asignables = DBSession.query(Usuario).from_statement('select * from Usuario where id not in (select idusuario from ProyectoUsuario where idproyecto=\'{0}\')'.format(id_proyecto)).all()
    
    asignados  = process_usuario_list(usuarios_asignados)
    asignables = process_usuario_list(usuarios_asignables)

    return {'success':True, 'asignados':asignados, 'asignables':asignables}
