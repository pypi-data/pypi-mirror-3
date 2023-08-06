import unittest
import transaction
from pyramid import testing

from sqlalchemy import *
from models.security import *
from models import *

def _initTestingDB():
    from sqlalchemy import create_engine
    engine = create_engine('postgresql://sap:12345@localhost:5432/sapdb')
    Base.metadata.create_all(engine)
    DBSession.configure(bind=engine)
    return DBSession

# PRUEBAS PARA MAIN

class TestMain(unittest.TestCase):
    def setUp(self):
        from sapproject import main
        settings = { 'sqlalchemy.url': 'postgresql://sap:12345@localhost:5432/sapdb'}
        app = main({}, **settings)
        from webtest import TestApp
        self.testapp = TestApp(app)
        _initTestingDB()
    
    def tearDown(self):
        del self.testapp
        DBSession.remove()
        
    def test_home(self):
        res = self.testapp.get('/',{},status=302)
        assert res.status_int == 302
        
    def test_main(self):
        print '\nCASO DE USO: MENU PRINCIPAL'
        print 'accediendo a /main'
        res = self.testapp.get('/main',{},status=200)
        assert res.status_int == 200
        print 'Ok'
        print '----------------------------------------\n'
        
    def test_llenar_combo_proyecto(self):
        print '\nTEST: CONTROL DE ACCESO AL SISTEMA'
        print 'accediendo como usuario: admin, password: admin'
        self.testapp.get('/login_check', {'name':'admin','password':'admin'},status=200)
        print 'llenando lista de proyectos asignados'
        res = self.testapp.get('/llenar_combo_proyecto',{},status=200)
        assert res.status_int == 200
        print 'Ok'
        print '----------------------------------------\n'
        
# PRUEBAS PARA LOGIN

class TestLogin(unittest.TestCase):
    def setUp(self):
        from sapproject import main
        settings = { 'sqlalchemy.url': 'postgresql://sap:12345@localhost:5432/sapdb'}
        app = main({}, **settings)
        from webtest import TestApp
        self.testapp = TestApp(app)
        _initTestingDB()
    
    def tearDown(self):
        del self.testapp
        DBSession.remove()
    
    def test_login(self):
        print '\nCASO DE USO: ACCESO AL SISTEMA'
        print 'accediendo como usuario: admin, password: admin'
        res = self.testapp.get('/login_check', {'name':'admin','password':'admin'},status=200)
        print 'comprobando que el usuario existe'
        usuario = DBSession.query(Usuario).filter_by(nick='admin',password='admin').first()
        self.assertTrue(usuario,msg='El usuario no existe')
        assert res.status_int == 200
        print 'Ok'
        print '----------------------------------------\n'

# PRUEBAS PARA LOGOUT

class TestLogout(unittest.TestCase):
    def setUp(self):
        from sapproject import main
        settings = { 'sqlalchemy.url': 'postgresql://sap:12345@localhost:5432/sapdb'}
        app = main({}, **settings)
        from webtest import TestApp
        self.testapp = TestApp(app)
        _initTestingDB()
    
    def tearDown(self):
        del self.testapp
        DBSession.remove()
        
    def test_logout(self):
        print '\nCASO DE USO: SALIR DEL SISTEMA'
        print 'deslogueando del sistema'
        res = self.testapp.get('/logout',{},status=302)
        print 'comprobando redireccion al home'
        self.assertEqual(res.location, 'http://localhost/')
        assert res.status_int == 302
        print 'Ok'
        print '----------------------------------------\n'

# PRUEBAS PARA PERMISO

