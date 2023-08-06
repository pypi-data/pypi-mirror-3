 Ext.define('sap.crearFasePanel', {
    extend: 'Ext.form.Panel',
    alias : 'sap.crearFasePanel',

    title :   'Crear Fase',
    id:       'panel_crear_fase',
    name:     'panel_crear_fase',
    layout:   'fit',
    frame:    true,
    closable: true,
    border:   false,
  
    initComponent: function() {
        var px=510;
        var py=-120;
        this.items = [{
            xtype:      'form',
            title:      'Datos de la Fase',
            autoScroll: true,
            fieldDefaults: {
                blankText:     'Este campo no puede ser nulo',
                msgTarget:     'side',
                autoFitErrors: false
            },
            items: [{
                xtype:      'textfield',
                margin:     '50 20 20 20',
                name :      'nombre',
                width: 480,
                labelWidth:  150,
                fieldLabel: '<b>Nombre de la Fase</b>',
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
                margin:     '5 20 20 20',
                name :      'fechafin',
                labelWidth:  150,
                width: 480,                
                fieldLabel: '<b>Fecha de Fin</b>',
                allowBlank: false
		  }, { 
				xtype:      'combo', 
                hiddenName: 'estado',  
                margin:     '5 20 20 20',
                name :      'estado',
                labelWidth:  150,
                width: 480,
                fieldLabel: '<b>Estado de la Fase</b>',
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
                        [2, 'DESARROLLO'],
                        [3, 'INICIADO'],
                        [4, 'FINALIZADO']
                    ]
                }),
                listeners: {  
                    beforerender: function(combo){  
                        combo.setValue('NO-INICIADO');  
                    }  
                },               
           }, {                           
				xtype:      'textarea',
                margin:     '5 20 20 20',
                name :      'observaciones',
                labelWidth:  150,
                multiline : true,
                width: 980,
                height: 100,
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
                var store = Ext.data.StoreManager.lookup('faseStore');
                store.load();
                // volvemos al panel de administracion
                Ext.getCmp('area-central').agregar_pestanha('panel_administrar_fase', null);
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
                url:       '/crear_fase',
                waitTitle: 'Connecting', 
                waitMsg:   'Sending data...',
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
        form.findField("nombre").focus(true,100);
    },
    
    form_cancel_handler: function() {
        this.up('panel').close();
    }
});
