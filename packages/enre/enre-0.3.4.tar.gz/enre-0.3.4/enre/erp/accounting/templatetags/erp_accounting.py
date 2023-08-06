# -*- coding: utf-8 -*- 

from django.template.base import Library
from enre.erp.accounting.models import PaymentMethodType

register = Library()

@register.assignment_tag
def get_payment_method_types():
    return PaymentMethodType.objects.exclude(codename__in=['cash'])
