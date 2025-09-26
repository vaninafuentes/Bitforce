from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView 
from AccountAdmin import views

urlpatterns = [
    path('admin/', admin.site.urls),
    # Apps
    path('api/', include('BitforceApp.urls')),
    path('api/AccountAdmin/', include('AccountAdmin.urls')),
    # Docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('login/', views.LoginView.as_view(), name='login'),  
    path('logout/', views.LogoutView.as_view(), name='logout'),  
    path('', include('AccountAdmin.urls')),   
]