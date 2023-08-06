Ext.onReady(function(){
    Ext.QuickTips.init();

    var login = new Ext.FormPanel({ 
        labelWidth:80,
        url:          '/login_check', 
        frame:        true,
        defaultType:  'textfield',
        monitorValid: true,
        items:[{ 
                fieldLabel: 'Username', 
                name:       'name', 
                id:         'name',
                allowBlank: false 
            },{ 
                fieldLabel: 'Password', 
                name:       'password', 
                id:         'password',
                inputType:  'password', 
                allowBlank: false 
            }],
        buttons:[{ 
                text:     'Login',
                formBind: true,
                handler: function(){ 
                    login.getForm().submit({ 
                        method:    'POST', 
                        waitTitle: 'Conectando', 
                        waitMsg:   'Enviando datos...',
                        success: function(form, action){
                            console.log(action.response.responseText);
                            obj = Ext.JSON.decode(action.response.responseText);
                            Ext.Msg.alert('INFO', obj.message, function(btn, text){
                                if (btn == 'ok'){
                                    var redirect = '/main'; 
                                    window.location = redirect;
                                }
                            });
                        }, 
                        failure:function(form, action){ 
                            obj = Ext.JSON.decode(action.response.responseText); 
                            Ext.Msg.alert('ERROR', obj.message); 
                            login.getForm().reset();
                            Ext.getCmp('name').focus(true, 1000);
                        } 
                    }); 
                } 
            }] 
    });
     
    var win = new Ext.Window({
        title:     'LOGIN',
        layout:    'fit',
        width:     300,
        height:    150,
        closable:  false,
        resizable: false,
        plain:     true,
        border:    false,
        items:     [login]
    });
    win.show();
});
