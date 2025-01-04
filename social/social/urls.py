from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin site
    path('', include('profiles.urls')),  # Include profiles URLs for the root path
    path('auth/', include('djoser.urls')),  # Djoser authentication endpoints
]
