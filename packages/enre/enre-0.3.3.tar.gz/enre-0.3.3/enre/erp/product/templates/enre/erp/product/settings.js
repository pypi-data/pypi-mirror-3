qx.Class.define('enre.erp.product.Settings', {

    extend: enre.erp.Module,

    construct: function(parent) {
        this.base(arguments, parent);
        this.setLayout(new qx.ui.layout.Basic());
        var lbl = new qx.ui.basic.Label('PRODUCT SETTINGS');
        this.add(lbl);
    }


});