from django.urls import path, include
from rest_framework import routers
from AccountAdmin import views

router = routers.DefaultRouter()
router.register(r'GymUser', views.GymUserViewSet, basename='GymUser')

urlpatterns = [
    path('AccountAdmin/', include(router.urls)),
]

