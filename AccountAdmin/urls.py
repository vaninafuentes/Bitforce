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
    path("api/clients/", ClientUserCreateView.as_view(), name="clients-create"),
]

