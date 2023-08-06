{% load i18n %}

qx.Class.define('enre.geo.views.CurrencyWindow', {
    extend:enre.ui.view.EditWindow,

    members: {
        _initControls: function() {
            this.base(arguments);
            this.setWidth(350);
            this.setCaption('{% trans 'Currency' %}');
            var form = new enre.ui.form.Form();
            var codeField = new qx.ui.form.TextField().set({required:true, maxLength:3});
            form.add(codeField, '{% trans 'Code' %}', null, 'code');
            var codeField = new qx.ui.form.TextField().set({required:true, maxLength:4});
            form.add(codeField, '{% trans 'Symbol' %}', null, 'symbol');
            var nameField = new qx.ui.form.TextField().set({required:true, maxLength:50, minWidth:200});
            form.add(nameField, '{% trans 'Name' %}', null, 'name');
            this.bindForm(form);
            this.addWidget(new enre.ui.form.SingleRenderer(form));
        }
    }
});

qx.Class.define('enre.geo.views.CurrencyView', {
    extend: enre.ui.view.ViewPanel,

    construct: function() {
        var editPanel = new enre.geo.views.CurrencyWindow();
        this.base(arguments, 'enre/geo/stores/CurrencyStore',
                [
                    ['{% trans 'Code' %}', '{% trans 'Symbol' %}' , '{% trans 'Name' %}'],
                    ['code', 'symbol', 'name']
                ],
                'enre.geo.services.CurrencyService',
                editPanel
        );
        this.setColumnWidth(0, '5%');
        this.setColumnWidth(1, '5%');
    }
});
