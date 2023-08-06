Ext.define('sap.modificarItemPanel', {
    extend: 'Ext.form.Panel',
    alias : 'sap.modificarItemPanel',

    title :    'Modificar Item',
    id:        'panel_modificar_item',
    name:      'panel_modificar_item',
    layout:    'fit',
    frame:      true,
    closable:   true,
    border:     false,
    renderTo:   Ext.getBody(),
  
    initComponent: function() {
        var self = this;
        this.items = [{
            xtype:      'form',
            title:      'Datos del Item',
            layout:     'column',
            frame:      false,
            border:     true,
            autoScroll: true,
            items: [{
                xtype:       'textfield',
                columnWidth: 1/2,
                margin:      '5 20 20 20',
                name:        'id',
                fieldLabel : '<b>Id</b>',
                listeners: {
                    'afterrender': function() {
                        this.disable();
                    }
                }
            }]
        }];
        this.buttons =[{
            text:    'Guardar',
            iconCls: 'save-icon',
            handler: this.form_submit_handler
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
                var store = Ext.data.StoreManager.lookup('itemStore');
                store.load();
                // volvemos al panel de administracion
                Ext.getCmp('area-central').agregar_pestanha('panel_administrar_item', null);
            }
        };
        
        this.callParent(arguments);
    },
    
    form_submit_handler: function(){
        var self = this;
        var form = this.up('form').getForm();
        if(form.isValid()){
            form.submit({
                method:    'POST',
                url:       '/modificar_item',
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
        var id = form.findField('id').getValue();
        form.reset();
        form.findField('id').setValue(id);
        form._fields.getAt(1).focus(true,100);
    },
    
    form_cancel_handler: function() {
        this.up('panel').close();
    },
    
    // Procesa los datos recibidos sobre los atributos para generar un form
    procesar_campos : function(total, campos){
        var form_items = this.items.getAt(0);        
        for(var i=0;i<total;i++){
            var obj = this.crear_campo(campos[i]);
            if(obj != null){
                form_items.add(obj);
            }
        }
    },
    
    // Crea un campo en base a la informacion enviada desde el servidor sobre el atributo
    crear_campo : function(data){
        var obj      = null;
        var name     = data.name;
        var text     = data.text;
        var nullable = data.nullable;
        var defvalue = data.defvalue;
        var value    = data.value;
        switch(data.type){
            case 'NUMERICO':
                obj = this.crear_campo_numerico(name, text, value, defvalue, nullable);
                break;
            case 'TEXTO':
                obj = this.crear_campo_texto(name, text, value, defvalue, nullable);
                break;
            case 'LOGICO':
                obj = this.crear_campo_logico(name, text, value, defvalue, nullable);
                break;
            case 'FECHA':
                obj = this.crear_campo_fecha(name, text, value, defvalue, nullable);
                break;
            case 'ARCHIVO':
                obj = this.crear_campo_archivo(name, text, value, defvalue, nullable);
                break;
            default:
                console.log('-- UNKNOWN TYPE --');
                console.log(data);
                console.log('------------------');
        }
        return obj;
    },
    
    crear_campo_numerico: function(name, text, value, defvalue, nullable){
        var numberfield = Ext.create('Ext.form.NumberField',{
            name:          name,
            hideTrigger:   true,
            columnWidth:   1/2,
            fieldLabel:    '<b>' + text + '</b>',
            allowBlank:    nullable,
            value:         (value != '' && value != null) ? value : defvalue,
            blankText:     'Este campo no puede ser nulo',
            autoFitErrors: false,
            margin:        '5 20 20 20'
        });
        return numberfield;
    },
    
    crear_campo_texto: function(name, text, value, defvalue, nullable){
        var textfield = Ext.create('Ext.form.TextField',{
            name:          name,
            columnWidth:   1/2,
            fieldLabel:    '<b>' + text + '</b>',
            allowBlank:    nullable,
            value:         (value != '' && value != null) ? value : defvalue,
            blankText:     'Este campo no puede ser nulo',
            autoFitErrors: false,
            margin:        '5 20 20 20'
        });
        return textfield;
    },
    
    crear_campo_fecha: function(name, text, value, defvalue, nullable){
        var datefield = Ext.create('Ext.form.DateField',{
            name:        name,
            columnWidth: 1/2,
            fieldLabel:  '<b>' + text + '</b>',
            allowBlank:  nullable,
            value:         (value != '' && value != null) ? value : defvalue,
            blankText:     'Este campo no puede ser nulo',
            autoFitErrors: false,
            margin:        '5 20 20 20'
        });
        return datefield;
    },
    
    crear_campo_logico: function(name, text, value, defvalue, nullable){
        var combobox = Ext.create('Ext.form.ComboBox',{
            name:          name,
            columnWidth:   1/2,
            fieldLabel:    '<b>' + text + '</b>',
            allowBlank:    nullable,
            value:         (value != '' && value != null) ? value : defvalue,
            blankText:     'Este campo no puede ser nulo',
            autoFitErrors: false,
            margin:        '5 20 20 20',
            mode:          'local',
            displayField:  'bool',
            editable:      false,
            valueField:    'bool',
            store: new Ext.data.SimpleStore({
                id:     0,  
                fields: ['bool'],  
                data:   [['Falso'],['Verdadero']]
             })
        });
        return combobox;
    },
    
    crear_campo_archivo: function(name, text, value, defvalue, nullable){
        var filefield = Ext.create('Ext.form.FileUploadField',{
            name:          name,
            columnWidth:   1/2,
            emptyText:     'Seleccione un archivo ...',
            fieldLabel:    '<b>' + text + '</b>',
            allowBlank:    nullable,
            value:         (value != '' && value != null) ? value : defvalue,
            blankText:     'Este campo no puede ser nulo',
            autoFitErrors: false,
            margin:        '5 20 20 20',
            buttonText:    '',
            buttonConfig: {
                iconCls: 'upload-icon'
            }
        });
        return filefield;
    },
});
