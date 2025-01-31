from django.db import models
from django.conf import settings
from Products.models import Product
from datetime import timedelta
from Cart.models import Order

# Create your models here.

class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_reviews')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_reviews')
    rate = ( (1, '1'),
             (2, '2'),
             (3, '3'),
             (4, '4'),
             (5, '5')
             )

    rating = models.PositiveIntegerField(choices=rate)
    comment = models.TextField(blank=True, null=True, max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} rates {self.rating} on {self.product}'

    def review_expires(self):
        return self.created_at + timedelta(days=30)
    
    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'

    