from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'is_staff', 'is_active', 'is_verified')
    fieldsets = UserAdmin.fieldsets + (
        ('Extra Fields', {'fields': ('is_verified',)}),
    )

admin.site.register(User, CustomUserAdmin)
