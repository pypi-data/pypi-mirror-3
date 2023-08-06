import re
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.view import view_config, forbidden_view_config
from pyramid.security import remember, forget, authenticated_userid
from sapproject.models.atributo import *
from sapproject.models.tipoitem import *
from sapproject.models.tipoitematributo import *

@view_config(route_name='crear_atributo_json', renderer='json')
def crear_atributo_json(request):
    """
    Nos permite traer los parametros que fueron cargados por el usuario
    y guardarlos en la base de datos.
    @param request: objeto que encapsula la peticion del cliente
    @return : True si la accion se realizo correctamente
    """     
    nombre        = request.params['nombre']
    tipodato      = request.params['tipodato']
    valordef      = request.params['valordef']
    # se agrega a la BD
    model         = Atributo(nombre, tipodato, valordef)
    DBSession.add(model)
    return {'success' : True}

@view_config(route_name='modificar_atributo_json', renderer='json')
def modificar_atributo_json(request):
    """
    Nos permite traer los parametros que fueron modificados por el usuario
    y guardar los cambios en la base de datos.
    @param request: objeto que encapsula la peticion del cliente
    @return: True si la accion se realizo correctamente
    """ 
    id           = request.params['id']
    nombre       = request.params['nombre']
    tipodato     = request.params['tipodato']
    valordef     = request.params['valordef']
    # Se modifica en la BD
    model         = Atributo(nombre,tipodato,valordef)
    model.id      = id
    DBSession.merge(model)   
    return {'success':True}

@view_config(route_name='eliminar_atributo_json', renderer='json')
def eliminar_atributo_json(request):
    """
    Nos permite traer el id del atributo a eliminar, eliminar las dependendcias
    del mismo con respecto a otras tablas y eliminar el registro de la base de datos.
    @param request: objeto que encapsula la peticion del cliente
    @return: True si la accion se realizo correctamente y False en caso contrario
    """ 
    id      = request.params['id']
    atributo = DBSession.query(Atributo).filter_by(id=id).first()
    if atributo is None:
        return {'success':False}
    DBSession.delete(atributo)
    return {'success' : True}

@view_config(route_name='consultar_atributo_json', renderer='json')
def consultar_atributo_json(request):
    """
    Nos permite traer los parametros de consulta(el filtro y el valor) y mostrar
    los atributos que cumplen con la condicion del filtro.
    @param request: objeto que encapsula la peticion del cliente
    @return: si la accion se realizo correctamente
    """ 
    atributos = None
    if 'filtro' in request.params:
        filtro    = request.params['filtro']
        valor     = request.params['valor']
        sentencia = 'SELECT * from Atributo WHERE {0}=\'{1}\''.format(filtro,valor)
        atributos  = DBSession.query(Atributo).from_statement(sentencia).all()
    else:
        atributos = DBSession.query(Atributo).all()
    
    data = []
    for atributo in atributos:
        item = {}
        item['id'] = atributo.id
        item['nombre'] = atributo.nombre
        item['tipodato'] = atributo.tipodato
        item['valordef'] = atributo.valordef
        data.append(item)
    return {'success':True, 'data':data, 'total':len(data)}

@view_config(route_name='consulta_asignar_atributos', renderer='json')
def consulta_asignar_atributos(request):
    """
    Nos permite traer todos los atributos asignados y asignables a un tipoitem
    @param request: objeto que encapsula la peticion del cliente
    @return: True si la accion se realizo correctamente, la lista de atributos asignados al tipoitem y la lista de atributos asignables al tipoitem
    """
    def process_atributo_list(list):
        """
        Serializa una lista de con los datos de los atributos para enviarla al cliente
        @param list: lista de objectos Atributo obtenidas desde la BD
        @return: result lista procesada de atributos
        """ 
        result = []
        for atributo in list:
            item = [None,None,None,None]
            item[0] = atributo.id
            item[1] = atributo.nombre
            item[2] = atributo.tipodato
            item[3] = atributo.valordef
            result.append(item)
        return result
    
    id_tipoitem = request.params['id']
    # Obtenemos la lista de atributos que fueron asignados al tipoitem
    # Atributos es de tipo TipoitemAtributo[] por tanto es necesario extraer el 'atributo' de la relacion
    atributos_asignados = [x.atributo for x in DBSession.query(Tipoitem).filter_by(id=id_tipoitem).first().atributos]
    # Obtenemos la lista de atributos que no fueron asignados al tipoitem
    atributos_asignables = DBSession.query(Atributo).from_statement('select * from Atributo where id not in (select idatributo from TipoitemAtributo where idtipoitem=\'{0}\')'.format(id_tipoitem)).all()
    
    asignados  = process_atributo_list(atributos_asignados)
    asignables = process_atributo_list(atributos_asignables)

    return {'success':True, 'asignados':asignados, 'asignables':asignables}


@view_config(route_name='asignar_desasignar_atributo', renderer='json')
def asignar_desasignar_atributo(request):
    """
    Nos permite asignar/desasignar atributos a un tipoitem
    @param request: objeto que encapsula la peticion del cliente
    @return: True si la accion se realizo correctamente
    """
    received   = eval(request.params['data'])
    # id del tipo de item a asignar/desasignar atributos
    id_tipoitem = received['id_tipoitem']
    # ids de atributos asignados
    data   = received['data']

    # obtenemos el tipo de item desde la BD
    tipoitem   = DBSession.query(Tipoitem).filter_by(id=id_tipoitem).first()
    # eliminamos sus atributos asignados anteriormente
    DBSession.query(TipoitemAtributo).filter_by(idtipoitem=id_tipoitem).delete(synchronize_session=False)
    # actualizamos el tipoitem
    DBSession.refresh(tipoitem);
    # creamos una nueva lista de atributos asignados
    for id_atributo in data:
        tipoitem.atributos.append(TipoitemAtributo(id_tipoitem, id_atributo))
    # guardamos los cambios
    DBSession.merge(tipoitem)
    
    return {'success':True}

@view_config(route_name='consulta_atributo_x_tipoitem_json', renderer='json')
def consulta_atributo_x_tipoitem_json(request):
    """
    Nos permite obtener la lista detallada de atributos asignados a un tipo de item
    @param request: objeto que encapsula la peticion del cliente
    @return: True si la accion se realizo correctamente
    """
    id_tipoitem = request.params['id_tipoitem']
    tipoitem    = DBSession.query(Tipoitem).filter_by(id=id_tipoitem).first()
    data = []
    for atributo in tipoitem.atributos:
        item = {}
        item['id'] = atributo.atributo.id
        item['nombre'] = atributo.atributo.nombre
        item['tipodato'] = atributo.atributo.tipodato
        item['valordef'] = atributo.atributo.valordef
        data.append(item)
    return {'success':True, 'data':data, 'total':len(data)}

