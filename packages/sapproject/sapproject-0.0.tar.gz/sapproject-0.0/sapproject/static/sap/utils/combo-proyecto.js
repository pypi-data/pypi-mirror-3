Ext.define('sap.comboProyecto', {
    extend: 'Ext.form.ComboBox',
    alias:  'sap.comboProyecto',
    id:             'combo-proyecto',
    name:           'combo-proyecto',
    fieldLabel:     'Proyecto Actual',
    emptyText:      'Seleccione un proyecto ...',
    displayField:   'proyecto_rol',
    valueField:     'rol',
    triggerAction:  'all',
    forceSelection: true,
    editable:       false,
    queryMode :     'remote',
    pageSize:       5,
    width:          450,
    
    initComponent: function() {
        this.listConfig = {
            getInnerTpl: function() {
                return '<div data-qtip="<b>ID Proyecto:</b>{idproyecto}<br/><b>Proyecto:</b>{proyecto}<br/><b>ID Rol:</b>{idrol}<br/><b>Rol:</b>{rol}"><b>{proyecto}</b> - <i>{rol}</i></div>';
            }
        }
        this.store = Ext.create('Ext.data.JsonStore',{
            autoLoad: true,
            fields: [
                {name:'idproyecto',   type:'string'},
                {name:'proyecto',     type:'string'},
                {name:'idrol',        type:'string'},
                {name:'rol',          type:'string'},
                {name:'proyecto_rol', type:'string'}
            ],
            proxy: {
                type: 'ajax',
                url: '/llenar_combo_proyecto',
                reader: {
                    type: 'json',
                    root: 'data',
                    totalProperty: 'total'
                }
            }
        });
        this.listeners = {
            select : function(combo){
                // Rol que tiene el usuario en el proyecto seleccionado
                var rol = combo.getValue();
                // Pedimos la lista de permisos codificados para el proyecto seleccionado
                Ext.Ajax.request({
                   url:    '/consulta_acciones',
                   params: {rol : rol},
                   success: function(response, opts) {
                      // Obtenemos la respuesta del servidor
                      var obj = Ext.decode(response.responseText);
                      var total = obj.total;
                      var data  = obj.data;
                      // Cambiamos la interfaz
                      Ext.getCmp('funcionalidades').cambiar_funcionalidades(total, data);
                   },
                   failure: function(response, opts) {
                      console.log('failure');
                   }
                });
            }
        }
        this.callParent(arguments);
    }
});
