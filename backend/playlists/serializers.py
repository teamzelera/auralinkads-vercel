from rest_framework import serializers
from .models import Playlist, PlaylistVideo, DeviceAssignment
from videos.serializers import VideoSerializer


class PlaylistVideoSerializer(serializers.ModelSerializer):
    video = VideoSerializer(read_only=True)
    video_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = PlaylistVideo
        fields = ["id", "video", "video_id", "order"]


class PlaylistSerializer(serializers.ModelSerializer):
    videos = PlaylistVideoSerializer(source="playlistvideos", many=True, read_only=True)
    created_by_username = serializers.CharField(source="created_by.username", read_only=True)
    video_count = serializers.SerializerMethodField()

    class Meta:
        model = Playlist
        fields = [
            "id", "name", "description", "is_active", "loop_enabled", 
            "title_overlay", "autoplay", "videos", "video_count", 
            "created_by", "created_by_username", "created_at"
        ]
        read_only_fields = ["id", "created_by", "created_at"]

    def get_video_count(self, obj):
        return obj.playlistvideos.count()


class PlaylistCreateSerializer(serializers.ModelSerializer):
    video_ids = serializers.ListField(child=serializers.UUIDField(), write_only=True, required=False)

    class Meta:
        model = Playlist
        fields = ["name", "description", "is_active", "loop_enabled", "title_overlay", "autoplay", "video_ids"]

    def create(self, validated_data):
        video_ids = validated_data.pop("video_ids", [])
        playlist = Playlist.objects.create(**validated_data)
        for idx, vid_id in enumerate(video_ids):
            PlaylistVideo.objects.create(playlist=playlist, video_id=vid_id, order=idx)
        return playlist


class DeviceAssignmentSerializer(serializers.ModelSerializer):
    playlist = PlaylistSerializer(read_only=True)
    video = VideoSerializer(read_only=True)
    playlist_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    video_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = DeviceAssignment
        fields = [
            "id", "device", "device_id", "playlist", "playlist_id", "video", "video_id",
            "loop_enabled", "active", "start_time", "end_time", "updated_at",
        ]
        read_only_fields = ["id", "device", "updated_at"]
