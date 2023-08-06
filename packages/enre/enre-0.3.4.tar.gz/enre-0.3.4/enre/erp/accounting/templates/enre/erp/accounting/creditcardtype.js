{% load i18n %}

qx.Class.define('enre.erp.accounting.views.CreditCardTypeWindow', {
    extend: enre.ui.view.EditWindow,

    construct: function(parent) {
        this.base(arguments, 'enre.erp.accounting.services.CreditCardTypeService', parent);
        this.setWidth(400);
        this.setCaption('{% trans 'Credit card type' %}');
        var form = new enre.ui.form.Form();
        var codeNameField = new qx.ui.form.TextField().set({required:true, maxLength:30});
        form.add(codeNameField, '{% trans 'Code name' %}', null, 'codename');
        var nameField = new qx.ui.form.TextField().set({required:true, maxLength:50});
        form.add(nameField, '{% trans 'Name' %}', null, 'name');
        this.bindForm(form);
        this.addWidget(new enre.ui.form.SingleRenderer(form));
    }

});


qx.Class.define('enre.erp.accounting.views.CreditCardTypeView', {
    extend:enre.ui.view.ViewPanel,

    construct: function() {
        this.base(arguments, 'enre/erp/accounting/stores/CreditCardTypeStore',
                [
                    ['{% trans 'Code name' %}', '{% trans 'Name' %}'],
                    ['codename', 'name']
                ],
                'enre.erp.accounting.services.CreditCardTypeService',
                enre.erp.accounting.views.CreditCardTypeWindow
        );
        this.setColumnWidth(0, '15%');
    }
});
