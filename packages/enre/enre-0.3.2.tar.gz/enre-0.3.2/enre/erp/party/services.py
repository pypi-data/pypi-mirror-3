# -*- coding: utf-8 -*- 

from enre.qx.services import ModelService
from models import PartyType, PartyRole

class PartyTypeService(ModelService):
    model = PartyType


class PartyRoleService(ModelService):
    model = PartyRole
