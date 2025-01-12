# accounts/views.py
import logging
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.contrib import messages
from .forms import RegistrationForm
from .models import CustomUser
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .forms import CustomAuthenticationForm
from .models import UserProfile
from .forms import UserProfileForm

# Setting up logger for error handling
logger = logging.getLogger(__name__)

@login_required
def user_logout(request):
    """Logs out the user and redirects to the login page."""
    # Log out the user
    logout(request)

    # Add a success message
    messages.success(request, "You have successfully logged out.")

    # Redirect to the login page
    return redirect('login')  # Adjust if you want to redirect elsewhere

# Registration View
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(str(user.pk).encode())  # Ensure proper encoding
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
                # Log the error for debugging and error tracking
                logger.error(f"Failed to send activation email: {e}")
                messages.error(request, "An error occurred while sending the activation email. Please try again.")
                return redirect('register')  # Redirect back to registration in case of failure

            return redirect('login')  # Redirect to login page on successful registration
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})

# Activate User View
def activate(request, uidb64, token):
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
        messages.error(request, "Activation link is invalid.")
        return redirect('login')

# Login View
def user_login(request):
    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')  # 'username' here refers to the email field
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('user_profile')  # Redirect to a home page or dashboard
            else:
                messages.error(request, "Invalid email or password.")
        else:
            messages.error(request, "Invalid email or password.")
    else:
        form = CustomAuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


def user_profile(request):
    user = request.user  # Get the logged-in user
    try:
        profile = user.profile  # Assuming a one-to-one relationship between User and UserProfile
    except UserProfile.DoesNotExist:
        profile = None

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('user_profile')  # Stay on the profile page after saving
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'accounts/user_profile.html', {'form': form, 'profile': profile})
