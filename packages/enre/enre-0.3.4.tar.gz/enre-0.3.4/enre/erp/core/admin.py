# -*- coding: utf-8 -*-

from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as _UserAdmin
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import UserChangeForm as _UserChangeForm
from references import refs, Reference


class UserChangeForm(_UserChangeForm):
    pass


class UserAdmin(_UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'erp_applications', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        )
    form = UserChangeForm

    pass

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

refs.register(Reference(name=_('Countries'), group=_('Geo'), url='enre/geo/views/CountryView'))
refs.register(Reference(name=_('Regions'), group=_('Geo'), url='enre/geo/views/RegionView'))
refs.register(Reference(name=_('Currencies'), group=_('Accounting'), url='enre/geo/views/CurrencyView'))
