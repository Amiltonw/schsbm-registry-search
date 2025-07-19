from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'user profile'

class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline, )
    add_fieldsets = UserAdmin.add_fieldsets + (('Personal info', {'fields': ('first_name', 'last_name', 'email')}),)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)