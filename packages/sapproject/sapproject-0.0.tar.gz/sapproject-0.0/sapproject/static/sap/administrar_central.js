Ext.define('sap.administrarCentralPanel', {
    extend: 'Ext.panel.Panel',
    alias : 'sap.administrarCentralPanel',

    title : 'Administrar Central',
    id:     'administrar_central',
    layout: 'vbox',
  
    initComponent: function() {
        this.items = [{
            xtype: 'clabel',
            id:    'administrar_proyecto',
            text:  'Administrar Proyecto',
            click: function(){
                Ext.getCmp('area-central').agregar_pestanha('panel_administrar_proyecto', 'sap.administrarProyectoPanel');
            }
        }, {
            xtype: 'clabel',
            id:    'administrar_usuario',
            text:  'Administrar Usuario',
            click: function(){
                Ext.getCmp('area-central').agregar_pestanha('panel_administrar_usuario', 'sap.administrarUsuarioPanel');
            }
        }, {
            xtype: 'clabel',
            id:    'administrar_rol',
            text:  'Administrar Rol',
            click: function(){
                Ext.getCmp('area-central').agregar_pestanha('panel_administrar_rol', 'sap.administrarRolPanel');
            }
        }, {
            xtype: 'clabel',
            id:    'administrar_permiso',
            text:  'Administrar Permiso',
            click: function(){
                Ext.getCmp('area-central').agregar_pestanha('panel_administrar_permiso', 'sap.administrarPermisoPanel');
            }
        }, {
            xtype: 'clabel',
            id:    'administrar_tipoitem',
            text:  'Administrar Tipo de Item',
            click: function(){
                Ext.getCmp('area-central').agregar_pestanha('panel_administrar_tipoitem', 'sap.administrarTipoitemPanel');
            }
        }, {
            xtype: 'clabel',
            id:    'administrar_atributo',
            text:  'Administrar Atributo',
            click: function(){
                Ext.getCmp('area-central').agregar_pestanha('panel_administrar_atributo', 'sap.administrarAtributoPanel');
            }
		}, {
            xtype: 'clabel',
            id:    'administrar_fase',
            text:  'Administrar Fase',
            click: function(){
                Ext.getCmp('area-central').agregar_pestanha('panel_administrar_fase', 'sap.administrarFasePanel');
            }
        }, {
            xtype: 'clabel',
            id:    'administrar_item',
            text:  'Administrar Item',
            click: function(){
                Ext.getCmp('area-central').agregar_pestanha('panel_administrar_item', 'sap.administrarItemPanel');
            }
        }];
        this.callParent(arguments);
    },
    
    ocultar_elementos : function(){
        var items = this.items;
        for(var i=0;i<items.length;i++){
            items.getAt(i).setVisible(false);
        }
    }
});
