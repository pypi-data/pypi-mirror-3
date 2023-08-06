{% load i18n %}
{% include 'enre/erp/party/partyrole_window.js' %}


qx.Class.define('enre.erp.party.views.PartyTypeWindow', {
    extend:enre.ui.view.EditWindow,

    members:{
        _initControls:function () {
            this.base(arguments);
            this.setWidth(400);
            this.setCaption('{% trans 'Party type' %}');
            var form = new enre.ui.form.Form();
            var codeNameField = new qx.ui.form.TextField().set({required:true, maxLength:30});
            form.add(codeNameField, '{% trans 'Code name' %}', null, 'codename');
            var nameField = new qx.ui.form.TextField().set({required:true, maxLength:50});
            form.add(nameField, '{% trans 'Name' %}', null, 'name');
            var templateField = new qx.ui.form.TextField().set({maxLength:100, minWidth:150});
            form.add(templateField, '{% trans 'Template' %}', null, 'template');
            this.bindForm(form);
            var panel = new enre.ui.container.Panel();
            panel.add(new enre.ui.form.SingleRenderer(form))
            this.addWidget(panel);
            var dlg = new enre.ui.view.RelationSelect('enre/erp/party/stores/PartyRoleStore', 'party_types',
                    '{% trans 'Select party role' %}', '{% trans 'Party role' %}'
            );
            var roleView = new enre.ui.view.RelationPanel(
                    'enre/erp/party/stores/PartyTypeStore',
                    [
                        ['{% trans 'Name' %}'],
                        ['name'],
                        'id'
                    ],
                    'enre.erp.party.services.PartyTypeService',
                    'partyrole_set',
                    dlg,
                    null,
                    this
            ).set({height:250});
            this.addWidget(roleView);
        }
    }
});


qx.Class.define('enre.erp.party.views.PartyTypeView', {
    extend:enre.ui.view.ViewPanel,

    construct:function () {
        this.base(arguments, 'enre/erp/party/stores/PartyTypeStore',
                [
                    ['{% trans 'Code name' %}', '{% trans 'Name' %}', '{% trans 'Template' %}'],
                    ['codename', 'name', 'template']
                ],
                'enre.erp.party.services.PartyTypeService',
                enre.erp.party.views.PartyTypeWindow
        );
        this.setColumnWidth(0, '15%');
        this.setColumnWidth(1, '50%');
    }
});
