# -*- coding: utf-8 -*-

from django.contrib import auth
from django.db import models
from django.db.models.related import RelatedObject
from enre.services import Service, ServiceError
from django.utils.translation import activate
from enre.services.decorators import login_exempt
from enre.db.models import SYSTEM_FIELDS

class ModelService(Service):
    model = None
    foregin_fields = []
    ignore_fields = SYSTEM_FIELDS

    def __init__(self, request):
        if not self.model:
            raise ServiceError('Model is not defined.')
        if not issubclass(self.model, models.Model):
            raise ServiceError('The wrong type of model.')
        super(ModelService, self).__init__(request)

    def __check_field(self, model, field_name):
        if field_name.find('__') >= 0 or field_name in self.ignore_fields:
            return False
        fc = model._meta.get_field_by_name(field_name)[0]
        if isinstance(fc, models.ManyToManyField) or isinstance(fc, RelatedObject):
            return False
        return True

    def get(self, pk=None):
        if pk:
            _model = self.model.objects.get(pk=pk)
            values = []
            for field_name in self.model._meta.get_all_field_names():
                if not self.__check_field(_model, field_name):
                    continue
                values.append(field_name)
            values = values + self.foregin_fields
            return self.model.objects.values(*values).get(pk=pk)
        return self.model()

    def save(self, obj):
        pk_name = self.model._meta.pk.name
        if obj.has_key(str(pk_name)) and obj[pk_name]:
            _model = self.model.objects.get_or_create(pk=obj[pk_name])[0]
        else:
            _model = self.model()
        for field_name in obj:
            if not self.__check_field(_model, field_name):
                continue
            fc = _model._meta.get_field_by_name(field_name)[0]
            if not isinstance(fc, models.ForeignKey):
                val = obj[field_name]
            elif obj[field_name]:
                fm = fc.rel.to
                val = fm.objects.get(pk=obj[field_name])
            else:
                continue
            setattr(_model, field_name, val)
        _model.save()
        return _model

    def delete(self, pk):
        rec = self.model.objects.get(pk=pk)
        rec.delete()
        return True

    def create_relation(self, relation, model_pk, relation_pk):
        _model = self.model.objects.get(pk=model_pk)
        _relation = getattr(_model, relation).model.objects.get(pk=relation_pk)
        getattr(_model, relation).add(_relation)
        return True

    def delete_relation(self, relation, mode, model_pk, relation_pk):
        _model = self.model.objects.get(pk=model_pk)
        _relation = getattr(_model, relation).get(pk=relation_pk)
        if mode == 'relation':
            getattr(_model, relation).remove(_relation)
        elif mode == 'record':
            _relation.delete()
        else:
            raise ServiceError('Bad delete mode')
        return True

    def create_relations(self, relation, model_pk, relations_pks):
        for pk in relations_pks:
            self.create_relation(relation, model_pk, pk)
        pass

    def delete_relations(self, relation, mode, model_pk, relations_pks):
        for pk in relations_pks:
            self.delete_relation(relation, mode, model_pk, pk)
        pass

    pass


class LanguageService(Service):
    auth = False
    permissions = []

    def set_language(self, lang_code):
        self.request.session['django_language'] = lang_code
        activate(lang_code)
        return True

    pass


class AuthService(Service):
    @login_exempt
    def login(self, username, password):
        if self.user.is_authenticated():
            return True
        user = auth.authenticate(username=username, password=password)
        if not user:
            raise ServiceError('Login failure.')
        if not user.is_active:
            raise ServiceError('Account is blocked.')
        auth.login(self.request, user)
        return True

    def logout(self):
        auth.logout(self.request)

    pass