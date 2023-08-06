from base import *
from sqlalchemy.orm import relationship
from sqlalchemy import Sequence

class Usuario(Base):
    """
    Clase que crea la tabla Usuario 
    """
    __tablename__    = 'usuario'
    id               = Column(Integer, Sequence('usuario_id_seq'), primary_key=True)
    ci               = Column(Integer, nullable=False, unique=True)
    nombres          = Column(Text, nullable=False)
    apellidos        = Column(Text, nullable=False)
    email            = Column(Text)
    telefono         = Column(Integer)
    direccion        = Column(Text)
    observaciones    = Column(Text)
    nick             = Column(Text, nullable=False, unique=True)
    password         = Column(Text, nullable=False)
    sexo             = Column(Text, nullable=False)
    fechanac         = Column(Text, nullable=False)
    # roles
    # proyectos
    roles_x_proyecto = relationship("ProyectoUsuarioRol")

    def __init__(self, ci, nombres, apellidos, nick, password, email, telefono, direccion, observaciones, sexo, fechanac):
        """
        Metodo de instancia constructor que inicializa los parametros del objeto usuario
        @type self: usuario
        @param self: referencia al objeto que llama el metodo en este caso usuario.
        @type ci: Integer
        @param ci: campo que almacenara la cedula del usuario.
        @type nombres: Text
        @param nombres: campo que almacenara los nombres del usuario.
        @type apellidos: Text
        @param apellidos: campo que almacenara los apellidos del usuario.
        @type email: Text
        @param email: campo que almacenara el correo electronico del usuario.
        @type telefono: Integer
        @param telefono: campo que almacenara el telefono del usuario.
        @type direccion: Text
        @param direccion: campo que almacenara la direccion del usuario.
        @type observaciones: Text
        @param observaciones: campo que almacenara alguna observacion sobre el usuario.
        @type nick: Text
        @param nick: campo que almacenara el nombre de usuario del usuario en el sistema.
        @type password: Text
        @param password: campo que almacenara la contrasenha del usuario en el sistema.
        @type sexo: Text
        @param sexo: campo que almacenara el sexo del usuario.
        @type fechanac: Date
        @param nick: campo que almacenara la fecha de nacimiento del usuario.
        """
        self.ci = ci
        self.nombres = nombres
        self.apellidos = apellidos
        self.nick = nick
        self.password = password
        self.email = email
        self.telefono = telefono
        self.direccion = direccion
        self.observaciones =observaciones
        self.sexo = sexo
        self.fechanac = fechanac
    
    def eliminar_dependencias(self):
        """
        Metodo de instancia que elimina todas los relaciones de un registro de la tabla Usuarios
        para que pueda ser eliminado.
        @type self: usuario
        @param self: referencia al objeto que llama el metodo en este caso usuario.
        """
        # En tabla proyectousuario
        for p in self.proyectos:
            DBSession.delete(p)
        # En tabla rolusuario
        for r in self.roles:
            DBSession.delete(r)
        # En tabla proyectousuariorol
        for ur in self.roles_x_proyecto:
            DBSession.delete(ur)

def groupfinder(userid, request):
    usuario = DBSession.query(Usuario).filter_by(nick=userid).first()
    if usuario is None:
        return None
    return ['admin']
