# -*- coding: utf-8 -*- 

from enre.qx.stores import ModelStore
from models import PartyType, PartyRole, Party
from django.db.models import F

class PartyTypeStore(ModelStore):
    query = PartyType.objects


class PartyRoleStore(ModelStore):
    query = PartyRole.objects


class PartyStore(ModelStore):
    query = Party.objects
    related_fields = ['party_type__name']