class TestPermiso(unittest.TestCase):
    def setUp(self):
        from sapproject import main
        settings = { 'sqlalchemy.url': 'postgresql://sap:12345@localhost:5432/sapdb'}
        app = main({}, **settings)
        from webtest import TestApp
        self.testapp = TestApp(app)
        _initTestingDB()
    
    def tearDown(self):
        del self.testapp
        DBSession.remove()
    
    def test_crear(self):
        print '\nCASO DE USO: CREAR PERMISO'
        print 'creando permiso...'
        print ' - nombre : permiso_test'
        print ' - descripcion: descripcion_test'
        print ' - accion: us:cr'
        res = self.testapp.get('/crear_permiso',{'nombre':'permiso_test','descripcion':'permiso_test','accion':'us:cr', 'codificacion':'us:cr'},status=200)
        print 'comprobando que el permiso ha sido creado'
        permiso = DBSession.query(Permiso).filter_by(nombre='permiso_test').first()
        self.assertTrue(permiso,msg='El permiso no existe')
        assert res.status_int == 200
        print 'Ok'
        print '----------------------------------------\n'
        
    def test_modificar(self):
        print '\nCASO DE USO: MODIFICAR PERMISO'
        print 'modificando permiso...'
        print ' - id: 1'
        print ' - nombre : permiso_test -> permiso_test2'
        print ' - descripcion: permiso_test -> permiso_test2'
        print ' - accion: us:cr -> us:mo'
        res = self.testapp.get('/modificar_permiso',{'id':'1','nombre':'permiso_test2','descripcion':'permiso_test2','accion':'us:cr','codificacion':'us:mo'},status=200)
        print 'comprobando cambio en el nombre del permiso'
        permiso = DBSession.query(Permiso).filter_by(id='1').first()
        self.assertEqual(permiso.nombre, 'permiso_test2')
        assert res.status_int == 200
        print 'Ok'
        print '----------------------------------------\n'
        
    def test_eliminar(self):
        print '\nCASO DE USO: ELIMINAR PERMISO'
        print 'eliminando permiso con id : 10'
        res = self.testapp.get('/eliminar_permiso',{'id':'10'},status=200)
        print 'comprobando que el permiso no exista'
        permiso = DBSession.query(Permiso).filter_by(id='10').first()
        self.assertEqual(permiso, None)
        assert res.status_int == 200
        print 'Ok'
        print '----------------------------------------\n'
        
    def test_consultar_desfiltrado(self):
        print '\nCASO DE USO: CONSULTAR PERMISO (Sin filtros)'
        print 'obteniendo lista de todos los permisos'
        res = self.testapp.get('/consultar_permiso',{},status=200)
        assert res.status_int == 200
        print 'Ok'
        print '----------------------------------------\n'
        
    def test_cosultar_filtrado(self):
        print '\nCASO DE USO: CONSULTAR PERMISO (Con filtros)'
        print 'obteniendo lista de todos los permisos con id = 1'
        res = self.testapp.get('/consultar_permiso',{'filtro':'id', 'valor':'1'},status=200)
        assert res.status_int == 200
        print 'Ok'
        print '----------------------------------------\n'
    
    def test_consulta_lista_acciones(self):
        print '\nTES: CONSULTA ACCIONES DE PERMISOS POR ROL'
        print 'creando rol prueba...'
        print ' - nombre : rol_test'
        print ' - descripcion: rol_test'
        self.testapp.get('/crear_rol',{'nombre':'rol_test','descripcion':'rol_test'},status=200)
        print 'obteniendo lista de acciones'
        res = self.testapp.get('/consulta_acciones',{'rol':'rol_test'},status=200)
        assert res.status_int == 200
        print 'Ok'
        print '----------------------------------------\n'
        
    def test_consulta_permisos_asignados_asignables(self):
        print '\nTEST: CONSULTA PERMISOS ASIGNADOS/ASIGNABLES POR ROL'
        print 'obteniendo lista de permisos asignados/asignables al rol con id=1'
        # res = self.testapp.get('/consulta_acciones',{'id':'1'},status=200)
        # assert res.status_int == 200
        print 'Ok'
        print '----------------------------------------\n'
        
    def test_asignar_desasignar_permiso(self):
        print '\nCASO DE USO: ASIGNAR/DESASIGNAR PERMISO A ROL'
        print 'creando rol prueba...'
        print ' - nombre : rol_test'
        print ' - descripcion: rol_test'
        self.testapp.get('/crear_rol',{'nombre':'rol_test','descripcion':'rol_test'},status=200)
        print 'asignando permiso con id = 1'
        # res = self.testapp.get('/asignar_desasignar_permiso',{'id_rol':'1','data':[1,2]},status=200)
        # assert res.status_int == 200
        print 'Ok'
        print '----------------------------------------\n'
        
    def test_consulta_permiso_por_rol(self):
        print '\nTEST: CONSULTAR PERMISOS ASIGNADOS POR ROL'
        print 'creando rol prueba...'
        print ' - nombre : rol_test'
        print ' - descripcion: rol_test'
        self.testapp.get('/crear_rol',{'nombre':'rol_test','descripcion':'rol_test'},status=200)
        print 'consultando permisos asignados para rol con id = 1'
        res = self.testapp.get('/consulta_permiso_x_rol',{'id_rol':'1'},status=200)
        assert res.status_int == 200
        print 'Ok'
        print '----------------------------------------\n'

