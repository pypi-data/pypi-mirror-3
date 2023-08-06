# -*- coding: utf-8 -*- 

from enre.qx.services import ModelService
from django.contrib.auth.models import User, Group, Permission
from models import Application
from enre.services.decorators import permissions_required

class UserService(ModelService):
    model = User

    def get(self, pk=None):
        model = super(UserService, self).get(pk)
        if isinstance(model, dict):
            model['password'] = '_hidden_password_'
        return model

    @permissions_required(['change_user'])
    def save(self, obj):
        _passwd = None
        if obj.has_key('password'):
            if obj['password'] != '_hidden_password_':
                _passwd = obj['password']
            del obj['password']
        user = super(UserService, self).save(obj)
        if _passwd:
            user.set_password(_passwd)
            user.save()
            user.password = '_hidden_password_'
        return user

    @permissions_required(['delete_user'])
    def delete(self, pk):
        super(UserService, self).delete(pk)

    pass


class GroupService(ModelService):
    model = Group


class PermissionService(ModelService):
    model = Permission


class ApplicationService(ModelService):
    model = Application

