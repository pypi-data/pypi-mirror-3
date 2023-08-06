{% load i18n %}

qx.Class.define('enre.geo.views.RegionWindow', {
    extend:enre.ui.view.EditWindow,

    members: {
        _initControls: function() {
            this.base(arguments);
            this.setWidth(400);
            this.setCaption('{% trans 'Region' %}');

            var form = new enre.ui.form.Form();
            var countrySelect = new enre.ui.model.Select('enre/geo/stores/CountryStore',
                    '{% trans 'Select country' %}',
                    '{% trans 'Country' %}').set({required: true});
            form.add(countrySelect, '{% trans 'Country' %}', null, 'country');
            var codeField = new qx.ui.form.TextField().set({required:true, maxLength:10});
            form.add(codeField, '{% trans 'Code' %}', null, 'code');
            var nameField = new qx.ui.form.TextField().set({required:true, maxLength:150, minWidth:200});
            form.add(nameField, '{% trans 'Name' %}', null, 'name');
            this.bindForm(form);
            this.addWidget(new enre.ui.form.SingleRenderer(form));
        }
    }
});

qx.Class.define('enre.geo.views.RegionView', {
    extend:enre.ui.view.ViewPanel,

    construct: function() {
        this.base(arguments, 'enre/geo/stores/RegionStore',
                [
                    ['{% trans 'Country' %}', '{% trans 'Code' %}', '{% trans 'Name' %}'],
                    ['country__name', 'code', 'name']
                ],
                'enre.geo.services.RegionService',
                enre.geo.views.RegionWindow
        );
        this.setColumnWidth(0, '30%');
        this.setColumnWidth(1, '10%');

        var filter = new enre.ui.view.FilterPanel();
        var filterForm = new qx.ui.form.Form();
        var countrySelect = new enre.ui.model.SelectBox(
                'enre/geo/stores/CountryStore',
                'name', 'id');

        filterForm.add(countrySelect, '{% trans 'Country' %}', null, 'country__id');
        var regionField = new qx.ui.form.TextField();
        filterForm.add(regionField, '{% trans 'Region' %}', null, 'name__icontains');
        filter.setForm(filterForm);
        this.setFilterPanel(filter);
    }

});
