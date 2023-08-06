import re
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.view import view_config, forbidden_view_config
from pyramid.security import remember, forget, authenticated_userid
from sapproject.models.fase import *
from sapproject.models.proyecto import *

@view_config(route_name='crear_fase_json', renderer='json')
def crear_fase_json(request):
    """
    Nos permite traer los parametros que fueron cargados por el usuario
    y guardarlos en la base de datos.
    @param request: objeto que encapsula la peticion del servidor
    @return: True si la accion se realizo correctamente
    """ 
    nombre        = request.params['nombre']
    descripcion   = request.params['descripcion']
    fechainicio   = request.params['fechainicio']
    fechafin      = request.params['fechafin']
    observaciones = request.params['observaciones']
    estado        = request.params['estado']
    #with transaction.manager:
    model         = Fase(nombre, descripcion, fechainicio, fechafin, observaciones, estado)
    DBSession.add(model)
    #    DBSession.commit()
    
    return {'success' : True}

@view_config(route_name='modificar_fase_json', renderer='json')
def modificar_fase_json(request):
    """
    Nos permite traer los parametros que fueron modificados por el usuario
    y guardar los cambios en la base de datos.
    @param request: objeto que encapsula la peticion del servidor
    @return: True si la accion se realizo correctamente
    """ 
    id            = request.params['id']
    nombre        = request.params['nombre']
    descripcion   = request.params['descripcion']
    fechainicio   = request.params['fechainicio']
    fechafin      = request.params['fechafin']
    observaciones = request.params['observaciones']
    estado        = request.params['estado']
    # se modifica en la BD
    model         = Fase(nombre, descripcion, fechainicio, fechafin, observaciones, estado)
    model.id      = id
    DBSession.merge(model)   
    return {'success' : True}

@view_config(route_name='eliminar_fase_json', renderer='json')
def eliminar_fase_json(request):
    """
    Nos permite traer el id de la fase a eliminar, eliminar las dependendcias
    de la misma con respecto a otras tablas y eliminar el registro de la base de datos.
    @param request: objeto que encapsula la peticion del servidor
    @return: True si la accion se realizo correctamente y False en caso contrario
    """    
    id      = request.params['id']
    fase = DBSession.query(Fase).filter_by(id=id).first()
    if fase is None:
        return {'success':False}
    DBSession.delete(fase)
    return {'success' : True}


@view_config(route_name='consultar_fase_json', renderer='json')
def consultar_fase_json(request):
    """
    Nos permite traer los parametros de consulta(el filtro y el valor) y mostrar
    las fases que cumplen con la condicion del filtro.
    @param request: objeto que encapsula la peticion del servidor
    @return: True si la accion se realizo correctamente
    """
    fases = None
    if 'filtro' in request.params:
        filtro    = request.params['filtro']
        valor     = request.params['valor']
        sentencia = 'SELECT * from Fase WHERE {0}=\'{1}\''.format(filtro,valor)
        fases  = DBSession.query(Fase).from_statement(sentencia).all()
    else:
        fases = DBSession.query(Fase).all()
    
    data = []
    for fase in fases:
        item = {}
        item['id'] = fase.id
        item['nombre'] = fase.nombre
        item['descripcion'] = fase.descripcion
        item['fechainicio'] = str(fase.fechainicio)
        item['fechafin'] = str(fase.fechafin)
        item['estado'] = fase.estado
        data.append(item)
    return {'success':True, 'data':data, 'total':len(data)}

@view_config(route_name='consultar_fase_proyecto_json', renderer='json')
def consultar_fase_proyecto_json(request):
    """
    Nos permite obtener una lista de fases por proyecto
    @param request: objeto que encapsula la peticion del servidor
    @return: True si la accion se realizo correctamente
    """
    id_proyecto = request.params['idproyecto']
    proyecto    = DBSession.query(Proyecto).filter_by(id=id_proyecto).first()
    data = []
    for rf in proyecto.fases:
        item = {}
        item['id'] = rf.fase.id
        item['nombre'] = rf.fase.nombre
        item['orden'] = rf.orden
        item['nombre_orden'] = '{0} ({1})'.format(rf.fase.nombre,rf.orden)
        data.append(item)
    return {'total':len(data), 'data':data}
