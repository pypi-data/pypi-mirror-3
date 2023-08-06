# -*- coding: utf-8 -*-

from enre.qx.services import ModelService
from models import Product, Brand


class ProductService(ModelService):
    auth = False
    model = Product
    foregin_fields = ['brand__name', 'product_type__name']

    pass


class BrandService(ModelService):
    auth = False
    model = Brand
