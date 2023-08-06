{% load i18n %}

qx.Class.define('enre.erp.party.views.PartyRoleWindow', {
    extend: enre.ui.view.EditWindow,

    construct: function(parent) {
        this.base(arguments, 'enre.erp.party.services.PartyRoleService', parent);
        this.setWidth(400);
        this.setCaption('{% trans 'Party role' %}');
        var form = new enre.ui.form.Form();
        var codeNameField = new qx.ui.form.TextField().set({required:true, maxLength:30});
        form.add(codeNameField, '{% trans 'Code name' %}', null, 'codename');
        var nameField = new qx.ui.form.TextField().set({required:true, maxLength:50});
        form.add(nameField, '{% trans 'Name' %}', null, 'name');
        this.bindForm(form);
        this.addWidget(new enre.ui.form.SingleRenderer(form));

    }
});

