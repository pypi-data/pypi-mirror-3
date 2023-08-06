# -*- coding: utf-8 -*- 

from enre.qx.stores import ModelStore
from models import Brand, Product, ProductType
from enre.db.utils import model_to_dict

class BrandStore(ModelStore):
    query = Brand.objects


class ProductTypeStore(ModelStore):
    query = ProductType.objects


class ProductStore(ModelStore):
    query = Product.objects

    def default(self):
        f = Product._meta.get_all_field_names()
        f = f + ['brand__name', 'product_type__name']
        self.query = self.query.values(*f)
        return super(ProductStore, self).default()

    pass
