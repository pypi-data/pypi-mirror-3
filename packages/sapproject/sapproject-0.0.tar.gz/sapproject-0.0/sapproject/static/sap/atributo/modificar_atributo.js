 Ext.define('sap.modificarAtributoPanel', {
    extend: 'Ext.form.Panel',
    alias : 'sap.modificarAtributoPanel',

    title :   'Modificar Atributo',
    id:       'panel_modificar_atributo',
    name:     'panel_modificar_atributo',
    layout:   'fit',
    frame:    true,
    closable: true,
    border:   false,
  
    initComponent: function() {
        this.items = [{
            xtype:      'form',
            frame:      true,
            title:      'Modificacion de datos del Atributo',
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
                name :      'nombre',
                width: 480,
                labelWidth:  150,
                fieldLabel: '<b>Nombre del Atributo</b>',
                allowBlank: false
            }, {
                xtype:      'combo',
                margin:     '5 20 20 20',
                hiddenName: 'tipodato',
                name :      'tipodato',
                editable:     false,
                mode:        'local',
                labelWidth:  150,
                width: 480,                
                fieldLabel: '<b>Tipo de Dato</b>',
                allowBlank: false,
                displayField: 'opcion',
                valueField:   'opcion',
                emptyText :   'Seleccione un tipo',
                store: new Ext.data.SimpleStore({  
                    id      : 0 ,  
                    fields  : ['id', 'opcion'],  
                    data    : [
                        [1, 'numérico'],
                        [2, 'texto'],
                        [3, 'lógico'],
                        [4, 'fecha'],
                        [5, 'archivo']
                    ]
                }),   
            }, {
                xtype:      'textfield',
                margin:     '5 20 20 20',
                name :      'valordef',
                width: 480,
                labelWidth:  150,
                fieldLabel: '<b>Valor por defecto</b>',
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
                var store = Ext.data.StoreManager.lookup('atributoStore');
                store.load();
                // volvemos al panel de administracion
                Ext.getCmp('area-central').agregar_pestanha('panel_administrar_atributo', null);
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
                url:       '/modificar_atributo',
                waitTitle: 'Conectando', 
                waitMsg:   'Enviando datos...',
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
