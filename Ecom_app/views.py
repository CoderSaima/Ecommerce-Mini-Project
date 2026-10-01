from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import product, Order, order_items
from django.db import transaction
from rest_framework.decorators import action
from .serializers import OrderSerializer, ProductSerializer

# Create your views here.
from django.shortcuts import render

def store_home(request):
    """Serves the main landing page framework out from your templates directory."""
    return render(request, 'main.html')

def start_page(request):
    """Serves your auxiliary clone layout file from the Part sub-directory."""
    return render(request, 'Part/index.html')



#....  Product ViewSet (Public Access)
class productViewSet(viewsets.ModelViewSet):
    """
    A viewset that provides default CRUD actions for Products.
    Anyone can view products, but only Admins can create/edit them.
    """
    queryset = product.objects.all().order_by('-id')
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']: # 🛠️ FIXED: Renamed 'lists' typo to standard DRF singular action name 'list'
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [perm() for perm in permission_classes] # 🛠️ FIXED: Initialized class loops properly without overlapping your module package namespace alias

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
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        # Automatically links the incoming order snapshot to the currently active user profile
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'], url_path='checkout')
    def checkout(self, request):
        """
        Custom endpoint to process shopping carts, create order items, 
        and securely deduct product inventory quantities automatically.
        """
        user = request.user
        cart_data = request.data.get('items', [])
        if not cart_data:
            return Response({'error': 'Your Shopping cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                # 1. Initialize a blank Order receipt
                # 🛠️ FIXED: Adjusted target lookup to point to Capitalized 'Order' class object manager safely
                new_order = Order.objects.create(user=user, total_price=0.00, status='Pending')
                running_total_price = 0
                
                # 2. Iterate through each line-item inside the payload array
                for item_node in cart_data:
                    product_id = item_node.get('product_id')
                    quantity = int(item_node.get('quantity', 1))

                    # Look up product safely
                    try:
                        # 🛠️ FIXED: Uniformed variable assignments to reference clean lowercase target instance arrays smoothly
                        target_product = product.objects.select_for_update().get(id=product_id)
                    except product.DoesNotExist:
                        raise Exception(f"Product Id {product_id} no longer exists in our database store.")

                    # Business Logic Check: Evaluate Stock Availability
                    if target_product.stock < quantity:
                        raise Exception(f"Insufficient Stock requirements for {target_product.product_name}") # 🛠️ FIXED: Changed matching parameter reference from .name to .product_name

                    # Deduct Inventory Stock Level
                    target_product.stock -= quantity
                    target_product.save()

                    # Track pricing adjustments and accumulate running calculation
                    item_price = target_product.price * quantity
                    running_total_price += item_price

                    # Build the database record item row
                    order_items.objects.create(
                        order=new_order,
                        product=target_product,
                        quantity=quantity,
                        price_at_purchase=target_product.price
                    )

                # Finalize order financial parameters and save
                new_order.total_price = running_total_price
                new_order.status = 'Paid'
                new_order.save()

                # Serialize the completed database row snapshot
                serializer = self.get_serializer(new_order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as error_msg:
            return Response({'error': str(error_msg)}, status=status.HTTP_400_BAD_REQUEST)