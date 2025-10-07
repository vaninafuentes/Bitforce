# BitforceApp/models.py (o donde definís Branch/Coach/Activity/Shift)
from django.db import models
from django.conf import settings

class Branch(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255)
    def __str__(self):
        return self.nombre

class Coach(models.Model):
    nombre = models.CharField(max_length=100)
    especialidad = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    def __str__(self):
        return self.nombre

class Activity(models.Model):
    nombre = models.CharField(max_length=100)
    duracion = models.IntegerField(help_text="Duración en minutos")
    capacidad_maxima = models.IntegerField()
    coach = models.ForeignKey(Coach, on_delete=models.CASCADE)
    def __str__(self):
        return self.nombre

class Shift(models.Model):
    fecha_hora = models.DateTimeField()
    gymuser = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shifts'
    )
    actividad = models.ForeignKey(Activity, on_delete=models.CASCADE)
    sucursal = models.ForeignKey(Branch, on_delete=models.CASCADE)
