Ext.define('sap.faseConsultaStore', {
    extend:   'Ext.data.Store',
    alias:    'sap.faseConsultaStore',
    autoLoad: true,
    pageSize: 20,
    storeId:  'faseStore',
    fields:   ['id', 'nombre', 'descripcion', 'fechainicio','fechafin', 'estado'],
    
    proxy: {
        type: 'ajax',
        url:  '/consultar_fase',
        reader: {
            type:          'json',
            root:          'data',
            totalProperty: 'total'
        }
    }
});
