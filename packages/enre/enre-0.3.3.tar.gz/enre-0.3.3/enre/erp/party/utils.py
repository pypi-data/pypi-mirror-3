# -*- coding: utf-8 -*- 

from django.conf import settings

def person_name_format(first_name, last_name, middle_name=None):
    fmt = getattr(settings, 'PARTY_PERSON_FORMAT', 'f m l')
    middle_name = middle_name or ''
    return fmt.replace('f', first_name).replace('l', last_name).replace('m', middle_name)