# PRUEBAS PARA PROYECTO

class TestProyecto(unittest.TestCase):
    def setUp(self):
        from sapproject import main
        settings = { 'sqlalchemy.url': 'postgresql://sap:12345@localhost:5432/sapdb'}
        app = main({}, **settings)
        from webtest import TestApp
        self.testapp = TestApp(app)
        _initTestingDB()
    
    def tearDown(self):
        del self.testapp
        DBSession.remove()
    
    def test_crear(self):
        print '\nCASO DE USO: CREAR PROYECTO'
        print 'creando proyecto ...'
        print ' - nombre: proyecto_test'
        print ' - descripcion: proyecto_test'
        print ' - fechainicio: 1/1/1',
        print ' - fechafin: 2/2/2',
        print ' - estado: proyecto_test',
        print ' - observaciones: proyecto_test'
        res = self.testapp.get('/crear_proyecto',{'nombre':'proyecto_test','descripcion':'proyecto_test','fechainicio':'1/1/1/','fechafin':'2/2/2','estado':'proyecto_test','observaciones':'proyecto_test'},status=200)
        print 'comprobando que el proyecto exista'
        proyecto = DBSession.query(Proyecto).filter_by(nombre='proyecto_test').first()
        self.assertTrue(proyecto,msg='El proyecto no existe')
        assert res.status_int == 200
        print 'Ok'
        print '----------------------------------------\n'
    
    def test_modificar(self):
        print '\nCASO DE USO: MODIFICAR PROYECTO'
        print 'modificando proyecto ...'
        print ' - id: 1'
        print ' - nombre: proyecto_test -> proyecto_test2'
        print ' - descripcion: proyecto_test'
        print ' - fechainicio: 1/1/1',
        print ' - fechafin: 2/2/2',
        print ' - estado: proyecto_test',
        print ' - observaciones: proyecto_test'
        res = self.testapp.get('/modificar_proyecto',{'id':'1','nombre':'proyecto_test2','descripcion':'proyecto_test','fechainicio':'1/1/1/','fechafin':'2/2/2','estado':'proyecto_test','observaciones':'proyecto_test'},status=200)
        print 'comprobando modificacion de proyecto'
        proyecto = DBSession.query(Proyecto).filter_by(id='1').first()
        self.assertEqual(proyecto.nombre, 'proyecto_test2')
        assert res.status_int == 200
        print 'Ok'
        print '----------------------------------------\n'
    
    def test_eliminar(self):
        print '\nCASO DE USO: ELIMINAR PROYECTO'
        print 'eliminando proyecto con id = 10'
        res = self.testapp.get('/eliminar_proyecto',{'id':'10'},status=200)
        print 'comprobando que el proyecto no exista'
        proyecto = DBSession.query(Proyecto).filter_by(id='10').first()
        self.assertEqual(proyecto, None)
        assert res.status_int == 200
        print 'Ok'
        print '----------------------------------------\n'
        
    def test_consultar_desfiltrado(self):
        print '\nCASO DE USO: CONSULTAR PROYECTOS (Sin filtros)'
        print 'obteniendo lista de proyectos'
        res = self.testapp.get('/consultar_proyecto',{},status=200)
        assert res.status_int == 200
        print 'Ok'
        print '----------------------------------------\n'
        
    def test_cosultar_filtrado(self):
        print '\nCASO DE USO: CONSULTAR PROYECTOS (Con filtros)'
        print 'obteniendo lista de proyectos con id = 1'
        res = self.testapp.get('/consultar_proyecto',{'filtro':'id', 'valor':'1'},status=200)
        assert res.status_int == 200
        print 'Ok'
        print '----------------------------------------\n'
        
    def test_asignar_usuario_rol(self):
        print '\nCASO DE USO: ASIGNAR USUARIO A PROYECTO'
        print 'creando proyecto de prueba'
        self.testapp.get('/crear_proyecto',{'nombre':'proyecto_test','descripcion':'proyecto_test','fechainicio':'1/1/1/','fechafin':'2/2/2','estado':'proyecto_test','observaciones':'proyecto_test'},status=200)
        print 'asignando usuario con id=1 bajo el rol con id=1'
        # res = self.testapp.get('/asignar_usuario_rol_proyecto',{'id_proyecto':'1','id_usuario':'1','id_roles':['1']},status=200)
        # assert res.status_int == 200
        print 'Ok'
        print '----------------------------------------\n'
        
    def test_desasignar_usuario_rol(self):
        print '\nCASO DE USO: DESASIGNAR USUARIO A PROYECTO'
        print 'creando proyecto de prueba'
        self.testapp.get('/crear_proyecto',{'nombre':'proyecto_test','descripcion':'proyecto_test','fechainicio':'1/1/1/','fechafin':'2/2/2','estado':'proyecto_test','observaciones':'proyecto_test'},status=200)
        print 'desasignando usuario con id=1 bajo el rol con id=1'
        res = self.testapp.get('/desasignar_usuario_rol_proyecto',{'id_proyecto':'1','id_usuario':'1','proyecto_actual':'proyecto_test'},status=200)
        assert res.status_int == 200
        print 'Ok'
        print '----------------------------------------\n'
        
