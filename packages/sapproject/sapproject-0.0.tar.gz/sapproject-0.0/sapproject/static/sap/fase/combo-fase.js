Ext.define('sap.comboFase', {
    extend: 'Ext.form.ComboBox',
    alias:  'sap.comboFase',
    
    fieldLabel:     'Fase',
    emptyText:      'Seleccione una fase ...',
    displayField:   'nombre_orden',
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
                return '<div data-qtip="<b>ID Fase:</b>{id}<br/><b>Fase:</b>{nombre}<br/><b>Orden:</b>{orden}"><b>{nombre}</b> - <i>{orden}</i></div>';
            }
        }
        this.store = Ext.create('Ext.data.JsonStore',{
            fields: [
                {name:'id',           type:'string'},
                {name:'nombre',       type:'string'},
                {name:'orden',        type:'string'},
                {name:'nombre_orden', type:'string'}
            ],
            proxy: {
                type: 'ajax',
                url: '/consultar_fase_proyecto',
                reader: {
                    type: 'json',
                    root: 'data',
                    totalProperty: 'total'
                }
            }
        });
        this.callParent(arguments);
    }
});
