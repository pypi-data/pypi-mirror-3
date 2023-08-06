{% load i18n %}
{% include 'enre/erp/party/party.js' %}

qx.Class.define('enre.erp.party.PersonView', {
    extend: enre.ui.view.ViewPanel,

    construct: function() {
        this.base(arguments, 'enre/erp/party/stores/PersonStore',
                [
                    ['{% trans 'First name' %}', '{% trans 'Last name' %}'],
                    ['first_name', 'last_name']
                ],
                'enre.erp.party.services.PersonService',
                enre.erp.party.PersonEditPanel
        );
        var filter = new enre.ui.view.FilterPanel();
        var filterForm = new qx.ui.form.Form();
        var firstName = new qx.ui.form.TextField();
        filterForm.add(firstName, '{% trans 'First name' %}', null, 'first_name__icontains');
        var lastName = new qx.ui.form.TextField();
        filterForm.add(lastName, '{% trans 'Last name' %}', null, 'last_name__icontains');
        filter.setForm(filterForm);
        this.setFilterPanel(filter);
    }
});


qx.Class.define('enre.erp.party.Person', {
    extend:enre.erp.Module,

    members: {
        _initControls: function() {
            this.setLayout(new qx.ui.layout.Grow());
            this.add(new enre.erp.party.PersonView());
        }
    }
});