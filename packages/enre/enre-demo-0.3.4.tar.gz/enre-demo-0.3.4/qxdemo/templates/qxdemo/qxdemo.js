{% load url from future %}


qx.Class.define('qxdemo.WidgetsPanel', {
    extend:qx.ui.container.Composite,

    construct:function () {
        this.base(arguments);
        var layout = new qx.ui.layout.Grid(5);
        layout.setColumnFlex(0, 1);
        this.setLayout(layout);
        var cpanel = new enre.ui.container.CollapsePanel('Collapse Panel');
        this.add(cpanel, {row:1, column:0});
    }
});

qx.Class.define('qxdemo.views.ProductPanel', {
    extend:enre.ui.view.EditPanel,

    construct:function (parent) {
        this.base(arguments);
        var form = new enre.ui.form.Form();

        var brandWindow = new enre.ui.model.Select('qxdemo/stores/BrandStore');
        brandWindow.setDialogCaption('Select Brand');
        brandWindow.setColumnCaption('Brand name');
        brandWindow.setRequired(true);
        form.add(brandWindow, 'Brand', null, 'brand');

        var articleField = new qx.ui.form.TextField().set({required:true});
        form.add(articleField, 'Article', null, 'article');
        var partNumberField = new qx.ui.form.TextField();
        form.add(partNumberField, 'Part number', null, 'part_number');

        var productTypeSelect = new enre.ui.model.SelectBox().set({required:true});
        productTypeSelect.setUrl('qxdemo/stores/ProductTypeStore');
        form.add(productTypeSelect, 'Product type', null, 'product_type');
        var nameField = new qx.ui.form.TextField().set({width:1000, required:true});
        form.add(nameField, 'Product name', null, 'name');
        this.bindForm(form);
        this.addWidget(new enre.ui.form.SingleRenderer(form));
    }

});

qx.Class.define('qxdemo.ViewPanel', {
    extend:qx.ui.container.Composite,

    construct:function (parent) {
        this.base(arguments, parent);
        this.setLayout(new qx.ui.layout.Grow());
        //var editPanel = ;

        var view = new enre.ui.view.ViewPanel('qxdemo/stores/ProductStore',
                [
                    ['brand__name', 'article', 'part_number', 'product_type__name', 'name'],
                    ['brand__name', 'article', 'part_number', 'product_type__name', 'name']
                ],
                'qxdemo.services.ProductService',
                qxdemo.views.ProductPanel
        );
        view.setColumnWidth(0, '10%');
        view.setColumnWidth(1, '10%');
        view.setColumnWidth(2, '10%');
        view.setColumnWidth(3, '10%');
        view.setColumnWidth(4, 1500);

        var filter = new enre.ui.view.FilterPanel();


        var filterForm = new qx.ui.form.Form();
        var brandSelect = new enre.ui.model.SelectBox(
                'qxdemo/stores/BrandStore',
                'name', 'id').set();

        filterForm.add(brandSelect, 'Brand', null, 'brand__id');

        var typeSelect = new enre.ui.model.SelectBox(
                'qxdemo/stores/ProductTypeStore',
                'name', 'id');
        qx.util.PropertyUtil.setUserValue(typeSelect, '__firstChange', true);
        filterForm.add(typeSelect, 'Type', null, 'product_type__id');

        var nameField = new qx.ui.form.TextField();
        filterForm.add(nameField, 'Name', null, 'name__icontains');

        filter.setForm(filterForm);

        view.setFilterPanel(filter);

        this.add(view);
    }

});

qx.Class.define('qxdemo.Application', {
    extend:qx.application.Standalone,

    members:{
        main:function () {
            this.base(arguments);
            var container = new qx.ui.container.Composite(new qx.ui.layout.Grow());
            container.setPadding(4);
            var tabview = new qx.ui.tabview.TabView();
            var viewPage = new qx.ui.tabview.Page('View');
            viewPage.setLayout(new qx.ui.layout.Grow());
            viewPage.add(new qxdemo.ViewPanel());
            tabview.add(viewPage);
            var widgetsPage = new qx.ui.tabview.Page('Widgets');
            widgetsPage.setLayout(new qx.ui.layout.Grow());
            var widgetsPanel = new qxdemo.WidgetsPanel();
            widgetsPage.add(widgetsPanel);
            tabview.add(widgetsPage);
            container.add(tabview);
            this.getRoot().add(container, {edge:0});
        }
    }
});
