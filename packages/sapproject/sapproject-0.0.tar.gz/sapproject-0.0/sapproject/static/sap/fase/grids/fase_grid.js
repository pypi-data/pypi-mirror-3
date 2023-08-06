 Ext.define('sap.faseGrid', {
    extend: 'Ext.grid.Panel',
    alias : 'sap.faseGrid',
    
    name:       'fase_grid',
    autoload:   true,
    autoScroll: true,
    border:     false,
    height:     320,
    forceFit:   true,
    
    initComponent: function() {
        this.store = Ext.create('sap.faseConsultaStore');
        this.layout = {
            type:  'fit',
            align: 'center'
        };
        this.columns = [
            { header: 'Id', flex: 0, dataIndex: 'id'},
            { header: 'Nombre de la Fase', flex: 0, dataIndex: 'nombre' },
            { header: 'Descripcion', flex: 0, dataIndex: 'descripcion'},
            { header: 'Fecha de Inicio', flex: 0, dataIndex: 'fechainicio' },
            { header: 'Fecha de Fin', flex: 0, dataIndex: 'fechafin' },
			{ header: 'Estado', flex: 0, dataIndex: 'estado' }
        ];
        this.tbar = Ext.create('Ext.PagingToolbar', {
            store: this.store,
            displayInfo: true,
            displayMsg: 'Total de elementos : {2}',
            emptyMsg:   "<b>No hay datos que mostrar</b>",
        }),
        this.callParent(arguments);
    }
});
