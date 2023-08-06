# -*- coding: utf-8 -*- 

from django.conf import settings

def init_module_settings(module, default_settings):
    if not hasattr(settings, module):
        setattr(settings, module, {})
    for key, val in default_settings.iteritems():
        if not getattr(settings, module).has_key(key):
            getattr(settings,module)[key] = val
        pass
    pass
