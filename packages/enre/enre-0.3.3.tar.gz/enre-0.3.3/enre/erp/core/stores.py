# -*- coding: utf-8 -*- 

from enre.qx.stores import Store, ModelStore
from references import refs
from django.contrib.auth.models import User, Group, Permission
from models import Application

class ReferenceStore(Store):
    def default(self, **kwargs):
        return refs.get_references()

    pass


class UserStore(ModelStore):
    fields = [
        'id',
        'username',
        'first_name',
        'last_name',
        'is_active',
        'is_staff',
        'is_superuser',
        'created_stamp',
        'created_user',
        'date_joined',
        'email',
        'last_login',
        'last_updated_user',
        'record_version',
        ]
    query = User.objects


class GroupStore(ModelStore):
    query = Group.objects


class PermissionStore(ModelStore):
    query = Permission.objects
    related_fields = ['content_type__name']


class ApplicationStore(ModelStore):
    query = Application.objects

