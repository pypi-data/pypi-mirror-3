from base import *
from sqlalchemy.orm import relationship, backref
from sqlalchemy import ForeignKey, Sequence

class Lineabase(Base):
    """
    Clase que crea la tabla Lineabase 
    """
    __tablename__ = 'lineabase'
    id          = Column(Integer, Sequence('lineabase_id_seq'), primary_key=True)
    nombre      = Column(Text, nullable=False, unique=True)
    descripcion = Column(Text)
    estado      = Column(Text, nullable=False)
    tipo        = Column(Text, nullable=False)
    idfase      = Column(Integer, ForeignKey('fase.id'))

    def __init__(self, nombre, descripcion, estado, tipo, idfase):
        """
        Metodo de instancia constructor que inicializa los parametros del objeto lineabase
        @type self: lineabase
        @param self: referencia al objeto que llama el metodo en este caso lineabase.
        @type nombre: Text
        @param nombre: campo que almacenara el nombre del lineabase.
        @type descripcion: Text
        @param descripcion: campo que almacenara la descripcion del lineabase.
        @type estado: Text
        @param estado: campo que indica el estado de la linea base.
        @type tipo: Text
        @param tipo: campo que indica si la linea base es parcial o final.
        @type idfase: Text
        @param idfase: campo que indica la fase a la que pertenece la linea base.
        """
        self.nombre      = nombre
        self.descripcion = descripcion
        self.estado      = estado
        self.tipo        = tipo
        self.idfase      = idfase
    
    def eliminar_dependencias(self):
        """
        Metodo de instancia que elimina todas los relaciones de un registro de la tabla Lineabase
        para que pueda ser eliminado.
        @type self: lineabase
        @param self: referencia al objeto que llama el metodo en este caso lineabase.
        """
        # TODO : implementar
        pass
