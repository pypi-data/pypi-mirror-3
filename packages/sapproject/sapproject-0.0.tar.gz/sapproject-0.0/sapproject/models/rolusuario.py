from base import *
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref

class RolUsuario(Base):
    """
    Clase que crea la tabla RolUsuario que permite las relaciones entre la tabla Rol y la tabla Usuario 
    """
    __tablename__ = 'rolusuario'
    idrol     = Column(Integer, ForeignKey('rol.id'), primary_key=True)
    idusuario = Column(Integer, ForeignKey('usuario.id'), primary_key=True)
    usuario   = relationship("Usuario", backref="roles")
    # rol
    
    def __init__(self, idrol, idusuario):
        """
        Metodo de instancia constructor que inicializa los parametros del objeto rolusuario.
        @type self: rolusuario.
        @param self: referencia al objeto que llama el metodo en este caso rolusuario.
        @type idrol: Integer
        @param idrol: campo que almacenara el id del rol.
        @type idusuario: Integer
        @param idusuario: campo que almacenara el id del usuario.
        """ 
        self.idrol = idrol
        self.idusuario = idusuario
