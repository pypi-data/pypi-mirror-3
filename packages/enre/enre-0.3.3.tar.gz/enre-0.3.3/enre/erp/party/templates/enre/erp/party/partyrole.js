{% load i18n %}

{% include 'enre/erp/party/partyrole_window.js' %}

qx.Class.define('enre.erp.party.views.PartyRoleView', {
    extend:enre.ui.view.ViewPanel,

    construct: function() {
        this.base(arguments, 'enre/erp/party/stores/PartyRoleStore',
                [
                    ['{% trans 'Code name' %}', '{% trans 'Name' %}'],
                    ['codename', 'name']
                ],
                'enre.erp.party.services.PartyRoleService',
                enre.erp.party.views.PartyRoleWindow
        );
        this.setColumnWidth(0, '15%');
    }
});
