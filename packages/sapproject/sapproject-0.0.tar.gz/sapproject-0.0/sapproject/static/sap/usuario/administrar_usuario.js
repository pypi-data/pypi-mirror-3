Ext.define('sap.administrarUsuarioPanel', {
    extend: 'Ext.form.Panel',
    alias : 'sap.administrarUsuarioPanel',

    title :   'Administrar Usuario',
    id:       'panel_administrar_usuario',
    name:     'panel_administrar_usuario',
    layout:   'fit',
    frame:    true,
    closable: true,
    border:   false,
  
    initComponent: function() {
        var grid_usuarios = Ext.create('sap.usuarioGrid');
        this.items = [{
            xtype:      'form',
            title:      'Administrar Usuario',
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
                        [1, 'Cedula', 'ci'],
                        [2, 'Nombre de Usuario', 'nick'],  
                        [3, 'Nombres', 'nombres'],
                        [4, 'Apellidos', 'apellidos'],
                        [5, 'Direccion', 'direccion'],
                        [6, 'Email', 'email']
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
                text: 'Buscar',    
                x: 520,
                y: -42,
                iconCls: 'search-icon',
                handler:  this.form_buscar_handler            
            },
            grid_usuarios
            ]
        }];
        this.buttons =[{
            text:    'Asignar roles',
            id:      'asignar_rol_btn',
            iconCls: 'asignar-icon',
            hidden:  true,
            grid:    grid_usuarios,
            handler: this.form_asignar_rol_handler
        }, {
            text:    'Modificar',
            id:      'modificar_usuario_btn',
            iconCls: 'update-icon',
            hidden:  true,
            grid:    grid_usuarios,
            handler: this.form_update_handler
        }, {
            text:    'Eliminar',
            id:      'eliminar_usuario_btn',
            iconCls: 'delete-icon',
            hidden:  true,
            grid:    grid_usuarios,
            handler: this.form_delete_handler
        }, {
            text:    'Nuevo',
            id:      'nuevo_usuario_btn',
            iconCls: 'new-icon',
            hidden:  true,
            handler: this.form_new_handler
        }, {
            text:    'Cancelar',
            id:      'cancelar_usuario_btn',
            iconCls: 'cancel-icon',            
            handler: this.form_cancel_handler
        }, {
            text:    'Limpiar',
            id:      'limpiar_usuario_btn',
            iconCls: 'clear-icon',
            handler: this.form_reset_handler
        }];
        this.listeners = {
            close : function() {
                // cerramos los paneles hijos abiertos (si hubiere)
                Ext.getCmp('area-central').cerrar_pestanhas([
                    'panel_modificar_usuario',
                    'panel_crear_usuario',
                    'panel_asignar_rol'
                ]);
            },
            render : function(){
                // mostramos los botones segun los permisos
                var permisos = Ext.getCmp('funcionalidades').permisos;
                if(permisos.indexOf('cr:us') != -1){
                    Ext.getCmp('nuevo_usuario_btn').setVisible(true);
                }
                if(permisos.indexOf('mo:us') != -1){
                    Ext.getCmp('modificar_usuario_btn').setVisible(true);
                }
                if(permisos.indexOf('el:us') != -1){
                    Ext.getCmp('eliminar_usuario_btn').setVisible(true);
                }
                if(permisos.indexOf('as:ro-us') != -1){
                    Ext.getCmp('asignar_rol_btn').setVisible(true);
                }
            }
        };
        this.callParent(arguments);
    },
    
    form_asignar_rol_handler : function() {
        var records = this.grid.getSelectionModel().getSelection();
        if(records == null || records.length == 0){
            Ext.Msg.alert('ERROR','Debe seleccionar un usuario para asignar / desasignar roles');
        }
        else{
            Ext.getCmp('area-central').agregar_pestanha('panel_asignar_rol','sap.asignarRolPanel');
            var panel  = Ext.getCmp('panel_asignar_rol');
            panel.setVisible(false);
            var id_usuario = records[0].data.id;
            // el campo 0 es nuestro campo oculto
            panel.items.getAt(0).setValue(id_usuario)
            panel.llenar_grids();
            panel.setVisible(true);
        }
    },
    
    form_update_handler : function() {
        var records = this.grid.getSelectionModel().getSelection();
        if(records == null || records.length == 0){
            Ext.Msg.alert('ERROR','Debe seleccionar un registro para modificar');
        }
        else{
            Ext.getCmp('area-central').agregar_pestanha('panel_modificar_usuario','sap.modificarUsuarioPanel');
            var cmp = Ext.getCmp('panel_modificar_usuario');
            cmp.form.loadRecord(records[0]);
            var id = cmp.getForm().findField('id').getValue();
            Ext.Ajax.request({
                   url:    '/consultar_usuario_completo',
                   params: {
                    filtro : 'id',
                    valor  : id
                },
                success: function(response, opts) {
                    // Obtenemos la respuesta del servidor
                    var obj = Ext.decode(response.responseText);
                    var data  = obj.data;
                    cmp.getForm().findField('password').setValue(obj.data[0].password);
                    cmp.getForm().findField('fechanac').setValue(obj.data[0].fechanac);
                    cmp.getForm().findField('observaciones').setValue(obj.data[0].observaciones);
                    cmp.getForm().findField('telefono').setValue(obj.data[0].telefono);
                    cmp.getForm().findField('sexo').setValue(obj.data[0].sexo);
                   },
                   failure: function(response, opts) {
                      console.log('failure en la carga del panel de moficacion de usuario');
                   }
            });
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
                            url:    '/eliminar_usuario',
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
    
    form_buscar_handler: function(){
        var form = this.up('form').getForm();
        var campo = form.findField('campo').getValue();
        var valor = form.findField('igual').getValue();
        if(valor == '' || campo == null){
            Ext.Msg.alert('ERROR','Los parametros de busqueda son ivalidos o estan incompletos');
        }
        else{
            Ext.StoreMgr.lookup('usuarioStore').load({
                params: {
                    filtro : campo,
                    valor:   valor
                }
            });
        }
    },
    
    form_new_handler: function() {
        Ext.getCmp('area-central').agregar_pestanha('panel_crear_usuario','sap.crearUsuarioPanel');
    },
    
    form_reset_handler: function() {
        // limpiamos el formulario y hacemos foco en el primer campo
        var form = this.up('form').getForm();
        form.reset();
        form.findField('campo').focus(true,100);
        // recargamos el store
        Ext.data.StoreManager.lookup('usuarioStore').load();
    },
    
    form_cancel_handler: function() {
        this.up('panel').close();
    }
});
