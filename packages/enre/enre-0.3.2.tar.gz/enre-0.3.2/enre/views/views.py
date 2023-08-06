# -*- coding: utf-8 -*- 

import datetime
from django.views.generic import TemplateView


class NoCacheMixin(object):
    no_cache = False

    def set_no_cache(self, response):
        if self.no_cache:
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = datetime.datetime.strftime(
                datetime.datetime.utcnow() - datetime.timedelta(seconds=1), '%a, %d %b %Y %H:%M:%S GMT'
            )
        return response

    pass


class ScriptView(NoCacheMixin, TemplateView):
    mime_type = 'text/javascript'

    def render_to_response(self, context, **response_kwargs):
        if not response_kwargs.has_key('mimetype'):
            response_kwargs['mimetype'] = self.mime_type
        return super(ScriptView, self).render_to_response(context, **response_kwargs)

    def get(self, request, *args, **kwargs):
        return self.set_no_cache(super(ScriptView, self).get(request, *args, **kwargs))

    pass


class AjaxView(ScriptView):

    pass