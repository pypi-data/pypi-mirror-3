# -*- coding: utf-8 -*- 

from enre.db.models import Model, BlobField
from django.db import models
from datetime import datetime

class Brand(Model):
    name = models.CharField(max_length=50, unique=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']

    pass


class ProductType(Model):
    name = models.CharField(max_length=50, unique=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']

    pass


class Product(Model):
    article = models.CharField(max_length=50, unique=True)
    part_number = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=255)
    brand = models.ForeignKey(Brand, on_delete=models.DO_NOTHING)
    product_type = models.ForeignKey(ProductType, on_delete=models.DO_NOTHING, null=True, blank=True)
    introduction_date = models.DateTimeField(default=datetime.now())
    release_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['article']

    pass
