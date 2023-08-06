Ext.define('sap.administrarItemPanel', {
    extend: 'Ext.form.Panel',
    alias : 'sap.administrarItemPanel',

    title :   'Administrar Item',
    id:       'panel_administrar_item',
    name:     'panel_administrar_item',
    layout:   'fit',
    frame:    true,
    closable: true,
    border:   false,
  
    initComponent: function() {
        var grid_items = Ext.create('sap.itemGrid');
        this.items = [{
            xtype:      'form',
            title:      'Administrar Item',
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
                        [1, 'Nombre del Item', 'nombre'],
                        [2, 'Descripcion', 'descripcion'],
                        [3, 'Version', 'version'],
                        [4, 'Prioridad', 'prioridad'],
                        [5, 'Complejidad', 'complejidad'],
                        [6, 'Estado', 'estado']
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
            grid_items
            ]
        }];
        
        this.buttons =[{
            text:    'Modificar',
            id:      'modificar_item_btn',
            iconCls: 'update-icon',
            hidden:  true,
            grid:    grid_items,
            handler: this.form_update_handler
        }, {
            text:    'Eliminar',
            id:      'eliminar_item_btn',
            iconCls: 'delete-icon',
            hidden:  true,
            grid:    grid_items,
            handler: this.form_delete_handler
        }, {
            text:    'Nuevo',
            id:      'nuevo_item_btn',
            iconCls: 'new-icon',
            hidden:  true,
            handler: this.form_new_handler
        }, {
            text:    'Cancelar',
            id:      'cancelar_item_btn',
            iconCls: 'cancel-icon',
            handler: this.form_cancel_handler
        }, {
            text:    'Limpiar',
            id:      'limpiar_item_btn',
            iconCls: 'clear-icon',
            handler: this.form_reset_handler
        }];
        
        this.listeners = {
            close : function() {
                // cerramos los paneles hijos abiertos (si hubiere)
                Ext.getCmp('area-central').cerrar_pestanhas([
                    'panel_modificar_item',
                    'panel_crear_item'
                ]);
            },
            render : function(){
                // mostramos los botones segun los permisos
                var permisos = Ext.getCmp('funcionalidades').permisos;
                if(permisos.indexOf('cr:it') != -1){
                    Ext.getCmp('nuevo_item_btn').setVisible(true);
                }
                if(permisos.indexOf('mo:it') != -1){
                    Ext.getCmp('modificar_item_btn').setVisible(true);
                }
                if(permisos.indexOf('el:it') != -1){
                    Ext.getCmp('eliminar_item_btn').setVisible(true);
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
                            url:    '/eliminar_item',
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
            Ext.Ajax.request({
                url:      '/consultar_campos_modificar_item',
                method:   'POST',
                params: {id_item : 1},
                success: function(response, opts) {
                    // Obtenemos la respuesta del servidor
                    var obj   = Ext.decode(response.responseText);
                    var total = obj.total;
                    var data  = obj.data;
                    // Creamos el form de acuerdo a los atributos del item
                    Ext.getCmp('area-central').agregar_pestanha('panel_modificar_item','sap.modificarItemPanel')
                    var panel = Ext.getCmp('panel_modificar_item');
                    panel.setVisible(false);
                    // Llenamos la informacion necesaria para modificar el item
                    var id_item     = records[0].data.id;
                    panel.items.getAt(0).items.getAt(0).setValue(id_item);
                    // Procesamos los atributos del tipo item seleccionado
                    panel.procesar_campos(total,data);
                    // Mostramos la interfaz de creacion para el tipo de item
                    panel.setVisible(true);
                    panel.doLayout();
                },
                failure: function(response, opts) {
                    Ext.Msg.alert('ERROR','Ocurrio un problema al realizar los cambios');
                }
            });
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
            Ext.StoreMgr.lookup('itemStore').load({
                params: {
                    filtro : campo,
                    valor:   valor
                }
            });
        }
    },
    
    form_new_handler: function() {
        /*
        var panel = Ext.create('sap.crearItemParamsPanel');
        var win = Ext.create('Ext.Window',{
            title:    'DATOS',
            height:   160,
            width:    350,
            modal:     true,
            frame:     false,
            border:    false,
            resizable: false,
            items:    [panel],
            buttons: [{
                xtype: 'button',
                text: 'Aceptar',
                handler: function(){
                    console.log('aceptar');
                }
            }]
        });
        win.show();
        */
        
        // TODO ESTO VA DENTRO DEL BOTON ACEPTAR
        Ext.Ajax.request({
            url:      '/consultar_campos_crear_item',
            method:   'POST',
            params: {id_tipoitem : 3},
            success: function(response, opts) {
                // Obtenemos la respuesta del servidor
                var obj   = Ext.decode(response.responseText);
                var total = obj.total;
                var data  = obj.data;
                // Creamos el form de acuerdo al tipo de item
                Ext.getCmp('area-central').agregar_pestanha('panel_crear_item','sap.crearItemPanel')
                var panel = Ext.getCmp('panel_crear_item');
                panel.setVisible(false);
                /* Llenamos la informacion necesaria para asignar el item a una fase
                var id_fase     = Ext.getCmp('combo_crear_en_fase');
                var id_tipoitem = Ext.getCmp('combo_tipo_de_item');
                panel.items.getAt(0).items.getAt(0).setValue(id_fase);
                panel.items.getAt(0).items.getAt(0).setValue(id_tipoitem);
                */
                // Procesamos los atributos del tipo item seleccionado
                panel.procesar_campos(total,data);
                // Mostramos la interfaz de creacion para el tipo de item
                panel.setVisible(true);
                panel.doLayout();
            },
            failure: function(response, opts) {
                Ext.Msg.alert('ERROR','Ocurrio un problema al realizar los cambios');
            }
        });
    },
    
    form_reset_handler: function() {
        // limpiamos el formulario y hacemos foco en el primer campo
        var form = this.up('form').getForm();
        form.reset();
        form.findField('campo').focus(true,100);
        // recargamos el store
        Ext.data.StoreManager.lookup('itemStore').load();
    },
    
    form_cancel_handler: function() {
        this.up('panel').close();
    }
});
