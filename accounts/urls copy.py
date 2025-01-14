# accounts/urls.py
from django.urls import path
from .views import LogoutView 
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    # Login page
    path(
        'login/',
        LoginView.as_view(
            template_name='accounts/login.html',
            redirect_authenticated_user=True,
        ),
        name='login',
    ),
    # Logout page
    path(
        'logout/',
        LogoutView.as_view(
            next_page='login',  # Redirect to login page after logout
        ),
        name='logout',
    ),
    # Registration page
    path('register/', views.register, name='register'),
    # Email activation link
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    # User profile page
    path('profile/', views.user_profile, name='user_profile'),
]
