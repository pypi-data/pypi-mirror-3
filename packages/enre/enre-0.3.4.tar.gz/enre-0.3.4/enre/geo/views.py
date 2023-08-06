# -*- coding: utf-8 -*- 

from enre.views import AjaxView

class CountryView(AjaxView):
    template_name = 'enre/geo/country.js'


class RegionView(AjaxView):
    template_name = 'enre/geo/region.js'


class CurrencyView(AjaxView):
    template_name = 'enre/geo/currency.js'
