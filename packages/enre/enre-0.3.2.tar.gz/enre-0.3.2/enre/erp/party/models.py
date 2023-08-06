# -*- coding: utf-8 -*- 

from django.db import models
from django.utils.translation import ugettext_lazy as _
from enre.db.models import Model, Manager

class PartyTypeManager(Manager):
    def get_by_natural_key(self, codename):
        return self.get(codename=codename)

    pass


class PartyType(Model):
    codename = models.CharField(_('party_codename'), max_length=30, unique=True)
    name = models.CharField(_('party_type_name'), max_length=50, unique=True)
    template = models.CharField(_('party_template'), max_length=100)
    objects = PartyTypeManager()

    class Meta:
        verbose_name = _('party_type')
        verbose_name_plural = _('party_types')
        ordering = ('name',)

    def __unicode__(self):
        return self.name

    def natural_key(self):
        return (self.codename,)

    pass


class PartyRoleManager(Manager):
    def get_by_natural_key(self, codename):
        return self.get(codename=codename)

    pass


class PartyRole(Model):
    codename = models.CharField(_('party_codename'), max_length=30, unique=True)
    name = models.CharField(_('party_role_name'), max_length=50, unique=True)
    party_types = models.ManyToManyField(PartyType, verbose_name=_('party_type_name'))
    objects = PartyRoleManager()

    class Meta:
        verbose_name = _('party_role')
        verbose_name_plural = _('party_roles')
        ordering = ('name',)

    def __unicode__(self):
        return self.name

    def natural_key(self):
        return (self.codename,)

    pass
