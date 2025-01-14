import logging
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm, CustomAuthenticationForm, UserProfileForm
from .models import CustomUser, UserProfile
from django.contrib.auth.views import LoginView, LogoutView

# Setting up logger for error handling
logger = logging.getLogger(__name__)

@login_required
def user_logout(request):
    """Logs out the user and redirects to the login page."""
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('login')

def register(request):
    """Handles user registration."""
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # Save the user instance without committing to DB
            user.set_password(form.cleaned_data["password"])  # Hash the password
            user.save()  # Save the user to the database (triggers the signal to create UserProfile)

            # Generate email activation link
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(str(user.pk).encode())
            activation_link = f"http://{get_current_site(request).domain}/accounts/activate/{uid}/{token}/"

            # Send activation email with error handling
            try:
                send_mail(
                    "Activate your account",
                    f"Click here to activate your account: {activation_link}",
                    'doictsadarbrahmanbarian@gmail.com',  # Sender email
                    [user.email],
                    fail_silently=False,
                )
                messages.success(request, "Please check your email to verify your account.")
            except Exception as e:
                logger.error(f"Failed to send activation email: {e}")
                messages.error(request, "An error occurred while sending the activation email. Please try again.")
                return redirect('register')  # Redirect to registration page on failure

            return redirect('login')  # Redirect to login page on success
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})

def activate(request, uidb64, token):
    """Handles account activation."""
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Account activated successfully!")
        return redirect('login')
    else:
        messages.error(request, "Activation link is invalid or expired.")
        return redirect('login')

def user_login(request):
    """Handles user login."""
    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')  # 'username' refers to the email field
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)  # Use `username=email`
            if user is not None:
                login(request, user)
                return redirect('user_profile')  # Redirect to profile or dashboard
            else:
                messages.error(request, "Invalid email or password.")
        else:
            messages.error(request, "Invalid email or password.")
    else:
        form = CustomAuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})

@login_required
def user_profile(request):
    """Handles user profile viewing and editing."""
    user = request.user  # Get the logged-in user
    try:
        profile = user.userprofile  # Access the UserProfile through the related name
    except UserProfile.DoesNotExist:
        profile = None  # Handle case where profile is missing

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect('user_profile')  # Stay on the profile page after saving
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'accounts/user_profile.html', {'form': form, 'profile': profile})
