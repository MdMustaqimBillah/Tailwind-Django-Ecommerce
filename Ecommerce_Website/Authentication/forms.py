from django import forms
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from .models import User



class SignUpForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField()
    last_name = forms.CharField()
    password1 = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = User
        fields = ['email','first_name','last_name', 'password1', 'password2']


class LoginForm(AuthenticationForm):
    username = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = User
        fields = ['username', 'password']