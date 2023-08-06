Ext.define('sap.funcionalidades', {
    extend: 'Ext.panel.Panel',
    alias : 'sap.funcionalidades',
    
    title:       'Funcionalidades',
    name:        'funcionalidades',
    id:          'funcionalidades',
    margin:      '1 1 1 1',
    region:      'west',
    layout:      'accordion',
    collapsible: true,
    width:       248,
    resizable:   false,
    config: {
        permisos : null,
    },
    
    constructor: function(options){
        this.initConfig(options);
        this.callParent(arguments);
    },
    
    initComponent: function() {
        this.items = [
            Ext.create('sap.administrarCentralPanel')
        ];
        this.permisos = new Array();
        this.callParent(arguments);
    },
    
    ocultar_funcionalidades: function(){
        // Cierra las pestañas activas
        Ext.getCmp('area-central').removeAll();

        var items = this.items;
        var panel_administrar = null;
        for(var i=0;i<items.length;i++){
            panel_administrar = items.getAt(i);
            panel_administrar.ocultar_elementos();
            panel_administrar.setVisible(false);
        }
    },
    
    cambiar_funcionalidades : function(total, permisos){
        // inicializamos la lista de permisos
        this.permisos = new Array();
        // ocultamos las funcionalidades
        this.ocultar_funcionalidades();
        // flags que habilitan los paneles de administracion
        var habilitar_administrar_proyecto = false;
        var habilitar_administrar_usuario  = false;
        var habilitar_administrar_rol      = false;
        var habilitar_administrar_permiso  = false;
        var habilitar_administrar_atributo = false;
        var habilitar_administrar_tipoitem = false;
        var habilitar_administrar_item     = false;

        for(var i=0;i<total;i++){
            // agregamos el permiso a la lista de permisos
            this.permisos.push(permisos[i].permiso);
            // Filtramos el permiso a una funcionalidad
            switch(permisos[i].permiso){
                // ADMINISTRAR PROYECTOS
                case 'cr:pr':
                case 'el:pr':
                case 'mo:pr':
                case 'co:pr':
                    habilitar_administrar_proyecto = true;
                    break;
                // ADMINISTRAR USUARIOS
                case 'cr:us':
                case 'el:us':
                case 'mo:us':
                case 'co:us':
                    habilitar_administrar_usuario = true;
                    break;
                case 'as:us-pr':
                case 'de:us-pr':
                    habilitar_administrar_proyecto = true;
                    break;
                // ADMINISTRAR ROLES
                case 'cr:ro':
                case 'el:ro':
                case 'mo:ro':
                case 'co:ro':
                    habilitar_administrar_rol = true;
                    break;
                case 'as:ro-us':
                case 'de:ro-us':
                    habilitar_administrar_usuario = true;
                    break;
                // ADMINISTRAR PERMISOS
                case 'cr:pe':
                case 'el:pe':
                case 'mo:pe':
                case 'co:pe':
                    habilitar_administrar_permiso = true;
                    break;
                case 'as:pe-ro':
                case 'de:pe-ro':
                    habilitar_administrar_rol = true;
                    break;
                // ADMINISTRAR ATRIBUTOS
                case 'cr:at':
                case 'el:at':
                case 'mo:at':
                case 'co:at':
                    habilitar_administrar_atributo = true;
                    break;
                case 'as:at-ti':
                case 'de:at-ti':
                    habilitar_administrar_tipoitem = true;
                    break;
                // ADMINISTRAR TIPOITEM
                case 'cr:ti':
                case 'el:ti':
                case 'mo:ti':
                case 'co:ti':
                    habilitar_administrar_tipoitem = true;
                    break;
                // ADMINISTRAR ITEM
                case 'cr:it':
                case 'el:it':
                case 'mo:it':
                case 'co:it':
                    habilitar_administrar_item = true;
                    break;
                default:
                    break;
            }
        }
        // Habilitamos la administracion central
        Ext.getCmp('administrar_central').setVisible(true);
        // Habilitamos los paneles de administracion que tengan una o mas funcionalidades habilitadas
        if(habilitar_administrar_proyecto == true){
            Ext.getCmp('administrar_proyecto').setVisible(true);
        }
        if(habilitar_administrar_usuario == true){
            Ext.getCmp('administrar_usuario').setVisible(true);
        }
        if(habilitar_administrar_rol == true){
            Ext.getCmp('administrar_rol').setVisible(true);
        }
        if(habilitar_administrar_permiso == true){
            Ext.getCmp('administrar_permiso').setVisible(true);
        }
        if(habilitar_administrar_atributo == true){
            Ext.getCmp('administrar_atributo').setVisible(true);
        }
        if(habilitar_administrar_tipoitem == true){
            Ext.getCmp('administrar_tipoitem').setVisible(true);
        }
        if(habilitar_administrar_item == true){
            Ext.getCmp('administrar_item').setVisible(true);
        }
        // Actualizamos la interfaz
        this.doLayout();
        // imprimimos la lista de permisos
        console.log(this.permisos);
    }
});
