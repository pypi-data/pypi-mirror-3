# -*- coding: utf-8 -*- 

from django.template.base import Library

register = Library()

@register.simple_tag(takes_context=True)
def csrf_token(context):
    return context.get('csrf_token', None)


@register.simple_tag
def run_application(app_cls):
    return "qx.Class.define('enre.Application',{extend:%s });" % app_cls

@register.simple_tag
def init_theme(theme_cls):
    return "qx.Theme.define('enre.theme.Theme', {extend: %s });" % theme_cls