Ext.define('sap.comboTipoitem', {
    extend: 'Ext.form.ComboBox',
    alias:  'sap.comboTipoitem',
    
    fieldLabel:     'Tipoitem',
    emptyText:      'Seleccione un tipo de item ...',
    displayField:   'nombre',
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
                return '<div data-qtip="<b>ID Tipoitem:</b>{id}<br/><b>Nombre:</b>{nombre}"><b>{nombre}</i></div>';
            }
        }
        this.store = Ext.create('Ext.data.JsonStore',{
            fields: [
                {name:'id',           type:'string'},
                {name:'nombre',       type:'string'}
            ],
            proxy: {
                type: 'ajax',
                url: '/consultar_tipoitem_fase',
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
