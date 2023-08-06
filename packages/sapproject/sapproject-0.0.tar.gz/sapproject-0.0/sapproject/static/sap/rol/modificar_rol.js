 Ext.define('sap.modificarRolPanel', {
    extend: 'Ext.form.Panel',
    alias : 'sap.modificarRolPanel',

    title :   'Modificar Rol',
    id:       'panel_modificar_rol',
    name:     'panel_modificar_rol',
    layout:   'fit',
    frame:    true,
    closable: true,
    border:   false,
  
    initComponent: function() {
        this.items = [{
            xtype:      'form',
            frame:      true,
            title:      'Modificacion de datos del Rol',
            autoScroll: true,
            fieldDefaults: {
                blankText:     'Este campo no puede ser nulo',
                msgTarget:     'side',
                autoFitErrors: false
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
                margin:     '50 20 20 20',
                name :      'nombre',
                width: 480,
                labelWidth:  150,
                fieldLabel: '<b>Nombre del Rol</b>',
                allowBlank: false
            }, {
                xtype:      'textfield',
                margin:     '50 20 20 20',
                name :      'descripcion',
                labelWidth:  150,
                width: 480,                
                fieldLabel: '<b>Descripcion</b>',
                allowBlank: false
            }]
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
                var store = Ext.data.StoreManager.lookup('rolStore');
                store.load();
                // volvemos al panel de administracion
                Ext.getCmp('area-central').agregar_pestanha('panel_administrar_rol', null);
            }
        };
        
        this.callParent(arguments);
    },
    
    form_submit_handler: function(){
        var self = this;
        var form = self.up('form').getForm();
        if(form.isValid()){
            form.submit({
                method:    'POST',
                url:       '/modificar_rol',
                waitTitle: 'Connecting', 
                waitMsg:   'Sending data...',
                // Aca se envian los parametros que estan disabled en el form
                params: {
                    id : form.findField('id').getValue()
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
        var form = this.up('form').getForm();
        var id = form.findField('id').getValue();
        form.reset();
        form.findField('id').setValue(id);
        form.findField('nombre').focus(true,100);
    },
    
    form_cancel_handler: function() {
        this.up('panel').close();
    }
});
