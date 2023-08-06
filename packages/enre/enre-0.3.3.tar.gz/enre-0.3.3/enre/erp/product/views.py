# -*- coding: utf-8 -*- 

from enre.erp.core.views import ApplicationView, Module


class ProductsView(ApplicationView):
    name = 'Products'

    modules = [
        Module(
            name = 'Catalog',
            path = 'catalog',
            template_name = 'enre/erp/product/catalog.js',
            script_class = 'enre.erp.product.Catalog',
            color='#CD853F'
        ),
        Module(
            name = 'Products',
            path = 'product',
            template_name = 'enre/erp/product/product.js',
            script_class = 'enre.erp.product.ProductList',
            color='#2E8B57'
        ),
        Module(
            name = 'Settings',
            path = 'settings',
            template_name = 'enre/erp/product/settings.js',
            script_class = 'enre.erp.product.Settings'
        )
    ]


