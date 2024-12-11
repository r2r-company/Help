from django.contrib import admin

from main.models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'secret_key', 'telegram_group_id')
    search_fields = ('user__username',)
