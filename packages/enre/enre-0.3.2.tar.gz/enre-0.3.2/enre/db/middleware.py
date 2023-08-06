# -*- coding: utf-8 -*- 

from django.db.models import signals
from django.utils.functional import curry
from django.db.models import Model

class RequestToModelMiddleware(object):
    def __request_to_model(self, request, sender, **kwargs):
        if not issubclass(sender, Model):
            return
        setattr(sender, '_request', request)

    def process_request(self, request):
        request_to_model = curry(self.__request_to_model, request)
        signals.pre_init.connect(request_to_model, dispatch_uid=request, weak=False)

    def process_response(self, request, response):
        signals.pre_init.disconnect(dispatch_uid=request)
        return response

    pass
