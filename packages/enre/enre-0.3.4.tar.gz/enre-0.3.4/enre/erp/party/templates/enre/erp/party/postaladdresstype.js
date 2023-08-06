{% load i18n %}

qx.Class.define('enre.erp.party.views.PostalAddressTypeWindow', {
    extend: enre.ui.view.EditWindow,

    construct: function(parent) {
        this.base(arguments, 'enre.erp.party.services.PostalAddressTypeService', parent);
        this.setWidth(400);
        this.setCaption('{% trans 'Postal address type' %}');
        var form = new enre.ui.form.Form();
        var codeNameField = new qx.ui.form.TextField().set({required:true, maxLength:30});
        form.add(codeNameField, '{% trans 'Code name' %}', null, 'codename');
        var nameField = new qx.ui.form.TextField().set({required:true, maxLength:50});
        form.add(nameField, '{% trans 'Name' %}', null, 'name');
        this.bindForm(form);
        this.addWidget(new enre.ui.form.SingleRenderer(form));

    }
});


qx.Class.define('enre.erp.party.views.PostalAddressTypeView', {
    extend:enre.ui.view.ViewPanel,

    construct: function() {
        this.base(arguments, 'enre/erp/party/stores/PostalAddressTypeStore',
                [
                    ['{% trans 'Code name' %}', '{% trans 'Name' %}'],
                    ['codename', 'name']
                ],
                'enre.erp.party.services.PostalAddressTypeService',
                enre.erp.party.views.PostalAddressTypeWindow
        );
        this.setColumnWidth(0, '15%');
    }
});