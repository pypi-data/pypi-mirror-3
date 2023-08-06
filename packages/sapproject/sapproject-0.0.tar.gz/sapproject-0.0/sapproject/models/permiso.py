from base import *
from sqlalchemy import Sequence

class Permiso(Base):
    """
    Clase que crea la tabla Permiso
    """
    __tablename__ = 'permiso'
    id          = Column(Integer, Sequence('permiso_id_seq'), primary_key=True)
    nombre      = Column(Text)
    descripcion = Column(Text)
    accion      = Column(Text)
    # roles

    def __init__(self, nombre, descripcion, accion):
        """
        Metodo de instancia constructor que inicializa los parametros del objeto permiso
        @type self: permiso
        @param self: referencia al objeto que llama el metodo en este caso permiso.
        @type nombre: Text
        @param nombre: campo que almacenara el nombre del permiso.
        @type descripcion: Text
        @param descripcion: campo que almacenara la descripcion del permiso.
        @type accion: Text
        @param accion: campo que almacenara la accion que realizara el permiso.
        """
        self.nombre      = nombre
        self.descripcion = descripcion
        self.accion      = accion
        
    def eliminar_dependencias(self):
        """
        Metodo de instancia que elimina todas los relaciones de un registro de la tabla Permisos
        para que pueda ser eliminado.
        @type self: permiso
        @param self: referencia al objeto que llama el metodo en este caso permiso.
        """
        # En tabla rolpermiso
        for r in self.roles:
            DBSession.delete(r)
