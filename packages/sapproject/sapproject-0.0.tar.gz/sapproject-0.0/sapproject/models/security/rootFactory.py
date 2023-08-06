from pyramid.security import Allow, Everyone, ALL_PERMISSIONS

"""
EL grupo admin corresponde a los usuarios habilitados para utilizar el
sistema sin importar el rol que tengan.
Les corresponde el permiso de 'admin' que lo habilita a ingresar a la
seccion principal del sistema.
"""
class RootFactory(object):
    __acl__ = [ (Allow, 'admin',  'admin') ]

    def __init__(self, request):
        pass