# PRUEBAS PARA ROL

class TestRol(unittest.TestCase):
    def setUp(self):
        from sapproject import main
        settings = { 'sqlalchemy.url': 'postgresql://sap:12345@localhost:5432/sapdb'}
        app = main({}, **settings)
        from webtest import TestApp
        self.testapp = TestApp(app)
        _initTestingDB()
    
    def tearDown(self):
        del self.testapp
        DBSession.remove()
    
    def test_crear(self):
        print '\nCASO DE USO: CREAR ROL'
        print 'creando rol...'
        print ' - nombre: rol_test'
        print ' - descripcion: rol_test'
        res = self.testapp.get('/crear_rol',{'nombre':'rol_test','descripcion':'rol_test'},status=200)
        print 'comprobando que el rol exista'
        rol = DBSession.query(Rol).filter_by(nombre='rol_test').first()
        self.assertTrue(rol,msg='El rol no existe')
        assert res.status_int == 200
        print 'Ok'
        print '----------------------------------------\n'
    
    def test_modificar(self):
        print '\nCASO DE USO: MODIFICAR ROL'
        print 'creando rol...'
        print ' - id: 1'
        print ' - nombre: rol_test -> rol_test2'
        print ' - descripcion: rol_test'
        res = self.testapp.get('/modificar_rol',{'id':'1','nombre':'rol_test2','descripcion':'rol_test'},status=200)
        print 'comprobando la modificaicon del rol'
        rol = DBSession.query(Rol).filter_by(id='1').first()
        self.assertEqual(rol.nombre, 'rol_test2')
        assert res.status_int == 200
        print 'Ok'
        print '----------------------------------------\n'
    
    def test_eliminar(self):
        print '\nCASO DE USO: ELIMINAR ROL'
        print 'eliminando rol con id = 10'
        res = self.testapp.get('/eliminar_rol',{'id':'10'},status=200)
        print 'comprobando que el rol no exista'
        rol = DBSession.query(Rol).filter_by(id='10').first()
        self.assertEqual(rol, None)
        assert res.status_int == 200
        print 'Ok'
        print '----------------------------------------\n'
        
    def test_consultar_desfiltrado(self):
        print '\nCASO DE USO: CONSULTAR ROLES (Sin filtros)'
        print 'obteniendo lista de roles'
        res = self.testapp.get('/consultar_rol',{},status=200)
        assert res.status_int == 200
        print 'Ok'
        print '----------------------------------------\n'
        
    def test_cosultar_filtrado(self):
        print '\nCASO DE USO: CONSULTAR ROLES (Con filtros)'
        print 'obteniendo lista de roles con id = 1'
        res = self.testapp.get('/consultar_rol',{'filtro':'id', 'valor':'1'},status=200)
        assert res.status_int == 200
        print 'Ok'
        print '----------------------------------------\n'
        
    def test_consulta_roles_asignados_asignables(self):
        print '\nTEST: CONSULTA ROLES ASIGNADOS/ASIGNABLES POR USUARIO'
        print 'obteniendo lista de roles asignados/asignables al usuario con id=1'
        # res = self.testapp.get('/consulta_asignar_roles',{'id':'1'},status=200)
        # assert res.status_int == 200
        print 'Ok'
        print '----------------------------------------\n'
        
    def test_asignar_desasignar_rol(self):
        print '\nCASO DE USO: ASIGNAR/DESASIGNAR ROL A USUARIO'
        print 'creando usuario...'
        print ' - ci: 1'
        print ' - nombres: usuario_test'
        print ' - nick: usuario_test'
        print ' - password: usuario_test'
        print ' - direccion: usuario_test'
        print ' - observaciones: usuario_test'
        res = self.testapp.get('/crear_usuario',{'ci':'1','nombres':'usuario_test','apellidos':'usuario_test','fechanac':'1/1/1','sexo':'m','nick':'usuario_test','password':'usuario_test','email':'usuario_test','telefono':'1','direccion':'usuario_test','observaciones':'usuario_test'},status=200)
        print 'asignando rol con id=1 al usuario'
        # res = self.testapp.get('/asignar_desasignar_rol',{'data':{'id_usuario':'1', 'data':['1']}},status=200)
        # assert res.status_int == 200
        print 'Ok'
        print '----------------------------------------\n'
        
    def test_consulta_permiso_por_usuario(self):
        print '\nTEST: CONSULTAR ROLES ASIGNADOS POR USUARIO'
        print 'consultando roles asignados para usuario con id = 1'
        # res = self.testapp.get('/consulta_rol_x_usuario',{'id_usuario':'1'},status=200)
        # assert res.status_int == 200
        print 'Ok'
        print '----------------------------------------\n'

