from django.contrib import admin
from .models import GymUser, Branch, Coach, Activity, Shift

admin.site.register(Branch)

admin.site.register(GymUser)
admin.site.register(Branch)
admin.site.register(Coach)
admin.site.register(Activity)
admin.site.register(Shift)

# Register your models here.
