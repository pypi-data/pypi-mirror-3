# -*- coding: utf-8 -*-

from django.contrib import admin
from models import Country, Region, Currency

class CountryAdmin(admin.ModelAdmin):
    pass

class RegionAdmin(admin.ModelAdmin):
    pass

class CurrencyAdmin(admin.ModelAdmin):
    pass

admin.site.register(Country, CountryAdmin)
admin.site.register(Region, RegionAdmin)
admin.site.register(Currency, CurrencyAdmin)



