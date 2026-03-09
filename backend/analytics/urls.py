from django.urls import path
from .views import DashboardStatsView, DeviceUptimeView

urlpatterns = [
    path("dashboard/", DashboardStatsView.as_view(), name="analytics-dashboard"),
    path("uptime/", DeviceUptimeView.as_view(), name="analytics-uptime"),
]
