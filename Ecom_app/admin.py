from django.contrib import admin
from .models import product, Order, order_items

# Register your models here.
admin.site.register(product)
admin.site.register(Order)
admin.site.register(order_items)