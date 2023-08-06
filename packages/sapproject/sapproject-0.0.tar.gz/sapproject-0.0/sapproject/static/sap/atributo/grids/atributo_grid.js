 Ext.define('sap.atributoGrid', {
    extend: 'Ext.grid.Panel',
    alias : 'sap.atributoGrid',
    
    name:       'atributo_grid',
    autoload:   true,
    autoScroll: true,
    border:     false,
    height:     320,
    forceFit:   true,
    
    initComponent: function() {
        this.store = Ext.create('sap.atributoConsultaStore');
        this.layout = {
            type:  'fit',
            align: 'center'
        };
        this.layout = {
            type:  'fit',
            align: 'center'
        };
        this.columns = [
            { header: 'Id', flex: 0, dataIndex: 'id'},
            { header: 'Nombre del Atributo', flex: 0, dataIndex: 'nombre' },
            { header: 'Tipo de dato', flex: 0, dataIndex: 'tipodato'},
            { header: 'Valor por defecto', flex: 0, dataIndex: 'valordef' }
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
