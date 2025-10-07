from django.urls import path, include
from rest_framework import routers
from AccountAdmin import views
from .views import GymUserView, LoginView, LogoutView
from .views import ClientUserCreateView
#from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

router = routers.DefaultRouter()
router.register(r'GymUser', views.GymUserView, basename='gymuser')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', views.LoginView.as_view(), name='login'),  # Ruta para LoginView #comentar porque el profe lo borra
    path('logout/', views.LogoutView.as_view(), name='logout'),  # Ruta para LogoutView
    path("api/clients/", ClientUserCreateView.as_view(), name="clients-create"),

     
]
#TODO crear un superusuario y este usuario crea un admin que va a crear a los clientes 
    
#TODO crear un endpoint para crear usuarios del tipo cliente, validar que solo un administrador pueda acceder a este endpoint

