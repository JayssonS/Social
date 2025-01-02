from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin site
    path('api/', include('profiles.urls')),  # Include all routes from profiles app
    path('auth/', include('djoser.urls')),  # Djoser authentication endpoints
    path('auth/', include('djoser.urls.authtoken')),  # Token-based authentication
    path('', include('profiles.urls')),  # Include profiles URLs for general routes like /login/
]
