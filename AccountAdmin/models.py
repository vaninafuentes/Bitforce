from django.db import models

class GymUser(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    address = models.TextField()
    phone = models.CharField(max_length=20, null =True, blank=True)

    def __str__(self):
        return self.nombre

# Create your models here.
