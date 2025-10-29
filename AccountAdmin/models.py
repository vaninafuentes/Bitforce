# AccountAdmin/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta

class GymUser(AbstractUser):
    ROLES = [
        ('admin', 'Administrador'),
        ('limMerchant', 'Limitado'),
    ]
    rol = models.CharField(max_length=20, choices=ROLES, default='limMerchant')
    branch = models.CharField(max_length=100, blank=True, default='')
    
    # ---- Créditos ----
    creditos = models.PositiveIntegerField(default=0)
    fecha_activacion = models.DateField(null=True, blank=True)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    activo = models.BooleanField(default=True)  # para bloquear reservas cuando vence o se queda sin créditos

    def __str__(self):
        return self.username

    # Asignar o renovar créditos
    def asignar_creditos(self, cantidad: int, dias_validez: int = 30):
        if cantidad <= 0:
            raise ValueError("Los créditos deben ser mayores a 0")
        hoy = timezone.now().date()
        self.creditos = cantidad
        self.fecha_activacion = hoy
        self.fecha_vencimiento = hoy + timedelta(days=dias_validez)
        self.activo = True
        self.save(update_fields=["creditos", "fecha_activacion", "fecha_vencimiento", "activo"])

    # Verificar si está habilitado (por vencimiento o créditos)
    def verificar_estado(self) -> bool:
        hoy = timezone.now().date()
        if self.creditos <= 0 or (self.fecha_vencimiento and hoy > self.fecha_vencimiento):
            if self.activo:
                self.activo = False
                self.save(update_fields=["activo"])
            return False
        if not self.activo:
            self.activo = True
            self.save(update_fields=["activo"])
        return True

    # Consumir 1 crédito (ej. al reservar)
    def consumir_credito(self):
        self.verificar_estado()
        if not self.activo:
            raise ValueError("Cuenta vencida o sin créditos.")
        if self.creditos <= 0:
            raise ValueError("No tenés créditos disponibles.")
        self.creditos -= 1
        if self.creditos == 0:
            self.activo = False
        self.save(update_fields=["creditos", "activo"])

    # --- Resetear créditos (anular asignación) ---
    def resetear_creditos(self):
        """Elimina todos los créditos y marca la cuenta como inactiva."""
        self.creditos = 0
        self.fecha_activacion = None
        self.fecha_vencimiento = None
        self.activo = False
        self.save(update_fields=["creditos", "fecha_activacion", "fecha_vencimiento", "activo"])
