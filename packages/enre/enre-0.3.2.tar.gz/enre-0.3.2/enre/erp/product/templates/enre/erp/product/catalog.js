qx.Class.define('enre.erp.product.Catalog', {

    extend:enre.erp.Module,

    construct:function (parent) {
        this.base(arguments, parent);
        this.setLayout(new qx.ui.layout.Basic());
        var lbl = new qx.ui.basic.Label('PRODUCT CATALOG');
        this.add(lbl);

        var tabview = new qx.ui.tabview.TabView();
        var page;
        for (var i = 1; i < 5; i++) {
            page = new qx.ui.tabview.Page('Page ' + i);
            tabview.add(page);
        }
        this.add(tabview, {top:25});
    }

});