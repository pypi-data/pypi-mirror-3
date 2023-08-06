{% load i18n %}
{% include 'enre/erp/party/party.js' %}

qx.Class.define('enre.erp.party.OrganizationView', {
    extend: enre.ui.view.ViewPanel,

    construct: function() {
        this.base(arguments, 'enre/erp/party/stores/OrganizationStore',
                [
                    ['{% trans 'Name' %}', '{% trans 'Short name' %}'],
                    ['name', 'short_name']
                ],
                'enre.erp.party.services.OrganizationService',
                enre.erp.party.OrganizationEditPanel
        );
        var filter = new enre.ui.view.FilterPanel();
        var filterForm = new qx.ui.form.Form();
        var nameField = new qx.ui.form.TextField();
        filterForm.add(nameField, '{% trans 'Name' %}', null, 'name__icontains');
        var shortNameField = new qx.ui.form.TextField();
        filterForm.add(shortNameField, '{% trans 'Short name' %}', null, 'short_name__icontains');
        filter.setForm(filterForm);
        this.setFilterPanel(filter);
    }
});


qx.Class.define('enre.erp.party.Organization', {
    extend:enre.erp.Module,

    members: {
        _initControls: function() {
            this.setLayout(new qx.ui.layout.Grow());
            this.add(new enre.erp.party.OrganizationView());
        }
    }
});
