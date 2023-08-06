# -*- coding: utf-8 -*- 

from enre.qx.views import AjaxView
from enre.erp.core.views import ApplicationView, Module

class PartyTypeView(AjaxView):
    template_name = 'enre/erp/party/partytype.js'


class PartyRoleView(AjaxView):
    template_name = 'enre/erp/party/partyrole.js'


class PartyView(ApplicationView):
    name = 'Party'
