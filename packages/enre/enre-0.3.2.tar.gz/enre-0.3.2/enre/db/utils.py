# -*- coding: utf-8 -*- 

from django.db.models import Model
from django.db.models.query import ValuesQuerySet, QuerySet
from django.core.exceptions import FieldError


def model_to_dict(instance, fields=None, exclude=None):
    opts = instance._meta
    data = {}
    for f in opts.fields:
        if not f.editable:
            continue
        if fields and not f.name in fields:
            continue
        if exclude and f.name in exclude:
            continue
        data[f.name] = f.value_from_object(instance)
    return data


def db_to_dict(obj, fields=None):
    cls = type(obj)
    if issubclass(cls, ValuesQuerySet):
        if fields:
            fd = set(fields).difference(obj.field_names)
            if len(fd) > 0:
                raise FieldError(" 'Cannot resolve keyword '%s' into field(s).\n"
                                 "Choices are: %s" % (', '.join(fd), ','.join(obj.field_names)))
            result = []
            for item in obj:
                result.append(dict([(key, val) for key, val in item.items() if key in fields]))
            pass
        else:
            result = obj
        result = list(result)
    elif issubclass(cls, QuerySet):
        result = obj.values(fields)
    elif issubclass(cls, Model):
        result = model_to_dict(obj, fields)
    else:
        raise TypeError("Type '%s' is not valid." % cls)
    return result
