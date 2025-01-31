from django.db import models
from django.conf import settings
from Cart.models import Order
# Create your models here.


class BillingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_billing_address')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_billing_address')
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    country = models.CharField(max_length=200)
    zip_code = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.address
    
    def is_fully_filled(self):
        field_names = [f.name for f in self._meta.get_fields()]
        
        for field_name in field_names:
            value = getattr(self, field_name)
            if value is None or value == '':
                return False
        return True
    
    class Meta:
        verbose_name = "Billing Addresses"