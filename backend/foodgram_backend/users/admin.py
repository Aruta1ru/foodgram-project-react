from django.contrib import admin

from .models import CustomUser, Follow


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'role')
    search_fields = ('email', 'username')


class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author',)


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Follow, FollowAdmin)
