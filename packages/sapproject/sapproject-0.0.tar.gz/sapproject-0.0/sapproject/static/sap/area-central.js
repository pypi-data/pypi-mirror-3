var panel_bienvenida = {
    title: 'Bienvenido/a',
    closable: true,
    html: '<br/><p align="center"><font size="6"><b>SAP BETA</b></font></p><br/> Hola, este es el mensaje de bienvenida de prueba!'
}

Ext.define('sap.areaCentral', {
    extend: 'Ext.TabPanel',
    alias : 'sap.areaCentral',
    
    region:     'center',
    id:         'area-central',
    name:       'area-central',
    layout:     'fit',
    margin:     '1 1 1 1',
    activeTab:  0,
    autoScroll: true,
    
    initComponent: function() {
        this.items = [panel_bienvenida];
        this.callParent(arguments);
    },
    
    agregar_pestanha : function(id, clase){
        var tmp = Ext.getCmp(id);
        if(tmp == null){
            // la pestaña se encuentra inactiva
            tmp = Ext.create(clase);
            this.add( tmp );
        }
        this.setActiveTab(tmp);
        this.doLayout();
    },
    
    cerrar_pestanhas : function(lista){
        for(var i=0;i<lista.length;i++){
            var tab = Ext.getCmp(lista[i]);
            if(tab != null){
                tab.close();
            }
        }
    }
});
