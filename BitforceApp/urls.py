from django.urls import path, include 
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'sucursal', views.SucursalView, basename='sucursal')
router.register(r'coach', views.CoachView, basename='coach')
router.register(r'actividades', views.ActividadView, basename='actividades')
router.register(r'turno', views.TurnoView, basename='turno')

urlpatterns = [
    path('BitforceApp/model/', include(router.urls)),
]



