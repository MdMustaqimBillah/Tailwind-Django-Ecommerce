from django.db import models
from Authentication.models import User
from django.urls import reverse
from django.utils.text import slugify

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['id']

    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
     

class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_seller')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='categorised_products')
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    slug = models.SlugField(max_length=100, unique=True)
    image = models.ImageField(upload_to='Product_images/', blank=True, null=True)
    image2 = models.ImageField(upload_to='product_images/', blank=True, null=True)
    image3 = models.ImageField(upload_to='product_images/', blank=True, null=True)
    image4 = models.ImageField(upload_to='product_images/', blank=True, null=True)
    availability = models.BooleanField(default=True)
    rating = models.PositiveIntegerField(default=0, null=True, blank=True)
    reviewer = models.PositiveIntegerField(default=0, null=True, blank=True)
    sold = models.PositiveIntegerField(default=0, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering =['id']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
