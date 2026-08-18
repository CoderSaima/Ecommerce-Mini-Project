from rest_framework import serializers
from .models import product, Order, order_items
from django.contrib.auth.models import User

# ......User-Serializer ..............
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        field = ['id', 'username', 'email']

# ......Product-Serializer ..............
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = product
        field = ['id', 'name', 'description', 'category', 'price', 'stock', 'img_url']

# ......Order-items-Serializer ..............
class orderItemsSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only = True)
    class Meta:
        model = order_items
        field = ['order', 'product', 'quantity', 'price_at_purchase']

# ......Order-Serializer ..............
class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only = True)
    items = orderItemsSerializer(many=True, read_only = True)
    class Meta:
        model = Order
        field = ['id', 'user', 'total_price', 'created_at', 'status', 'items' ]