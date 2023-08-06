# -*- coding: utf-8 -*- 

import inspect
from enre.views import url_to_class

class ReferencesPool(object):
    __references = []

    @classmethod
    def register(cls, reference):
        cls.__references.append(reference)

    @classmethod
    def unregister(cls, reference):
        cls.__references.remove(reference)

    @classmethod
    def get_references(cls):
        refs = []
        for ref in cls.__references:
            refs.append({
                'name': ref.name,
                'url': ref.url,
                'group': ref.group,
                'class_name': ref.class_name
            })
        return refs

    pass


class Reference(object):
    name = None
    url = None
    group = None
    class_name = None
    permissions = []

    def __init__(self, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)
        if self.url and not self.class_name:
            cls, args, class_name = url_to_class(self.url)
            self.class_name = class_name
        pass

    pass

refs = ReferencesPool
