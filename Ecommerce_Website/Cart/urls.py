from django.urls import path
from . import views

app_name = 'Cart'

urlpatterns = [
    path('cart/',views.user_cart, name='user_cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('buy-now/<int:product_id>/', views.proceed_to_checkout, name='buy_now'),
    path('proceed-to-checkout/', views.proceed_to_checkout, name='proceed_to_checkout'),
    path('increase-item/<int:pk>/', views.increment, name='increase_item'),
    path('decrease-item/<int:pk>/', views.decrement, name='decrease_item'),
    path('remove-item/<int:pk>/', views.remove_from_cart, name='remove_item'),
    path('my-orders/', views.OrderSummaryView.as_view(), name='my_orders'),
    path('download-invoice/<int:order_id>/', views.download_invoice, name='download_invoice'),
    path('pending-orders/', views.pending_orders, name='pending_orders'),
    path('delivered-orders/', views.delivered_orders, name='delivered_orders'),
    path('delivered-order-details/<int:order_id>/', views.detail_delivered_order, name='details_delivered_order'),
    path('pending-order-details/<int:order_id>/', views.detail_pending_order, name='details_pending_order'),
]