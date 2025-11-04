from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom admin for User model"""

    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'department', 'get_manager_display', 'is_active']
    list_filter = ['role', 'department', 'is_active', 'is_staff']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'department']
    ordering = ['username']
    readonly_fields = ['date_joined', 'updated_at']

    def get_manager_display(self, obj):
        """Only show manager for employees"""
        if obj.role == 'EMPLOYEE' and obj.manager:
            return obj.manager.get_full_name()
        return '-'
    get_manager_display.short_description = 'Manager'

    def get_fieldsets(self, request, obj=None):
        """Dynamically show manager field only for employees"""
        fieldsets = super().get_fieldsets(request, obj)

        # If editing existing user and they're not an employee, hide manager field
        if obj and obj.role != 'EMPLOYEE':
            additional_fields = ('role', 'department', 'phone_number', 'updated_at')
        else:
            additional_fields = ('role', 'department', 'manager', 'phone_number', 'updated_at')

        # Return fieldsets with conditional manager field
        return fieldsets + (
            ('Additional Info', {
                'fields': additional_fields,
                'description': 'Note: Manager field is only applicable for employees.'
            }),
        )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('role', 'department', 'manager', 'phone_number', 'first_name', 'last_name', 'email'),
            'description': 'Manager should only be assigned to employees.'
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('manager')
