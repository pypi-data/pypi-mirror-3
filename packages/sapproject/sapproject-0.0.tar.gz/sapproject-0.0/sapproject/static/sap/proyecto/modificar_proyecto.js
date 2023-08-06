 Ext.define('sap.modificarProyectoPanel', {
    extend: 'Ext.form.Panel',
    alias : 'sap.modificarProyectoPanel',

    title :   'Modificar Proyecto',
    id:       'panel_modificar_proyecto',
    name:     'panel_modificar_proyecto',
    layout:   'fit',
    frame:    true,
    closable: true,
    border:   false,
  
    initComponent: function() {
        var px=510;
        var py=-120;
        this.items = [{
            xtype:      'form',
            frame: true,
            title:      'Modificacion de datos del Proyecto',
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
                fieldLabel: '<b>Nombre del Proyecto</b>',
                allowBlank: false
            }, {
                xtype:      'textfield',
                margin:     '5 20 20 20',
                name :      'descripcion',
                labelWidth:  150,
                width: 480,                
                fieldLabel: '<b>Descripcion</b>',
                allowBlank: false
            }, {
                xtype:      'datefield',
                format:     'd/m/Y',
                margin:     '5 20 20 20',
                name :      'fechainicio',
                labelWidth:  150,
                width: 480,                
                fieldLabel: '<b>Fecha de Inicio</b>',
                allowBlank: false
            }, {
                xtype:      'datefield',
                format:     'd/m/Y',
                x:            px,
                y:            py,                
                margin:     '5 10 10 10',
                name :      'fechafin',
                labelWidth:  150,
                width: 480,                
                fieldLabel: '<b>Fecha de Fin</b>',
                allowBlank: false
            }, {
                xtype:      'combo',
                fieldLabel: '<b>Sexo</b>', 
                hiddenName: 'estado',  
                margin:     '5 10 10 10',
                name :      'estado',
                labelWidth:  150,
                width: 480,
                x:            px,
                y:            py+10,
                fieldLabel: '<b>Estado del Proyecto</b>',
                allowBlank: false,
                editable:    false,  
                mode:       'local',   
                displayField: 'opcion',  
                valueField:   'opcion',  
                store: new Ext.data.SimpleStore({  
                    id      : 0 ,  
                    fields  : ['id', 'opcion' ],  
                    data    : [  
                        [1, 'NO-INICIADO'],  
                        [2, 'INICIADO'],
                        [3, 'PENDIETE'],
                        [4, 'ANULADO'],
                        [5, 'FINALIZADO']
                    ]
                }),
                listeners: {  
                    beforerender: function(combo){  
                        combo.setValue('NO-INICIADO');  
                    }  
                },               
           }, {
                xtype:      'textarea',
                margin:     '5 10 10 20',
                name :      'observaciones',
                labelWidth:  150,
                multiline : true,
                width: 980,
                height: 100,
                x:0,
                y:py+80,
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
                var store = Ext.data.StoreManager.lookup('proyectoStore');
                store.load();
                // volvemos al panel de administracion
                Ext.getCmp('area-central').agregar_pestanha('panel_administrar_proyecto', null);
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
                url:       '/modificar_proyecto',
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
