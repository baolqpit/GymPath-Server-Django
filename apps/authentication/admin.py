from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined']
    list_filter = ['is_active', 'is_staff']
    search_fields = ['username', 'email', 'first_name', 'last_name']

    # Thêm các field custom vào form chỉnh sửa trong admin
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Thông tin GymPath', {
            'fields': ('phone', 'date_of_birth', 'height_cm', 'weight_kg', 'bio')
        }),
    )
