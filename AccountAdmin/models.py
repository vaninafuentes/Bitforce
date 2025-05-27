from django.db import models
from django.contrib.auth.models import AbstractUser

class GymUser(AbstractUser):

    ROLES = [
        ('admin', 'Administrador'),
        ('limMerchant', 'Limitado'),
    ]
    rol = models.CharField(max_length=20, choices=ROLES, default='limMerchant')
    Branch = models.CharField(max_length=100, default='')  
    username = models.CharField(max_length=150, unique=True, default='default_username')  # Agrega un valor predeterminado



    def __str__(self):
        return self.email
# Create your models here.


