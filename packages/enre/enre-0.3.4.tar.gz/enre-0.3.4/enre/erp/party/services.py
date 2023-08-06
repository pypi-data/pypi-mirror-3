# -*- coding: utf-8 -*- 

from enre.qx.services import ModelService
from models import (PartyType,
                    PartyRole,
                    Party,
                    PartyRelationship,
                    Organization,
                    Person,
                    ContactInfoType,
                    ContactInfo,
                    PostalAddressType,
                    PostalAddress
                    )


class PartyTypeService(ModelService):
    model = PartyType


class PartyRoleService(ModelService):
    model = PartyRole


class PartyService(ModelService):
    model = Party

    def set_is_own(self, pk, is_own):
        model = self.model.objects.get(pk=pk)
        model.is_own = is_own
        model.save()
        return True

    pass

class PartyRelationshipService(ModelService):
    model = PartyRelationship


class OrganizationService(PartyService):
    model = Organization


class PersonService(PartyService):
    model = Person


class ContactInfoTypeService(ModelService):
    model = ContactInfoType


class PostalAddressTypeService(ModelService):
    model = PostalAddressType


class ContactInfoService(ModelService):
    model = ContactInfo


class PostalAddressService(ModelService):
    model = PostalAddress
