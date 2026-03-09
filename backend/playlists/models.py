"""
Playlists app — models: Playlist, PlaylistVideo, DeviceAssignment
"""
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from devices.models import Device
from videos.models import Video

User = get_user_model()


class Playlist(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=300)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="playlists")
    description = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)
    loop_enabled = models.BooleanField(default=True)
    title_overlay = models.CharField(max_length=300, blank=True, default="")
    autoplay = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class PlaylistVideo(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, related_name="playlistvideos")
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name="playlist_entries")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        unique_together = [["playlist", "video"]]

    def __str__(self):
        return f"{self.playlist.name} → {self.video.title} (#{self.order})"


class DeviceAssignment(models.Model):
    device = models.OneToOneField(Device, on_delete=models.CASCADE, related_name="assignment")
    playlist = models.ForeignKey(Playlist, on_delete=models.SET_NULL, null=True, blank=True, related_name="assignments")
    video = models.ForeignKey(Video, on_delete=models.SET_NULL, null=True, blank=True, related_name="assignments")
    loop_enabled = models.BooleanField(default=True)
    active = models.BooleanField(default=True)
    start_time = models.TimeField(null=True, blank=True, help_text="Start time for scheduled playback")
    end_time = models.TimeField(null=True, blank=True, help_text="End time for scheduled playback")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.device.name} → {self.playlist.name if self.playlist else 'No playlist'}"
