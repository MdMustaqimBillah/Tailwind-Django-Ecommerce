from django.contrib import admin
from django.urls import include, path
from Products.views import product_list
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', product_list, name='product_list'),
    path('', include('Products.urls')),
    path('auth/',include('Authentication.urls')),
    path('profile/',include('Profile.urls')),
    path('cart/',include('Cart.urls')),
    path('pay/',include('Payment.urls')),
    path('review/',include('Review.urls')),
    path('carousel/',include('Carousel.urls')),
    path('social-auth/', include('social_django.urls', namespace='social'))
] + static(settings.STATIC_URL, document_root= settings.STATIC_ROOT)

if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL,
                              document_root=settings.MEDIA_ROOT)