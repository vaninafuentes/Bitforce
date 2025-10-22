from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView 
from AccountAdmin import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from AccountAdmin.views import LogoutJWTView, MeView

urlpatterns = [
    path('admin/', admin.site.urls),
    # Apps
    path('api/', include('BitforceApp.urls')),
    path('api/AccountAdmin/', include('AccountAdmin.urls')),

     # Docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # JWT
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("api/logout/", LogoutJWTView.as_view(), name="jwt_logout"),
    path("api/me/", MeView.as_view(), name="me"),
]

