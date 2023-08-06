Ext.define('sap.atributoConsultaStore', {
    extend:   'Ext.data.Store',
    alias:    'sap.atributoConsultaStore',
    autoLoad: true,
    pageSize: 20,
    storeId:  'atributoStore',
    fields:   ['id', 'nombre', 'tipodato', 'valordef'],
    
    proxy: {
        type: 'ajax',
        url:  '/consultar_atributo',
        reader: {
            type:          'json',
            root:          'data',
            totalProperty: 'total'
        }
    }
});
