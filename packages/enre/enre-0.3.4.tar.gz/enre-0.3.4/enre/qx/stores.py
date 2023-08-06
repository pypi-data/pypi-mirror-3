# -*- coding: utf-8 -*- 

import inspect
from django.db import transaction
from django.db.models import Q
from enre.services import DispatcherError, Service, ServiceError
from enre.qx.qxjson import Json
from enre.views import url_to_class

class StoreDispatcher(object):
    def __init__(self, request):
        self._request = request

    def _run_store(self):
        cls, _args, class_name = url_to_class(self._path, Store)
        method = 'default'
        args = list(_args)
        if len(args) > 0:
            method = args[0]
            del args[0]
        if not hasattr(cls, method):
            raise DispatcherError("Method '%s' was not found in class '%s'." % (method, cls.__name__))
        if method[0] == '_':
            raise DispatcherError("A method called '%s' can not be called remotely." % method)
        _method = getattr(cls(self._request), method)
        if not inspect.ismethod(_method):
            raise DispatcherError("Method '%s' is not a class method '%s'." % (method, cls.__name__))
        return _method(*args)

    @transaction.commit_manually
    def dispatch(self, path):
        self._path = path
        try:
            res = self._run_store()
            transaction.commit()
            return res
        except Exception, ex:
            transaction.rollback()
            raise ex
        pass

    pass


class StoreError(ServiceError):
    pass


class Store(Service):
    def default(self, **kwargs):
        raise StoreError('Not implemented.')

    pass


class ModelStore(Store):
    query = None
    params = {}
    fields = []
    related_fields = []

    def __init__(self, request, **kwargs):
        super(ModelStore, self).__init__(request, **kwargs)
        if not self.query:
            raise StoreError("Need to initialize the property 'query'.")
        if request.method == 'GET':
            self.params = dict(request.GET.items())
        else:
            self.params = Json.decode(request.raw_post_data)
        pass

    def _interval(self, result):
        _from = None if not self.params.has_key('_from') else int(self.params['_from'])
        _to = None if not self.params.has_key('_to') else int(self.params['_to']) + 1
        return result[_from:_to]

    def _parse_args(self, filter):
        arg_list = []
        for st in filter:
            if type(st) == dict:
                arg_list.append(Q(**st))
            elif type(st) == list:
                arg_list.append(self._parse_args(st))
            elif st == 'or' or st == 'and':
                arg_list.append(st)
            pass
        if len(arg_list) == 1:
            return arg_list[0]
        q = arg_list[0]
        for i in range(1, len(arg_list), 2):
            st = arg_list[i]
            arg = arg_list[i + 1]
            if st == 'or':
                q = q | arg
            elif st == 'and':
                q = q & arg
            else:
                raise ValueError('Bad logical statement')
        return q

    def _query_method(self, params_name, result):
        qry = result
        method = params_name[1:]
        flt = Json.decode(self.params[params_name])
        if (type(flt) == dict or type(flt) == list) and len(flt) == 0:
            return qry
        if type(flt) == dict:
            qry = getattr(qry, method)(**flt)
        elif type(flt) == list:
            qry = getattr(qry, method)(self._parse_args(flt))
        else:
            raise StoreError('Bad query method type')
        return qry

    def _fields(self, result):
        if len(self.fields) == 0 and len(self.related_fields) == 0:
            return result
        qry = result
        if len(self.fields) == 0:
            self.fields = self.query.model._meta.get_all_field_names()
        elif isinstance(self.fields, tuple):
            self.fields = list(self.fields)
        if len(self.related_fields) > 0:
            self.fields.extend(self.related_fields)
        return qry.values(*self.fields)

    def _order_names(self, order):
        names = []
        for name in order:
            if name.startswith('-'):
                names.append(name[1:])
            else:
                names.append(name)
            pass
        return names

    def _query(self, distinct=[]):
        qry = self._fields(self.query)
        if self.params.has_key('_filter'):
            qry = self._query_method('_filter', qry)
        if self.params.has_key('_exclude'):
            qry = self._query_method('_exclude', qry)
        order = []
        if self.params.has_key('_order'):
            order = Json.decode(self.params['_order'])
        if self.params.has_key('_distinct'):
            order.extend(Json.decode(self.params['_distinct']))
        if len(distinct)> 0:
            order.extend(distinct)
        if len(order) > 0:
            qry = qry.order_by(*order)
            if self.params.has_key('_distinct') or len(distinct) > 0:
                qry = qry.distinct(*self._order_names(order))
            pass
        return qry

    def _get_relation(self, relation, pk, method=None, *args, **kwargs):
        if pk == 'null':
            return []
        query = getattr(self.query.get(pk=pk), relation)
        store = ModelStore(self.request, query=query, **kwargs)
        if not hasattr(kwargs, 'auth'):
            store.auth = self.auth
        if not hasattr(kwargs, 'permissions'):
            store.permissions = self.permissions
        if not method:
            return store.default()
        if method[0] == '_':
            raise DispatcherError("A method called '%s' can not be called remotely." % method)
        _method = getattr(store, method)
        return _method(*args)

    def relation(self, relation, pk, method=None, *args):
        return self._get_relation(relation, pk, method)

    def row_count(self):
        return self._query().count()

    def default(self):
        qry = self._query()
        if not self.params.has_key('_filter') and not self.params.has_key('_exclude'):
            qry = qry.all()
        return list(self._interval(qry))

    pass
