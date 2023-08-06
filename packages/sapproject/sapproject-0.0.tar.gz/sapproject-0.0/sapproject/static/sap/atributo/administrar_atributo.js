Ext.define('sap.administrarAtributoPanel', {
    extend: 'Ext.form.Panel',
    alias : 'sap.administrarAtributoPanel',

    title :   'Administrar Atributo',
    id:       'panel_administrar_atributo',
    name:     'panel_administrar_atributo',
    layout:   'fit',
    frame:    true,
    closable: true,
    border:   false,
  
    initComponent: function() {
        var grid_atributos = Ext.create('sap.atributoGrid');
        this.items = [{
            xtype:      'form',
            title:      'Administrar Atributos',
            autoScroll: true,
            fieldDefaults: {
                blankText:     'Este campo no puede ser nulo',
                msgTarget:     'side',
                autoFitErrors: false
            },
            items: [{
                xtype:       'combo',
                margin:      '50 20 20 20',
                fieldLabel:  '<b>Buscar por</b>', 
                hiddenName:  'campo',  
                name:        'campo',
                editable:     false,
                mode:        'local',
                width:        480,
                labelWidth:   150,
                allowBlank:   false,
                displayField: 'opcion',
                valueField:   'campo',
                emptyText :   'Seleccione un campo', 
                store: new Ext.data.SimpleStore({  
                    id      : 0 ,  
                    fields  : ['id', 'opcion', 'campo'],  
                    data    : [
                        [1, 'Nombre del Atributo', 'nombre'],
                        [2, 'Tipo de dato', 'tipodato']
                    ]
                }),   
            }, {
                xtype:      'textfield',
                margin:     '5 20 20 20',
                name :      'igual',
                labelWidth:  150,
                width: 480,                
                fieldLabel: '<b>Igual a</b>',
                allowBlank: false
            },{
                xtype: 'button',
                text:  'Buscar',    
                x: 520,
                y: -42,
                iconCls: 'search-icon',
                handler:  this.form_buscar_handler            
            },
            grid_atributos
            ]
        }];
        
        this.buttons =[{
            text:    'Modificar',
            id:      'modificar_atributo_btn',
            iconCls: 'update-icon',
            hidden:  true,
            grid:    grid_atributos,
            handler: this.form_update_handler
        }, {
            text:    'Eliminar',
            id:      'eliminar_atributo_btn',
            iconCls: 'delete-icon',
            hidden:  true,
            grid:    grid_atributos,
            handler: this.form_delete_handler
        }, {
            text:    'Nuevo',
            id:      'nuevo_atributo_btn',
            iconCls: 'new-icon',
            hidden:  true,
            handler: this.form_new_handler
        }, {
            text:    'Cancelar',
            id:      'cancelar_atributo_btn',
            iconCls: 'cancel-icon',
            handler: this.form_cancel_handler
        }, {
            text:    'Limpiar',
            id:      'limpiar_atributo_btn',
            iconCls: 'clear-icon',
            handler: this.form_reset_handler
        }];
        
        this.listeners = {
            close : function() {
                // cerramos los paneles hijos abiertos (si hubiere)
                Ext.getCmp('area-central').cerrar_pestanhas([
                    'panel_modificar_atributo',
                    'panel_crear_atributo'
                ]);
            },
            render : function(){               
                // mostramos los botones segun los permisos
                var permisos = Ext.getCmp('funcionalidades').permisos;
                if(permisos.indexOf('cr:at') != -1){
                    Ext.getCmp('nuevo_atributo_btn').setVisible(true);
                }
                if(permisos.indexOf('mo:at') != -1){
                    Ext.getCmp('modificar_atributo_btn').setVisible(true);
                }
                if(permisos.indexOf('el:at') != -1){
                    Ext.getCmp('eliminar_atributo_btn').setVisible(true);
                }
            }
        };
        this.callParent(arguments);
    },
    
    form_delete_handler : function() {
        var records = this.grid.getSelectionModel().getSelection();
        if(records == null || records.length == 0){
            Ext.Msg.alert('ERROR','Debe seleccionar un registro para eliminar');
        }
        else{
            var grid = this.grid;
            Ext.Msg.show({
                title:'INFO',
                msg: 'Esta seguro que desea eliminar este registro?',
                buttons: Ext.Msg.YESNO,
                fn: function(btn){
                    if(btn == 'yes'){
                        // ELIMINACION
                        Ext.Ajax.request({
                            url:    '/eliminar_atributo',
                            params: {id : records[0].data.id},
                            success: function(response, opts) {
                                // recargamos los datos
                                Ext.Msg.alert('INFO','Registro eliminado con exito');
                                grid.getStore().load();
                            },
                            failure: function(response, opts) {
                                Ext.Msg.alert('ERROR','Ocurrio un problema al eliminar el registro!');
                            }
                        });
                    }
                }
            });
        }
    },
    
    form_update_handler : function() {
        var records = this.grid.getSelectionModel().getSelection();
        if(records == null || records.length == 0){
            Ext.Msg.alert('ERROR','Debe seleccionar un registro para modificar');
        }
        else{
            Ext.getCmp('area-central').agregar_pestanha('panel_modificar_atributo','sap.modificarAtributoPanel');
            Ext.getCmp('panel_modificar_atributo').form.loadRecord(records[0]);
        }
    },
    
    form_buscar_handler: function(){
        var form = this.up('form').getForm();
        var campo = form.findField('campo').getValue();
        var valor = form.findField('igual').getValue();
        if(valor == '' || campo == null){
            Ext.Msg.alert('ERROR','Los parametros de busqueda son ivalidos o estan incompletos');
        }
        else{
            Ext.StoreMgr.lookup('atributoStore').load({
                params: {
                    filtro : campo,
                    valor:   valor
                }
            });
        }
    },
    
    form_new_handler: function() {
        Ext.getCmp('area-central').agregar_pestanha('panel_crear_atributo','sap.crearAtributoPanel');
    },
    
    form_reset_handler: function() {
        // limpiamos el formulario y hacemos foco en el primer campo
        var form = this.up('form').getForm();
        form.reset();
        form.findField('campo').focus(true,100);
        // recargamos el store
        Ext.data.StoreManager.lookup('atributoStore').load();
    },
    
    form_cancel_handler: function() {
        this.up('panel').close();
    }
});
