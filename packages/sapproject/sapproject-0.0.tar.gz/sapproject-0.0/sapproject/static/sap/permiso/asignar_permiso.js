Ext.define('sap.asignarPermisoPanel', {
    extend: 'Ext.Panel',
    alias : 'sap.asignarPermisoPanel',

    title :    'Asignar Permiso',
    id:        'panel_asignar_permiso',
    name:      'panel_asignar_permiso',
    layout:    'column',
    frame:      true,
    closable:   true,
    border:     false,
    autoScroll: true,
    
    initComponent: function() {
        // creamos los stores
        var store_permisos_asignados = Ext.create('sap.permisoAsignacionArrayStore',{
            storeId: 'store-permisos-asignados'
        });
        var store_permisos_asignables = Ext.create('sap.permisoAsignacionArrayStore',{
            storeId: 'store-permisos-asignables'
        });
        
        // creamos los grids
        var column_model = [
            { header: 'Id', flex: 0, dataIndex: 'id'},
            { header: 'Nombre del Permiso', flex: 0, dataIndex: 'nombre' },
            { header: 'Descripcion', flex: 0, dataIndex: 'descripcion'},
            { header: 'Accion', flex: 0, dataIndex: 'accion'}
        ];
        var grid_asignables = Ext.create('Ext.grid.Panel',{
            title:       'PERMISOS ASIGNABLES',
            multiSelect: true,
            autoScroll:  true,
            store:       store_permisos_asignables,
            layout:      'fit',
            renderTo:    Ext.getBody(),
            height:      500,
            columns:     column_model
        });
        var grid_asignados = Ext.create('Ext.grid.Panel',{
            title:       'PERMISOS ASIGNADOS',
            multiSelect: true,
            autoScroll:  true,
            store:       store_permisos_asignados,
            layout:      'fit',
            renderTo:    Ext.getBody(),
            height:      500,
            columns:     column_model
        });
        
        // Otras configuraciones
        this.items = [{
            xtype: 'hiddenfield',
            name:  'id_rol'
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
            id:      'asignar_permiso_btn_grid',
            iconCls: 'asignar-icon',
            grid:    grid_asignables,
            handler : function(){
                var grid    = this.grid;
                var records = grid.getSelectionModel().getSelection();
                if(records != null && records.length != 0){
                    var store = Ext.data.StoreManager.lookup('store-permisos-asignados');
                    grid.store.remove(records);
                    store.add(records);
                }
                else{
                    Ext.Msg.alert('ERROR','Debe seleccionar un permiso (o varios con Ctrl + Click) para asignar');
                }
            }
        }, {
            xtype:   'button',
            text:    'Desasignar',
            id:      'desasignar_permiso_btn_grid',
            iconCls: 'desasignar-icon',
            grid:    grid_asignados,
            handler : function(){
                var grid    = this.grid;
                var records = grid.getSelectionModel().getSelection();
                if(records != null && records.length != 0){
                    var store   = Ext.data.StoreManager.lookup('store-permisos-asignables');
                    grid.store.remove(records);
                    store.add(records);
                }
                else{
                    Ext.Msg.alert('ERROR','Debe seleccionar un permiso (o varios con Ctrl + Click) para desasignar');
                }
            }
        }, {
            text:    'Guardar',
            iconCls: 'save-icon',
            handler: this.form_submit_handler
        }, {
            text:    'Cancelar',
            iconCls: 'cancel-icon',
            handler: this.form_cancel_handler
        }];
        this.listeners = {
            close : function(){
                // volvemos al panel de administracion de roles
                Ext.getCmp('area-central').agregar_pestanha('panel_administrar_rol', null);
            }
        };
        this.callParent(arguments);
    },
    
    form_submit_handler : function(){
        var self      = this;
        var id_rol    = this.up('panel').items.getAt(0).getValue();
        var records   = Ext.data.StoreManager.lookup('store-permisos-asignados').getRange();
        // generamos una lista de ids de los permisos asignados
        var asignados = [];
        for(var i=0;i<records.length;i++){
            asignados.push(records[i].data.id);
        }
        // datos a enviar al servidor
        var post = {'id_rol':id_rol, 'data':asignados}
        Ext.Ajax.request({
            url:      '/asignar_desasignar_permiso',
            method:   'POST',
            params: {data : Ext.encode(post) },
            success: function(response, opts) {
                Ext.Msg.alert('INFO','Cambios realizados con exito', function(btn, text){
                    if (btn == 'ok'){
                        // Cerramos el panel
                        self.up('panel').close();
                    }
                });
            },
            failure: function(response, opts) {
                Ext.Msg.alert('ERROR','Ocurrio un problema al realizar los cambios');
            }
        });
    },
    
    form_cancel_handler: function() {
        this.up('panel').close();
    },
    
    llenar_grids: function() {
        var self   = this;
        var id_rol = this.items.getAt(0).getValue();
        Ext.Ajax.request({
            url:    '/consulta_asignar_permisos',
            method: 'POST',
            // enviamos el id del rol que nos interesa
            params: {id : id_rol},
            success: function(response, opts) {
                // llenamos los grids con los valores obtenidos
                var obj = Ext.decode(response.responseText);
                self.llenar_array_store('store-permisos-asignados', obj.asignados);
                self.llenar_array_store('store-permisos-asignables',obj.asignables);
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
