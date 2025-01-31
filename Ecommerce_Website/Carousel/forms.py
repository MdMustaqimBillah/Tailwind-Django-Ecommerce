from django import forms
from .models import Carousel

class CarouselForm(forms.ModelForm):
    class Meta:
        model = Carousel
        fields = ['title', 'description', 'image']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'mt-1 block w-full shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm',
                'placeholder': 'Enter title',
                'rows':2
            }),
            'description': forms.Textarea(attrs={
                'class': 'mt-1 block w-full shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm',
                'placeholder': 'Enter description',
                'rows': 4
            }),
            'image': forms.FileInput(attrs={
                'class': 'sr-only',
                'accept': 'image/*'
            })
        }