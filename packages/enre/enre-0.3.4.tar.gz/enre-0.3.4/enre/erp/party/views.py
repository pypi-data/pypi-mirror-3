# -*- coding: utf-8 -*- 

from enre.qx.views import AjaxView
from enre.erp.core.views import ApplicationView, Module


class PartyTypeView(AjaxView):
    template_name = 'enre/erp/party/partytype.js'


class PartyRoleView(AjaxView):
    template_name = 'enre/erp/party/partyrole.js'


class ContactInfoTypeView(AjaxView):
    template_name = 'enre/erp/party/contactinfotype.js'


class PostalAddressTypeView(AjaxView):
    template_name = 'enre/erp/party/postaladdresstype.js'


class OwnPartiesView(AjaxView):
    template_name = 'enre/erp/party/ownparties.js'


class PartiesModule(Module):
    name = 'All parties'
    path = 'all'
    template_name = 'enre/erp/party/allparties.js'
    script_class = 'enre.erp.party.AllParties'


class OrganizationModule(Module):
    name = 'Organizations'
    path = 'organization'
    template_name = 'enre/erp/party/organization.js'
    script_class = 'enre.erp.party.Organization'


class PersonModule(Module):
    name = 'Persons'
    path = 'person'
    template_name = 'enre/erp/party/person.js'
    script_class = 'enre.erp.party.Person'


class OwnPartiesModule(Module):
    name = 'Own parties'
    path = 'own'
    template_name = 'enre/erp/party/ownparties.js'
    script_class = 'enre.erp.party.OwnParties'


class SettingsModule(Module):
    name = 'Settings'
    path = 'settings'
    template_name = 'enre/erp/party/settings.js'
    script_class = 'enre.erp.party.Settings'


class PartyView(ApplicationView):
    name = 'Parties'
    modules = [PartiesModule(), OrganizationModule(), PersonModule(), OwnPartiesModule(), SettingsModule()]
