# -*- coding: utf-8 -*-

from enre.qx.services import ModelService
from models import Product, Brand


class ProductService(ModelService):
    model = Product
    foregin_fields = ['brand__name', 'product_type__name']

    pass


class BrandService(ModelService):
    model = Brand
