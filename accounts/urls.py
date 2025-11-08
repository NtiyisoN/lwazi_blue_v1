from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('email-confirmation/', views.email_confirmation, name='email_confirmation'),
    path('otp-login/', views.otp_login, name='otp_login'),
    path('request-otp/', views.request_otp, name='request_otp'),
]

