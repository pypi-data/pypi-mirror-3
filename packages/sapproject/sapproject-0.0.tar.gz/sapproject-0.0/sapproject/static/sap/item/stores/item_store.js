Ext.define('sap.itemConsultaStore', {
    extend:   'Ext.data.Store',
    alias:    'sap.itemConsultaStore',
    autoLoad: true,
    pageSize: 20,
    storeId:  'itemStore',
    fields :  ['id','nombre', 'descripcion', 'version', 'prioridad', 'complejidad', 'estado'],
    
    proxy: {
        type:     'ajax',
        url:      '/consultar_item',
        reader: {
            type:          'json',
            root:          'data',
            totalProperty: 'total'
        }
    }
});
