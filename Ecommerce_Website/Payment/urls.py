from django.urls import path
from . import views

app_name = 'Payment'

urlpatterns = [
    path('checkout/<int:order_id>/', views.checkout, name='checkout'),
]