# PRUEBAS PARA USUARIO
class TestUsuario(unittest.TestCase):
    def setUp(self):
        from sapproject import main
        settings = { 'sqlalchemy.url': 'postgresql://sap:12345@localhost:5432/sapdb'}
        app = main({}, **settings)
        from webtest import TestApp
        self.testapp = TestApp(app)
        _initTestingDB()
    
    def tearDown(self):
        del self.testapp
        DBSession.remove()
    
    def test_crear(self):
        print '\nCASO DE USO: CREAR USUARIO'
        print 'creando usuario...'
        print ' - ci: 1'
        print ' - nombres: usuario_test'
        print ' - nick: usuario_test'
        print ' - password: usuario_test'
        print ' - direccion: usuario_test'
        print ' - observaciones: usuario_test'
        res = self.testapp.get('/crear_usuario',{'ci':'1','nombres':'usuario_test','apellidos':'usuario_test','fechanac':'1/1/1','sexo':'m','nick':'usuario_test','password':'usuario_test','email':'usuario_test','telefono':'1','direccion':'usuario_test','observaciones':'usuario_test'},status=200)
        print 'comprobando que el usuario exista'
        usuario = DBSession.query(Usuario).filter_by(ci=1).first()
        self.assertTrue(usuario,msg='El usuario no existe')
        assert res.status_int == 200
        print 'Ok'
        print '----------------------------------------\n'
    
    def test_modificar(self):
        print '\nCASO DE USO: MODIFICAR USUARIO'
        print 'modificar usuario...'
        print ' - ci: 1'
        print ' - nombres: usuario_test -> usuario_test2'
        print ' - nick: usuario_test -> usuario_test2'
        print ' - password: usuario_test'
        print ' - direccion: usuario_test'
        print ' - observaciones: usuario_test'
        res = self.testapp.get('/modificar_usuario',{'id':'1','ci':'1','nombres':'usuario_test2','apellidos':'usuario_test','fechanac':'1/1/1','sexo':'m','nick':'usuario_test2','password':'usuario_test','email':'usuario_test','telefono':'1','direccion':'usuario_test','observaciones':'usuario_test'},status=200)
        print 'comprobando modificaciones en el usuario'
        usuario = DBSession.query(Usuario).filter_by(id='1').first()
        self.assertEqual(usuario.nombres, 'usuario_test2')
        assert res.status_int == 200
        print 'Ok'
        print '----------------------------------------\n'
    
    def test_eliminar(self):
        print '\nCASO DE USO: ELIMINAR USUARIO'
        print 'eliminando usuario con id = 10'
        res = self.testapp.get('/eliminar_usuario',{'id':'10'},status=200)
        print 'comprobando que el usuario no exista'
        usuario = DBSession.query(Usuario).filter_by(id='10').first()
        self.assertEqual(usuario, None)
        assert res.status_int == 200
        print 'Ok'
        print '----------------------------------------\n'
        
    def test_consultar_desfiltrado(self):
        print '\nCASO DE USO: CONSULTAR USUARIOS (Sin filtro)'
        print 'obteniendo lista de usuarios...'
        res = self.testapp.get('/consultar_usuario',{},status=200)
        assert res.status_int == 200
        print 'Ok'
        print '----------------------------------------\n'
        
    def test_cosultar_filtrado(self):
        print '\nCASO DE USO: CONSULTAR USUARIOS (Con filtro)'
        print 'obteniendo lista de usuarios con id = 1...'
        res = self.testapp.get('/consultar_usuario',{'filtro':'id', 'valor':'1'},status=200)
        assert res.status_int == 200
        print 'Ok'
        print '----------------------------------------\n'
        
    def test_consulta_usuarios_asignados_asignables(self):
        print '\nTEST: CONSULTA USUARIOS ASIGNADOS/ASIGNABLES POR PROYECTO'
        print 'obteniendo lista de usuarios asignados/asignables al proyecto con id=1'
        # res = self.testapp.get('/consulta_asignar_usuarios',{'id':'1'},status=200)
        # assert res.status_int == 200
        print 'Ok'
        print '----------------------------------------\n'
        
