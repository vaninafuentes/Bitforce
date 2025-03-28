from django.db import models

# Create your models here.

class GymUser(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

class Sucursal(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255)

class Coach(models.Model):
    nombre = models.CharField(max_length=100)
    especialidad = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

class Actividad(models.Model):
    nombre = models.CharField(max_length=100)
    duracion = models.IntegerField(help_text="Duración en minutos")
    capacidad_maxima = models.IntegerField()
    coach = models.ForeignKey(Coach, on_delete=models.CASCADE)

class Turno(models.Model):
    fecha_hora = models.DateTimeField()
    gymuser = models.ForeignKey(GymUser, on_delete=models.CASCADE)
    actividad = models.ForeignKey(Actividad, on_delete=models.CASCADE)
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE)
