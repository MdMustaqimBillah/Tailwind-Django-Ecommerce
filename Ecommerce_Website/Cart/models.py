from django.db import models
from django.conf import settings
from Products.models import Product


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_cart')
    products = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_in_cart')
    quantity = models.PositiveIntegerField(default=1)
    purchased = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.email}"
    
    def get_unpurchased_carts(self):
        return self.objects.filter(purchased=False).count()
    
    def total(self):
        total= self.quantity * self.products.price
        return float(total)
    

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_order')
    carts = models.ManyToManyField(Cart, related_name='cart_for_order')
    ordered= models.BooleanField(default=False)
    delivered= models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order_id = models.CharField(max_length=264, null=True, blank=True)
    payment_id = models.CharField(max_length=264, null=True, blank=True)

    def __str__(self):
        return f"Order for {self.user.email}"
    
    def total(self):
        total= sum([cart.total() for cart in self.carts.all()])
        return format(int(total), '0.2f' )


class UserOrder(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_total_order')
    count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"UserOrder for {self.user.email}"
    
class TotalOrder(models.Model):
    count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"TotalOrder"