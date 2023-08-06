 Ext.define('sap.modificarUsuarioPanel', {
    extend: 'Ext.form.Panel',
    alias : 'sap.modificarUsuarioPanel',

    title :   'Modificar Usuario',
    id:       'panel_modificar_usuario',
    name:     'panel_modificar_usuario',
    layout:   'fit',
    frame:    true,
    closable: true,
    border:   false,
  
    initComponent: function() {
        var px=510;
        var py=-210;
        this.items = [{
            xtype:      'form',
            frame:      true,
            title:      'Modificacion de datos de Usuario',
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
                margin:     '5 20 20 20',
                name :      'ci',
                width:      480,
                labelWidth: 150,
                fieldLabel: '<b>Cedula de identidad</b>',
                allowBlank: false
            }, {
                xtype:      'textfield',
                margin:     '5 20 20 20',
                name :      'nombres',
                labelWidth:  150,
                width: 480,                
                fieldLabel: '<b>Nombres</b>',
                allowBlank: false
            }, {
                xtype:      'textfield',
                margin:     '5 20 20 20',
                name :      'apellidos',
                labelWidth:  150,
                width: 480,
                fieldLabel: '<b>Apellidos</b>',
                allowBlank: false
            }, {
                xtype:      'datefield',
                format:     'd/m/Y',
                margin:     '5 20 20 20',
                name :      'fechanac',
                labelWidth:  150,
                width: 480,                
                fieldLabel: '<b>Fecha de Nacimiento</b>'
            }, {
                xtype:      'combo',
                fieldLabel: '<b>Sexo</b>', 
                hiddenName: 'sexo',  
                margin:     '5 20 20 20',
                name:       'sexo',
                width: 480,
                editable:    false,  
                mode:       'local',  
                labelWidth:   150,
                allowBlank: false,   
                displayField: 'opcion',  
                valueField:   'opcion',  
                store: new Ext.data.SimpleStore({  
                    id      : 0 ,  
                    fields  : ['id', 'opcion' ],  
                    data    : [  
                        [1, 'Femenino'],  
                        [2, 'Masculino']  
                    ]  
                 }), 
                listeners   : {  
                    beforerender: function(combo){  
                        combo.setValue('Femenino');  
                    }  
                },               
            }, {
                xtype:      'textfield',
                margin:     '5 10 10 10',
                name :      'nick',
                labelWidth:  150,
                width: 480,
                x:            px,
                y:            py,
                fieldLabel: '<b>Nombre de Usuario</b>',
                allowBlank: false
            }, {
                xtype:      'textfield',
                margin:     '5 10 10 10',
                name :      'password',
                width: 480,
                labelWidth:  150,
                x:px,
                y:            py+10,
                fieldLabel: '<b>Contrase&ntilde;a de Acceso</b>'
            }, {
                xtype:     'textfield',
                margin:     '5 10 10 10',
                name :      'email',
                width: 480,                
                labelWidth:  150,
                x:px,
                y:            py+20,
                fieldLabel: '<b>Correo Electronico</b>'
            }, {
                xtype:      'textfield',
                margin:     '5 10 10 10',
                name :      'direccion',
                labelWidth:  150,
                width: 480,
                x:px,
                y:            py+30,
                fieldLabel: '<b>Direccion</b>'
            }, {
                xtype:      'textfield',
                margin:     '5 10 10 10',
                name :      'telefono',
                labelWidth:  150,
                width: 480,
                x:px,
                y:            py+40,
                fieldLabel: '<b>Telefono</b>'
            }, {
                xtype:      'textarea',
                margin:     '5 10 10 20',
                name :      'observaciones',
                labelWidth:  150,
                multiline : true,
                width: 980,
                height: 100,
                x:0,
                y:py+60,
                fieldLabel: '<b>Observaciones</b>'
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
                var store = Ext.data.StoreManager.lookup('usuarioStore');
                store.load();
                // volvemos al panel de administracion
                Ext.getCmp('area-central').agregar_pestanha('panel_administrar_usuario', null);
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
                url:       '/modificar_usuario',
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
        form.findField("ci").focus(true,100);
    },
    
    form_cancel_handler: function() {
        this.up('panel').close();
    }
});
