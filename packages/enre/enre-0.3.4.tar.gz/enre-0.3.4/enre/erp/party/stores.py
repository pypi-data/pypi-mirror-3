# -*- coding: utf-8 -*- 

from enre.qx.stores import ModelStore
from models import (PartyType,
                    PartyRole,
                    Party,
                    Organization,
                    Person,
                    ContactInfo,
                    ContactInfoType,
                    PostalAddressType,
                    PostalAddress)


class PartyTypeStore(ModelStore):
    query = PartyType.objects


class PartyRoleStore(ModelStore):
    query = PartyRole.objects


class PartyStore(ModelStore):
    query = Party.objects
    related_fields = ['party_type__codename', 'party_type__name']

    def relation(self, relation, pk, method=None, *args):
        kwargs = {}
        if relation == 'contactinfo_set':
            kwargs['fields'] = [
                'id', 'info', 'contact_info_type__id', 'contact_info_type__codename',
                'contact_info_type__name', 'record_version'
            ]
        if relation == 'parent_party':
            kwargs['fields'] = [
                'id', 'parent_party', 'related_party__display_name', 'related_party_role__name', 'record_version'
            ]
        if relation == 'paymentmethod_set':
            kwargs['fields'] = [
                'id', 'method', 'payment_method_type__id', 'payment_method_type__codename',
                'payment_method_type__name', 'record_version'
            ]
        return super(PartyStore, self)._get_relation(relation, pk, method, *args, **kwargs)

    def _query(self, distinct=[]):
        return super(PartyStore, self)._query(['id'])

    def own_parties(self, method=None):
        self.query = self.query.filter(is_own=True)
        if method:
            return self.row_count()
        return self.default()

    pass


class ContactInfoTypeStore(ModelStore):
    query = ContactInfoType.objects


class ContactInfoStore(ModelStore):
    query = ContactInfo.objects


class PostalAddressTypeStore(ModelStore):
    query = PostalAddressType.objects


class PostalAddressStore(ModelStore):
    query = PostalAddress.objects


class OrganizationStore(ModelStore):
    query = Organization.objects


class PersonStore(ModelStore):
    query = Person.objects
