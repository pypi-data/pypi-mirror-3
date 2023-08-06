# -*- coding: utf-8 -*- 

from django.template.base import Library
from enre.erp.party.models import ContactInfoType

register = Library()

@register.assignment_tag
def get_contact_info_types():
    return ContactInfoType.objects.all()
