from base import *
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Sequence

class Rol(Base):
    """
    Clase que crea la tabla Rol 
    """
    __tablename__ = 'rol'
    id          = Column(Integer, Sequence('rol_id_seq'), primary_key=True)
    nombre      = Column(Text, nullable=False, unique=True)
    descripcion = Column(Text)
    permisos    = relationship("RolPermiso", backref="rol")
    usuarios    = relationship("RolUsuario", backref="rol")
    # usuarios
    # proyectos
    usuarios_x_proyecto = relationship("ProyectoUsuarioRol")

    def __init__(self, nombre, descripcion):
        """
        Metodo de instancia constructor que inicializa los parametros del objeto rol
        @type self: rol
        @param self: referencia al objeto que llama el metodo en este caso rol.
        @type nombre: Text
        @param nombre: campo que almacenara el nombre del rol.
        @type descripcion: Text
        @param descripcion: campo que almacenara la descripcion del rol.
        """
        self.nombre      = nombre
        self.descripcion = descripcion
    
    def eliminar_dependencias(self):
        """
        Metodo de instancia que elimina todas los relaciones de un registro de la tabla Rol
        para que pueda ser eliminado.
        @type self: rol
        @param self: referencia al objeto que llama el metodo en este caso rol.
        """
        # En tabla rolusuario
        for u in self.usuarios:
            DBSession.delete(u)
        # En tabla rolpermiso
        for p in self.permisos:
            DBSession.delete(p)
       # En tabla proyectousuariorol
        for up in self.usuarios_x_proyecto:
            DBSession.delete(up)
