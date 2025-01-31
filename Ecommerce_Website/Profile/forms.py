from django import forms
from .models import Profile, PhoneNumber
from phonenumber_field.modelfields import PhoneNumberField


class UserProfileForm(forms.ModelForm):
    country = forms.CharField()
    city = forms.CharField()
    address = forms.CharField()
    postal_code = forms.CharField()
    profile_picture = forms.ImageField(label='Avatar',required=False)
    class Meta:
        model = Profile
        fields = ['country', 'city', 'address','postal_code','profile_picture']

class PhoneNumberForm(forms.ModelForm):
    phone_number = PhoneNumberField(max_length=15)

    class Meta:
        model = PhoneNumber
        fields = ['phone_number']


class UpdateNameForm(forms.ModelForm):
    first_name = forms.CharField()
    last_name = forms.CharField()
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name']