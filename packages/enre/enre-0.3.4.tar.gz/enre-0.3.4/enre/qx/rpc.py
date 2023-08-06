# -*- coding: utf-8 -*-

import inspect
from django.utils.importlib import import_module
from enre.services import Service, Dispatcher, DispatcherError
from enre.qx.qxjson import Json

class RpcDispatcherError(DispatcherError):

    ORIGIN_SERVER_ERROR = 1
    ORIGIN_METHOD_ERROR = 2

    ILLEGAL_SERVICE = 1
    SERVICE_NOT_FOUND = 2
    CLASS_NOT_FOUND = 3
    METHOD_NOT_FOUND = 4
    PARAMETER_MISMATCH = 5
    PERMISSION_DENIED = 6

    '''
    __server_messages = {
        1: "Illegal Service",
        2: "Service Not Found",
        3: "Class Not Found",
        4: "Method Not Found",
        5: "Parameter Mismatch",
        6: "Permission Denied",
        }
    '''

    def __init__(self, origin, code, message):
        self.origin = origin
        self.code = code
        self.message = message

    def __str__(self):
        return '{"origin": %s, "code": %s, "message ": "%s"}' % (self.origin, self.code, self.message)

    def error(self):
        return {'origin': self.origin, 'code': self.code, 'message': self.message}

    pass

#TODO: Проверить экранирование входных параметров
class RpcDispatcher(Dispatcher):

    def _run_service(self, service, method, *params):
        module_name = service
        if module_name.rfind('.') < 0:
            raise RpcDispatcherError(RpcDispatcherError.ORIGIN_SERVER_ERROR,
                RpcDispatcherError.ILLEGAL_SERVICE,
                "Bad service name '%s'" % module_name)
        else:
            service_name = module_name[module_name.rfind('.') + 1:]
            module_name = module_name[0:module_name.rfind('.')]
        try:
            module = import_module(module_name)
        except Exception, ex:
            raise RpcDispatcherError(RpcDispatcherError.ORIGIN_SERVER_ERROR,
                RpcDispatcherError.SERVICE_NOT_FOUND,
                ex.message)
        if not hasattr(module, service_name):
            raise RpcDispatcherError(RpcDispatcherError.ORIGIN_SERVER_ERROR,
                RpcDispatcherError.CLASS_NOT_FOUND,
                "Class '%s' is not found in module '%s'." % (service_name, module_name))
        cls = getattr(module, service_name)
        if not inspect.isclass(cls):
            raise RpcDispatcherError(RpcDispatcherError.ORIGIN_SERVER_ERROR,
                RpcDispatcherError.CLASS_NOT_FOUND,
                "Object '%s' is not a class." % service_name)
        if not issubclass(cls, Service):
            raise RpcDispatcherError(RpcDispatcherError.ORIGIN_SERVER_ERROR,
                RpcDispatcherError.PERMISSION_DENIED,
                "Class '%s' is not a descendant of the 'Service' class." % service_name)
        if not hasattr(cls, method):
            raise RpcDispatcherError(RpcDispatcherError.ORIGIN_SERVER_ERROR,
                RpcDispatcherError.METHOD_NOT_FOUND,
                "Method '%s' was not found in class '%s'." % (method, service_name))
        if method[0] == '_':
            raise RpcDispatcherError(RpcDispatcherError.ORIGIN_SERVER_ERROR,
                RpcDispatcherError.PERMISSION_DENIED,
                "A method called '%s' can not be called remotely." % method)
        method = getattr(cls(self._request), method)
        if not inspect.ismethod(method):
            raise RpcDispatcherError(RpcDispatcherError.ORIGIN_SERVER_ERROR,
                RpcDispatcherError.METHOD_NOT_FOUND,
                "Method '%s' is not a class method '%s'." % (method, service_name))
        _params = []
        if len(params) > 0:
            for param in params:
                _params.append(Json.check_value(param))
            pass
        return method(*_params)

    pass