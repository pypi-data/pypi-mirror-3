# -*- coding: utf-8 -*- 

import inspect
from django.conf.urls import patterns, url, include
from django.contrib import admin
from views import ApplicationView, SettingsView
from models import Application

admin.autodiscover()

def application_url(regex_prefix, view):
    if not issubclass(view, ApplicationView):
        raise ValueError('Bad view type')
    if regex_prefix.endswith('$'):
        raise ValueError("Bad regex_prefix '%s' ('$' not supported)" % regex_prefix)
    if regex_prefix.endswith('/'):
        regex_prefix = regex_prefix[len(regex_prefix) - 1]
    regex = regex_prefix + '/(?P<path>[^\s]*)'
    view_name = '_'.join((inspect.getmodule(view).__name__.replace('.', '_'), view.__name__)).lower()
    app = Application.objects.get_or_create(view_name=view_name)[0]
    app.name = view.name
    count = Application.objects.get_apps_count()
    if count > 0:
        app.order = count
    else:
        app.order = 65534
    app.active=True
    app.save()
    Application.objects.inc_apps_count()
    return url(regex, view.as_view(), name=view_name)


urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    application_url(r'^settings', SettingsView),
    url(r'^login', 'django.contrib.auth.views.login', {'template_name': 'enre/erp/core/login.html'},
        name='enre_erp_core_login'),
    url(r'^logout', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='enre_erp_core_logout'),
)
