# -*- coding: utf-8 -*-

from enre.qx.services import ModelService
from models import Country, Region, Currency

class CountryService(ModelService):
    model = Country


class RegionService(ModelService):
    model = Region


class CurrencyService(ModelService):
    model = Currency

