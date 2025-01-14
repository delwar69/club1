from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    # Login page
    path('login/', LoginView.as_view(
        template_name='accounts/login.html',
        redirect_authenticated_user=True,
    ), name='login'),

    # Logout page
    path('logout/', views.user_logout, name='logout'),  # Using the custom logout view

    # Registration page
    path('register/', views.register, name='register'),

    # User profile page
    path('profile/', views.user_profile, name='user_profile'),

    # Activation and other routes...
]
