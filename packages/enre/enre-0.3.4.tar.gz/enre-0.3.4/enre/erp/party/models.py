# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from enre.db.models import Model, Manager
from enre.geo.models import Country, Region, Currency
from enre.erp.core.models import BaseReference
from utils import default_settings, person_name_format, postal_address_format
import transdef

default_settings()

class PartyType(BaseReference):
    class Meta:
        verbose_name = _('Party type')
        verbose_name_plural = _('Party types')
        ordering = ('name',)

    pass


class PartyRole(BaseReference):
    party_types = models.ManyToManyField(PartyType, verbose_name=_('Party types'))

    class Meta:
        verbose_name = _('Party role')
        verbose_name_plural = _('Party roles')
        ordering = ('name',)

    pass


class Party(Model):
    display_name = models.CharField(_('Name'), max_length=150)
    short_display_name = models.CharField(_('Short name'), max_length=150, null=True, blank=True)
    description = models.CharField(_('Description'), max_length=1000, null=True, blank=True)
    party_type = models.ForeignKey(PartyType, on_delete=models.DO_NOTHING, verbose_name=_('Party type'))
    country = models.ForeignKey(Country, on_delete=models.DO_NOTHING, null=True, blank=True, verbose_name=_('Country'))
    currency = models.ForeignKey(Currency, on_delete=models.DO_NOTHING, null=True, blank=True,
        verbose_name=_('Currency'))
    is_own = models.BooleanField(_('Own party'), default=False)
    users = models.ManyToManyField(User, verbose_name=_('Users'))
    ogrn = models.CharField(_('OGRN'), max_length=13, null=True, blank=True)
    okpo = models.CharField(_('OKPO'), max_length=11, null= True, blank=True)
    okato = models.CharField(_('OKATO'), max_length=11, null=True, blank=True)

    class Meta:
        verbose_name = _('Party')
        verbose_name_plural = _('Parties')


    def get_display_name(self):
        return self.display_name

    def get_short_display_name(self):
        return self.short_display_name

    def __unicode__(self):
        return self.get_display_name()

    def save(self, force_insert=False, force_update=False, using=None):
        self.display_name = self.get_display_name()
        self.short_display_name = self.get_short_display_name()
        super(Party, self).save(force_insert, force_update, using)

    pass


class Organization(Party):
    name = models.CharField(_('Name'), max_length=100, unique=True)
    short_name = models.CharField(_('Short name'), max_length=50, null=True, blank=True)
    inn = models.CharField(_('INN'), max_length=10, null=True, blank=True)
    kpp = models.CharField(_('KPP'), max_length=9, null=True, blank=True)

    class Meta:
        verbose_name = _('Organization')
        verbose_name_plural = _('Organizations')

    def get_display_name(self):
        return self.name

    def get_short_display_name(self):
        return self.short_name

    def save(self, force_insert=False, force_update=False, using=None):
        if not hasattr(self, 'party_type'):
            self.party_type = PartyType.objects.get_by_natural_key('organization')
        super(Organization, self).save(force_insert, force_update, using)

    pass


class Person(Party):
    first_name = models.CharField(_('First name'), max_length=50)
    last_name = models.CharField(_('Last name'), max_length=50)
    middle_name = models.CharField(_('Middle name'), max_length=50, null=True, blank=True)
    birthday = models.DateField(_('Birthday'), null=True, blank=True)
    is_business_owner = models.BooleanField(_('Business owner'), default=False)
    inn = models.CharField(_('INN'), max_length=12, null=True, blank=True)

    class Meta:
        unique_together = ('first_name', 'last_name', 'middle_name', 'birthday')
        verbose_name = _('Person')
        verbose_name_plural = _('Persons')

    def get_display_name(self):
        return person_name_format(self.first_name, self.last_name, self.middle_name)

    def get_short_display_name(self):
        return self.get_display_name()

    def save(self, force_insert=False, force_update=False, using=None):
        if not hasattr(self, 'party_type'):
            self.party_type = PartyType.objects.get_by_natural_key('person')
        super(Person, self).save(force_insert, force_update, using)

    pass


class PartyRelationship(Model):
    parent_party = models.ForeignKey(Party, on_delete=models.DO_NOTHING, related_name='parent_party',
        verbose_name=_('Parent party'))
    related_party = models.ForeignKey(Party, on_delete=models.DO_NOTHING, related_name='related_party',
        verbose_name=_('Related party'))
    related_party_role = models.ForeignKey(PartyRole, on_delete=models.DO_NOTHING, verbose_name=_('Role'))

    class Meta:
        unique_together = ('parent_party', 'related_party', 'related_party_role')
        verbose_name = _('Party relationship')
        verbose_name_plural = _('Party relationships')

    pass


class ContactInfoType(BaseReference):
    order = models.IntegerField(_('Order'), default=0)

    class Meta:
        verbose_name = _('Contact info type')
        verbose_name_plural = _('Contact info types')
        ordering = ('order',)

    pass


class ContactInfo(Model):
    contact_info_type = models.ForeignKey(ContactInfoType, on_delete=models.DO_NOTHING,
        verbose_name=_('Contact info type'))
    party = models.ForeignKey(Party, verbose_name=_('Party'))
    info = models.CharField(_('Contact'), max_length=255)
    description = models.TextField(_('Description'), null=True, blank=True)
    is_solicitation = models.BooleanField(_('Allow solicitation'), default=True)
    is_active = models.BooleanField(_('Active'), default=True)

    class Meta:
        verbose_name = _('Contact info')
        unique_together = (('party', 'info'),)

    def __unicode__(self):
        return self.info

    def get_info(self):
        return self.info

    def save(self, force_insert=False, force_update=False, using=None):
        self.info = self.get_info()
        super(ContactInfo, self).save(force_insert, force_update, using)

    pass


class PostalAddressType(BaseReference):
    class Meta:
        verbose_name = _('Postal address type')
        verbose_name_plural = _('Postal address types')

    pass


class PostalAddress(ContactInfo):
    postal_address_types = models.ManyToManyField(PostalAddressType, verbose_name=_('Party addresses'))
    to_name = models.CharField(_('To name'), max_length=150, null=True, blank=True)
    address = models.CharField(_('Address'), max_length=255)
    address2 = models.CharField(_('Address2'), max_length=255, null=True, blank=True)
    city = models.CharField(_('City'), max_length=50)
    postal_code = models.CharField(_('Postal code'), max_length=50, null=True, blank=True)
    region = models.ForeignKey(Region, on_delete=models.DO_NOTHING, null=True, blank=True, verbose_name=_('Region'))
    country = models.ForeignKey(Country, on_delete=models.DO_NOTHING, null=True, blank=True, verbose_name=_('Country'))

    def get_info(self):
        region = None
        country = None
        if self.region:
            region = self.region.name
        if self.country:
            country = self.country.name
        return postal_address_format(self.address, self.address2, self.city, region, self.postal_code, country,
            self.to_name)

    class Meta:
        verbose_name = _('Postal address')
        verbose_name_plural = _('Postal addresses')

    pass


def __party_pre_save(sender, instance, raw, **kwargs):
    if not raw:
        return
    if isinstance(instance, Organization) or isinstance(instance, Person):
        party = Party.objects.get(pk=instance.pk)
        party.display_name = instance.get_display_name()
        party.short_display_name = instance.get_short_display_name()
        party.save()
    elif isinstance(instance, PostalAddress):
        contact_info = ContactInfo.objects.get(pk=instance.pk)
        contact_info.info = instance.get_info()
        contact_info.save()
        pass
    pass

models.signals.pre_save.connect(__party_pre_save)
