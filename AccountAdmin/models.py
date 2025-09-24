# AccountAdmin/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

class GymUser(AbstractUser):
    ROLES = [
        ('admin', 'Administrador'),
        ('limMerchant', 'Limitado'),
    ]
    rol = models.CharField(max_length=20, choices=ROLES, default='limMerchant')
    branch = models.CharField(max_length=100, default='')  # nombre de sucursal del usuario

    def __str__(self):
        # Evitá depender de email si puede estar vacío
        return self.username
