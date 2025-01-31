from django.urls import path
from . import views

app_name = 'Carousel'

urlpatterns = [
    path('add-carousel/', views.CarouselCreateView.as_view(), name='add_carousel'),
    path('update-carousel/<int:pk>', views.CarouselUpdateView.as_view(),name='update_carousel'),
    path('delete-carousel/<int:pk>', views.CarouselDeleteView.as_view(), name='delete_carousel'),
    path('', views.CarouselListView.as_view(), name='carousel_list'),
]