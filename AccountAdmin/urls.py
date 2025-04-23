from django.urls import path, include
from rest_framework import routers
from AccountAdmin import views

router = routers.DefaultRouter()
router.register(r'GymUser', views.GymUserViewSet, basename='GymUser')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', views.LoginView.as_view(), name='login'),  # Ruta para LoginView
    path('logout/', views.LogoutView.as_view(), name='logout'),  # Ruta para LogoutView
]


