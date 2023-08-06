# -*- coding: utf-8 -*- 

from enre.erp.core.views import ApplicationView, Module


class ProductsView(ApplicationView):
    name = 'Products'

    modules = {
        'catalog':  Module(
            name = 'Catalog',
            template_name = 'enre/erp/product/catalog.js',
            script_class = 'enre.erp.product.Catalog',
            color='#CD853F'
        ),
        'product': Module(
            name = 'Products',
            template_name = 'enre/erp/product/product.js',
            script_class = 'enre.erp.product.ProductList',
            color='#2E8B57'
        ),
        'settings':  Module(
            name = 'Settings',
            template_name = 'enre/erp/product/settings.js',
            script_class = 'enre.erp.product.Settings'
        )
    }


