from django.contrib import admin
from .models import BillingAddress

# Register your models here.

class BillingAddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'address', 'city', 'zip_code', 'country']

admin.site.register(BillingAddress, BillingAddressAdmin)