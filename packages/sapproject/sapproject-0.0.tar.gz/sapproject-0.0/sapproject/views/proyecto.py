import re
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.view import view_config, forbidden_view_config
from pyramid.security import remember, forget, authenticated_userid
from sapproject.models.proyecto import *
from sapproject.models.usuario import *
from sapproject.models.proyectousuario import *
from sapproject.models.proyectousuariorol import *

@view_config(route_name='crear_proyecto_json', renderer='json')
def crear_proyecto_json(request):
    """
    Nos permite traer los parametros que fueron cargados por el usuario
    y guardarlos en la base de datos.
    @param request: objeto que encapsula la peticion del cliente
    @return: True si la accion se realizo correctamente
    """ 
    nombre        = request.params['nombre']
    descripcion   = request.params['descripcion']
    fechainicio   = request.params['fechainicio']
    fechafin      = request.params['fechafin']
    estado        = request.params['estado']
    observaciones = request.params['observaciones']
    #with transaction.manager:
    model         = Proyecto(nombre, descripcion, fechainicio, fechafin, estado, observaciones)
    DBSession.add(model)
    #    DBSession.commit()
    
    return {'success' : True}

@view_config(route_name='modificar_proyecto_json', renderer='json')
def modificar_proyecto_json(request):
    """
    Nos permite traer los parametros que fueron modificados por el usuario
    y guardar los cambios en la base de datos.
    @param request: objeto que encapsula la peticion del cliente
    @return: True si la accion se realizo correctamente
    """ 
    id            = request.params['id']
    nombre        = request.params['nombre']
    descripcion   = request.params['descripcion']
    fechainicio   = request.params['fechainicio']
    fechafin      = request.params['fechafin']
    estado        = request.params['estado']
    observaciones = request.params['observaciones']
    # se modifica en la BD
    model         = Proyecto(nombre, descripcion, fechainicio, fechafin, estado, observaciones)
    model.id      = id
    DBSession.merge(model)   
    return {'success' : True}

@view_config(route_name='eliminar_proyecto_json', renderer='json')
def eliminar_proyecto_json(request):
    """
    Nos permite traer el id del proyecto a eliminar, eliminar las dependendcias
    del mismo con respecto a otras tablas y eliminar el registro de la base de datos.
    @param request: objeto que encapsula la peticion del cliente
    @return: True si la accion se realizo correctamente y False en caso contrario
    """    
    id      = request.params['id']
    proyecto = DBSession.query(Proyecto).filter_by(id=id).first()
    if proyecto is None:
        return {'success':False}
    DBSession.delete(proyecto)
    return {'success' : True}


@view_config(route_name='consultar_proyecto_json', renderer='json')
def consultar_proyecto_json(request):
    """
    Nos permite traer los parametros de consulta(el filtro y el valor) y mostrar
    los proyectos que cumplen con la condicion del filtro.
    @param request: objeto que encapsula la peticion del cliente
    @return: True si la accion se realizo correctamente
    """
    usuarios = None
    if 'filtro' in request.params:
        filtro    = request.params['filtro']
        valor     = request.params['valor']
        sentencia = 'SELECT * from Proyecto WHERE {0}=\'{1}\''.format(filtro,valor)
        proyectos  = DBSession.query(Proyecto).from_statement(sentencia).all()
    else:
        proyectos = DBSession.query(Proyecto).all()
    
    data = []
    for proyecto in proyectos:
        item = {}
        item['id'] = proyecto.id
        item['nombre'] = proyecto.nombre
        item['descripcion'] = proyecto.descripcion
        item['fechainicio'] = str(proyecto.fechainicio)
        item['fechafin'] = str(proyecto.fechafin)
        item['estado'] = proyecto.estado
        data.append(item)
    return {'success':True, 'data':data, 'total':len(data)}

@view_config(route_name='asignar_usuario_rol_proyecto_json', renderer='json')
def asignar_usuario_rol_proyecto_json(request):
    """
    Nos permite realizar la asignacion de un usuario a un proyecto
    @param request: objeto que encapsula la peticion del cliente
    @return: True si la accion se realizo correctamente
    """
    # id del proyecto al que se le asigna un usuario
    id_proyecto = request.params['id_proyecto']
    # id del usuario a asignar
    id_usuario  = request.params['id_usuario']
    # lista de id de roles del usuario en el proyecto
    id_roles    = eval(request.params['id_roles'])
    
    # obtenemos el proyecto desde la BD
    proyecto = DBSession.query(Proyecto).filter_by(id=id_proyecto).first()
    # eliminamos las relaciones con el usuario en la tabla 'proyectousuario'
    DBSession.query(ProyectoUsuario).filter_by(idproyecto=id_proyecto,idusuario=id_usuario).delete(synchronize_session=False)
    # eliminamos las relaciones con el usuario en la tabla 'proyectousuariorol'
    DBSession.query(ProyectoUsuarioRol).filter_by(idproyecto=id_proyecto,idusuario=id_usuario).delete(synchronize_session=False)
    # actualizamos el proyecto
    DBSession.refresh(proyecto)
    # creamos una nueva asignacion proyecto-usuario en la tabla 'proyectousuario'
    proyecto.usuarios.append(ProyectoUsuario(id_proyecto, id_usuario))
    # creamos una nueva lista de usuarios asignados (con sus roles) al proyecto en la tabla 'proyectousuariorol'
    for id_rol in id_roles:
        proyecto.usuarios_x_rol.append(ProyectoUsuarioRol(id_proyecto,id_usuario, id_rol))
    
    # guardamos los cambios
    DBSession.merge(proyecto)
    
    return {'success':True}

@view_config(route_name='desasignar_usuario_rol_proyecto_json', renderer='json')
def desasignar_usuario_rol_proyecto_json(request):
    """
    Nos permite realizar la desasignacion de un usuario de un proyecto
    @param request: objeto que encapsula la peticion del cliente
    @return: True si la accion se realizo correctamente
    """
    usuario_actual       = DBSession.query(Usuario).filter_by(nick=authenticated_userid(request)).first()
    id_proyecto_actual   = int(request.params['id_proyecto_actual'])
    id_proyecto_asignado = int(request.params['id_proyecto_asignado'])
    id_usuario           = int(request.params['id_usuario'])
    
    # Comprobamos que no tratemos de desasignarnos de nuestro proyecto actual
    if id_proyecto_asignado == id_proyecto_actual and usuario_actual.id == id_usuario:
        # imposible de desasignar al usuario
        return {'success':False}
    else:
        # podemos desasignar al usuario
        # eliminamos las relaciones con el usuario en la tabla 'proyectousuario'
        DBSession.query(ProyectoUsuario).filter_by(idproyecto=id_proyecto_asignado,idusuario=id_usuario).delete(synchronize_session=False)
        # eliminamos las relaciones con el usuario en la tabla 'proyectousuariorol'
        DBSession.query(ProyectoUsuarioRol).filter_by(idproyecto=id_proyecto_asignado,idusuario=id_usuario).delete(synchronize_session=False)       
        return {'success':True}
