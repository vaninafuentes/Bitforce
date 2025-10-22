from django.urls import path, include
from rest_framework import routers
from AccountAdmin import views
from .views import ClientUserCreateView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from .jwt_views import MyTokenObtainPairView

router = routers.DefaultRouter()
router.register(r'GymUser', views.GymUserView, basename='gymuser')

urlpatterns = [
    path('', include(router.urls)),
    #path('login/', views.LoginView.as_view(), name='login'),  # Ruta para LoginView #comentar porque el profe lo borra
    #path('logout/', views.LogoutView.as_view(), name='logout'),  # Ruta para 
    path('token/', MyTokenObtainPairView.as_view(), name='my_token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='my_token_refresh'),
    path("api/clients/", ClientUserCreateView.as_view(), name="clients-create"),

     
]


