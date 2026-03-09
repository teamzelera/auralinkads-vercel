import uuid
import secrets
from django.db import models


class Device(models.Model):
    STATUS_ONLINE = "online"
    STATUS_OFFLINE = "offline"
    STATUS_CHOICES = [(STATUS_ONLINE, "Online"), (STATUS_OFFLINE, "Offline")]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    device_code = models.CharField(max_length=12, unique=True)
    auth_token = models.CharField(max_length=64, unique=True, blank=True)
    location = models.CharField(max_length=300, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_OFFLINE)
    last_seen = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.device_code})"

    def generate_auth_token(self):
        self.auth_token = secrets.token_hex(32)
        self.save(update_fields=["auth_token"])
        return self.auth_token


class Heartbeat(models.Model):
    PLAYBACK_STATUS_CHOICES = [
        ("playing", "Playing"),
        ("idle", "Idle"),
        ("error", "Error"),
    ]

    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="heartbeats")
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=PLAYBACK_STATUS_CHOICES, default="playing")

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.device.name} — {self.timestamp}"
