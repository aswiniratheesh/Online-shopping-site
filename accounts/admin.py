from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from . models import Account
# Register your models here.

class AccountAdmin(UserAdmin):
    list_display = {'email', 'first_name', 'last_name'}
admin.site.register(Account)