from base import *
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref

class TipoitemAtributo(Base):
    """
    Clase que crea la tabla TipoitemAtributo que permite las relaciones entre la tabla Tipoitem y la tabla Atributo 
    """
    __tablename__ = 'tipoitematributo'
    idtipoitem    = Column(Integer, ForeignKey('tipoitem.id'), primary_key=True)
    idatributo    = Column(Integer, ForeignKey('atributo.id'), primary_key=True)
    atributo      = relationship("Atributo", backref="tipoitems")
    # tipoitem
    # rol
    
    def __init__(self, idtipoitem, idatributo):
        """
        Metodo de instancia constructor que inicializa los parametros del objeto tipoitematributo.
        @type self: tipoitematributo.
        @param self: referencia al objeto que llama el metodo en este caso tipoitematributo.
        @type idtipoitem: Integer
        @param idtipoitem: campo que almacenara el id del tipoitem.
        @type idatributo: Integer
        @param idatributo: campo que almacenara el id del atributo.
        """
        self.idtipoitem = idtipoitem
        self.idatributo = idatributo
