from rest_framework import serializers
from .models import product, Order, order_items
from django.contrib.auth.models import User

# ......User-Serializer ..............
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

# ......Product-Serializer ..............
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = product
        fields = ['id', 'product_name', 'description', 'category', 'price', 'stock', 'img_url']

# ......Order-items-Serializer ..............
class OrderItemsSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only = True)
    class Meta:
        model = order_items
        # fields = ['order', 'product', 'quantity', 'price_at_purchase']
        fields = ['id', 'product', 'quantity', 'price_at_purchase']

# ......Order-Serializer ..............
class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only = True)
    items = OrderItemsSerializer(many=True, read_only = True)
    class Meta:
        model = Order
        fields = ['id', 'user', 'total_price', 'created_at', 'status', 'items' ]