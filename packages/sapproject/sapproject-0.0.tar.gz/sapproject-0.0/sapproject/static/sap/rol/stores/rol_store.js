Ext.define('sap.rolConsultaStore', {
    extend:   'Ext.data.Store',
    alias:    'sap.rolConsultaStore',
    autoLoad: true,
    pageSize: 20,
    storeId:  'rolStore',
    fields :  ['id', 'nombre', 'descripcion'],
    
    proxy: {
        type:     'ajax',
        url:      '/consultar_rol',
        reader: {
            type:          'json',
            root:          'data',
            totalProperty: 'total'
        }
    }
});
