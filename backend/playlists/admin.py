from django.contrib import admin
from .models import Playlist, PlaylistVideo, DeviceAssignment


@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ["name", "created_by", "created_at"]
    search_fields = ["name"]
    readonly_fields = ["id", "created_at"]


@admin.register(PlaylistVideo)
class PlaylistVideoAdmin(admin.ModelAdmin):
    list_display = ["playlist", "video", "order"]
    list_filter = ["playlist"]


@admin.register(DeviceAssignment)
class DeviceAssignmentAdmin(admin.ModelAdmin):
    list_display = ["device", "playlist", "active", "loop_enabled", "updated_at"]
    list_filter = ["active"]
