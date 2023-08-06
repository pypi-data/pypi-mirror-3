from base import *
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Sequence

class Atributo(Base):
    """
    Clase que crea la tabla Atributo 
    """
    __tablename__ = 'atributo'
    id          = Column(Integer, Sequence('atributo_id_seq'), primary_key=True)
    nombre      = Column(Text, nullable=False, unique=True)
    tipodato    = Column(Text, nullable=False)
    valordef    = Column(Text, nullable=False)
    # tipoitems

    def __init__(self, nombre, tipodato, valordef):
        """
        Metodo de instancia constructor que inicializa los parametros del objeto atributo
        @type self: atributo
        @param self: referencia al objeto que llama el metodo en este caso atributo.
        @type nombre: Text
        @param nombre: campo que almacenara el nombre del atributo.
        @type tipodato: Text
        @param tipodato: campo que almacenara el tipo de dato del atributo.
        @type valordef: Text
        @param valordef: campo que almacenara el valor por defecto del tipo de dato.
        """
        self.nombre   = nombre
        self.tipodato = tipodato
        self.valordef = valordef

    def eliminar_dependencias(self):
        """
        Metodo de instancia que elimina todas los relaciones de un registro de la tabla Atributo
        para que pueda ser eliminado.
        @type self: atributo
        @param self: referencia al objeto que llama el metodo en este caso atributo.
        """
        # En tabla tipoitematributo
        for t in self.tipoitems:
            DBSession.delete(t)
