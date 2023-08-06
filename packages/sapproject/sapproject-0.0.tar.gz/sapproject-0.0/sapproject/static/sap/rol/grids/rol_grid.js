Ext.define('sap.rolGrid', {
    extend: 'Ext.grid.Panel',
    alias : 'sap.rolGrid',
    
    name:       'rol_grid',
    autoload:   true,
    autoScroll: true,
    border:     false,
    height:     320,
    forceFit:   true,
    
    initComponent: function() {
        var self = this;
        this.store = Ext.create('sap.rolConsultaStore');
        this.layout = {
            type:  'fit',
            align: 'center'
        };
        this.columns = [
            { header: 'Id', flex: 0, dataIndex: 'id'},
            { header: 'Nombre del Rol', flex: 0, dataIndex: 'nombre' },
            { header: 'Descripcion', flex: 0, dataIndex: 'descripcion'}
        ];
        this.tbar = Ext.create('Ext.PagingToolbar', {
            store:       this.store,
            displayInfo: true,
            pageSize:    10,
            displayMsg:  'Total de elementos : {2}',
            emptyMsg:    "<b>No hay datos que mostrar</b>",
            items: ['-',{
                xtype:   'button',
                grid:    self,
                text:    '<b>Ver permisos<b>',
                id:      'consulta_permisos_btn_grid',
                iconCls: 'details-icon',
                handler: this.form_permiso_x_rol_handler
            }]
        });
        this.callParent(arguments);
    },
    
    form_permiso_x_rol_handler : function(){
        var records = this.grid.getSelectionModel().getSelection();
        var id_rol  = records[0].data.id;
        var panel   = Ext.create('sap.PermisoPorRolPanel');
        panel.items.getAt(0).setValue(id_rol);
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
