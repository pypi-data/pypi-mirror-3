{% load i18n %}

qx.Class.define('enre.geo.views.CountryWindow', {
    extend:enre.ui.view.EditWindow,

    members:{
        _initControls:function () {
            this.base(arguments);
            this.setWidth(400);
            this.setCaption('{% trans 'Country' %}');
            var form = new enre.ui.form.Form();
            var codeField = new qx.ui.form.TextField().set({required:true, maxLength:2});
            form.add(codeField, '{% trans 'Code' %}', null, 'code');
            var nameField = new qx.ui.form.TextField().set({required:true, maxLength:150, minWidth:200});
            form.add(nameField, '{% trans 'Name' %}', null, 'name');
            this.bindForm(form);
            this.addWidget(new enre.ui.form.SingleRenderer(form));
        }
    }

});


qx.Class.define('enre.geo.views.CountryView', {
    extend:enre.ui.view.ViewPanel,

    construct: function() {
        this.base(arguments, 'enre/geo/stores/CountryStore',
                [
                    ['', '{% trans 'Code' %}', '{% trans 'Name' %}'],
                    ['flag', 'code', 'name']
                ],
                'enre.geo.services.CountryService',
                enre.geo.views.CountryWindow
        );
        var renderer = new qx.ui.table.cellrenderer.Image(16, 11);
        this.getTable().getTableColumnModel().setDataCellRenderer(0, renderer);
        this.setColumnWidth(0, 35);
        this.setColumnWidth(1, 40);
        this.sortByColumn(2);
    }

});
