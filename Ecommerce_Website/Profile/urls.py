from django.urls import path
from Profile import views

app_name = 'Profile'

urlpatterns =[
    
    path('profile/', views.profile, name='profile'),
    path('profile_setup/', views.profile_setup, name='profile_setup'),
    path('verification/', views.verification_view, name='verification'),
    path('verify-code/<str:phone_number>/', views.verify_code, name='verify_code'),
    path('resend-code/', views.resend_code, name='resend_code'),
    path('change-name/', views.change_name, name='change_name'),
]