# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.db.utils import DatabaseError
from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from enre.db.models import BaseModel, Model, Manager
import transdef

class ApplicationManager(Manager):
    __apps_count = int(0)

    @classmethod
    def set_apps_count(cls, value):
        cls.__apps_count = value

    @classmethod
    def get_apps_count(cls):
        return cls.__apps_count

    @classmethod
    def inc_apps_count(cls):
        cls.set_apps_count(cls.get_apps_count() + 1)

    @staticmethod
    @transaction.commit_manually
    def init_apps():
        def _init_apps():
            for app in Application.objects.all():
                app.order = 65535
                app.is_active = False
                app.save()
            pass

        try:
            _init_apps()
        except DatabaseError, e:
            if (e.args[0].find('relation "erp_application" does not exist') != 0
                and e.args[0].find('relation "auth_user" does not exist') != 0
                and e.args[0].find('no such table: erp_application') != 0
                and e.args[0].find('no such table: auth_user') != 0):
                transaction.rollback()
                raise e
            pass
        transaction.commit()

    def all(self, show_inactive=False):
        def _all(show_inactive):
            objects = super(ApplicationManager, self)
            if not show_inactive:
                objects = objects.filter(is_active=True)
            if  not self.request.user.is_superuser:
                objects = objects.filter(user=self.request.user)
            return objects.all()

        try:
            return _all(show_inactive)
        except DatabaseError, e:
            if e.args[0].find('relation "erp_application" does not exist') != 0:
                raise e
            pass
        pass

    pass


class Application(BaseModel):
    view_name = models.CharField(primary_key=True, max_length=150)
    name = models.CharField(max_length=50, unique=True)
    order = models.IntegerField(default=65535)
    is_active = models.BooleanField(default=False)
    objects = ApplicationManager()

    class Meta:
        db_table = 'erp_application'
        ordering = ('order', )

    def __unicode__(self):
        return self.name

    pass

User.add_to_class('erp_applications', models.ManyToManyField(Application, blank=True))


class BaseReferenceManager(Manager):
    def get_by_natural_key(self, codename):
        return self.get(codename=codename)

    pass


class BaseReference(Model):
    codename = models.CharField(_('Codename'), max_length=30, unique=True)
    name = models.CharField(_('Name'), max_length=50, unique=True)
    objects = BaseReferenceManager()

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.name

    def natural_key(self):
        return (self.codename,)

    pass
