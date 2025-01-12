# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login
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
                    'doictsadarbrahmanbaria@gmail.com',  # Sender email
                    [user.email],
                    fail_silently=False,
                )
                messages.success(request, "Please check your email to verify your account.")
            except Exception as e:
                # Improved error handling with logging the exact error
                messages.error(request, f"Failed to send activation email: {str(e)}")
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
            user = form.get_user()
            login(request, user)
            return redirect('home')  # Update to your desired redirect URL
        else:
            messages.error(request, "Invalid email or password. Please try again.")
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})