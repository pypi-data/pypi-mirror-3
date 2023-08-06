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

refs.register(Reference(name=_('Parties roles'), group=_('Parties'), url='enre/erp/party/views/PartyRoleView'))
refs.register(Reference(name=_('Parties types'), group=_('Parties'), url='enre/erp/party/views/PartyTypeView'))
refs.register(
    Reference(name=_('Contact info types'), group=_('Parties'), url='enre/erp/party/views/ContactInfoTypeView')
)
refs.register(
    Reference(name=_('Postal address types'), group=_('Parties'), url='enre/erp/party/views/PostalAddressTypeView')
)
refs.register(Reference(name=_('Own parties'), group=_('Parties'), url='enre/erp/party/views/OwnPartiesView',
    class_name='enre.erp.party.OwnPartiesView')
)