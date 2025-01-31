from django.urls import include, path
from Authentication import views
from django.contrib.auth.decorators import login_required

app_name = 'Authentication'

urlpatterns = [
    path('login/', views.user_login, name='user_login'),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<str:token>/', views.reset_password, name='reset_password'),
    path('reset-verification/', views.reset_password_code_check, name='reset_password_code_check'),
    path('change_password/', views.change_password, name='change_password'),
    path('verify_email/<str:token>/', views.verify_email, name='verify_email'),
    path('resend_verification/', views.resend_verification, name='resend_verification'),
    path('logout/', views.user_logout, name='logout'),
]