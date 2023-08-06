{% load url from future %}


qx.Class.define('enre.erp.product.ProductPanel', {
    extend:enre.ui.view.EditPanel,

    construct:function (parent) {
        this.base(arguments);
        var form = new enre.ui.form.Form();

        var brandWindow = new enre.ui.model.Select('enre/erp/product/stores/BrandStore');
        brandWindow.setDialogCaption('Select Brand');
        brandWindow.setColumnCaption('Brand name');
        brandWindow.setRequired(true);
        form.add(brandWindow, 'Brand', null, 'brand');

        var articleField = new qx.ui.form.TextField().set({required:true});
        form.add(articleField, 'Article', null, 'article');
        var partNumberField = new qx.ui.form.TextField();
        form.add(partNumberField, 'Part number', null, 'part_number');

        var productTypeSelect = new enre.ui.model.SelectBox().set({required:true});
        productTypeSelect.setUrl('enre/erp/product/stores/ProductTypeStore');
        form.add(productTypeSelect, 'Product type', null, 'product_type');
        var nameField = new qx.ui.form.TextField().set({width:1000, required:true});
        form.add(nameField, 'Product name', null, 'name');

        this.bindForm(form);
        this.addWidget(new enre.ui.form.SingleRenderer(form));
    }

});


qx.Class.define('enre.erp.product.ProductList', {

    extend:enre.erp.Module,

    construct:function (parent) {
        this.base(arguments, parent);


        this.setLayout(new qx.ui.layout.Grow());
        var editPanel = new enre.erp.product.ProductPanel();

        var crud = new enre.ui.view.ViewPanel('enre/erp/product/stores/ProductStore',
                [
                    ['brand__name', 'article', 'part_number', 'product_type__name', 'name'],
                    ['brand__name', 'article', 'part_number', 'product_type__name', 'name']
                ],
                'dhs.opentaps.services.ProductService',
                editPanel
        );
        crud.setColumnWidth(0, '10%');
        crud.setColumnWidth(1, '10%');
        crud.setColumnWidth(2, '10%');
        crud.setColumnWidth(3, '10%');
        crud.setColumnWidth(4, 1500);

        var filter = new enre.ui.view.FilterPanel();


        var filterForm = new qx.ui.form.Form();
        var brandSelect = new enre.ui.model.SelectBox(
                'enre/erp/product/stores/BrandStore',
                'name', 'id').set();

        filterForm.add(brandSelect, 'Brand', null, 'brand__id');

        var typeSelect = new enre.ui.model.SelectBox(
                'enre/erp/product/stores/ProductTypeStore',
                'name', 'id');
        qx.util.PropertyUtil.setUserValue(typeSelect, '__firstChange', true);
        filterForm.add(typeSelect, 'Type', null, 'product_type__id');

        var nameField = new qx.ui.form.TextField();
        filterForm.add(nameField, 'Name', null, 'name__icontains');

        filter.setForm(filterForm);

        crud.setFilterPanel(filter);

        this.add(crud);
    },

    members:{
        __timer:null,

        __onTimer:function (e) {
            alert('Timer');
            this.__timer.stop();
        }
    }

});
