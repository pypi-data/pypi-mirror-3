# -*- coding: utf-8 -*- 

import inspect
from django.conf import settings
from django.views.generic import View, TemplateView
from django.http import HttpResponse, HttpResponseServerError
from django.utils.importlib import import_module
from enre.views import NoCacheMixin, AjaxView, url_to_class
from rpc import RpcDispatcher, RpcDispatcherError
from stores import StoreDispatcher
from qxjson import Json

#TODO: Добавить трассирову ошибок в Debug режиме
class RpcView(NoCacheMixin, View):
    no_cache = True

    def post(self, request, *args, **kwargs):
        result = None
        error = None
        try:
            _request = Json.decode(request.raw_post_data)
        except:
            return HttpResponseServerError('Waiting for request in json format.')
        if (not _request.has_key('id') or not _request.has_key('service') or not _request.has_key('method')
            or not _request.has_key('params')):
            return HttpResponseServerError('Request parameters are not correct.')
        id = _request['id']
        try:
            dispatcher = RpcDispatcher(request)
            result = dispatcher.dispatch(_request['service'], _request['method'], *_request['params'])
        except RpcDispatcherError, ex:
            error = ex.error()
        except Exception, ex:
            error = RpcDispatcherError(RpcDispatcherError.ORIGIN_METHOD_ERROR,
                RpcDispatcherError.ILLEGAL_SERVICE,
                ex.message).error()
        try:
            response = Json.encode({'result': result, 'error': error, 'id': id})
        except Exception, ex:
            error = RpcDispatcherError(RpcDispatcherError.ORIGIN_METHOD_ERROR,
                RpcDispatcherError.ILLEGAL_SERVICE,
                ex.message).error()
            response = Json.encode({'result': None, 'error': error, 'id': id})
        http_response = self.set_no_cache(HttpResponse(response, mimetype='application/json'))
        return http_response

    pass


class StoreView(NoCacheMixin, View):
    no_cache = True
    module = None

    def _dispatch(self, request, *args, **kwargs):
        if not request.method.lower() in ['get', 'post']:
            return HttpResponseServerError("Method '%s' is not supported." % request.method)
        path = kwargs['path']
        try:
            dispatcher = StoreDispatcher(request)
            response = Json.encode(dispatcher.dispatch(path))
            http_response = HttpResponse(response, mimetype='application/json')
            return self.set_no_cache(http_response)
        except Exception, ex:
            return HttpResponseServerError(ex.message)
        pass

    pass

    def get(self, request, *args, **kwargs):
        return self.set_no_cache(self._dispatch(request, *args, **kwargs))

    def post(self, request, *args, **kwargs):
        return self.set_no_cache(self._dispatch(request, *args, **kwargs))

    pass


class AjaxRendererView(View):
    def get(self, request, *args, **kwargs):
        if not request.method.lower() in ['get', 'post']:
            return HttpResponseServerError("Method '%s' is not supported." % request.method)
        path = kwargs['path']
        view, _args, cls = url_to_class(path, AjaxView)
        args += _args
        return view().dispatch(request, *args, **kwargs)

    pass


class ApplicationView(TemplateView):
    template_name = 'enre/qx/application.html'
    script_template = None
    script_class = None
    theme_url = settings.STATIC_URL + 'enre/qx/theme/simple.js'
    theme_class = 'enre.theme.Simple'
    scripts_src = []

    def get_context_data(self, **kwargs):
        data = {
            'script_template': self.script_template,
            'script_class': self.script_class,
            'theme_url': self.theme_url,
            'theme_class': self.theme_class,
            'scripts_src': self.scripts_src
        }
        return data

    pass
