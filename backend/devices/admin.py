from django.contrib import admin
from .models import Device, Heartbeat


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ["name", "device_code", "status", "is_active", "last_seen", "created_at"]
    list_filter = ["status", "is_active"]
    search_fields = ["name", "device_code", "location"]
    readonly_fields = ["id", "device_code", "auth_token", "last_seen", "created_at"]


@admin.register(Heartbeat)
class HeartbeatAdmin(admin.ModelAdmin):
    list_display = ["device", "status", "timestamp"]
    list_filter = ["status"]
    readonly_fields = ["timestamp"]
