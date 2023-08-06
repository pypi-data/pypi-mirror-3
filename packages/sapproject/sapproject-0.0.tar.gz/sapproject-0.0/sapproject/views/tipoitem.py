import re
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.view import view_config, forbidden_view_config
from pyramid.security import remember, forget, authenticated_userid
from sapproject.models.tipoitem import *
from sapproject.models.fase import *

@view_config(route_name='crear_tipoitem_json', renderer='json')
def crear_tipoitem_json(request):
    """
    Nos permite traer los parametros que fueron cargados por el usuario
    y guardarlos en la base de datos.
    @param request: objeto que encapsula la peticion del cliente
    @return : True si la accion se realizo correctamente
    """     
    nombre        = request.params['nombre']
    descripcion   = request.params['descripcion']
    prefijo       = request.params['prefijo']
    # se agrega a la BD
    model         = Tipoitem(nombre, descripcion, prefijo)
    DBSession.add(model)
    return {'success' : True}

@view_config(route_name='modificar_tipoitem_json', renderer='json')
def modificar_tipoitem_json(request):
    """
    Nos permite traer los parametros que fueron modificados por el usuario
    y guardar los cambios en la base de datos.
    @param request: objeto que encapsula la peticion del cliente
    @return: True si la accion se realizo correctamente
    """ 
    id           = request.params['id']
    nombre       = request.params['nombre']
    descripcion  = request.params['descripcion']
    prefijo      = request.params['prefijo']
    # Se modifica en la BD
    model         = Tipoitem(nombre,descripcion,prefijo)
    model.id      = id
    DBSession.merge(model)   
    return {'success':True}

@view_config(route_name='eliminar_tipoitem_json', renderer='json')
def eliminar_tipoitem_json(request):
    """
    Nos permite traer el id del tipoitem a eliminar, eliminar las dependendcias
    del mismo con respecto a otras tablas y eliminar el registro de la base de datos.
    @param request: objeto que encapsula la peticion del cliente
    @return: True si la accion se realizo correctamente y False en caso contrario
    """ 
    id      = request.params['id']
    tipoitem = DBSession.query(Tipoitem).filter_by(id=id).first()
    if tipoitem is None:
        return {'success':False}
    DBSession.delete(tipoitem)
    return {'success' : True}

@view_config(route_name='consultar_tipoitem_json', renderer='json')
def consultar_tipoitem_json(request):
    """
    Nos permite traer los parametros de consulta(el filtro y el valor) y mostrar
    los tipoitems que cumplen con la condicion del filtro.
    @param request: objeto que encapsula la peticion del cliente
    @return: si la accion se realizo correctamente
    """ 
    tipoitems = None
    if 'filtro' in request.params:
        filtro    = request.params['filtro']
        valor     = request.params['valor']
        sentencia = 'SELECT * from Tipoitem WHERE {0}=\'{1}\''.format(filtro,valor)
        tipoitems  = DBSession.query(Tipoitem).from_statement(sentencia).all()
    else:
        tipoitems = DBSession.query(Tipoitem).all()
    
    data = []
    for tipoitem in tipoitems:
        item = {}
        item['id'] = tipoitem.id
        item['nombre'] = tipoitem.nombre
        item['descripcion'] = tipoitem.descripcion
        item['prefijo'] = tipoitem.prefijo
        data.append(item)
    return {'success':True, 'data':data, 'total':len(data)}

@view_config(route_name='consultar_tipoitem_fase_json', renderer='json')
def consultar_tipoitem_fase_json(request):
    """
    Nos permite obtener una lista de tipo item por fase
    @param request: objeto que encapsula la peticion del cliente
    @return: True si la accion se realizo correctamente
    """
    id_fase = request.params['idfase']
    fase = DBSession.query(Fase).filter_by(id=id_fase).first()
    data = []
    for rti in fase.tipoitems:
        item = {}
        item['id'] = rti.tipoitem.id
        item['nombre'] = rti.tipoitem.nombre
        data.append(item)
    return {'success':True, 'total':len(data), 'data':data}
