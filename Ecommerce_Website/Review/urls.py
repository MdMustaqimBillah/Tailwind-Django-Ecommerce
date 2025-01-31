from django.urls import path
from . import views

app_name = 'Review'

urlpatterns =[
    path('review/<int:product_id>/', views.review, name='review'),
]