from base import *
from sqlalchemy.orm import relationship, backref
from sqlalchemy import ForeignKey, Sequence

class Item(Base):
    """
    Clase que crea la tabla Item 
    """
    __tablename__           = 'item'
    id                      = Column(Integer, Sequence('item_id_seq'), primary_key=True)
    numfase                 = Column(Text)
    nombre                  = Column(Text, nullable=False, unique=True)
    descripcion             = Column(Text)
    version                 = Column(Integer, nullable=False)
    prioridad               = Column(Integer, nullable=False)
    complejidad             = Column(Integer, nullable=False)
    estado                  = Column(Text, nullable=False)
    idlineabase             = Column(Integer, ForeignKey('lineabase.id'))
    idtipoitem              = Column(Integer, ForeignKey('tipoitem.id'))
    idfase                  = Column(Integer, ForeignKey('fase.id'))
    tipoitem                = relationship("Tipoitem", backref="items")
    valoratributo_x_version = relationship("ItemAtributoValor", backref="item")
    
    def __init__(self, numfase, nombre, descripcion, version, prioridad, complejidad, estado, idlineabase, idtipoitem, idfase):
        """
        Metodo de instancia constructor que inicializa los parametros del objeto item
        @type numfase: Text
        @param numfase: campo que indica la numeracion del item dentro de una fase
        @type nombre: Text
        @param nombre: campo que almacenara el nombre del item
        @type descripcion: Text
        @param nombre: campo que almacenara la descripcion del item
        @type version: Integer
        @param version: campo que almacenara la version del item
        @type prioridad: Integer
        @param prioridad: campo que almacenara la prioridad del item
        @type complejidad: Integer
        @param complejidad: campo que almacenara la complejidad del item
        @type estado: Text
        @param estado: campo que almacenara el estado del item
        @type idlineabase: Integer
        @param idlineabase: campo que indica a que linea base pertenece el item
        @type idtipoitem: Integer
        @param idtipoitem: campo que indica el tipo del item
        @type idfase: Integer
        @param idfase: campo que indicia la fase al que pertenece el item
        """
        self.numfase = numfase
        self.nombre = nombre
        self.descripcion = descripcion
        self.version = version
        self.prioridad = prioridad
        self.complejidad = complejidad
        self.estado = estado
        self.idlineabase = idlineabase
        self.idtipoitem = idtipoitem
        self.idfase = idfase

    def eliminar_dependencias(self):
        """
        Metodo de instancia que elimina todas los relaciones de un registro de la tabla Items
        para que pueda ser eliminado.
        @type self: item
        @param self: referencia al objeto que llama el metodo en este caso item.
        """
        # TODO : implementar
        pass
