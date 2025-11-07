from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.forms import PasswordChangeForm
from .forms import UserLoginForm, UserRegistrationForm, UserProfileForm
from .models import User


def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('reports:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Check if user exists first
        try:
            user_check = User.objects.get(username=username)

            # Check if password is correct
            if user_check.check_password(password):
                # Password is correct, now check if account is active
                if not user_check.is_active:
                    # Account exists with correct password but is inactive
                    messages.warning(
                        request,
                        'Your account is pending approval. '
                        'Please contact your administrator to activate your account.'
                    )
                    form = UserLoginForm()
                    return render(request, 'accounts/login.html', {'form': form})
                else:
                    # Account is active, log them in
                    login(request, user_check)
                    messages.success(request, f'Welcome back, {user_check.get_full_name()}!')
                    next_url = request.GET.get('next', 'reports:dashboard')
                    return redirect(next_url)
            else:
                # Password is incorrect
                messages.error(request, 'Invalid username or password.')
                form = UserLoginForm()
        except User.DoesNotExist:
            # Username doesn't exist
            messages.error(request, 'Invalid username or password.')
            form = UserLoginForm()
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """User logout view"""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('accounts:login')


class RegisterView(CreateView):
    """User registration view"""
    model = User
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('reports:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Set new users as inactive until admin assigns manager and activates
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        messages.success(
            self.request,
            'Registration successful! Your account is pending approval. '
            'An administrator will assign you a manager and activate your account.'
        )
        return redirect(self.success_url)


@login_required
def profile_view(request):
    """User profile view"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)

            # Handle profile photo removal
            if form.cleaned_data.get('clear_profile_photo'):
                if user.profile_photo:
                    # Delete old photo file
                    user.profile_photo.delete(save=False)
                    user.profile_photo = None

            user.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'accounts/profile.html', {'form': form})


@login_required
def change_password_view(request):
    """Change password view for logged-in users"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Important: Update session to prevent logout after password change
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password has been changed successfully!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'accounts/change_password.html', {'form': form})
