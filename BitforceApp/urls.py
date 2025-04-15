from django.urls import path, include 
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'branch', views.SucursalView, basename='branch')
router.register(r'coach', views.CoachView, basename='coach')
router.register(r'activity', views.ActividadView, basename='activity')
router.register(r'shift', views.TurnoView, basename='shift')

urlpatterns = [
    path('BitforceApp/model/', include(router.urls)),
]



