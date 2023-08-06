from base import *
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref

class RolPermiso(Base):
    """
    Clase que crea la tabla RolPermiso que permite las relaciones entre la tabla Rol y la tabla Permiso 
    """
    __tablename__ = 'rolpermiso'
    idrol     = Column(Integer, ForeignKey('rol.id'), primary_key=True)
    idpermiso = Column(Integer, ForeignKey('permiso.id'), primary_key=True)
    permiso   = relationship("Permiso", backref="roles")
    # rol
    
    def __init__(self, idrol, idpermiso):
        """
        Metodo de instancia constructor que inicializa los parametros del objeto rolpermiso.
        @type self: rolpermiso.
        @param self: referencia al objeto que llama el metodo en este caso rolpermiso.
        @type idrol: Integer
        @param idrol: campo que almacenara el id del rol.
        @type idpermiso: Integer
        @param idpermiso: campo que almacenara el id del permiso.
        """
        self.idrol = idrol
        self.idpermiso = idpermiso
