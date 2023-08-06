from base import *
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Sequence

class Fase(Base):
    """
    Clase que crea la tabla Fase 
    """
    __tablename__    = 'fase'
    id               = Column(Integer, Sequence('fase_id_seq'), primary_key=True)
    nombre           = Column(Text, nullable=False, unique=True)
    descripcion      = Column(Text)
    fechainicio      = Column(Date, nullable=False)
    fechafin         = Column(Date, nullable=False)
    estado           = Column(Text, nullable=False)
    observaciones    = Column(Text)
    tipoitems        = relationship("FaseTipoitem", backref="fase")
    
    def __init__(self, nombre, descripcion, fechainicio, fechafin, observaciones, estado):
        """
        Metodo de instancia constructor que inicializa los parametros del objeto fase
        @type self: fase
        @param self: referencia al objeto que llama el metodo en este caso fase.
        @type nombre: Text
        @param nombre: campo que almacenara el nombre de la fase.
        @type descripcion: Text
        @param descripcion: campo que almacenara la descripcion de la fase.
        @type fechainicio: Date
        @param fechainicio: campo que almacenara la fecha de inicio de la fase.
        @type fechafin: Text
        @param fechafin: campo que almacenara la fecha de fin de la fase.
        @type observaciones: Text
        @param observaciones: campo que almacenara observaciones sobre la fase.
        @type estado: Text
        @param estado: campo que almacenara el estado sobre la fase.
        """
        self.nombre = nombre
        self.descripcion = descripcion
        self.fechainicio = fechainicio
        self.fechafin = fechafin
        self.observaciones = observaciones
        self.estado = estado
