Ext.define('sap.PermisoPorRolPanel', {
    extend: 'Ext.Panel',
    alias : 'sap.PermisoPorRolPanel',
    
    title :     'Permisos',
    id:         'panel_permiso_x_rol',
    name:       'panel_permiso_x_rol',
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
            store:      Ext.create('sap.permisoConsultaStore',{
                storeId: 'store-lista-permisos-x-rol',
                autoLoad: false,
                proxy: {
                    type: 'ajax',
                    url:  '/consulta_permiso_x_rol',
                    reader: {
                        type: 'json',
                        root: 'data',
                        totalProperty: 'total'
                    }
                }
            }),
            columns:    [
                { header: 'Id', flex: 0, dataIndex: 'id'},
                { header: 'Nombre del Permiso', flex: 0, dataIndex: 'nombre' },
                { header: 'Descripcion', flex: 0, dataIndex: 'descripcion'},
                { header: 'Accion', flex: 0, dataIndex: 'accion'}
            ]
        });
        
        this.items = [{
            xtype: 'hiddenfield',
            name:  'id_rol'
        },
        grid ];
        this.callParent(arguments);
    },
    
    llenar_grid: function() {
        var id_rol = this.items.getAt(0).getValue();
        var store = Ext.data.StoreManager.lookup('store-lista-permisos-x-rol');
        store.load({
            params: {
                id_rol : id_rol
            }
        });
    }
});
