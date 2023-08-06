import re
from pyramid.view import view_config
from pyramid.security import authenticated_userid

from sapproject.models.rol import *
from sapproject.models.permiso import *
from sapproject.models.rolpermiso import *

@view_config(route_name='crear_permiso_json', renderer='json')
def crear_permiso_json(request):
    """
    Nos permite traer los parametros que fueron cargados por el usuario
    y guardarlos en la base de datos.
    @param request: objeto que encapsula la peticion del cliente
    @return: True si la accion se realizo correctamente
    """ 
    nombre       = request.params['nombre']
    descripcion  = request.params['descripcion']
    codificacion = request.params['codificacion']
    # Se agrega a la BD
    model = Permiso(nombre,descripcion,codificacion)
    DBSession.add(model)
    return {'success':True}

@view_config(route_name='modificar_permiso_json', renderer='json')
def modificar_permiso_json(request):
    """
    Nos permite traer los parametros que fueron modificados por el usuario
    y guardar los cambios en la base de datos.
    @param request: objeto que encapsula la peticion del cliente
    @return: True si la accion se realizo correctamente
    """ 
    id           = request.params['id']
    nombre       = request.params['nombre']
    descripcion  = request.params['descripcion']
    accion       = request.params['accion']
    codificacion = request.params['codificacion']   # posible nueva accion
    if accion != codificacion:
        accion = codificacion
    # Se modifica en la BD
    model         = Permiso(nombre,descripcion,accion)
    model.id      = id
    DBSession.merge(model)   
    return {'success':True}

@view_config(route_name='eliminar_permiso_json', renderer='json')
def eliminar_permiso_json(request):
    """
    Nos permite traer el id del permiso a eliminar, eliminar las dependendcias
    del mismo con respecto a otras tablas y eliminar el registro de la base de datos.
    @param request: objeto que encapsula la peticion del cliente
    @return: True si la accion se realizo correctamente y False en caso contrario
    """ 
    id      = request.params['id']
    permiso = DBSession.query(Permiso).filter_by(id=id).first()
    if permiso is None:
        return {'success':False}
    DBSession.delete(permiso)
    return {'success' : True}

@view_config(route_name='consultar_permiso_json', renderer='json')
def consultar_permiso_json(request):
    """
    Nos permite traer los parametros de consulta(el filtro y el valor) y mostrar
    los permisos que cumplen con la condicion del filtro.
    @param request: objeto que encapsula la peticion del cliente
    @return: si la accion se realizo correctamente
    """ 
    permisos = None
    if 'filtro' in request.params:
        filtro    = request.params['filtro']
        valor     = request.params['valor']
        sentencia = 'SELECT * from Permiso WHERE {0}=\'{1}\''.format(filtro,valor)
        permisos  = DBSession.query(Permiso).from_statement(sentencia).all()
    else:
        permisos = DBSession.query(Permiso).all()
    
    data = []
    for permiso in permisos:
        item = {}
        item['id'] = permiso.id
        item['nombre'] = permiso.nombre
        item['descripcion'] = permiso.descripcion
        item['accion'] = permiso.accion
        data.append(item)
    return {'success':True, 'data':data, 'total':len(data)}

@view_config(route_name='consulta_acciones_json', renderer='json')
def consulta_acciones_json(request):
    """
    Nos permite traer todas las acciones posibles que pueden realizarce con los permisos
    @param request: objeto que encapsula la peticion del cliente
    @return: True si la accion se realizo correctamente, la cantidad de acciones y la lista de acciones
    """ 
    nombre_rol = request.params['rol']
    rol = DBSession.query(Rol).filter_by(nombre=nombre_rol).first()
    lista = rol.permisos
    if len(lista) == 0:
        return {'success':True, 'total':0}
    else:
        data = []
        for p in lista:
            item = {}
            item['permiso'] = p.permiso.accion
            data.append(item)
        return {'success':True, 'total':len(data), 'data':data}

@view_config(route_name='consulta_asignar_permisos_json', renderer='json')
def consulta_asignar_permisos_json(request):
    """
    Nos permite traer todos los permisos asignados y asignables a un rol
    @param request: objeto que encapsula la peticion del cliente
    @return: True si la accion se realizo correctamente, la lista de permisos asignados al rol y la lista de permisos asignables al rol
    """
    def process_permiso_list(list):
        """
        Serializa una lista de con los datos de los permisos para enviarla al cliente
        @param list: lista de objectos Permiso obtenidas desde la BD
        @return: result lista procesada de permisos
        """
        result = []
        for permiso in list:
            item = [None,None,None,None]
            item[0] = permiso.id
            item[1] = permiso.nombre
            item[2] = permiso.descripcion
            item[3] = permiso.accion
            result.append(item)
        return result
    
    id_rol = request.params['id']
    # Obtenemos la lista de permisos que fueron asignados al rol
    # Permisos es de tipo RolPermiso[] por tanto es necesario extraer el 'permiso' de la relacion
    permisos_asignados = [x.permiso for x in DBSession.query(Rol).filter_by(id=id_rol).first().permisos]
    # Obtenemos la lista de permisos que no fueron asignados al rol
    permisos_asignables = DBSession.query(Permiso).from_statement('select * from Permiso where id not in (select idpermiso from RolPermiso where idrol=\'{0}\')'.format(id_rol)).all()
    
    asignados  = process_permiso_list(permisos_asignados)
    asignables = process_permiso_list(permisos_asignables)

    return {'success':True, 'asignados':asignados, 'asignables':asignables}
    
@view_config(route_name='asignar_desasignar_permiso_json', renderer='json')
def asignar_desasignar_permiso_json(request):
    """
    Nos permite asignar/desasignar permisos a un rol
    @param request: objeto que encapsula la peticion del cliente
    @return: True si la accion se realizo correctamente
    """
    received   = eval(request.params['data'])
    # id del rol a asignar/desasignar roles
    id_rol = received['id_rol']
    # ids de permisos asignados
    data   = received['data']

    # obtenemos el rol desde la BD
    rol   = DBSession.query(Rol).filter_by(id=id_rol).first()
    # eliminamos sus permisos asignados anteriormente
    DBSession.query(RolPermiso).filter_by(idrol=id_rol).delete(synchronize_session=False)
    # actualizamos el rol
    DBSession.refresh(rol);
    # creamos una nueva lista de permisos asignados
    for id_permiso in data:
        rol.permisos.append(RolPermiso(id_rol, id_permiso))
    # guardamos los cambios
    DBSession.merge(rol)
    
    return {'success':True}

@view_config(route_name='consulta_permiso_x_rol_json', renderer='json')
def consulta_permiso_x_rol_json(request):
    """
    Nos permite obtener la lista detallada de permisos asignados a un rol
    @param request: objeto que encapsula la peticion del cliente
    @return: True si la accion se realizo correctamente
    """
    id_rol = request.params['id_rol']
    rol    = DBSession.query(Rol).filter_by(id=id_rol).first()
    data = []
    for permiso in rol.permisos:
        item = {}
        item['id'] = permiso.permiso.id
        item['nombre'] = permiso.permiso.nombre
        item['descripcion'] = permiso.permiso.descripcion
        item['accion'] = permiso.permiso.accion
        data.append(item)
    return {'success':True, 'data':data, 'total':len(data)}
