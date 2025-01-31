from django.contrib import admin
from .models import Product, Category

# Register your models here.

class CategoryAdmin (admin.ModelAdmin):
    list_display = ['name','id','slug']
    prepopulated_fields = {'slug':('name',)}


class ProductAdmin (admin.ModelAdmin):
    list_display = ['name','id', 'price','sold', 'category', 'availability']

admin.site.register( Category, CategoryAdmin )
admin.site.register( Product, ProductAdmin )