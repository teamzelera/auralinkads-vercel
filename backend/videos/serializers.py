from rest_framework import serializers
from .models import Video


class VideoSerializer(serializers.ModelSerializer):
    uploaded_by_username = serializers.CharField(source="uploaded_by.username", read_only=True)

    class Meta:
        model = Video
        fields = [
            "id", "title", "cloudinary_url", "cloudinary_public_id",
            "thumbnail", "duration", "rotation", "uploaded_by", "uploaded_by_username", "created_at",
        ]
        read_only_fields = ["id", "uploaded_by", "created_at"]


class VideoUploadSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=300)
    cloudinary_url = serializers.URLField()
    cloudinary_public_id = serializers.CharField(max_length=500, required=False, allow_blank=True)
    thumbnail = serializers.URLField(required=False, allow_blank=True)
    duration = serializers.FloatField(required=False, default=0)
