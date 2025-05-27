from django.shortcuts import render
from rest_framework import viewsets #agregar permissions
#from modeles import Activity, Branch, Coach, Shift
#from serializer import ActivitySerializer, BranchSerializer, CoachSerializer, ShiftSerializer
#from django.db.models import 0
from .serializer import *
from .models import *



class ActividadView(viewsets.ModelViewSet):
    serializer_class = ActivitySerializer
    queryset = Activity.objects.all()

class SucursalView(viewsets.ModelViewSet):
    serializer_class = BranchSerializer
    queryset = Branch.objects.all()

class CoachView(viewsets.ModelViewSet):
    serializer_class = CoachSerializer
    queryset = Coach.objects.all()

class ShiftView(viewsets.ModelViewSet):
    serializer_class = ShiftSerializer
    queryset = Shift.objects.all()




