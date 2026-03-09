from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="AuraLink API",
      default_version='v1',
      description="API documentation for the AuraLink digital signage system.",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="admin@example.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/devices/", include("devices.urls")),
    path("api/videos/", include("videos.urls")),
    path("api/playlists/", include("playlists.urls")),
    path("api/analytics/", include("analytics.urls")),
    
    # Specific endpoints requested in the CDN implementation prompt
    path("api/admin/upload-video/", __import__('videos.views').views.VideoListCreateView.as_view(), name="admin-upload-video"),
    path("api/device/get-playlist/", __import__('devices.views').views.DeviceAssignmentView.as_view(), name="device-get-playlist"),

    # Swagger Documentation
    path("swagger/", schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path("redoc/", schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
