Ext.define('sap.RolPorUsuarioPanel', {
    extend: 'Ext.Panel',
    alias : 'sap.RolPorUsuarioPanel',
    
    title :     'Roles',
    id:         'panel_rol_x_usuario',
    name:       'panel_rol_x_usuario',
    layout:     'fit',
    frame:      true,
    closable:   false,
    border:     false,
    autoScroll: true,
    
    initComponent: function() {
        var grid = Ext.create('Ext.grid.Panel',{
            autoScroll: true,
            border:     false,
            forceFit:   true,
            layout:     'fit',
            store:      Ext.create('sap.rolConsultaStore',{
                storeId: 'store-lista-roles-x-usuario',
                autoLoad: false,
                proxy: {
                    type: 'ajax',
                    url:  '/consulta_rol_x_usuario',
                    reader: {
                        type: 'json',
                        root: 'data',
                        totalProperty: 'total'
                    }
                }
            }),
            columns: [
            { header: 'Id', flex: 0, dataIndex: 'id'},
            { header: 'Nombre del Rol', flex: 0, dataIndex: 'nombre' },
            { header: 'Descripcion', flex: 0, dataIndex: 'descripcion'}        ]
        });
        
        this.items = [{
            xtype: 'hiddenfield',
            name:  'id_usuario'
        },
        grid ];
        this.callParent(arguments);
    },
    
    llenar_grid: function() {
        var id_usuario = this.items.getAt(0).getValue();
        var store = Ext.data.StoreManager.lookup('store-lista-roles-x-usuario');
        store.load({
            params: {
                id_usuario : id_usuario
            }
        });
    }
});
