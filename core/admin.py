from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User,News, UserBadge
from django.utils.translation import gettext_lazy as _

admin.site.register(User)


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
