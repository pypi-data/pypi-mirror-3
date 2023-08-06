# -*- coding: utf-8 -*- 

from django.db import models
from django.utils.translation import ugettext_lazy as _
from enre.db.models import Model, Manager
from enre.geo.models import Country, Currency
from utils import person_name_format
import transdef

class PartyTypeManager(Manager):
    def get_by_natural_key(self, codename):
        return self.get(codename=codename)

    pass


class PartyType(Model):
    codename = models.CharField(_('Codename'), max_length=30, unique=True)
    name = models.CharField(_('Name'), max_length=50, unique=True)
    template = models.CharField(_('Template'), max_length=100)
    objects = PartyTypeManager()

    class Meta:
        verbose_name = _('Party type')
        verbose_name_plural = _('Party types')
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
    codename = models.CharField(_('Codename'), max_length=30, unique=True)
    name = models.CharField(_('Name'), max_length=50, unique=True)
    party_types = models.ManyToManyField(PartyType, verbose_name=_('Party types'))
    objects = PartyRoleManager()

    class Meta:
        verbose_name = _('Party role')
        verbose_name_plural = _('Party roles')
        ordering = ('name',)

    def __unicode__(self):
        return self.name

    def natural_key(self):
        return (self.codename,)

    pass


class Party(Model):
    display_name = models.CharField(_('Name'), max_length=150, null=True, blank=True)
    description = models.CharField(_('Description'), max_length=1000, null=True, blank=True)
    party_type = models.ForeignKey(PartyType, on_delete=models.DO_NOTHING, verbose_name=_('Party type'))
    country = models.ForeignKey(Country, on_delete=models.DO_NOTHING, null=True, blank=True, verbose_name=_('Country'));
    currency = models.ForeignKey(Currency, on_delete=models.DO_NOTHING, null=True, blank=True,
        verbose_name=_('Currency'));

    def __unicode__(self):
        return self.display_name or ''

    class Meta:
        verbose_name = _('Party')
        verbose_name_plural = _('Parties')

    pass


class PartyRelationship(Model):
    party_from = models.ForeignKey(Party, on_delete=models.DO_NOTHING, related_name='party_from',
        verbose_name=_('Party from'))
    party_to = models.ForeignKey(Party, on_delete=models.DO_NOTHING, related_name='party_to',
        verbose_name=_('Party to'))
    role_to = models.ForeignKey(PartyRole, on_delete=models.DO_NOTHING, verbose_name=_('Role to'))

    class Meta:
        verbose_name = _('Party relationship')
        verbose_name_plural = _('Party relationships')

    pass


class Person(Model):
    party = models.OneToOneField(Party)
    first_name = models.CharField(_('First name'), max_length=50)
    last_name = models.CharField(_('Last name'), max_length=50)
    middle_name = models.CharField(_('Middle name'), max_length=50, null=True, blank=True)

    @property
    def display_name(self):
        return person_name_format(self.first_name, self.last_name, self.middle_name)

    class Meta:
        verbose_name = _('Person')
        verbose_name_plural = _('Persons')

    pass


class Organization(Model):
    party = models.OneToOneField(Party)
    name = models.CharField(max_length=100)

    @property
    def display_name(self):
        return self.name

    class Meta:
        verbose_name = _('Organization')
        verbose_name_plural = _('Organizations')

    pass


def __party_pre_save(sender, instance, raw, **kwargs):
    if isinstance(instance, Organization) or isinstance(instance, Person):
        party = Party.objects.get(pk=instance.pk)
        party.display_name = instance.display_name
        party.save()

    pass

models.signals.pre_save.connect(__party_pre_save)
