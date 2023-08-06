from base import *
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref

class ProyectoFase(Base):
    """
    Clase que crea la tabla ProyectoFase que permite las relaciones entre la tabla Proyecto y la tabla Fase 
    """
    __tablename__ = 'proyectofase'
    idproyecto    = Column(Integer, ForeignKey('proyecto.id'), primary_key=True)
    idfase        = Column(Integer, ForeignKey('fase.id'), primary_key=True)
    orden         = Column(Integer, nullable=False)
    proyecto      = relationship("Proyecto", backref="fases")
    # fase
    
    def __init__(self, idproyecto, idfase,orden):
        """
        Metodo de instancia constructor que inicializa los parametros del objeto proyectofase.
        @type self: proyectofase.
        @param self: referencia al objeto que llama el metodo en este caso proyectofase.
        @type idproyecto: Integer
        @param idproyecto: campo que almacenara el id del proyecto.
        @type idfase: Integer
        @param idfase: campo que almacenara el id de la fase.
        @type orden: Integer
        @param orden: campo que indica el orden de la fase en el proyecto.
        """
        self.idproyecto = idproyecto
        self.idfase     = idfase
        self.orden      = orden
