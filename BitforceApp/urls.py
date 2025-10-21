from django.urls import path, include 
from rest_framework import routers
from . import views
from rest_framework.routers import DefaultRouter
from .views import SucursalView, ActividadView, CoachView,ReservarPorSlotView, ClaseProgramadaView, BookingView, ReservarSlotBookingView

router = routers.DefaultRouter()
router.register(r'branch', views.SucursalView, basename='branch')
router.register(r'coach', views.CoachView, basename='coach')
router.register(r'activity', views.ActividadView, basename='activity')
router.register(r'claseprogramada', views.ClaseProgramadaView, basename='claseprogramada')
router.register(r'booking', views.BookingView, basename='booking')  

urlpatterns = [
    *router.urls,
    path('bookings/reservar/', ReservarSlotBookingView.as_view(), name='booking-reservar'),
    path('BitforceApp/model/', include(router.urls)),
]



