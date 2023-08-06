# -*- coding: utf-8 -*- 

from django.contrib import admin
from enre.erp.product.models import Brand, ProductType, Product

class BrandAdmin(admin.ModelAdmin):
    pass

admin.site.register(Brand, BrandAdmin)

class ProductTypeAdmin(admin.ModelAdmin):
    pass

admin.site.register(ProductType, ProductTypeAdmin)

class ProductAdmin(admin.ModelAdmin):
    pass

admin.site.register(Product, ProductAdmin)