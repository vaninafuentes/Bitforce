from django.shortcuts import render

from rest_framework import viewsets
from .serializer import *
from .models import *

class GymUserView(viewsets.ModelViewSet):
    serializer_class = GymUserSerializer
    queryset = GymUser.objects.all()

class SucursalView(viewsets.ModelViewSet):
    serializer_class = SucursalSerializer
    queryset = Sucursal.objects.all()

class CoachView(viewsets.ModelViewSet):
    serializer_class = CoachSerializer
    queryset = Coach.objects.all()

class ActividadView(viewsets.ModelViewSet):
    serializer_class = ActividadSerializer
    queryset = Actividad.objects.all()

class TurnoView(viewsets.ModelViewSet):
    serializer_class = TurnoSerializer
    queryset = Turno.objects.all()



