 Ext.define('sap.permisoGrid', {
    extend: 'Ext.grid.Panel',
    alias : 'sap.permisoGrid',
    
    name:       'permiso_grid',
    autoload:   true,
    autoScroll: true,
    border:     false,
    height:     320,
    forceFit:   true,
    
    initComponent: function() {
        this.store  = Ext.create('sap.permisoConsultaStore');
        this.layout = {
            type:  'fit',
            align: 'center'
        };
        this.columns = [
            { header: 'Id', flex: 0, dataIndex: 'id'},
            { header: 'Nombre del Permiso', flex: 0, dataIndex: 'nombre' },
            { header: 'Descripcion', flex: 0, dataIndex: 'descripcion'},
            { header: 'Accion', flex: 0, dataIndex: 'accion'}
        ];
        this.tbar = Ext.create('Ext.PagingToolbar', {
            store:       this.store,
            displayInfo: true,
            displayMsg:  'Total de elementos : {2}',
            emptyMsg:    "<b>No hay datos que mostrar</b>",
        }),
        this.callParent(arguments);
    }
});