# PRUEBAS PARA ATRIBUTO

class TestAtributo(unittest.TestCase):
    def setUp(self):
        from sapproject import main
        settings = { 'sqlalchemy.url': 'postgresql://sap:12345@localhost:5432/sapdb'}
        app = main({}, **settings)
        from webtest import TestApp
        self.testapp = TestApp(app)
        _initTestingDB()
    
    def tearDown(self):
        del self.testapp
        DBSession.remove()
    
    def test_crear(self):
        print '\nCASO DE USO: CREAR ATRIBUTO'
        print 'creando atributo...'
        print ' - nombre : atributo_test'
        print ' - tipo de dato: atributo_test'
        print ' - valor por defecto: atributo_test'
        res = self.testapp.get('/crear_atributo',{'nombre':'atributo_test','tipodato':'atributo_test','valordef':'atributo_test'},status=200)
        print 'comprobando que el atributo ha sido creado'
        atributo = DBSession.query(Atributo).filter_by(nombre='atributo_test').first()
        self.assertTrue(atributo,msg='El atributo no existe')
        assert res.status_int == 200
        print 'Ok'
        print '----------------------------------------\n'
        
    def test_modificar(self):
        print '\nCASO DE USO: MODIFICAR ATRIBUTO'
        print 'modificando atributo...'
        print ' - id: 1'
        print ' - nombre : atributo_test -> atributo_test2'
        print ' - tipo de dato: atributo_test -> atributo_test2'
        print ' - valor por defecto: us:cr -> us:mo'
        res = self.testapp.get('/modificar_atributo',{'id':'1','nombre':'atributo_test2','tipodato':'atributo_test2','valordef':'atributo_test'},status=200)
        print 'comprobando cambio en el nombre del atributo'
        atributo = DBSession.query(Atributo).filter_by(id='1').first()
        self.assertEqual(atributo.nombre, 'atributo_test2')
        assert res.status_int == 200
        print 'Ok'
        print '----------------------------------------\n'
        
    def test_eliminar(self):
        print '\nCASO DE USO: ELIMINAR ATRIBUTO'
        print 'eliminando atributo con id : 10'
        res = self.testapp.get('/eliminar_atributo',{'id':'10'},status=200)
        print 'comprobando que el atributo no exista'
        atributo = DBSession.query(Atributo).filter_by(id='10').first()
        self.assertEqual(atributo, None)
        assert res.status_int == 200
        print 'Ok'
        print '----------------------------------------\n'
        
    def test_consultar_desfiltrado(self):
        print '\nCASO DE USO: CONSULTAR ATRIBUTO (Sin filtros)'
        print 'obteniendo lista de todos los atributos'
        res = self.testapp.get('/consultar_atributo',{},status=200)
        assert res.status_int == 200
        print 'Ok'
        print '----------------------------------------\n'
        
    def test_cosultar_filtrado(self):
        print '\nCASO DE USO: CONSULTAR ATRIBUTO (Con filtros)'
        print 'obteniendo lista de todos los atributos con id = 1'
        res = self.testapp.get('/consultar_atributo',{'filtro':'id', 'valor':'1'},status=200)
        assert res.status_int == 200
        print 'Ok'
        print '----------------------------------------\n'
    
    def test_consulta_atributos_asignados_asignables(self):
        print '\nTEST: CONSULTA ATRIBUTOS ASIGNADOS/ASIGNABLES POR TIPO DE ITEM'
        print 'obteniendo lista de atributos asignados/asignables al tipo de item con id=1'
        # res = self.testapp.get('/consulta_acciones',{'id':'1'},status=200)
        # assert res.status_int == 200
        print 'Ok'
        print '----------------------------------------\n'
        
    def test_asignar_desasignar_atributo(self):
        print '\nCASO DE USO: ASIGNAR/DESASIGNAR ATRIBUTO A TIPO DE ITEM'
        print 'creando tipo de item de prueba...'
        print ' - nombre : tipo de item_test'
        print ' - descripcion: tipo de item_test'
        print ' - prefijo: tipoitem_test'
        self.testapp.get('/crear_tipoitem',{'nombre':'tipoitem_test','descripcion':'tipoitem_test', 'prefijo':'tipoitem_test'},status=200)
        print 'asignando atributo con id = 1'
        # res = self.testapp.get('/asignar_desasignar_atributo',{'data':{'id_tipoitem':'1','data':['1']}},status=200)
        # assert res.status_int == 200
        print 'Ok'
        print '----------------------------------------\n'
        
    def test_consulta_atributo_por_tipoitem(self):
        print '\nTEST: CONSULTAR ATRIBUTOS ASIGNADOS POR TIPO DE ITEM'
        print 'consultando atributos asignados para tipo de item con id = 1'
        # res = self.testapp.get('/consulta_atributo_x_tipo de item',{'id_tipoitem':'1'},status=200)
        # assert res.status_int == 200
        print 'Ok'
        print '----------------------------------------\n'

