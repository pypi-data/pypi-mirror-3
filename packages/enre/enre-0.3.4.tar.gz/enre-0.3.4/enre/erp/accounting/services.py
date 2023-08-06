# -*- coding: utf-8 -*- 

from enre.qx.services import ModelService
from models import PaymentMethodType, CreditCardType, PaymentMethod, BankAccount, CreditCard


class PaymentMethodTypeService(ModelService):
    model = PaymentMethodType


class CreditCardTypeService(ModelService):
    model = CreditCardType


class PaymentMethodService(ModelService):
    model = PaymentMethod


class BankAccountService(ModelService):
    model = BankAccount


class CreditCardService(ModelService):
    model = CreditCard