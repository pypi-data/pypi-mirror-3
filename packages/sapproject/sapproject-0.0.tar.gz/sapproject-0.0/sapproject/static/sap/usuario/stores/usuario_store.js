Ext.define('sap.usuarioConsultaStore', {
    extend:   'Ext.data.Store',
    alias:    'sap.usuarioConsultaStore',
    autoLoad: true,
    pageSize: 20,
    storeId:  'usuarioStore',
    fields:   ['id', 'ci', 'nick', 'nombres','apellidos','direccion','email'],
    
    proxy: {
        type: 'ajax',
        url:  '/consultar_usuario',
        reader: {
            type:          'json',
            root:          'data',
            totalProperty: 'total'
        }
    }
});
