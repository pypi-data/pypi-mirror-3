from base import *
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref

class ProyectoUsuarioRol(Base):
    """
    Clase que crea la tabla PermisoUsuarioRol que permite las relaciones entre la tabla Usuario,la tabla Proyecto y la tabla Rol 
    """
    __tablename__ = 'proyectousuariorol'
    idproyecto = Column(Integer, ForeignKey('proyecto.id'), primary_key=True)
    idusuario  = Column(Integer, ForeignKey('usuario.id'), primary_key=True)
    idrol      = Column(Integer, ForeignKey('rol.id'), primary_key=True)
    proyecto   = relationship("Proyecto")
    rol        = relationship("Rol")
    
    def __init__(self, idproyecto, idusuario, idrol):
        """
        Metodo de instancia constructor que inicializa los parametros del objeto proyectousuariorol
        @type self: proyectousuariorol
        @param self: referencia al objeto que llama el metodo en este caso proyectousuariorol.
        @type idproyecto: Integer
        @param idproyecto: campo que almacenara el id del proyecto.
        @type idusuario: Integer
        @param idusuario: campo que almacenara el id del usuario.
        @type idrol: Integer
        @param idrol: campo que almacenara el id del rol.
        """
        self.idproyecto = idproyecto
        self.idusuario = idusuario
        self.idrol = idrol
