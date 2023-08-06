Ext.define('sap.proyectoConsultaStore', {
    extend:   'Ext.data.Store',
    alias:    'sap.proyectoConsultaStore',
    autoLoad: true,
    pageSize: 20,
    storeId:  'proyectoStore',
    fields:   ['id', 'nombre', 'descripcion', 'fechainicio','fechafin','estado'],
    
    proxy: {
        type: 'ajax',
        url:  '/consultar_proyecto',
        reader: {
            type:          'json',
            root:          'data',
            totalProperty: 'total'
        }
    }
});
