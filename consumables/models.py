from django.db import models
from django.conf import settings
from accounts.models import User

import stripe

class Product(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    stripe_product_identifier = models.CharField('Stripe product identifier', max_length=100, blank=False, null=False)
    image = models.ImageField(max_length=100, blank=True, null=True)
    unit_label = models.CharField(max_length=20, blank=False, null=False, default='hour')

    def __str__(self):
        if self.name:
            return self.name
        return self.stripe_product_identifier

    def sync(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        product = stripe.Product.retrieve(self.stripe_product_identifier)
        self.name = product.name
        self.description = product.description
        self.save()

    def get_price(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        prices = stripe.Price.list(product=self.stripe_product_identifier)
        return prices.data[0].unit_amount / 100.0
