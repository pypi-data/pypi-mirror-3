import re
import transaction
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.view import view_config, forbidden_view_config
from pyramid.security import remember, forget, authenticated_userid
from sqlalchemy import func 
from sapproject.models.item import *
from sapproject.models.tipoitem import *
from sapproject.models.itematributovalor import *

@view_config(route_name='crear_item_json', renderer='json')
def crear_item_json(request):
    """
    Nos permite traer los parametros que fueron cargados por el usuario
    y guardarlos en la base de datos.
    @param request: objeto que encapsula la peticion del cliente
    @return: True si la accion se realizo correctamente
    """
    id_fase     = request.params['id_fase']
    id_tipoitem = request.params['id_tipoitem']
    
    # Tipo de item
    tipoitem   = DBSession.query(Tipoitem).filter_by(id=id_tipoitem).first()
    
    # Calculamos la numeracion dentro de la fase
    maxnumfase = DBSession.query(func.max(Item.numfase)).scalar()
    numfase    = ''
    if maxnumfase is None:
        numfase = tipoitem.prefijo + '-1'
    else:
        numfase = tipoitem.prefijo + '-' + str(int(str(maxnumfase[4:])) + 1)
    
    # Obtenemos los demas atributos base necesarios
    nombre       = request.params['1']
    descripcion  = request.params['2']
    prioridad    = request.params['3']
    complejidad  = request.params['4']
    version      = 1
    estado       = 'ACTIVO'
    id_lineabase = None
    
    # Creamos el nuevo item y guardamos en la BD
    model = Item(numfase, nombre, descripcion, version, prioridad, complejidad, estado, id_lineabase, id_tipoitem, id_fase)
    DBSession.add(model)
    
    # Recuperamos el item recien creado
    item    = DBSession.query(Item).filter_by(idfase=id_fase,idtipoitem=id_tipoitem,numfase=numfase).first()
    id_item = item.id
    
    # Mantenemos solo los atributos del tipo item
    params = [it for it in request.params.items() if it[0] != u'id_tipoitem' and it[0] != u'id_fase']
    for param in params:
        # Guardamos el valor de sus atributos para esta version
        item_value = ItemAtributoValor(id_item, param[0], 1, param[1])
        item.valoratributo_x_version.append(item_value)
    
    # Guardamos el item con sus atributos en la BD
    DBSession.merge(item)
    
    return {'success' : True}

@view_config(route_name='modificar_item_json', renderer='json')
def modificar_item_json(request):
    """
    Nos permite traer los parametros que fueron modificados por el usuario
    y guardar los cambios en la base de datos.
    @param request: objeto que encapsula la peticion del cliente
    @return: True si la accion se realizo correctamente
    """   
    return {'success' : True}

@view_config(route_name='consultar_item_json', renderer='json')
def consultar_item_json(request):
    """
    Nos permite traer los parametros de consulta(el filtro y el valor) y mostrar
    los itemes que cumplen con la condicion del filtro.
    @param request: objeto que encapsula la peticion del cliente
    @return: si la accion se realizo correctamente
    """ 
    usuarios = None
    if 'filtro' in request.params:
        filtro    = request.params['filtro']
        valor     = request.params['valor']
        sentencia = 'SELECT * from Item WHERE {0}=\'{1}\''.format(filtro,valor)
        items  = DBSession.query(Item).from_statement(sentencia).all()
    else:
        items = DBSession.query(Item).all()
    data = []
    for item in items:
        element = {}
        element['id'] = item.id
        element['nombre'] = item.nombre
        element['descripcion'] = item.descripcion
        element['version'] = item.version
        element['prioridad'] = item.prioridad
        element['complejidad'] = item.complejidad
        element['estado'] = item.estado
        data.append(element)
    return {'success':True, 'data':data, 'total':len(data)}

@view_config(route_name='eliminar_item_json', renderer='json')
def eliminar_item_json(request):
    """
    Nos permite traer el id del item a eliminar, eliminar las dependendcias
    del mismo con respecto a otras tablas y eliminar el registro de la base de datos.
    @param request: objeto que encapsula la peticion del cliente
    @return: True si la accion se realizo correctamente y False en caso contrario
    """ 
    id   = request.params['id']
    item = DBSession.query(Item).filter_by(id=id).first()
    item.estado = 'ELIMINADO'
    DBSesion.merge(item)
    return {'success' : True}

@view_config(route_name='consultar_campos_crear_item_json', renderer='json')
def consultar_campos_crear_item_json(request):
    """
    Nos permite obtener los campos de un tipo item para generar un formulario de creacion
    para los items de una fase.
    @param request: objeto que encapsula la peticion del cliente
    @return: True si la accion se realizo correctamente y False en caso contrario
    """
    id_tipoitem = request.params['id_tipoitem']
    tipoitem  = DBSession.query(Tipoitem).filter_by(id=id_tipoitem).first()
    data = []
    for atributo in tipoitem.atributos:
        item = {}
        item['name'] = atributo.atributo.id
        item['text'] = atributo.atributo.nombre
        item['type'] = atributo.atributo.tipodato
        item['defvalue'] = atributo.atributo.valordef
        item['nullable'] = True # true para los campos no base, de momento siempre es true
        data.append(item)
    return {'success':True, 'data':data, 'total':len(data)}
    
@view_config(route_name='consultar_campos_modificar_item_json', renderer='json')
def consultar_campos_modificar_item_json(request):
    """
    Nos permite obtener los campos de un tipo item , y sus valores, para generar un formulario
    de modificacion para los items de una fase.
    @param request: objeto que encapsula la peticion del servidor
    @return: True si la accion se realizo correctamente y False en caso contrario
    """
    id_item = request.params['id_item']
    item    = DBSession.query(Item).filter_by(id=id_tipoitem).first()
    version = item.version
    sentencia = 'SELECT * from ItemAtributoValor WHERE iditem=\'{0}\' and version=\'{1}\''.format(id_item, version)
    atributos  = DBSession.query(ItemAtributoValor).from_statement(sentencia).all()
    data = []
    for atributo in atributos:
        item = {}
        item['name'] = atributo.atributo.id
        item['text'] = atributo.atributo.nombre
        item['type'] = atributo.atributo.tipodato
        item['defvalue'] = atributo.atributo.valordef
        item['value'] = atributo.valor
        item['nullable'] = True # true para los campos no base, de momento siempre es true
        data.append(item)
    return {'success':True, 'data':data, 'total':len(data)}
