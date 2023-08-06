# -*- coding: utf-8 -*- 

from django.conf.urls import patterns, url
from enre.views import ScriptView
from views import RpcView, StoreView, AjaxRendererView

urlpatterns = patterns('',
    url(r'^enre/qx/qx_django.js$', ScriptView.as_view(template_name='enre/qx/qx_django.js', no_cache=True),
        name='enre_qx_django'
    ),
    url(r'^enre/qx/.rpc', RpcView.as_view(), name='enre_qx_rpc'),
    url(r'^enre/qx/.store/(?P<path>[^\s]*)', StoreView.as_view(), name='enre_qx_store'),
    url(r'^enre/qx/.ajax/(?P<path>[^\s]*)', AjaxRendererView.as_view(), name='enre_qx_ajax'),
)
