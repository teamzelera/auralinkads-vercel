from rest_framework import serializers
from .models import Device, Heartbeat, FileTransfer


class DeviceSerializer(serializers.ModelSerializer):
    active_content = serializers.SerializerMethodField()

    class Meta:
        model = Device
        fields = [
            "id", "name", "device_code", "location",
            "status", "last_seen", "is_active", "created_at", "active_content"
        ]
        read_only_fields = ["id", "device_code", "status", "last_seen", "created_at"]

    def get_active_content(self, obj):
        if hasattr(obj, "assignment") and obj.assignment and obj.assignment.active:
            if obj.assignment.playlist:
                return f"Playlist: {obj.assignment.playlist.name}"
            if obj.assignment.video:
                return f"Video: {obj.assignment.video.title}"
        return None


class DeviceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ["name", "location"]


class DeviceAuthSerializer(serializers.Serializer):
    device_code = serializers.CharField(max_length=12)


class HeartbeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Heartbeat
        fields = ["id", "device", "timestamp", "status"]
        read_only_fields = ["id", "device", "timestamp"]


class FileTransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileTransfer
        fields = ["id", "device", "file_name", "file_url", "file_type", "file_size", "status", "created_at"]
        read_only_fields = ["id", "created_at"]

