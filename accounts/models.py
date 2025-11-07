from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError


class User(AbstractUser):
    """
    Custom User model with role-based access control
    """
    ROLE_CHOICES = (
        ('EMPLOYEE', 'Employee'),
        ('MANAGER', 'Manager'),
        ('ADMIN', 'Admin'),
    )

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='EMPLOYEE',
        help_text='User role in the organization'
    )
    department = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Department name'
    )
    manager = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='team_members',
        limit_choices_to={'role': 'MANAGER'},
        help_text='Direct manager (for employees)'
    )
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )
    profile_photo = models.ImageField(
        upload_to='profile_photos/%Y/%m/',
        blank=True,
        null=True,
        help_text='Profile photo (optional, max 2MB, JPG/PNG only)'
    )
    # Note: date_joined is inherited from AbstractUser
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['username']
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"

    def is_employee(self):
        return self.role == 'EMPLOYEE'

    def is_manager(self):
        return self.role == 'MANAGER'

    def is_admin_user(self):
        return self.role == 'ADMIN'

    def get_team_members(self):
        """Returns team members for managers"""
        if self.is_manager():
            return self.team_members.all()
        return User.objects.none()

    def get_initials(self):
        """Returns user initials (e.g., 'JD' for John Doe)"""
        if self.first_name and self.last_name:
            return f"{self.first_name[0]}{self.last_name[0]}".upper()
        elif self.first_name:
            return self.first_name[0].upper()
        elif self.username:
            return self.username[0].upper()
        return '?'

    def get_avatar_color(self):
        """Returns consistent color for user based on username"""
        colors = [
            '#3498db',  # Blue
            '#2ecc71',  # Green
            '#e74c3c',  # Red
            '#f39c12',  # Orange
            '#9b59b6',  # Purple
            '#1abc9c',  # Turquoise
            '#34495e',  # Dark gray
            '#e67e22',  # Carrot
            '#95a5a6',  # Silver
            '#d35400',  # Pumpkin
        ]
        # Use hash of username to pick a consistent color
        index = sum(ord(c) for c in self.username) % len(colors)
        return colors[index]

    def clean(self):
        """Validate user data"""
        super().clean()
        # Only enforce manager assignment for active employees being edited (not during registration)
        if self.pk and self.role == 'EMPLOYEE' and not self.manager and self.is_active:
            raise ValidationError('Active employees must have a manager assigned.')
        if self.role in ['MANAGER', 'ADMIN'] and self.manager:
            # Managers and admins shouldn't have managers
            self.manager = None
