from django.urls import path, include
from rest_framework import routers
from AccountAdmin import views
from .views import GymUserView, LoginView, LogoutView
#from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

router = routers.DefaultRouter()
router.register(r'GymUser', views.GymUserView, basename='gymuser')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', views.LoginView.as_view(), name='login'),  # Ruta para LoginView #comentar porque el profe lo borra
    path('logout/', views.LogoutView.as_view(), name='logout'),  # Ruta para LogoutView
]


