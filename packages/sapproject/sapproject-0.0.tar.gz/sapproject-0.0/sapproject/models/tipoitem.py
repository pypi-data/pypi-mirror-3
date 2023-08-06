from base import *
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Sequence

class Tipoitem(Base):
    """
    Clase que crea la tabla Tipo de Item 
    """
    __tablename__ = 'tipoitem'
    id          = Column(Integer, Sequence('tipoitem_id_seq'), primary_key=True)
    nombre      = Column(Text, nullable=False, unique=True)
    descripcion = Column(Text, nullable=False)
    prefijo     = Column(Text, nullable=False, unique=True)
    atributos   = relationship("TipoitemAtributo", backref="tipoitem")
    # fases
    # items

    def __init__(self, nombre, descripcion, prefijo):
        """
        Metodo de instancia constructor que inicializa los parametros del objeto tipo de item
        @type self: tipoitem
        @param self: referencia al objeto que llama el metodo en este caso tipo de item.
        @type nombre: Text
        @param nombre: campo que almacenara el nombre del tipo de item.
        @type descripcion: Text
        @param descripcion: campo que almacenara la descripcion del tipo de dato.
        @type prefijo: Text
        @param prefijo: campo que almacenara el prefijo que representara el tipo de item.
        """
        self.nombre      = nombre
        self.descripcion = descripcion
        self.prefijo     = prefijo

    def eliminar_dependencias(self):
        """
        Metodo de instancia que elimina todas los relaciones de un registro de la tabla Tipoitem
        para que pueda ser eliminado.
        @type self: tipoitem
        @param self: referencia al objeto que llama el metodo en este caso tipoitem.
        """
        # En tabla tipoitematributo
        for a in self.atributos:
            DBSession.delete(a)
