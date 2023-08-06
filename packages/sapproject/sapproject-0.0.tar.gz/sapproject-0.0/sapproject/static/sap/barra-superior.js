Ext.define('sap.barraSuperior', {
    extend: 'Ext.panel.Panel',
    alias : 'sap.barraSuperior',
    
    title:  'SAP - Sistema de Administracion de Proyectos',
    name:   'barra-superior',
    id:     'barra-superior',
    margin: '1 1 1 1',
    region: 'north',
    layout: 'fit',
    border: false,
    
    initComponent: function() {
        this.tbar = [{
                text:    'Nombre de usuario',
                iconCls: 'user-icon',
            }, '-',
                Ext.create('sap.comboProyecto')
            ,'->','-',{
                text:    'Logout',
                iconCls: 'logout-icon',
                handler: function(){
                    window.location = '/logout';
                }
        }];
        this.callParent(arguments);
    }
});
