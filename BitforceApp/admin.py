from django.contrib import admin
from .models import Coach, Activity, Shift, Branch



admin.site.register(Branch)
admin.site.register(Coach)
admin.site.register(Activity)
admin.site.register(Shift)

# Register your models here.
