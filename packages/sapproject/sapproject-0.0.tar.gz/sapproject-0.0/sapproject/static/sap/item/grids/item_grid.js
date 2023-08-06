Ext.define('sap.itemGrid', {
    extend: 'Ext.grid.Panel',
    alias : 'sap.itemGrid',
    
    name:        'item_grid',
    autoload:    true,
    autoSciteml: true,
    border:      false,
    height:      320,
    forceFit:    true,
    
    initComponent: function() {
        var self    = this;
        this.store  = Ext.create('sap.itemConsultaStore');
        this.layout = {
            type:  'fit',
            align: 'center'
        };
        this.columns = [
            { header: 'Id', flex: 0, dataIndex: 'id'},
            { header: 'Nombre del Item', flex: 0, dataIndex: 'nombre'},
            { header: 'Descripcion', flex: 0, dataIndex: 'descripcion'},
            { header: 'Version', flex: 0, dataIndex: 'version'},
            { header: 'Prioridad', flex: 0, dataIndex: 'prioridad'},
            { header: 'Complejidad', flex: 0, dataIndex: 'complejidad'},
            { header: 'Estado', flex: 0, dataIndex: 'estado'}
        ];
        this.tbar = Ext.create('Ext.PagingToolbar', {
            store:       this.store,
            displayInfo: true,
            pageSize:    10,
            displayMsg:  'Total de elementos : {2}',
            emptyMsg:    "<b>No hay datos que mostrar</b>"
        });
        this.callParent(arguments);
    }
});
