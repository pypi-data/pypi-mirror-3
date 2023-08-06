Ext.define('sap.usuarioGrid', {
    extend: 'Ext.grid.Panel',
    alias : 'sap.usuarioGrid',
    
    name:       'usuario_grid',
    autoload:   true,
    autoScroll: true,
    border:     false,
    height:     320,
    forceFit:   true,
    
    initComponent: function() {
        var self = this;
        this.store = Ext.create('sap.usuarioConsultaStore');
        this.layout = {
            type:  'fit',
            align: 'center'
        };
        this.columns = [
            { header: 'Id', flex: 0, dataIndex: 'id'},
            { header: 'Cedula', flex: 0, dataIndex: 'ci' },
            { header: 'Nombre de Usuario', flex: 0, dataIndex: 'nick'},
            { header: 'Nombres', flex: 0, dataIndex: 'nombres' },
            { header: 'Apellidos', flex: 0, dataIndex: 'apellidos' },
            { header: 'Direccion', flex: 0, dataIndex: 'direccion' },
            { header: 'Email', flex: 0, dataIndex: 'email' }
        ];
        this.tbar = Ext.create('Ext.PagingToolbar', {
            store: this.store,
            displayInfo: true,
            displayMsg: 'Total de elementos : {2}',
            emptyMsg: "<b>No hay datos que mostrar</b>",
            items: ['-',{
                xtype:   'button',
                grid:    self,
                text:    '<b>Ver roles<b>',
                id:      'consulta_roles_btn_grid',
                iconCls: 'details-icon',
                handler: this.form_rol_x_usuario_handler
            }]
        });
        this.callParent(arguments);
    },
    
    form_rol_x_usuario_handler : function(){
        var records = this.grid.getSelectionModel().getSelection();
        var id_usuario  = records[0].data.id;
        var panel   = Ext.create('sap.RolPorUsuarioPanel');
        panel.items.getAt(0).setValue(id_usuario);
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
