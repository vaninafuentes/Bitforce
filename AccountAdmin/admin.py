from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import GymUser
from .models import *

@admin.register(GymUser)
class GymUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Extra", {"fields": ("rol", "branch")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Extra", {"fields": ("rol", "branch")}),
    )



# Register your models here.
