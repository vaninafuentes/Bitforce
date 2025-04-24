from django.db import models
from django.contrib.auth.models import AbstractUser

class GymUser(AbstractUser):

    ROLES = [
        ('admin', 'Administrador'),
        ('limMerchant', 'Limitado'),
    ]
    role = models.CharField(max_length=20, choices=ROLES, default='limMerchant')
    Branch = models.CharField(max_length=100, default='')  
    email= models.EmailField(unique=True)


    def _str_(self):
        return self.email
# Create your models here.

