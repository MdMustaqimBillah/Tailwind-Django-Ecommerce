from django.urls import path
from . import views

app_name = 'Products'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('product-add/',views.ProductFormView.as_view(), name='add_product'),
    path('product-edit/<int:product_id>/', views.update_product, name='edit_product'),
    path('my-products/',views.my_products, name='my_products'),  # Move this before category_slug
    path('delete-product/<int:pk>/', views.DeleteProduct.as_view(), name='delete_product'),
    path('<slug:category_slug>/', views.product_list, name='product_list'),  # Move this to the end
    path('product_details/<slug:slug>/<int:id>/', views.product_details, name='product_details'),
]