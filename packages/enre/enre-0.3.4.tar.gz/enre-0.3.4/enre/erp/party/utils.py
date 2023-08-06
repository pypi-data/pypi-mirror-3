# -*- coding: utf-8 -*- 

from django.conf import settings
from enre.erp.core.utils import init_module_settings
import re

def default_settings():
    init_module_settings('ERP_PARTY', {
        'PERSON_FORMAT': 'first middle last',
        'POSTAL_ADDRESS_FORMAT': 'to_name, address, address2, region code, city, country'
    });


def person_name_format(first_name, last_name, middle_name=None):
    fmt = settings.ERP_PARTY['PERSON_FORMAT']
    middle_name = middle_name or ''
    return fmt.replace('first', first_name).replace('last', last_name).replace('middle', middle_name)


def postal_address_format(address=None, address2=None, city=None, region=None, code=None, country=None, to_name=None):
    fmt = settings.ERP_PARTY['POSTAL_ADDRESS_FORMAT']
    address = address or ''
    address2 = address2 or ''
    city = city or ''
    region = region or ''
    code = code or ''
    country = country or ''
    to_name = to_name or ''
    fmt = fmt.replace('address2', address2).replace('address', address).replace('city', city).replace('region',
        region).replace('code', code).replace('country', country).replace('to_name', to_name)
    fmt = re.sub(r', {1,}', ',', fmt)
    fmt = re.sub(r' {2,}', ' ', fmt)
    fmt = re.sub(r',{2,}', ', ', fmt)
    fmt = re.sub(r'^,', '', fmt)
    fmt = re.sub(r',$', '', fmt)
    fmt = fmt.replace(',', ', ')
    return fmt
