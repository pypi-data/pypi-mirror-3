Ext.define('sap.AtributoPorTipoitemPanel', {
    extend: 'Ext.Panel',
    alias : 'sap.AtributoPorTipoitemPanel',
    
    title :     'Atributos',
    id:         'panel_atributo_x_tipoitem',
    name:       'panel_atributo_x_tipoitem',
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
            store:      Ext.create('sap.atributoConsultaStore',{
                storeId: 'store-lista-atributos-x-tipoitem',
                autoLoad: false,
                proxy: {
                    type: 'ajax',
                    url:  '/consulta_atributo_x_tipoitem',
                    reader: {
                        type: 'json',
                        root: 'data',
                        totalProperty: 'total'
                    }
                }
            }),
            columns:    [
                { header: 'Id', flex: 0, dataIndex: 'id'},
                { header: 'Nombre del Atributo', flex: 0, dataIndex: 'nombre' },
                { header: 'Tipo de dato', flex: 0, dataIndex: 'tipodato'},
                { header: 'Valor por defecto', flex: 0, dataIndex: 'valordef'}
            ]
        });
        
        this.items = [{
            xtype: 'hiddenfield',
            name:  'id_tipoitem'
        },
        grid ];
        this.callParent(arguments);
    },
    
    llenar_grid: function() {
        var id_tipoitem = this.items.getAt(0).getValue();
        var store = Ext.data.StoreManager.lookup('store-lista-atributos-x-tipoitem');
        store.load({
            params: {
                id_tipoitem : id_tipoitem
            }
        });
    }
});
