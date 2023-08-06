from base import *
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref

class ItemAtributoValor(Base):
    """
    Clase que crea la tabla ValorVersion que permite almacenar los valores de los atributos del item de acuerdo a la version
    """
    __tablename__ = 'itematributovalor'
    iditem        = Column(Integer, ForeignKey('item.id'), primary_key=True)
    idatributo    = Column(Integer, ForeignKey('atributo.id'), primary_key=True)
    version       = Column(Integer)
    valor         = Column(Text, nullable=False)
    atributo      = relationship("Atributo")
    # item
    
    def __init__(self, iditem, idatributo, version, valor):
        """
        Metodo de instancia constructor que inicializa los parametros del objeto itematributo.
        @type self: itematributo.
        @param self: referencia al objeto que llama el metodo en este caso itematributo.
        @type iditem: Integer
        @param iditem: campo que almacenara el id del item.
        @type idatributo: Integer
        @param idatributo: campo que almacenara el id del atributo.
        @type version: Integer
        @param version: campo que indica la version del item
        @type valor: Text
        @param valor: valor del atributo del item
        """ 
        self.iditem = iditem
        self.idatributo = idatributo
        self.version = version
        self.valor = valor
