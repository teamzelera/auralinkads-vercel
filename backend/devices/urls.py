from django.urls import path
from .views import (
    DeviceListCreateView,
    DeviceDetailView,
    GenerateDeviceCodeView,
    DeviceAuthView,
    DeviceHeartbeatView,
    DeviceAssignmentView,
    DeviceRestartView,
)

urlpatterns = [
    path("", DeviceListCreateView.as_view(), name="device-list"),
    path("generate-code/", GenerateDeviceCodeView.as_view(), name="device-generate-code"),
    path("authenticate/", DeviceAuthView.as_view(), name="device-auth"),
    path("heartbeat/", DeviceHeartbeatView.as_view(), name="device-heartbeat"),
    path("me/assignment/", DeviceAssignmentView.as_view(), name="device-assignment"),
    path("<uuid:pk>/", DeviceDetailView.as_view(), name="device-detail"),
    path("<uuid:pk>/restart/", DeviceRestartView.as_view(), name="device-restart"),
]
