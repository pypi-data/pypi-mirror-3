{% load i18n %}

qx.Class.define('enre.erp.accounting.views.PaymentMethodTypeWindow', {
    extend: enre.ui.view.EditWindow,

    construct: function(parent) {
        this.base(arguments, 'enre.erp.accounting.services.PaymentMethodTypeService', parent);
        this.setWidth(400);
        this.setCaption('{% trans 'Payment method type' %}');
        var form = new enre.ui.form.Form();
        var codeNameField = new qx.ui.form.TextField().set({required:true, maxLength:30});
        form.add(codeNameField, '{% trans 'Code name' %}', null, 'codename');
        var nameField = new qx.ui.form.TextField().set({required:true, maxLength:50});
        form.add(nameField, '{% trans 'Name' %}', null, 'name');
        this.bindForm(form);
        this.addWidget(new enre.ui.form.SingleRenderer(form));

    }

});


qx.Class.define('enre.erp.accounting.views.PaymentMethodTypeView', {
    extend:enre.ui.view.ViewPanel,

    construct: function() {
        this.base(arguments, 'enre/erp/accounting/stores/PaymentMethodTypeStore',
                [
                    ['{% trans 'Code name' %}', '{% trans 'Name' %}'],
                    ['codename', 'name']
                ],
                'enre.erp.accounting.services.PaymentMethodTypeService',
                enre.erp.accounting.views.PaymentMethodTypeWindow
        );
        this.setColumnWidth(0, '15%');
    }
});