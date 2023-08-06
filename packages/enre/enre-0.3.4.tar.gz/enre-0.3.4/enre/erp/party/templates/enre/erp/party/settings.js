{% load i18n %}
{% include 'enre/erp/party/partytype.js' %}
{% include 'enre/erp/party/partyrole.js' %}
{% include 'enre/erp/party/contactinfotype.js' %}
{% include 'enre/erp/party/postaladdresstype.js' %}

qx.Class.define('enre.erp.party.Settings', {
    extend:enre.erp.Module,

    construct: function(parent) {
        this.base(arguments, parent, new qx.ui.layout.Grow());
        var tabView = new qx.ui.tabview.TabView('left');
        var partiesTypesPage = new qx.ui.tabview.Page('{% trans 'Parties types' %}').set({layout:new qx.ui.layout.Grow()});
        partiesTypesPage.addListener('appear', function(e) {
            if (partiesTypesPage.getChildren().length == 0) {
                partiesTypesPage.add(new enre.erp.party.views.PartyTypeView());
            }
        }, this);
        tabView.add(partiesTypesPage);
        var partiesRolesPage = new qx.ui.tabview.Page('{% trans 'Parties roles' %}').set({layout:new qx.ui.layout.Grow()});
        partiesRolesPage.addListener('appear', function(e) {
            if (partiesRolesPage.getChildren().length == 0) {
                partiesRolesPage.add(new enre.erp.party.views.PartyRoleView());
            }
        }, this);
        tabView.add(partiesRolesPage);
        var contactInfoTypesPage = new qx.ui.tabview.Page('{% trans 'Contact info types' %}').set({layout:new qx.ui.layout.Grow()});
        contactInfoTypesPage.addListener('appear', function(e) {
            if (contactInfoTypesPage.getChildren().length == 0) {
                contactInfoTypesPage.add(new enre.erp.party.views.ContactInfoTypeView());
            }
        }, this);
        tabView.add(contactInfoTypesPage);
        var postalAddressTypesPage = new qx.ui.tabview.Page('{% trans 'Postal address types' %}').set({layout:new qx.ui.layout.Grow()});
        postalAddressTypesPage.addListener('appear', function(e) {
            if (postalAddressTypesPage.getChildren().length == 0) {
                postalAddressTypesPage.add(new enre.erp.party.views.PostalAddressTypeView());
            }
        }, this);
        tabView.add(postalAddressTypesPage);
        this.add(tabView);
    }

});