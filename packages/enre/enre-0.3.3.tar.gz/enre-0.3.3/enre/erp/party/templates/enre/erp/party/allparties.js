{% load i18n %}

qx.Class.define('enre.erp.party.AllParties', {
    extend:enre.ui.view.ViewPanel,

    construct:function () {
        this.base(arguments, 'enre/erp/party/stores/PartyStore',
                [
                    ['{% trans 'Name' %}', '{% trans 'Party type' %}'],
                    ['display_name', 'party_type__name']
                ]
        );
        this.setColumnWidth(1, '20%');
    }


});
