from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'department', 'is_staff', 'is_active')
    list_filter = ('role', 'department', 'is_staff', 'is_active')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Observatory System Details', {'fields': ('role', 'department', 'designation', 'phone', 'avatar_color', 'theme_preference')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Observatory System Details', {'fields': ('role', 'department', 'designation', 'phone')}),
    )
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
