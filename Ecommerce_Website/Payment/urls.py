from django.urls import path
from . import views

app_name = 'Payment'

urlpatterns = [
    path('checkout/<int:order_id>/', views.checkout, name='checkout'),
    path('pay/<int:order_id>/', views.payment, name='payment'),
    path('complete/<int:id>/',views.complete, name='complete'),
    path('purchase/<str:tran_id>/<str:val_id>/<int:id>/', views.purchased, name='purchased'),
]
