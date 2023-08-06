# -*- coding: utf-8 -*- 

from enre.qx.stores import ModelStore
from models import PaymentMethodType, CreditCardType, PaymentMethod


class PaymentMethodTypeStore(ModelStore):
    query = PaymentMethodType.objects


class CreditCardTypeStore(ModelStore):
    query = CreditCardType.objects


class PaymentMethodStore(ModelStore):
    query = PaymentMethod.objects