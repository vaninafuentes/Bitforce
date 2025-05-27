from django.contrib import admin
from .models import GymUser, Coach, Activity, Shift



admin.site.register(GymUser)
admin.site.register(Coach)
admin.site.register(Activity)
admin.site.register(Shift)

# Register your models here.
