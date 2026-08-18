from django.db import models
from django.contrib.auth.models import User

# Create your models here

#........ User Model .........
# class User(models.Model):
#     username = models.CharField(max_length=255)
#     Email = models.EmailFieldField(max_length=255)
#     Password = models.CharField(max_length=255)

# ..... Product Model .....
class product(models.Model):
    product_name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    img_url = models.CharField(max_length=500)

    def __str__(self):
        return self.name
    
# ..... Order Model .....
class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Shipped', 'Shipped'),
    ]
    
    user = models.ForeignKey(User, related_name='order', on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"


    # .....Order-items ....
class order_items(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(product, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField()
    price_at_purchase = models.DecimalField( max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name if self.product else 'Deleted Product'} (Order #{self.order.id})"