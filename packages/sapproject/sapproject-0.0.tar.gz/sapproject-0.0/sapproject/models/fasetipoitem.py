from base import *
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref

class FaseTipoitem(Base):
    """
    Clase que crea la tabla FaseTipoitem que permite las relaciones entre la tabla Tipoitem y la tabla Fase 
    """
    __tablename__ = 'fasetipoitem'
    idfase        = Column(Integer, ForeignKey('fase.id'), primary_key=True)
    idtipoitem    = Column(Integer, ForeignKey('tipoitem.id'), primary_key=True)
    tipoitem      = relationship("Tipoitem", backref="fases")
    # fase
    
    def __init__(self, idfase, idtipoitem):
        """
        Metodo de instancia constructor que inicializa los parametros del objeto fasetipoitem
        @type self: fasetipoitem
        @param self: referencia al objeto que llama el metodo en este caso fasetipoitem.
        @type idfase: Integer
        @param idfase: campo que almacenara el id de la fase.
        @type idtipoitem: Integer
        @param idtipoitem: campo que almacenara el id del tipo de item.
        """
        self.idfase = idfase
        self.idtipoitem = idtipoitem
