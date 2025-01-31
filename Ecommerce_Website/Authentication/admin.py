from django.contrib import admin
from .models import User, EmailVerification

class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'is_superuser']

class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'token', 'created_at']

admin.site.register(User, UserAdmin)
admin.site.register(EmailVerification, EmailVerificationAdmin)