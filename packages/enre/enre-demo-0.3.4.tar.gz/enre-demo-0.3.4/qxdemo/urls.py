# -*- coding: utf-8 -*- 

from django.conf.urls import patterns, include, url
from views import QxDemoView

urlpatterns = patterns('',
    url(r'^$', QxDemoView.as_view()),
    url(r'^', include('enre.qx.urls')),
    url(r'^login', 'django.contrib.auth.views.login', {'template_name': 'enre/qx/login.html'},
        name='qxdemo_login'),
    url(r'^logout', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='qxdemo_logout'),
)
