from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User


class UserLoginForm(AuthenticationForm):
    """Custom login form"""

    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )


class UserRegistrationForm(UserCreationForm):
    """Registration form for new users"""

    email = forms.CharField(
        required=True,
        max_length=150,
        label='Email Username',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter username (e.g., john.doe)',
            'autocomplete': 'off'
        }),
        help_text='Enter your username only. @gammaedge.io will be added automatically.'
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'department', 'phone_number', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'department': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Department (optional)'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number (optional)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})

    def clean_email(self):
        """Validate username format and append @gammaedge.io domain"""
        import re

        email_username = self.cleaned_data.get('email', '').strip().lower()

        # Remove @gammaedge.io if user accidentally included it
        if '@' in email_username:
            if email_username.endswith('@gammaedge.io'):
                email_username = email_username.replace('@gammaedge.io', '')
            else:
                raise forms.ValidationError(
                    'Please enter only the username part without @domain. '
                    'Only @gammaedge.io emails are allowed.'
                )

        # Validate username format (alphanumeric, dots, hyphens, underscores)
        if not re.match(r'^[a-z0-9._-]+$', email_username):
            raise forms.ValidationError(
                'Username can only contain lowercase letters, numbers, dots (.), hyphens (-), and underscores (_).'
            )

        # Check if starts or ends with special characters
        if email_username.startswith(('.', '-', '_')) or email_username.endswith(('.', '-', '_')):
            raise forms.ValidationError(
                'Username cannot start or end with dots, hyphens, or underscores.'
            )

        # Check minimum length
        if len(email_username) < 2:
            raise forms.ValidationError('Username must be at least 2 characters long.')

        # Construct full email
        full_email = f'{email_username}@gammaedge.io'

        # Check if email already exists
        if User.objects.filter(email=full_email).exists():
            raise forms.ValidationError(
                f'An account with {full_email} already exists.'
            )

        return full_email


class UserProfileForm(forms.ModelForm):
    """Form for updating user profile"""

    clear_profile_photo = forms.BooleanField(
        required=False,
        label='Remove current profile photo',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'department', 'phone_number', 'profile_photo']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def clean_profile_photo(self):
        """Validate and resize profile photo"""
        photo = self.cleaned_data.get('profile_photo')

        if not photo:
            return photo

        # Check file size (2MB max)
        if photo.size > 2 * 1024 * 1024:
            raise forms.ValidationError('Image file size must be under 2MB.')

        # Check file type
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png']
        if hasattr(photo, 'content_type') and photo.content_type not in allowed_types:
            raise forms.ValidationError('Only JPG and PNG files are allowed.')

        # Check file extension
        import os
        ext = os.path.splitext(photo.name)[1].lower()
        if ext not in ['.jpg', '.jpeg', '.png']:
            raise forms.ValidationError('Only JPG and PNG files are allowed.')

        # Resize image to 300x300px
        try:
            from PIL import Image
            from io import BytesIO
            from django.core.files.uploadedfile import InMemoryUploadedFile
            import sys

            # Open image
            img = Image.open(photo)

            # Convert to RGB if necessary (for PNG with transparency)
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Resize to 300x300
            output_size = (300, 300)
            img.thumbnail(output_size, Image.Resampling.LANCZOS)

            # Save to BytesIO
            output = BytesIO()
            img.save(output, format='JPEG', quality=85)
            output.seek(0)

            # Create new InMemoryUploadedFile
            photo = InMemoryUploadedFile(
                output,
                'ImageField',
                f"{os.path.splitext(photo.name)[0]}.jpg",
                'image/jpeg',
                sys.getsizeof(output),
                None
            )
        except Exception as e:
            raise forms.ValidationError(f'Error processing image: {str(e)}')

        return photo
