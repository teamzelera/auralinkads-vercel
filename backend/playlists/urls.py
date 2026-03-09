from django.urls import path
from .views import (
    PlaylistListCreateView, PlaylistDetailView, DeviceAssignmentView,
    PlaylistAddVideoView, PlaylistRemoveVideoView, PlaylistReorderView, PlaylistSettingsView
)

urlpatterns = [
    path("", PlaylistListCreateView.as_view(), name="playlist-list"),
    path("<uuid:pk>/", PlaylistDetailView.as_view(), name="playlist-detail"),
    path("<uuid:pk>/add-video/", PlaylistAddVideoView.as_view(), name="playlist-add-video"),
    path("<uuid:pk>/remove-video/<uuid:video_id>/", PlaylistRemoveVideoView.as_view(), name="playlist-remove-video"),
    path("<uuid:pk>/reorder/", PlaylistReorderView.as_view(), name="playlist-reorder"),
    path("<uuid:pk>/settings/", PlaylistSettingsView.as_view(), name="playlist-settings"),
    path("assignments/", DeviceAssignmentView.as_view(), name="device-assignment"),
]
