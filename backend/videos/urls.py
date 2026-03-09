from django.urls import path
from .views import VideoListCreateView, VideoDetailView, CloudinarySignatureView, VideoRotateView

urlpatterns = [
    path("", VideoListCreateView.as_view(), name="video-list"),
    path("<uuid:pk>/", VideoDetailView.as_view(), name="video-detail"),
    path("<uuid:pk>/rotate/", VideoRotateView.as_view(), name="video-rotate"),
    path("cloudinary-signature/", CloudinarySignatureView.as_view(), name="cloudinary-signature"),
]
