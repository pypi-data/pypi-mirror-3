# -*- coding: utf-8 -*- 

from enre.qx.stores import ModelStore
from models import Brand, Product, ProductType


class BrandStore(ModelStore):
    query = Brand.objects


class ProductTypeStore(ModelStore):
    query = ProductType.objects


class ProductStore(ModelStore):
    query = Product.objects
    related_fields = ['brand__name', 'product_type__name']

