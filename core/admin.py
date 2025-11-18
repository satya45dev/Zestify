from django.contrib import admin
from .models import Product, Order

# Register your models here so they show up in the admin panel
admin.site.register(Product)
admin.site.register(Order)