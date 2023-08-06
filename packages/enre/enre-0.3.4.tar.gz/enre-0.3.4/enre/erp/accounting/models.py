# -*- coding: utf-8 -*- 

from django.db import models
from django.utils import simplejson
from enre.erp.core.models import BaseReference
from django.utils.translation import ugettext_lazy as _
from enre.db.models import Model, Manager
from enre.erp.party.models import Party
from utils import default_settings, bank_account_format, credit_card_format
import transdef

default_settings()

class PaymentMethodType(BaseReference):
    class Meta:
        verbose_name = _('Payment method type')
        verbose_name_plural = _('Payment method types')

    pass


class CreditCardType(BaseReference):
    class Meta:
        verbose_name = _('Card type')
        verbose_name_plural = _('Card types')

    pass


class PaymentMethod(Model):
    party = models.ForeignKey(Party, on_delete=models.DO_NOTHING, verbose_name=_('Party'))
    payment_method_type = models.ForeignKey(PaymentMethodType, on_delete=models.DO_NOTHING,
        verbose_name=_('Payment method type'))
    method = models.CharField(_('Payment method'), max_length=255)
    description = models.TextField(_('Description'), null=True, blank=True)
    is_active = models.BooleanField(_('Active'), default=True)

    class Meta:
        unique_together = ('party', 'method')
        verbose_name = _('Payment method')
        verbose_name_plural = _('Payment methods')

    def __unicode__(self):
        return self.get_method()

    def get_method(self):
        return self.method

    def save(self, force_insert=False, force_update=False, using=None):
        self.method = self.get_method()
        super(PaymentMethod, self).save(force_insert, force_update, using)

    pass


class BankAccount(PaymentMethod):
    bank_name = models.CharField(_('Bank name'), max_length=100)
    account = models.CharField(_('Bank account'), max_length=100)
    corr_account = models.CharField(_('Corr. account'), max_length=100, null=True, blank=True)
    bank_code = models.CharField(_('Bank code'), max_length=9, null=True, blank=True)

    class Meta:
        verbose_name = _('Bank account')
        verbose_name_plural = _('Bank accounts')

    def get_method(self):
        return bank_account_format(self.bank_name, self.account, self.corr_account, self.bank_code)

    pass


class CreditCard(PaymentMethod):
    credit_card_type = models.ForeignKey(CreditCardType, on_delete=models.DO_NOTHING,
        verbose_name=_('Сard type'))
    number = models.CharField(_('Number'), max_length=100)
    first_name = models.CharField(_('First name'), max_length=50)
    last_name = models.CharField(_('Last name'), max_length=50)
    expire_date = models.DateField(_('Expire date'))

    class Meta:
        unique_together = ('number', 'expire_date')
        verbose_name = _('Credit card')
        verbose_name_plural = _('Credit cards')

    def get_method(self):
        return credit_card_format(self.first_name, self.last_name, self.credit_card_type.name, self.number,
            str(self.expire_date.month) + '/' + str(self.expire_date.year))

    pass


def __accounting_pre_save(sender, instance, raw, **kwargs):
    if not raw:
        return
    if isinstance(instance, BankAccount) or isinstance(instance, CreditCard):
        payment_method = PaymentMethod.objects.get(pk=instance.pk)
        payment_method.method = instance.get_method()
        payment_method.save()
    pass

models.signals.pre_save.connect(__accounting_pre_save)
