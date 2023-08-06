Ext.define('sap.permisoAsignacionArrayStore', {
    extend:   'Ext.data.ArrayStore',
    alias:    'sap.permisoAsignacionArrayStore',
    storeId:  'permisoArrayStore',
    fields:   ['id', 'nombre', 'descripcion','accion']
});
