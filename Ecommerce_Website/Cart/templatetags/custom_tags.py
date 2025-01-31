from django import template
from Cart.models import Cart

register = template.Library()

@register.simple_tag
def unpurchased_carts(user):
    if user.is_authenticated:
        return Cart.objects.filter(user=user, purchased=False).count()
    return 0
