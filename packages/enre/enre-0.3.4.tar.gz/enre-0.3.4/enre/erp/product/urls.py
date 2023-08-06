# -*- coding: utf-8 -*- 

from django.conf.urls import patterns
from enre.erp.core.urls import application_url
from views import ProductsView

urlpatterns = patterns('',
    application_url(r'^', ProductsView),
)
