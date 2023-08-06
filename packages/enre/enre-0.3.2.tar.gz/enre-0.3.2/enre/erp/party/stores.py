# -*- coding: utf-8 -*- 

from enre.qx.stores import ModelStore
from models import PartyType, PartyRole

class PartyTypeStore(ModelStore):
    query = PartyType.objects


class PartyRoleStore(ModelStore):
    query = PartyRole.objects
