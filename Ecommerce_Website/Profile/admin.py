from django.contrib import admin
from .models import Profile, PhoneNumber, NumberVerification, NameChanger

# Register your models here.

class ProfileAdmin(admin.ModelAdmin):
    # Changed 'email' to 'user' since email is in User model
    list_display = ['user', 'postal_code']  # or any other fields that exist in Profile model

class PhoneNumberAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'user']

class NumberVerificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'verification_code','created_at', 'expires_at']

class NameChangerAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'updated_at']

admin.site.register(Profile, ProfileAdmin)
admin.site.register(PhoneNumber, PhoneNumberAdmin)
admin.site.register(NumberVerification, NumberVerificationAdmin)
admin.site.register(NameChanger, NameChangerAdmin)