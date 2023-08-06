# -*- coding: utf-8 -*- 

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from enre.erp.core.references import refs, Reference
from models import PartyType, PartyRole

class PartyTypeAdmin(admin.ModelAdmin):
    pass


class PartyRoleAdmin(admin.ModelAdmin):
    pass

admin.site.register(PartyType, PartyTypeAdmin)
admin.site.register(PartyRole, PartyRoleAdmin)

refs.register(Reference(name=_('party_types'), group=_('parties'), url='enre/erp/party/views/PartyTypeView'))
refs.register(Reference(name=_('party_roles'), group=_('parties'), url='enre/erp/party/views/PartyRoleView'))