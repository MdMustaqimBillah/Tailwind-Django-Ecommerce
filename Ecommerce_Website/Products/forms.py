from django import forms
from .models import Product


class ProductForm(forms.ModelForm):
    new_category = forms.CharField(required=False)

    class Meta:
        model = Product
        fields = ['name', 'category', 'price', 'description', 'image','image2','image3','image4', 'availability']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].required = False