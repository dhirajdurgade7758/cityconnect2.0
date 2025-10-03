from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User,News, UserBadge
from django.utils.translation import gettext_lazy as _


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'area')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions', 'role','department'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Eco System'), {'fields': ('eco_coins',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email', 'role','department', 'area', 'eco_coins'),
        }),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'role','department', 'eco_coins', 'area', 'is_staff')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'area')
    ordering = ('username',)


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'created_at')
    search_fields = ('title', 'created_by__username')
    readonly_fields = ('created_at',)

@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ('user', 'badge_name', 'badge_type', 'unlocked_at')
    list_filter = ('badge_type',)
    search_fields = ('user__username', 'badge_name')
    readonly_fields = ('unlocked_at',)
