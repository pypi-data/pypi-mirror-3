# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils.decorators import method_decorator
from enre.qx.views import ApplicationView

class QxDemoView(ApplicationView):
    script_template = 'qxdemo/qxdemo.js'
    script_class = 'qxdemo.Application'
    theme_url = settings.STATIC_URL + 'enre/qx/theme/indigo.js'
    theme_class = 'enre.theme.Indigo'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(QxDemoView, self).dispatch(request, *args, **kwargs)

    pass