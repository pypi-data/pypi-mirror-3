 Ext.define('sap.tipoitemGrid', {
    extend: 'Ext.grid.Panel',
    alias : 'sap.tipoitemGrid',
    
    name:       'tipoitem_grid',
    autoload:   true,
    autoScroll: true,
    border:     false,
    height:     320,
    forceFit:   true,
    initComponent: function() {
          var self = this;    
        this.store  = Ext.create('sap.tipoitemConsultaStore');
        this.layout = {
            type:  'fit',
            align: 'center'
        };
        this.columns = [
            { header: 'Id', flex: 0, dataIndex: 'id'},
            { header: 'Nombre del Tipo de item', flex: 0, dataIndex: 'nombre' },
            { header: 'Descripcion', flex: 0, dataIndex: 'descripcion'},
            { header: 'Prefijo', flex: 0, dataIndex: 'prefijo' }
        ];
        this.tbar = Ext.create('Ext.PagingToolbar', {
            store:       this.store,
            displayInfo: true,
            displayMsg:  'Total de elementos : {2}',
            emptyMsg:    "<b>No hay datos que mostrar</b>",
            items: ['-',{
                xtype:   'button',
                grid:    self,
                text:    '<b>Ver atributos<b>',
                id:      'consulta_atributos_btn_grid',
                iconCls: 'details-icon',
                handler: this.form_atributo_x_tipoitem_handler
            }]
        });
        this.callParent(arguments);
    },
    
    form_atributo_x_tipoitem_handler : function(){
        var records = this.grid.getSelectionModel().getSelection();
        var id_tipoitem  = records[0].data.id;
        var panel   = Ext.create('sap.AtributoPorTipoitemPanel');
        panel.items.getAt(0).setValue(id_tipoitem);
        panel.llenar_grid();
        
        var win = Ext.create('Ext.Window',{
            modal :     true,
            autoScroll: true,
            height:     '80%',
            width:      '80%',
            frame:      false,
            border:     false,
            items:      [panel]
        });
        win.show();
    }
});
