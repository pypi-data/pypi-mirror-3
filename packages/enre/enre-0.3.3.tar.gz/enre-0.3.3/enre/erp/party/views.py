# -*- coding: utf-8 -*- 

from enre.qx.views import AjaxView
from enre.erp.core.views import ApplicationView, Module

class PartyTypeView(AjaxView):
    template_name = 'enre/erp/party/partytype.js'


class PartyRoleView(AjaxView):
    template_name = 'enre/erp/party/partyrole.js'


class PartiesModule(Module):
    name = 'All parties'
    path = 'all'
    template_name = 'enre/erp/party/allparties.js'
    script_class = 'enre.erp.party.AllParties'


class OrganizationModule(Module):
    name = 'Organization'
    path = 'organization'
    template_name = 'enre/erp/party/organization.js'
    script_class = 'enre.erp.party.Organization'


class PersonModule(Module):
    name = 'Person'
    path = 'person'
    template_name = 'enre/erp/party/person.js'
    script_class = 'enre.erp.party.Person'


class PartyView(ApplicationView):
    name = 'Parties'
    modules = [PartiesModule(), OrganizationModule(), PersonModule()]
