# accounts/urls.py
from django.urls import path
from .views import LogoutView 
from django.contrib.auth.views import LogoutView
from django.contrib.auth.views import LoginView, LogoutView 
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),  # Add manual logout method
    path('profile/', views.user_profile, name='user_profile'),

]


