from django.db import models
from Authentication.models import User
from datetime import timedelta
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField
# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100 , blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.user.email}'s Profile"
    
    def is_fully_filled(self):
        fields = [self.address, self.city, self.country, self.postal_code]
        for field in fields:
            item_str = str(field).strip().upper()
            if not item_str or item_str =='NONE':
                return False
        return True
    def is_name_added(self):
        fields =[self.first_name, self.last_name]
        for field in fields:
            item_str = str(field).strip().upper()
            if not item_str or item_str =='NONE':
                return False
            return True
def is_social_profile(self):
    return self.user.is_social_user if hasattr(self.user, 'is_social_user') else False
                

class PhoneNumber(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_phone_number')
    phone_number = PhoneNumberField(max_length=15, unique=True )
    is_verified = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.phone_number = self.phone_number.as_e164
        super().save(*args, **kwargs)
    
    def is_valid(self):
        if self.is_verified:
            return True
        return False



class NumberVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)

    def is_valid(self):
        current_time = timezone.now()
        return current_time <= self.expires_at
    

class NameChanger(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='name_changer')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_valid(self):
        if self.created_at == self.updated_at:
            return True
        if timezone.now()-timedelta(days=60) > self.updated_at:
            return True
        return False
