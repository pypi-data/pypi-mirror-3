Ext.define('sap.tipoitemConsultaStore', {
    extend:   'Ext.data.Store',
    alias:    'sap.tipoitemConsultaStore',
    autoLoad: true,
    pageSize: 20,
    storeId:  'tipoitemStore',
    fields:   ['id', 'nombre', 'descripcion', 'prefijo'],
    
    proxy: {
        type: 'ajax',
        url:  '/consultar_tipoitem',
        reader: {
            type:          'json',
            root:          'data',
            totalProperty: 'total'
        }
    }
});
