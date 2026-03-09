"""
Videos app models — stores video metadata, Cloudinary hosts the actual files.
"""
import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Video(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=300)
    cloudinary_url = models.URLField(max_length=1000)
    cloudinary_public_id = models.CharField(max_length=500, blank=True)
    thumbnail = models.URLField(max_length=1000, blank=True)
    duration = models.FloatField(default=0, help_text="Duration in seconds")
    rotation = models.IntegerField(default=0, help_text="Rotation angle in degrees (0, 90, 180, 270)")
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="videos")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
