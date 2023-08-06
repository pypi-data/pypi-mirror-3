 Ext.define('sap.crearItemParamsPanel', {
    extend: 'Ext.Panel',
    alias : 'sap.crearItemParamsPanel',

    id:         'crear_items_params_panel',
    name:       'crear_items_params_panel',
    layout:     'vbox',
    height: 100,
    frame:      true,
    closable:   false,
    border:     false,
  
    initComponent: function() {
        this.items = [{
            xtype:      'combo',
            id:         'combo_crear_en_fase',
            fieldLabel: '<b>Crear en fase</b>',
            width: 300,
            margin: '2 2 2 2'
        }, {
            xtype:      'combo',
            id:         'combo_tipo_de_item',
            fieldLabel: '<b>Tipo de item</b>',
            width: 300,
            margin: '2 2 2 2'
        }];
        this.callParent(arguments);
    }
});
