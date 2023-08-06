# -*- coding: utf-8 -*- 

from django.template.base import Library
from django.conf import settings

register = Library()

@register.filter
def is_application(application):
    return application in settings.INSTALLED_APPS
