from base import *
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref

class ProyectoUsuario(Base):
    """
    Clase que crea la tabla ProyectoUsuario que permite las relaciones entre la tabla Usuario y la tabla Proyecto 
    """
    __tablename__ = 'proyectousuario'
    idproyecto = Column(Integer, ForeignKey('proyecto.id'), primary_key=True)
    idusuario  = Column(Integer, ForeignKey('usuario.id'), primary_key=True)
    usuario    = relationship("Usuario", backref="proyectos")
    # proyecto
    
    def __init__(self, idproyecto, idusuario):
        """
        Metodo de instancia constructor que inicializa los parametros del objeto proyectousuario
        @type self: proyectousuario
        @param self: referencia al objeto que llama el metodo en este caso proyectousuario.
        @type idproyecto: Integer
        @param idproyecto: campo que almacenara el id del proyecto.
        @type idusuario: Integer
        @param idusuario: campo que almacenara el id del usuario.
        """
        self.idproyecto = idproyecto
        self.idusuario = idusuario
