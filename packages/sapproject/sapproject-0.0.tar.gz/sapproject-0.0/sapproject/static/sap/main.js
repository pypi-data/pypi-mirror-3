Ext.onReady(function(){
    Ext.QuickTips.init();
   
    setTimeout(function(){
        Ext.get('loading').remove();
        Ext.get('loading-mask').fadeOut({remove:true});
    }, 250);
    
    var view_port =  Ext.create('Ext.container.Viewport', {
        layout: 'border',
        items: [
            Ext.create('sap.barraSuperior'),
            Ext.create('sap.funcionalidades'),
            Ext.create('sap.areaCentral')
        ]
    });
    
    //Ext.getCmp('funcionalidades').ocultar_funcionalidades();
    
    bubble.msg('Bienvenido', 'Esto es SAP, Sistema de Administracion de Proyectos', 1500);
});
