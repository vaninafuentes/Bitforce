# BitforceApp/admin.py
from django.contrib import admin
from .models import Branch, Coach, Activity, ClaseProgramada, Shift, Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("user","slot","creado")
    list_filter  = ("slot__sucursal","slot__actividad","creado")
    search_fields = ("user__username", "slot__actividad__nombre", "slot__sucursal__nombre")

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ("nombre", "direccion")
    search_fields = ("nombre", "direccion")
    list_per_page = 25

@admin.register(Coach)
class CoachAdmin(admin.ModelAdmin):
    list_display = ("nombre", "especialidad", "email")
    search_fields = ("nombre", "especialidad", "email")
    list_per_page = 25

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ("nombre", "duracion", "capacidad_maxima", "cutoff_minutes", "activo")
    list_filter = ("activo",)
    search_fields = ("nombre",)
    list_per_page = 25

@admin.register(ClaseProgramada)
class ClaseProgramadaAdmin(admin.ModelAdmin):
    list_display = ("actividad", "sucursal", "inicio", "fin_display", "capacidad", "cutoff_minutes", "activo")
    list_filter = ("actividad", "sucursal", "activo")
    search_fields = ("actividad__nombre", "sucursal__nombre", "sucursal__direccion")
    date_hierarchy = "inicio"
    list_per_page = 25

    def fin_display(self, obj):
        return obj.fin
    fin_display.short_description = "Fin"

