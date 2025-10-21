from django.db import models
from django.conf import settings
from datetime import timedelta

class Branch(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255)

    class Meta:
        unique_together = ('nombre', 'direccion')
        ordering = ['nombre', 'direccion']

    def __str__(self):
        return f"{self.nombre} - {self.direccion}"


class Coach(models.Model):
    nombre = models.CharField(max_length=100)
    especialidad = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.nombre


class Activity(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    duracion = models.PositiveIntegerField(help_text="Duración en minutos")
    capacidad_maxima = models.PositiveIntegerField(help_text="Cupo máximo por horario")
    cutoff_minutes = models.PositiveIntegerField(default=10, help_text="Minutos antes del inicio en que se cierra la inscripción")
    coach = models.ForeignKey(Coach, on_delete=models.SET_NULL, null=True, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class ClaseProgramada(models.Model):
    """Slot publicado por el admin para que los clientes reserven."""
    actividad = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='slots')
    sucursal  = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='slots')
    coach     = models.ForeignKey(Coach, on_delete=models.SET_NULL, null=True, blank=True)
    inicio    = models.DateTimeField()
    capacidad = models.PositiveIntegerField(help_text="Cupo del slot (default: actividad.capacidad_maxima)")
    cutoff_minutes = models.PositiveIntegerField(null=True, blank=True, help_text="Override; si es null usa el de la actividad")
    activo    = models.BooleanField(default=True)

    class Meta:
        ordering = ["inicio"]
        unique_together = ("actividad", "sucursal", "inicio")
        indexes = [
            models.Index(fields=["actividad", "sucursal", "inicio"]),
            models.Index(fields=["inicio"]),
            models.Index(fields=["activo"]),
        ]

    def __str__(self):
        return f"{self.actividad} @ {self.sucursal} [{self.inicio}]"

    @property
    def fin(self):
        return self.inicio + timedelta(minutes=self.actividad.duracion)

    @property
    def cutoff(self):
        return self.cutoff_minutes if self.cutoff_minutes is not None else self.actividad.cutoff_minutes


class Shift(models.Model):
    """Reserva de un usuario sobre un slot (ClaseProgramada)."""
    slot    = models.ForeignKey(ClaseProgramada, on_delete=models.CASCADE, related_name='reservas', null=False, blank=False)
    gymuser = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shifts')
    creado  = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = "bitforceapp_shift"
        constraints = [
            models.UniqueConstraint(fields=["gymuser", "slot"], name="unique_booking_per_user_per_slot_v2")
        ]
        indexes = [
            models.Index(fields=["slot"]),
            models.Index(fields=["gymuser"]),
        ]
        ordering = ["-creado"]

    def __str__(self):
        return f"{self.gymuser} → {self.slot}"

# --- NUEVO: reservas en tabla nueva ---
class Booking(models.Model):
    """Reserva de un usuario sobre un slot (ClaseProgramada) — TABLA NUEVA."""
    slot    = models.ForeignKey(
        ClaseProgramada, on_delete=models.CASCADE, related_name='bookings', null=False, blank=False
    )
    user    = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings'
    )
    creado  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "bitforceapp_booking"  # nombre de tabla explícito y NUEVO
        constraints = [
            models.UniqueConstraint(fields=["user", "slot"], name="unique_booking_per_user_per_slot_new")
        ]
        indexes = [
            models.Index(fields=["slot"]),
            models.Index(fields=["user"]),
        ]
        ordering = ["-creado"]

    def __str__(self):
        return f"{self.user} → {self.slot}"

