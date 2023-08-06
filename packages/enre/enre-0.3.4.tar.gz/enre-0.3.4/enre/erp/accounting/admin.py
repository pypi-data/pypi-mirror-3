# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from enre.erp.core.references import Reference, refs

refs.register(Reference(name=_('Payment method types'), group=_('Accounting'), url='enre/erp/accounting/views/PaymentMethodTypeView'))
refs.register(Reference(name=_('Credit card types'), group=_('Accounting'), url='enre/erp/accounting/views/CreditCardTypeView'))
