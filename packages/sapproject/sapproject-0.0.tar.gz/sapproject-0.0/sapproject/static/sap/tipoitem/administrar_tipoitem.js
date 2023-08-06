Ext.define('sap.administrarTipoitemPanel', {
    extend: 'Ext.form.Panel',
    alias : 'sap.administrarTipoitemPanel',

    title :   'Administrar Tipoitem',
    id:       'panel_administrar_tipoitem',
    name:     'panel_administrar_tipoitem',
    layout:   'fit',
    frame:    true,
    closable: true,
    border:   false,
  
    initComponent: function() {
        var grid_tipoitems = Ext.create('sap.tipoitemGrid');
        this.items = [{
            xtype:      'form',
            title:      'Administrar Tipoitems',
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
                        [1, 'Nombre del Tipoitem', 'nombre'],
                        [2, 'Descripcion', 'descripcion'],
                        [3, 'Prefijo', 'prefijo']
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
            grid_tipoitems
            ]
        }];
        
        this.buttons =[{
            text:     'Asignar atributos',
            id:       'asignar_atributo_btn',
            iconCls:  'asignar-icon',
            hidden:  true,
            grid:     grid_tipoitems,
            handler:  this.form_asignar_atributo_handler
        }, {    
            text:    'Modificar',
            id:      'modificar_tipoitem_btn',
            iconCls: 'update-icon',
            hidden:  true,
            grid:    grid_tipoitems,
            handler: this.form_update_handler
        }, {
            text:    'Eliminar',
            id:      'eliminar_tipoitem_btn',
            iconCls: 'delete-icon',
            hidden:  true,
            grid:    grid_tipoitems,
            handler: this.form_delete_handler
        }, {
            text:    'Nuevo',
            id:      'nuevo_tipoitem_btn',
            iconCls: 'new-icon',
            hidden:  true,
            handler: this.form_new_handler
        }, {
            text:    'Cancelar',
            id:      'cancelar_tipoitem_btn',
            iconCls: 'cancel-icon',
            handler: this.form_cancel_handler
        }, {
            text:    'Limpiar',
            id:      'limpiar_tipoitem_btn',
            iconCls: 'clear-icon',
            handler: this.form_reset_handler
        }];
        
        this.listeners = {
            close : function() {
                // cerramos los paneles hijos abiertos (si hubiere)
                Ext.getCmp('area-central').cerrar_pestanhas([
                    'panel_modificar_tipoitem',
                    'panel_crear_tipoitem',
                    'panel_asignar_atributo'
                ]);
            },
            render : function(){
                // mostramos los botones segun los permisos
                var permisos = Ext.getCmp('funcionalidades').permisos;
                if(permisos.indexOf('cr:ti') != -1){
                    Ext.getCmp('nuevo_tipoitem_btn').setVisible(true);
                }
                if(permisos.indexOf('mo:ti') != -1){
                    Ext.getCmp('modificar_tipoitem_btn').setVisible(true);
                }
                if(permisos.indexOf('el:ti') != -1){
                    Ext.getCmp('eliminar_tipoitem_btn').setVisible(true);
                }
                if(permisos.indexOf('as:at-ti') != -1){
                    Ext.getCmp('asignar_atributo_btn').setVisible(true);
                }
            }
        };
        
        this.callParent(arguments);
    },
    form_asignar_atributo_handler : function() {
        var records = this.grid.getSelectionModel().getSelection();
        if(records == null || records.length == 0){
            Ext.Msg.alert('ERROR','Debe seleccionar un tipo de item para asignar / desasignar atributos');
        }
        else{
            Ext.getCmp('area-central').agregar_pestanha('panel_asignar_atributo','sap.asignarAtributoPanel');
            var panel  = Ext.getCmp('panel_asignar_atributo');
            panel.setVisible(false);
            var id_tipoitem = records[0].data.id;
            // el campo 0 es nuestro campo oculto
            panel.items.getAt(0).setValue(id_tipoitem)
            panel.llenar_grids();
            panel.setVisible(true);
            //panel.doLayout();
        }
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
                            url:    '/eliminar_tipoitem',
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
            Ext.getCmp('area-central').agregar_pestanha('panel_modificar_tipoitem','sap.modificarTipoitemPanel');
            Ext.getCmp('panel_modificar_tipoitem').form.loadRecord(records[0]);
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
            Ext.StoreMgr.lookup('tipoitemStore').load({
                params: {
                    filtro : campo,
                    valor:   valor
                }
            });
        }
    },
    
    form_new_handler: function() {
        Ext.getCmp('area-central').agregar_pestanha('panel_crear_tipoitem','sap.crearTipoitemPanel');
    },
    
    form_reset_handler: function() {
        // limpiamos el formulario y hacemos foco en el primer campo
        var form = this.up('form').getForm();
        form.reset();
        form.findField('campo').focus(true,100);
        // recargamos el store
        Ext.data.StoreManager.lookup('tipoitemStore').load();
    },
    
    form_cancel_handler: function() {
        this.up('panel').close();
    }
});
