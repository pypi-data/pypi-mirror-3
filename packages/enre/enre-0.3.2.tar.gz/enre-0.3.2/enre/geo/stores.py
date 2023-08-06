# -*- coding: utf-8 -*-

from enre.qx.stores import ModelStore
from models import Country, Region, Currency

class CountryStore(ModelStore):
    query = Country.objects


class RegionStore(ModelStore):
    query = Region.objects
    related_fields = ['country__name']


class CurrencyStore(ModelStore):
    query = Currency.objects
