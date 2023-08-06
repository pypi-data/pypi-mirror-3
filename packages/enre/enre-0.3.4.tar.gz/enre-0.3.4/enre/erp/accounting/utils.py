# -*- coding: utf-8 -*- 

from django.conf import settings
import re
from enre.erp.core.utils import init_module_settings

def default_settings():
    init_module_settings('ERP_ACCOUNTING', {
        'BANK_ACCOUNT_FORMAT': 'bank_name, account, corr_account, bank_code',
        'CREDIT_CARD_FORMAT': 'first_name last_name - card_name number expire_date'
    });


def bank_account_format(bank_name, account, corr_account=None, bank_code=None):
    corr_account = corr_account or ''
    bank_code = bank_code or ''
    fmt = settings.ERP_ACCOUNTING['BANK_ACCOUNT_FORMAT']
    fmt = re.sub(r'bank_name', bank_name, fmt)
    fmt = re.sub(r'corr_account', corr_account, fmt)
    fmt = re.sub(r'account', account, fmt)
    fmt = re.sub(r'bank_code', bank_code, fmt)
    return fmt


def credit_card_format(first_name, last_name, card_name, number, expire_date):
    fmt = settings.ERP_ACCOUNTING['CREDIT_CARD_FORMAT']
    fmt = fmt.replace('first_name', first_name).replace('last_name', last_name).replace('card_name', card_name).replace(
        'number', number).replace('expire_date', expire_date)
    return fmt
