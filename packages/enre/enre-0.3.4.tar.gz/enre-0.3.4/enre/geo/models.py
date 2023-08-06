# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.staticfiles.storage import StaticFilesStorage
from enre.db.models import Model, Manager
import transdef

class CountryManager(Manager):
    def get_by_natural_key(self, code):
        return self.get(code=code)

    pass


class Country(Model):
    code = models.CharField(_('Code'), max_length=2, unique=True)
    name = models.CharField(_('Name'), max_length=150, unique=True)
    flag = models.ImageField(_('Flag'), upload_to='enre/geo/flags', null=True, blank=True,
        storage=StaticFilesStorage()
    )
    objects = CountryManager()

    class Meta:
        verbose_name = _('Country')
        verbose_name_plural = _('Countries')
        ordering = ('name', )

    def __unicode__(self):
        return self.name

    def natural_key(self):
        return (self.code,)

    pass


class RegionManager(Manager):
    def get_by_natural_key(self, code, country_code):
        return self.get(code=code, country=Country.objects.get_by_natural_key(country_code))

    pass


class Region(Model):
    code = models.CharField(_('Code'), max_length=10)
    name = models.CharField(_('Name'), max_length=150)
    country = models.ForeignKey(Country, on_delete=models.DO_NOTHING, verbose_name=_('Country'))
    objects = RegionManager()

    class Meta:
        verbose_name = _('Region')
        verbose_name_plural = _('Regions')
        unique_together = (('country', 'code'), ('country', 'name'))
        ordering = ('country__name', 'name')

    def __unicode__(self):
        return self.name

    def natural_key(self):
        return (self.code,) + self.country.natural_key()

    pass


class CurrencyManager(Manager):
    def get_by_natural_key(self, code):
        return self.get(code=code)

    pass


class Currency(Model):
    code = models.CharField(_('Code'), max_length=3, unique=True)
    symbol = models.CharField(_('Symbol'), max_length=4, unique=True)
    name = models.CharField(_('Name'), max_length=50, unique=True)
    is_active = models.BooleanField(_('Active'), default=True)
    objects = CurrencyManager()

    class Meta:
        verbose_name = _('Currency')
        verbose_name_plural = _('Currencies')
        ordering = ('code', )

    def __unicode__(self):
        return self.name

    def natural_key(self):
        return (self.code,)

    pass
