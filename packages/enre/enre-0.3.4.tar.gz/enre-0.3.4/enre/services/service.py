# -*- coding: utf-8 -*- 

import inspect
from django.db import transaction
from django.utils.importlib import import_module

class DispatcherError(Exception):
    pass


class Dispatcher(object):
    def __init__(self, request):
        self._request = request

    def _run_service(self, service, method, *params):
        if type(service) == str:
            module_name = service
            if module_name.rfind('.') < 0:
                raise DispatcherError("Bad service name '%s'" % module_name)
            else:
                service_name = module_name[module_name.rfind('.') + 1:]
                module_name = module_name[0:module_name.rfind('.')]
            try:
                module = import_module(module_name)
            except Exception, ex:
                raise DispatcherError(ex.message)
            if not hasattr(module, service_name):
                raise DispatcherError("Class '%s' is not found in module '%s'." % (service_name, module_name))
            cls = getattr(module, service_name)
        else:
            cls = service
        if not inspect.isclass(cls):
            raise DispatcherError("Object '%s' is not a class." % repr(service))
        if not issubclass(cls, Service):
            raise DispatcherError("Class '%s' is not a descendant of the 'Service' class." % repr(service))
        if not hasattr(cls, method):
            raise DispatcherError("Method '%s' was not found in class '%s'." % (method, repr(service)))
        if method[0] == '_':
            raise DispatcherError("A method called '%s' can not be called remotely." % method)
        method = getattr(cls(self._request), method)
        if not inspect.ismethod(method):
            raise DispatcherError("Method '%s' is not a class method '%s'." % (method, repr(service)))
        return method(*params)

    @transaction.commit_manually
    def dispatch(self, service, method, *params):
        try:
            res = self._run_service(service, method, *params)
            transaction.commit()
            return res
        except Exception, ex:
            transaction.rollback()
            raise ex
        pass

    pass


class ServiceError(Exception):
    pass


class Service(object):
    request = None
    auth = True
    permissions = []
    user = None

    def __init__(self, request, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)
        self.request = request
        if not hasattr(request, 'user'):
            raise ServiceError("Feature request 'User' is not defined.")
        self.user = request.user

    def __getattribute__(self, name):
        attr = super(Service, self).__getattribute__(name)
        if name[0] == '_' or not inspect.ismethod(attr):
            return attr
        if not hasattr(attr, 'auth'):
            setattr(attr.__func__, 'auth', self.auth)
        if attr.auth and not self.user.is_authenticated():
            raise ServiceError('User is not authenticated.')
        if not hasattr(attr, 'permissions'):
            setattr(attr.__func__, 'permissions', self.permissions)
        if len(attr.permissions) > 0:
            for permission in attr.permissions:
                if not self.user.has_perm(permission):
                    raise ServiceError("Permission '%s' denied." % permission)
                pass
            pass
        return attr

    pass