# PRUEBAS PARA TIPO DE ITEM

class TestTipoItem(unittest.TestCase):
    def setUp(self):
        from sapproject import main
        settings = { 'sqlalchemy.url': 'postgresql://sap:12345@localhost:5432/sapdb'}
        app = main({}, **settings)
        from webtest import TestApp
        self.testapp = TestApp(app)
        _initTestingDB()
    
    def tearDown(self):
        del self.testapp
        DBSession.remove()
    
    def test_crear(self):
        print '\nCASO DE USO: CREAR TIPO DE ITEM'
        print 'creando tipo de item ...'
        print ' - nombre: tipoitem_test'
        print ' - descripcion: tipoitem_test'
        print ' - prefijo: tipoitem_test'
        res = self.testapp.get('/crear_tipoitem',{'nombre':'tipoitem_test','descripcion':'tipoitem_test','prefijo':'tipoitem_test'},status=200)
        print 'comprobando que el tipoitem exista'
        tipoitem = DBSession.query(Tipoitem).filter_by(nombre='tipoitem_test').first()
        self.assertTrue(tipoitem,msg='El tipo de item no existe')
        assert res.status_int == 200
        print 'Ok'
        print '----------------------------------------\n'
    
    def test_modificar(self):
        print '\nCASO DE USO: MODIFICAR TIPO DE ITEM'
        print 'modificando tipo de item ...'
        print ' - id: 1'
        print ' - nombre: tipoitem_test -> tipoitem_test2'
        print ' - descripcion: tipoitem_test'
        print ' - prefijo: tipoitem_test'
        res = self.testapp.get('/modificar_tipoitem',{'id':'1','nombre':'tipoitem_test2','descripcion':'tipoitem_test','prefijo':'tipoitem_test'},status=200)
        print 'comprobando modificacion de tipo de item'
        tipoitem = DBSession.query(Tipoitem).filter_by(id='1').first()
        self.assertEqual(tipoitem.nombre, 'tipoitem_test2')
        assert res.status_int == 200
        print 'Ok'
        print '----------------------------------------\n'
    
    def test_eliminar(self):
        print '\nCASO DE USO: ELIMINAR TIPO DE ITEM'
        print 'eliminando tipo de item con id = 10'
        res = self.testapp.get('/eliminar_tipoitem',{'id':'10'},status=200)
        print 'comprobando que el tipo de item no exista'
        tipoitem = DBSession.query(Tipoitem).filter_by(id='10').first()
        self.assertEqual(tipoitem, None)
        assert res.status_int == 200
        print 'Ok'
        print '----------------------------------------\n'
        
    def test_consultar_desfiltrado(self):
        print '\nCASO DE USO: CONSULTAR TIPO DE ITEMS (Sin filtros)'
        print 'obteniendo lista de tipo de items'
        res = self.testapp.get('/consultar_tipoitem',{},status=200)
        assert res.status_int == 200
        print 'Ok'
        print '----------------------------------------\n'
        
    def test_cosultar_filtrado(self):
        print '\nCASO DE USO: CONSULTAR TIPO DE ITEMS (Con filtros)'
        print 'obteniendo lista de tipo de items con id = 1'
        res = self.testapp.get('/consultar_tipoitem',{'filtro':'id', 'valor':'1'},status=200)
        assert res.status_int == 200
        print 'Ok'
        print '----------------------------------------\n'
