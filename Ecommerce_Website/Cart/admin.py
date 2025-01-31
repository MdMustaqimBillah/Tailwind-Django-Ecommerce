from django.contrib import admin
from .models import Order, Cart, UserOrder, TotalOrder


# Register your models here.

class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'order_id', 'ordered', 'delivered']

class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'products', 'quantity', 'purchased']

class UserOrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'count',]

class TotalOrderAdmin(admin.ModelAdmin):
    list_display = ['count']


admin.site.register(Order, OrderAdmin)

admin.site.register(Cart, CartAdmin)

admin.site.register(UserOrder, UserOrderAdmin)

admin.site.register(TotalOrder, TotalOrderAdmin)