Ext.define('sap.permisoConsultaStore', {
    extend:   'Ext.data.Store',
    alias:    'sap.permisoConsultaStore',
    autoLoad: true,
    pageSize: 20,
    storeId:  'permisoStore',
    fields:   ['id', 'nombre', 'descripcion','accion'],
    
    proxy: {
        type: 'ajax',
        url:  '/consultar_permiso',
        reader: {
            type: 'json',
            root: 'data',
            totalProperty: 'total'
        }
    }
});
