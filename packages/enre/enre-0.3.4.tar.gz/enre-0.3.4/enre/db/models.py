# -*- coding: utf-8 -*- 

from django.db import models
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User, Permission, Group
from django.conf import settings
from django.core.exceptions import FieldError
from django.utils import timezone
from django.test.client import RequestFactory
from django.db import transaction

SYSTEM_FIELDS = ['created_stamp', 'created_user', 'last_updated_stamp', 'last_updated_user']

class RecordVersionField(models.BigIntegerField):
    def __init__(self):
        kwargs = {'default': 0}
        super(RecordVersionField, self).__init__(**kwargs)

    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname)
        if add:
            return value
        old_instance = model_instance.__class__.objects.get(pk=model_instance.pk)
        if value and getattr(old_instance, self.attname) != value:
            raise FieldError('Record updated by another user')
        if not value:
            value = getattr(old_instance, self.attname)
        if value < self.MAX_BIGINT:
            value = value + 1
        else:
            value = 0
        setattr(model_instance, self.attname, value)
        return value

    pass

class CurrentUserField(models.CharField):
    def __init__(self, on_update=False, **kwargs):
        self.on_update = on_update
        kwargs['blank'] = True
        kwargs['max_length'] = 30
        kwargs['default'] = 'system'
        super(CurrentUserField, self).__init__(**kwargs)

    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname)
        if value and not self.on_update:
            return value
        if hasattr(model_instance, '_request') and model_instance._request:
            value = model_instance._request.user.username
        return value

    pass


class BlobField(models.Field):
    def db_type(self, connection):
        engine = connection.settings_dict['ENGINE']
        if engine == 'django.db.backends.postgresql_psycopg2':
            return 'bytea'
        elif engine == 'django.db.backends.mysql':
            return 'longblob'
        elif engine == 'django.db.backends.sqlite3':
            return 'blob'
        elif engine == 'django.db.backends.oracle':
            return 'blob'
        else:
            raise NotImplementedError
        pass

    pass


class Manager(models.Manager):
    @property
    def request(self):
        _request = self.model()._request
        if not _request:
            _request = RequestFactory()
            transaction.commit_manually()
            setattr(_request, 'user', User.objects.get(username='system'))
            transaction.commit()
        return _request

    pass


class BaseModel(models.Model):
    _request = None
    objects = Manager()

    class Meta:
        abstract = True

    pass


class TimestampModel(BaseModel):
    created_stamp = models.DateTimeField(default=timezone.now())
    last_updated_stamp = models.DateTimeField(default=timezone.now(), auto_now=True)

    class Meta:
        abstract = True

    pass


class VersionModel(BaseModel):
    record_version = RecordVersionField()

    class Meta:
        abstract = True

    pass


class Model(TimestampModel, VersionModel):
    created_user = CurrentUserField()
    last_updated_user = CurrentUserField(True)

    class Meta:
        abstract = True

    pass


#
# EXTEND SYSTEM MODEL
#
def __timestamp_model_patch(model):
    model.add_to_class('created_stamp', models.DateTimeField(default=timezone.now()))
    model.add_to_class('last_updated_stamp', models.DateTimeField(default=timezone.now(), auto_now=True))


def __version_model_patch(model):
    model.add_to_class('record_version', RecordVersionField())


def __model_patch(model):
    __timestamp_model_patch(model)
    __version_model_patch(model)
    model.add_to_class('created_user', CurrentUserField(blank=True))
    model.add_to_class('last_updated_user', CurrentUserField(True, blank=True))


def __extend():
    if not 'django.contrib.auth' in settings.INSTALLED_APPS or not 'django.contrib.sessions' in settings.INSTALLED_APPS:
        raise RuntimeError("'django.contrib.auth' or  'django.contrib.sessions' is not installed")
    __timestamp_model_patch(Session)
    __model_patch(Permission)
    __model_patch(Group)
    __model_patch(User)

__extend()


#
# INITIALIZING DB
#
def __init_db(sender, **kwargs):
    if not User.objects.filter(username='system').exists():
        print 'Create system account'
        user = User()
        user.username = 'system'
        user.password = '*'
        user.is_active = True
        user.is_superuser = True
        user.is_staff = True
        user.save()
    _models = kwargs['created_models']
    if  len(_models) == 0:
        return
    for model in _models:
        model._meta.permissions = [("view_%s" % model.__name__.lower(), "Can view"), ]
    pass

models.signals.post_syncdb.connect(__init_db)
