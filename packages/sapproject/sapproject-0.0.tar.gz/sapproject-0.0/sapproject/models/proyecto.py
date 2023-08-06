from base import *
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Sequence

class Proyecto(Base):
    """
    Clase que crea la tabla Proyecto 
    """
    __tablename__    = 'proyecto'
    id               = Column(Integer, Sequence('proyecto_id_seq'), primary_key=True)
    nombre           = Column(Text, nullable=False, unique=True)
    descripcion      = Column(Text)
    fechainicio      = Column(Date, nullable=False)
    fechafin         = Column(Date, nullable=False)
    estado           = Column(Text, nullable=False)
    nfases           = Column(Integer)
    complejidadtotal = Column(Integer)
    observaciones    = Column(Text)
    usuarios         = relationship("ProyectoUsuario", backref="proyecto")
    # roles
    # usuarios
    # fases
    usuarios_x_rol = relationship("ProyectoUsuarioRol")

    def __init__(self, nombre, descripcion, fechainicio, fechafin, estado,observaciones):
        """
        Metodo de instancia constructor que inicializa los parametros del objeto proyecto
        @type self: proyecto
        @param self: referencia al objeto que llama el metodo en este caso proyecto.
        @type nombre: Text
        @param nombre: campo que almacenara el nombre del proyecto.
        @type descripcion: Text
        @param descripcion: campo que almacenara la descripcion del proyecto.
        @type fechainicio: Date
        @param fechainicio: campo que almacenara la fecha de inicio del proyecto.
        @type fechafin: Text
        @param fechafin: campo que almacenara la fecha de fin del proyecto.
        @type estado: Text
        @param estado: campo que almacenara el estado del proyecto.
        @type observaciones: Text
        @param observaciones: campo que almacenara observaciones sobre el proyecto.
        """
        self.nombre = nombre
        self.descripcion = descripcion
        self.fechainicio = fechainicio
        self.fechafin = fechafin
        self.estado = estado
        self.observaciones = observaciones
        self.nfases = 0
        self.complejidadtotal = 0

    def eliminar_dependencias(self):
        """
        Metodo de instancia que elimina todas los relaciones de un registro de la tabla Proyectos
        para que pueda ser eliminado.
        @type self: proyecto
        @param self: referencia al objeto que llama el metodo en este caso proyecto.
        """
        # En tabla proyectousuario
        for u in self.usuarios:
            DBSession.delete(u)
        # En tabla proyectousuariorol
        for ur in self.usuarios_x_rol:
            DBSession.delete(ur)
