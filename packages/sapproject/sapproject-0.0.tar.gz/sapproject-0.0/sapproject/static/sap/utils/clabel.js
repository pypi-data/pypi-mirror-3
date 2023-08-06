Ext.define('sap.clickable.Label', {
    extend: 'Ext.form.Label',
    alias:  'widget.clabel',
    cls:     'clabel',
    overCls: 'clabel-hover',
    margin: '2 2 0 2',
    config: {
        click : null,
    },
    
    constructor: function(options){
        this.initConfig(options);
        this.callParent(arguments);
    },
    
    initComponent: function() {
        this.listeners = {
            'render' : function(){
                var this_label = this;
                Ext.fly(this.id).on('click', function(e,t){
                    this_label.click();
                });
            }
        }
        this.callParent(arguments);
    }
});
