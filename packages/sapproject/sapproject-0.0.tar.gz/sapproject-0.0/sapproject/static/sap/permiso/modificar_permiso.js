var tipo_modificar     = 0;
var accion_modificar   = null;
var entidad1_modificar = null;
var entidad2_modificar = null;
var accio_original     = null;

Ext.define('sap.modificarPermisoPanel', {
    extend: 'Ext.form.Panel',
    alias : 'sap.modificarPermisoPanel',

    title :   'Modificar Permiso',
    id:       'panel_modificar_permiso',
    name:     'panel_modificar_permiso',
    layout:   'fit',
    frame:    true,
    closable: true,
    border:   false,
  
    initComponent: function() {
        var grid_permisos = Ext.create('sap.permisoGrid');
        var combo_entidad = {
            xtype:       'combo',
            id:          'combo_entidad',
            hiddenName:  'entidad',
            name:        'entidad',
            editable:     false,
            mode:        'local',
            displayField: 'entidad',
            valueField:   'codigo',
            emptyText:    'seleccione una accion_modificar',
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
                    entidad1_modificar = item;
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
            emptyText:    'seleccione una accion_modificar',
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
                    entidad2_modificar = item;
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
            emptyText:    'seleccione una accion_modificar',
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
                    entidad1_modificar = item;
                }
            }
        };
        
        var combo_accion = {
            xtype:       'combo',
            fieldLabel:  '<b>Permiso para</b>',
            id:          'combo_accion',
            hiddenName:  'permiso',  
            name:        'permiso',
            editable:     false,  
            mode:        'local',
            displayField: 'accion_modificar',  
            valueField:   'codigo',
            emptyText:    'seleccione una opcion',
            store: Ext.create('Ext.data.ArrayStore',{  
                id      : 0 ,  
                fields  : ['accion_modificar', 'codigo'],  
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
                    accion_modificar = item;
                    var cmp = null;
                    switch(item){
                        case 'cr':
                        case 'el':
                        case 'mo':
                        case 'co':
                            tipo_modificar = 1;
                            entidad1_modificar = null;
                            Ext.getCmp('combo_entidad').reset();
                            Ext.getCmp('combo_entidad').setVisible(true);
                            Ext.getCmp('combo_asignadesasigna_1').setVisible(false);
                            Ext.getCmp('combo_asignadesasigna_2').setVisible(false);
                            break;
                        case 'as':
                        case 'de':
                            tipo_modificar = 2;
                            Ext.getCmp('combo_entidad').setVisible(false);
                            entidad1_modificar = null;
                            Ext.getCmp('combo_asignadesasigna_1').reset();
                            Ext.getCmp('combo_asignadesasigna_1').setVisible(true);
                            entidad2_modificar = null;
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
                width:       480,
                labelWidth:  150,
                name:        'id',
                fieldLabel : '<b>Id</b>',
                listeners: {
                    'afterrender': function() {
                        this.disable();
                    }
                }
            }, {
                xtype:      'textfield',
                margin:     '5 20 20 20',
                name :      'nombre',
                fieldLabel: '<b>Nombre</b>',
                allowBlank: false
            }, {
                xtype:      'textfield',
                name :      'descripcion',
                margin:     '5 20 20 20',           
                fieldLabel: '<b>Descripcion</b>',
            }, {
                xtype: 'checkbox',
                margin:     '5 20 20 20',           
                fieldLabel: '<b>Modificar accion</b>',
                handler : function(combo){
                    var value = combo.getValue();
                    if(value == true){
                        Ext.getCmp('combo_accion').setVisible(true);
                    }
                    else{
                        tipo_modificar     = 0;
                        accion_modificar   = null;
                        entidad1_modificar = null;
                        entidad2_modificar = null;
                        Ext.getCmp('combo_accion').reset();
                        Ext.getCmp('combo_entidad').reset();
                        Ext.getCmp('combo_asignadesasigna_1').reset();
                        Ext.getCmp('combo_asignadesasigna_2').reset();
                        Ext.getCmp('combo_accion').setVisible(false);
                        Ext.getCmp('combo_entidad').setVisible(false);
                        Ext.getCmp('combo_asignadesasigna_1').setVisible(false);
                        Ext.getCmp('combo_asignadesasigna_2').setVisible(false);
                    }
                }
            },combo_accion, combo_entidad, combo_asignadesasigna_1, combo_asignadesasigna_2],
            listeners: {
                render : function(){
                    Ext.getCmp('combo_accion').setVisible(false);
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
            if(tipo_modificar == 1 && entidad1_modificar == null){
                Ext.Msg.alert('ERROR','Debe seleccionar una entidad');
                return;
            }
            if(tipo_modificar == 2 && (entidad1_modificar == null || entidad2_modificar == null)){
                Ext.Msg.alert('ERROR','Los campos de la asociacion son incorrectos o estan incompletos');
                return;
            }
            permiso_codificado = accion_modificar + ':' + entidad1_modificar;
            if(entidad2_modificar != null){
                permiso_codificado = permiso_codificado + '-' + entidad2_modificar;
            }
            console.log(permiso_codificado);
            form.submit({
                method:    'POST',
                url:       '/modificar_permiso',
                waitTitle: 'Connecting', 
                waitMsg:   'Sending data...',
                // Aca se envian los parametros que estan disabled en el form
                params: {
                    id : form.findField('id').getValue(),
                    codificacion : permiso_codificado,
                    accion : accion_original
                },
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
        accion_original = null;
        var form = this.up('form').getForm();
        var id = form.findField('id').getValue();
        form.reset();
        tipo_modificar     = 0;
        accion_modificar   = null;
        entidad1_modificar = null;
        entidad2_modificar = null;
        Ext.getCmp('combo_accion').reset();
        Ext.getCmp('combo_entidad').reset();
        Ext.getCmp('combo_asignadesasigna_1').reset();
        Ext.getCmp('combo_asignadesasigna_2').reset();
        Ext.getCmp('combo_accion').setVisible(false);
        Ext.getCmp('combo_entidad').setVisible(false);
        Ext.getCmp('combo_asignadesasigna_1').setVisible(false);
        Ext.getCmp('combo_asignadesasigna_2').setVisible(false);
        form.findField('id').setValue(id);
        form.findField('nombre').focus(true,100);
    },
    
    form_cancel_handler: function() {
        this.up('panel').close();
    }
});
