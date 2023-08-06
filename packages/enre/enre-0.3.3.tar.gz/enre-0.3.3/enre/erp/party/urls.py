# -*- coding: utf-8 -*- 

from django.conf.urls import patterns
from enre.erp.core.urls import application_url
from views import PartyView

urlpatterns = patterns('',
    application_url(r'^', PartyView),
)
