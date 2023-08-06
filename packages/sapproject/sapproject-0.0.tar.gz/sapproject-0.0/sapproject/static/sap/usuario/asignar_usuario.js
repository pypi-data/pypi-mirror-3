Ext.define('sap.asignarUsuarioPanel', {
    extend: 'Ext.Panel',
    alias : 'sap.asignarUsuarioPanel',

    title :    'Asignar Usuario',
    id:        'panel_asignar_usuario',
    name:      'panel_asignar_usuario',
    layout:    'column',
    frame:      true,
    closable:   true,
    border:     false,
    autoScroll: true,
    foo:        null,
    
    initComponent: function() {
        var self = this;
        // creamos los stores
        var store_usuarios_asignados = Ext.create('sap.usuarioAsignacionArrayStore',{
            storeId: 'store-usuarios-asignados'
        });
        var store_usuarios_asignables = Ext.create('sap.usuarioAsignacionArrayStore',{
            storeId: 'store-usuarios-asignables'
        });
        
        // creamos los grids
        var column_model = [
            { header: 'Id', flex: 0, dataIndex: 'id'},
            { header: 'Nombre de Usuario', flex: 0, dataIndex: 'nick'},
            { header: 'Nombres', flex: 0, dataIndex: 'nombres' },
            { header: 'Apellidos', flex: 0, dataIndex: 'apellidos' }
        ];
        var grid_asignables = Ext.create('Ext.grid.Panel',{
            title:       'USUARIOS ASIGNABLES',
            autoScusuariol:  true,
            store:       store_usuarios_asignables,
            layout:      'fit',
            renderTo:    Ext.getBody(),
            height:      500,
            columns:     column_model
        });
        var grid_asignados = Ext.create('Ext.grid.Panel',{
            title:       'USUARIOS ASIGNADOS',
            multiSelect: true,
            autoScusuariol:  true,
            store:       store_usuarios_asignados,
            layout:      'fit',
            renderTo:    Ext.getBody(),
            height:      500,
            columns:     column_model
        });
        
        // Otras configuraciones
        this.items = [{
            xtype: 'hiddenfield',
            name:  'id_proyecto'
        }, {
            columnWidth: 1/2,
            baseCls:     'x-plain',
            bodyStyle:   'padding:5px 0 5px 5px',
            items:       [grid_asignables]
        }, {
            columnWidth: 1/2,
            baseCls:     'x-plain',
            bodyStyle:   'padding:5px 0 5px 5px',
            items:       [grid_asignados]
        }];
        this.buttons = [{
            xtype:   'button',
            text:    'Asignar',
            id:      'asignar_usuario_btn_grid',
            iconCls: 'asignar-icon',
            grid:    grid_asignables,
            handler : function(){
                var grid    = this.grid;
                var records = grid.getSelectionModel().getSelection();
                if(records != null && records.length != 0){
                    var id_proyecto = self.items.getAt(0).getValue();
                    var id_usuario  = records[0].data.id;
                    var panel       = Ext.create('sap.asignarUsuarioRolProyectoPanel');
                    panel.items.getAt(0).setValue(id_proyecto);
                    panel.items.getAt(1).setValue(id_usuario);
                    panel.llenar_grid();
                    // ventana auxiliar de seleccion de roles por usuario asignado
                    var win = Ext.create('Ext.Window',{
                        modal : true,
                        height: '80%',
                        width:  '80%',
                        frame:  false,
                        border: false,
                        items: [panel],
                        buttons: [{
                            text:    'Guardar',
                            iconCls: 'save-icon',
                            handler: function(){
                                var grid_roles = panel.items.getAt(2);
                                var records = grid_roles.getSelectionModel().getSelection();
                                var filas = panel.items.getAt(2).store.data.length;
                                if(filas == 0){
                                    Ext.Msg.alert('ERROR','El usuario no posee roles. No puede ser asignado al proyecto');
                                }
                                else{
                                    if(records != null && records.length != 0){
                                        // generamos una lista de ids de los roles del usuario en el proyecto
                                        var id_roles = [];
                                        for(var i=0;i<records.length;i++){
                                            id_roles.push(records[i].data.id);
                                        }
                                        // Pedimos al servidor que realize la asignacion en la BD
                                        Ext.Ajax.request({
                                            url:      '/asignar_usuario_rol_proyecto',
                                            method:   'POST',
                                            params: {
                                                id_proyecto: id_proyecto,
                                                id_usuario:  id_usuario,
                                                id_roles :   Ext.encode(id_roles)
                                            },
                                            success: function(response, opts) {
                                                Ext.Msg.alert('INFO','Cambios realizados con exito', function(btn, text){
                                                    if (btn == 'ok'){
                                                        // movemos el usuario seleccionado a la seccion de asignados
                                                        var record = grid.getSelectionModel().getSelection()
                                                        grid.store.remove(record);
                                                        Ext.data.StoreManager.lookup('store-usuarios-asignados').add(record);
                                                        // Cerramos el panel
                                                        win.close();
                                                    }
                                                });
                                            },
                                            failure: function(response, opts) {
                                                Ext.Msg.alert('ERROR','Ocurrio un problema al realizar los cambios');
                                            }
                                        });
                                    }
                                    else{
                                        Ext.Msg.alert('ERROR','Debe seleccionar uno o mas roles para asignar el usuario al proyecto');
                                    }
                                }
                            }
                        },{
                            text:    'Cancelar',
                            iconCls: 'cancel-icon',
                            handler: function(){
                                win.close();
                            }
                        }]
                    });
                    win.show();
                }
                else{
                    Ext.Msg.alert('ERROR','Debe seleccionar un usuario para asignar');
                }
            }
        }, {
            xtype:   'button',
            text:    'Desasignar',
            id:      'desasignar_usuario_btn_grid',
            iconCls: 'desasignar-icon',
            grid:    grid_asignados,
            handler : function(){
                var grid    = this.grid;
                var records = grid.getSelectionModel().getSelection();
                if(records != null && records.length != 0){
                    var record = grid.getSelectionModel().getSelection();
                    var id_proyecto_asignado = self.items.getAt(0).getValue();
                    var id_usuario           = records[0].data.id;
                    // proyecto seleccionado en el combo
                    var id_proyecto_actual = 0;
                    if(Ext.getCmp('combo-proyecto').getValue() != null){
                        id_proyecto_actual = Ext.getCmp('combo-proyecto').valueModels[0].data.idproyecto;
                    }
                    // Pedimos al servidor que realize la desasignacion en la BD
                    Ext.Ajax.request({
                        url:      '/desasignar_usuario_rol_proyecto',
                        params: {
                            id_proyecto_asignado: id_proyecto_asignado,
                            id_usuario:           id_usuario,
                            id_proyecto_actual:   id_proyecto_actual
                        },
                        success: function(response, opts) {
                            obj = Ext.JSON.decode(response.responseText);
                            console.log(obj.success);
                            console.log(obj.success == true);
                            console.log(obj.success == 'true');
                            if(obj.success){
                                // movemos el usuario seleccionado a la seccion de asignables
                                var record = grid.getSelectionModel().getSelection();
                                grid.store.remove(record);
                                Ext.data.StoreManager.lookup('store-usuarios-asignables').add(record);
                            }
                            else{
                                Ext.Msg.alert('ERROR','Este usuario no puede desasignarse de este proyecto');
                            }
                        }
                    });
                }
                else{
                    Ext.Msg.alert('ERROR','Debe seleccionar un usuario para desasignar');
                }
            }
        }, {
            text:    'Cancelar',
            iconCls: 'cancel-icon',
            handler: this.form_cancel_handler
        }];
        this.listeners = {
            close : function(){
                // volvemos al panel de administracion de proyectos
                Ext.getCmp('area-central').agregar_pestanha('panel_administrar_proyecto', null);
            }
        };
        this.callParent(arguments);
    },
    
    form_cancel_handler: function() {
        this.up('panel').close();
    },
    
    llenar_grids: function() {
        var self   = this;
        var id_proyecto = this.items.getAt(0).getValue();
        Ext.Ajax.request({
            url:    '/consulta_asignar_usuarios',
            method: 'POST',
            // enviamos el id del usuario que nos interesa
            params: {id : id_proyecto},
            success: function(response, opts) {
                // llenamos los grids con los valores obtenidos
                var obj = Ext.decode(response.responseText);
                self.llenar_array_store('store-usuarios-asignados', obj.asignados);
                self.llenar_array_store('store-usuarios-asignables',obj.asignables);
            },
            failure: function(response, opts) {
                Ext.Msg.alert('ERROR','Ocurrio un problema al cargar los grids');
            }
        });
    },
    
    llenar_array_store: function(storeId, data){
        var store = Ext.data.StoreManager.lookup(storeId);
        store.loadData(data);
    }
});
