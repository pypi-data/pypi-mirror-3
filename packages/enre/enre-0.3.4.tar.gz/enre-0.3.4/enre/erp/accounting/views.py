# -*- coding: utf-8 -*- 

from enre.qx.views import AjaxView

class PaymentMethodTypeView(AjaxView):
    template_name = 'enre/erp/accounting/paymentmethodtype.js'


class CreditCardTypeView(AjaxView):
    template_name = 'enre/erp/accounting/creditcardtype.js'
