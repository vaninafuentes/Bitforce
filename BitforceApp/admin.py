from django.contrib import admin
from .models import Coach, Activity, Shift
from AccountAdmin.models import GymUser


admin.site.register(GymUser)
admin.site.register(Coach)
admin.site.register(Activity)
admin.site.register(Shift)

# Register your models here.
