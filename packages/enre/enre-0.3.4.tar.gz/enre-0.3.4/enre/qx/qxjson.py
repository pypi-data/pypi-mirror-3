# -*- coding: utf-8 -*- 

import json
from decimal import Decimal
from datetime import date, datetime
from json.decoder import WHITESPACE
from django.db.models import Model
from django.db.models.fields.files import FieldFile
from django.db.models.query import ValuesQuerySet, QuerySet
from django.utils.timezone import utc
from django.utils.functional import Promise
from enre.db.utils import db_to_dict


class JSONEncoder(json.JSONEncoder):
    def _encode_datetime(self, obj):
        if isinstance(obj, datetime):
            return 'new Date(Date.UTC(%d,%d,%d,%d,%d,%d,%d))' % (obj.year, obj.month - 1, obj.day, obj.hour,
                                                                 obj.minute, obj.second, obj.microsecond * 0.001)
        else:
            return 'new Date(Date.UTC(%d,%d,%d,0,0,0,0))' % (obj.year, obj.month - 1, obj.day)

    def default(self, obj):
        if isinstance(obj, date) or isinstance(obj, datetime):
            return self._encode_datetime(obj)
        elif isinstance(obj, Decimal):
            return str(obj)
        elif isinstance(obj, FieldFile):
            if hasattr(obj, 'url'):
                return obj.url
            else:
                return None
            pass
        elif isinstance(obj, ValuesQuerySet) or isinstance(obj, QuerySet) or isinstance(obj, Model):
            return db_to_dict(obj)
        elif isinstance(obj, Promise):
            return unicode(obj)
        return  json.JSONEncoder.default(self, obj)

    pass


class JSONDecoder(json.JSONDecoder):
    '''
    def _check_datetime(self, obj):
        if obj[:18] != 'new Date(Date.UTC(' or obj[-2:] != '))':
            return obj
        t = [int(i) for i in obj.split("UTC(")[1].split("))")[0].split(",")]
        if len(t) == 3:
            return date(*t)
        if len(t) == 6:
            return datetime(*t)
        if len(t) == 7:
            t[6] *= 1000
            return datetime(*t)
        raise ValueError('Invalid number of arguments: %s' % obj)
    '''

    def _custom_decode(self, obj):
        if isinstance(obj, dict):
            for key in obj:
                obj[key] = self._custom_decode(obj[key])
        elif isinstance(obj, list):
            lst = list()
            for l in obj:
                lst.append(self._custom_decode(l))
            obj = lst
        elif isinstance(obj, str) or isinstance(obj, unicode):
            obj = Json.check_datetime(obj)
            if obj == '_null_value_':
                obj = None
            pass
        return obj

    def decode(self, s, _w=WHITESPACE.match):
        obj = super(JSONDecoder, self).decode(s, _w)
        return self._custom_decode(obj)

    pass


class Json:
    @staticmethod
    def encode(obj):
        cls = type(obj)
        if issubclass(cls, ValuesQuerySet) or issubclass(cls, QuerySet) or issubclass(cls, Model):
            return Json.db_encode(obj)
        return JSONEncoder().encode(obj)

    @staticmethod
    def decode(obj):
        return JSONDecoder().decode(obj)

    @staticmethod
    def db_encode(obj, fields=None):
        obj = db_to_dict(obj, fields)
        return JSONEncoder().encode(obj)

    @staticmethod
    def db_decode(obj, model):
        pass

    @staticmethod
    def is_json(obj):
        if (type(obj) == str or type(obj) == unicode)\
           and (obj[0] == '{' or obj[0] == '[') and (obj.endswith('}') or obj.endswith(']')):
            return True
        return False

    @staticmethod
    def check_datetime(obj):
        if obj[:18] != 'new Date(Date.UTC(' or obj[-2:] != '))':
            return obj
        t = [int(i) for i in obj.split("UTC(")[1].split("))")[0].split(",")]
        t[1] += 1
        if len(t) == 3:
            return datetime(*t).replace(tzinfo=utc)
        if len(t) == 6:
            return datetime(*t).replace(tzinfo=utc)
        if len(t) == 7:
            t[6] *= 1000
            return datetime(*t).replace(tzinfo=utc)
        raise ValueError('Invalid number of arguments: %s' % obj)

    @staticmethod
    def check_value(obj):
        if isinstance(obj, str) or isinstance(obj, unicode):
            if Json.is_json(obj):
                return Json.decode(obj)
            else:
                return Json.check_datetime(obj)
            pass
        else:
            return obj
        pass

    pass
