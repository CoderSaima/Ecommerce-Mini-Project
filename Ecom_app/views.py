from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import product, Order, order_items
from django.db import transaction
from rest_framework.decorators import action
from .serializers import OrderSerializer, ProductSerializer

# Create your views here.

#....  Product ViewSet (Public Access)
class productViewSet(viewsets.ModelViewSet):
    """
    A viewset that provides default CRUD actions for Products.
    Anyone can view products, but only Admins can create/edit them.
    """
    queryset = product.objects.all().order_by('-id')
    serializer_class = ProductSerializer


    def get_permission(self):
        if self.action in ['lists', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permissions() for permissions in permission_classes]

#.... Order ViewSet (Protected Private Access)
class orderViewSet(viewsets.ModelViewSet):
    """
    A viewset that provides default CRUD actions for Orders.
    Users can only see and manage their own orders.
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Strict Multi-Tenancy Data Security
        # Ensures a logged-in user can never query or view someone else's receipt logs
        return Order.object.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        # Automatically links the incoming order snapshot to the currently active user profile
        serializer.save(user=self.request.user)

@action(detail=False, methods=['post'], url_path=('checkout'))
def checkout(self, request):
    """
    Custom endpoint to process shopping carts, create order items, 
    and securely deduct product inventory quantities automatically.
    """
    user = request.user
    cart_data  = request.data.get('items', [])
    if not cart_data:
        return Response({'error': 'Your Shopping card is empty'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        with transaction.atomic():
        # 1. Initialize a blank Order receipt
            order=order.objects.create(user=user, total_price=0.00, status='pending')
        # 2. Iterate through each line-item inside the payload array
            for items in cart_data:
                product_id = items.get('product_id')
                quantity = int(items.get('quantity', 1))

                # Look up product from PostgreSQL safely
                try:
                    Product = product.objects.select_for_update().get(id=product_id)
                except Product.DoesNotExist:
                    raise Exception (f"Product Id {product_id} no longer exists in our database store.")

                # Business Logic Check: Evaluate Stock Availability
                if product.stock < quantity:
                    raise Exception(f"Insufficient Stock requirements for {product.name}")

                # Deduct Inventory Stock Level
                product.stock -= quantity
                product.save()

                # Track pricing adjustments and accumulate running calculation
                item_price = product.price * quantity
                total_price += item_price

                # Build the database record item row
                order_items.objects.create(
                    order = order,
                    product = product,
                    quantity = quantity,
                    price_at_purchase = product.price
                )

            # Finalize order financial parameters and save
            order_total_price = total_price
            order.status = 'paid'
            order.save()

            # Serialize the completed database row snapshot
            serializer = order.get_serializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as error_msg:
        return Response({'error': str(error_msg)},status=status.HTTP_400_BAD_REQUEST)



