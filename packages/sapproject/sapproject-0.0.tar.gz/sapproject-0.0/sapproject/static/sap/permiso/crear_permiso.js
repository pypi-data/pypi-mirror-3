var tipo_crear     = 0;
var accion_crear   = null;
var entidad1_crear = null;
var entidad2_crear = null;

Ext.define('sap.crearPermisoPanel', {
    extend: 'Ext.form.Panel',
    alias : 'sap.crearPermisoPanel',

    title :   'Crear Permiso',
    id:       'panel_crear_permiso',
    name:     'panel_crear_permiso',
    layout:   'fit',
    frame:    true,
    closable: true,
    border:   false,
  
    initComponent: function() {    
        var combo_entidad = {
            xtype:       'combo',
            id:          'combo_entidad',
            hiddenName:  'entidad',
            name:        'entidad',
            editable:     false,
            mode:        'local',
            displayField: 'entidad',
            valueField:   'codigo',
            emptyText:    'seleccione una accion_crear',
            store: Ext.create('Ext.data.ArrayStore',{
                fields: ['entidad' ,'codigo'],
                data:   [
                    ['Proyecto', 'pr'],
                    ['Usuario', 'us'],
                    ['Rol', 'ro'],
                    ['Permiso', 'pe']
                ]
            }),
            listeners:{
                select : function(combo){
                    var item = combo.getValue();
                    entidad1_crear = item;
                }
            }
        };
        
        var combo_asignadesasigna_2 = {
            xtype:       'combo',
            id:          'combo_asignadesasigna_2',
            hiddenName:  'entidad',
            name:        'entidad',
            editable:     false,
            mode:        'local',
            displayField: 'entidad',
            valueField:   'codigo',
            emptyText:    'seleccione una accion_crear',
            store: Ext.create('Ext.data.ArrayStore',{
                fields: ['entidad', 'codigo'],
                data:   [
                    ['Proyecto', 'pr'],
                    ['Usuario', 'us'],
                    ['Rol', 'ro']
                ]
            }),
            listeners:{
                select : function(combo){
                    var item = combo.getValue();
                    entidad2_crear = item;
                }
            }
        };
        
        var combo_asignadesasigna_1 = {
            xtype:       'combo',
            id:          'combo_asignadesasigna_1',
            hiddenName:  'entidad',
            name:        'entidad',
            editable:     false,
            mode:        'local',
            displayField: 'entidad',
            valueField:   'codigo',
            emptyText:    'seleccione una accion_crear',
            store: Ext.create('Ext.data.ArrayStore',{
                fields  : ['entidad', 'codigo'],
                data    : [
                    ['Usuario', 'us'],
                    ['Rol', 'ro'],
                    ['Permiso', 'pe']
                ]
            }),
            listeners:{
                select : function(combo){
                    var item = combo.getValue();
                    entidad1_crear = item;
                }
            }
        };
        
        var combo_accion_crear = {
            xtype:       'combo',
            fieldLabel:  '<b>Permiso para</b>', 
            hiddenName:  'permiso',  
            name:        'permiso',
            editable:     false,  
            mode:        'local',
            allowBlank:   false,   
            displayField: 'accion_crear',  
            valueField:   'codigo',
            emptyText:    'seleccione una opcion',
            store: Ext.create('Ext.data.ArrayStore',{  
                id      : 0 ,  
                fields  : ['accion_crear', 'codigo'],  
                data    : [
                    ['Crear', 'cr'],
                    ['Eliminar', 'el'],
                    ['Modificar', 'mo'],
                    ['Consultar', 'co'],
                    ['Asignar', 'as'],
                    ['Desasignar','de']
                ]
            }),
            listeners:{
                select : function(combo){
                    var item = combo.getValue();
                    accion_crear = item;
                    var cmp = null;
                    switch(item){
                        case 'cr':
                        case 'el':
                        case 'mo':
                        case 'co':
                            tipo_crear = 1;
                            entidad1_crear = null;
                            Ext.getCmp('combo_entidad').reset();
                            Ext.getCmp('combo_entidad').setVisible(true);
                            Ext.getCmp('combo_asignadesasigna_1').setVisible(false);
                            Ext.getCmp('combo_asignadesasigna_2').setVisible(false);
                            break;
                        case 'as':
                        case 'de':
                            tipo_crear = 2;
                            Ext.getCmp('combo_entidad').setVisible(false);
                            entidad1_crear = null;
                            Ext.getCmp('combo_asignadesasigna_1').reset();
                            Ext.getCmp('combo_asignadesasigna_1').setVisible(true);
                            entidad2_crear = null;
                            Ext.getCmp('combo_asignadesasigna_2').reset();
                            Ext.getCmp('combo_asignadesasigna_2').setVisible(true);
                            break;
                    }
                }
            }
        };
        this.items = [{
            xtype:      'form',
            title:      'Datos del Permiso',
            autoScroll: true,
            fieldDefaults: {
                blankText:     'Este campo no puede ser nulo',
                msgTarget:     'side',
                autoFitErrors: false,
                margin:        '5 20 20 20',
                width:         480,
                labelWidth:    150,
            },
            items: [{
                xtype:      'textfield',
                margin:     '50 20 20 20',
                name :      'nombre',
                fieldLabel: '<b>Nombre</b>',
                allowBlank: false
            }, {
                xtype:      'textfield',
                name :      'descripcion',             
                fieldLabel: '<b>Descripcion</b>',
            }, combo_accion_crear, combo_entidad, combo_asignadesasigna_1, combo_asignadesasigna_2],
            listeners: {
                render : function(){
                    Ext.getCmp('combo_entidad').setVisible(false);
                    Ext.getCmp('combo_asignadesasigna_1').setVisible(false);
                    Ext.getCmp('combo_asignadesasigna_2').setVisible(false);
                }
            }
        }];
        
        this.buttons =[{
            text:     'Guardar',
            iconCls:  'save-icon',
            handler:  this.form_submit_handler
        }, {
            text:    'Cancelar',
            iconCls: 'cancel-icon',            
            handler: this.form_cancel_handler
        }, {
            text:    'Limpiar',
            iconCls: 'clear-icon',
            handler: this.form_reset_handler
        }];
        
        this.listeners = {
            close : function(){
                // actualizamos el store
                var store = Ext.data.StoreManager.lookup('permisoStore');
                store.load();
                // volvemos al panel de administracion
                Ext.getCmp('area-central').agregar_pestanha('panel_administrar_permiso', null);
            }
        };
        
        this.callParent(arguments);
    },
    
    form_submit_handler: function(){
        var self = this;
        var form = self.up('form').getForm();
        if(form.isValid()){
            if(tipo_crear == 1 && entidad1_crear == null){
                Ext.Msg.alert('ERROR','Debe seleccionar una entidad');
                return;
            }
            if(tipo_crear == 2 && (entidad1_crear == null || entidad2_crear == null)){
                Ext.Msg.alert('ERROR','Los campos de la asociacion son incorrectos o estan incompletos');
                return;
            }
            permiso_codificado = accion_crear + ':' + entidad1_crear;
            if(entidad2_crear != null){
                permiso_codificado = permiso_codificado + '-' + entidad2_crear;
            }
            form.submit({
                method:    'POST',
                url:       '/crear_permiso',
                waitTitle: 'Connecting', 
                waitMsg:   'Sending data...',
                params:    {codificacion : permiso_codificado},
                success: function(form,action){
                    Ext.Msg.alert('INFO','Registro almacenado con exito!', function(btn, text){
                        if (btn == 'ok'){
                            self.up('panel').close();
                        }
                    });
                },
                failure: function(form, action){
                    Ext.Msg.alert('ERROR','Ocurrio un problema al guardar el registro!');
                }
            });
        }
    },
    
    form_reset_handler: function() {
        var form = this.up('form').getForm();
        form.reset();
        tipo_crear     = 0;
        accion_crear   = null;
        entidad1_crear = null;
        entidad2_crear = null;
        Ext.getCmp('combo_entidad').setVisible(false);
        Ext.getCmp('combo_asignadesasigna_1').setVisible(false);
        Ext.getCmp('combo_asignadesasigna_2').setVisible(false);
        form.findField('nombre').focus(true,100);
    },
    
    form_cancel_handler: function() {
        this.up('panel').close();
    }
});
