from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import Playlist, PlaylistVideo, DeviceAssignment
from .serializers import PlaylistSerializer, PlaylistCreateSerializer, DeviceAssignmentSerializer
from devices.models import Device
from videos.models import Video


class PlaylistListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        playlists = Playlist.objects.prefetch_related("playlistvideos__video").all()
        return Response(PlaylistSerializer(playlists, many=True).data)

    def post(self, request):
        serializer = PlaylistCreateSerializer(data=request.data)
        if serializer.is_valid():
            playlist = serializer.save(created_by=request.user)
            return Response(PlaylistSerializer(playlist).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=400)


class PlaylistDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_playlist(self, pk):
        try:
            return Playlist.objects.prefetch_related("playlistvideos__video").get(pk=pk)
        except Playlist.DoesNotExist:
            return None

    def get(self, request, pk):
        playlist = self._get_playlist(pk)
        if not playlist:
            return Response({"error": "Playlist not found."}, status=404)
        return Response(PlaylistSerializer(playlist).data)

    def patch(self, request, pk):
        playlist = self._get_playlist(pk)
        if not playlist:
            return Response({"error": "Playlist not found."}, status=404)
        
        update_fields = []
        for field in ["name", "description", "is_active", "loop_enabled", "title_overlay", "autoplay"]:
            if field in request.data:
                setattr(playlist, field, request.data[field])
                update_fields.append(field)
                
        if update_fields:
            playlist.save(update_fields=update_fields)

        # Replace video list if provided (legacy support, or full overwrite)
        if "video_ids" in request.data:
            playlist.playlistvideos.all().delete()
            for idx, vid_id in enumerate(request.data["video_ids"]):
                PlaylistVideo.objects.create(playlist=playlist, video_id=vid_id, order=idx)
        return Response(PlaylistSerializer(self._get_playlist(pk)).data)

    def delete(self, request, pk):
        playlist = self._get_playlist(pk)
        if not playlist:
            return Response({"error": "Playlist not found."}, status=404)
        playlist.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PlaylistAddVideoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            playlist = Playlist.objects.get(pk=pk)
        except Playlist.DoesNotExist:
            return Response({"error": "Playlist not found."}, status=404)
            
        video_ids = request.data.get("video_ids", [])
        if "video_id" in request.data and not video_ids:
            video_ids = [request.data["video_id"]]
            
        if not video_ids:
            return Response({"error": "video_id or video_ids required"}, status=400)
            
        current_count = playlist.playlistvideos.count()
        added_count = 0
        
        for vid_id in video_ids:
            if not PlaylistVideo.objects.filter(playlist=playlist, video_id=vid_id).exists():
                PlaylistVideo.objects.create(playlist=playlist, video_id=vid_id, order=current_count + added_count)
                added_count += 1
                
        playlist = Playlist.objects.prefetch_related("playlistvideos__video").get(pk=pk)
        return Response(PlaylistSerializer(playlist).data, status=status.HTTP_200_OK)


class PlaylistRemoveVideoView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk, video_id):
        try:
            playlist = Playlist.objects.get(pk=pk)
        except Playlist.DoesNotExist:
            return Response({"error": "Playlist not found."}, status=404)
            
        PlaylistVideo.objects.filter(playlist=playlist, video_id=video_id).delete()
        
        # Reorder remaining
        for idx, pv in enumerate(playlist.playlistvideos.all().order_by('order')):
            if pv.order != idx:
                pv.order = idx
                pv.save(update_fields=['order'])
                
        playlist = Playlist.objects.prefetch_related("playlistvideos__video").get(pk=pk)
        return Response(PlaylistSerializer(playlist).data, status=status.HTTP_200_OK)


class PlaylistReorderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            playlist = Playlist.objects.get(pk=pk)
        except Playlist.DoesNotExist:
            return Response({"error": "Playlist not found."}, status=404)
            
        video_order = request.data.get("video_order", [])
        if not video_order:
            return Response({"error": "video_order required"}, status=400)
            
        # Create a mapping of video_id to order index
        order_map = {str(vid_id): idx for idx, vid_id in enumerate(video_order)}
        
        for pv in playlist.playlistvideos.all():
            vid_str = str(pv.video_id)
            if vid_str in order_map:
                pv.order = order_map[vid_str]
                pv.save(update_fields=['order'])
                
        playlist = Playlist.objects.prefetch_related("playlistvideos__video").get(pk=pk)
        return Response(PlaylistSerializer(playlist).data, status=status.HTTP_200_OK)


class PlaylistSettingsView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            playlist = Playlist.objects.get(pk=pk)
        except Playlist.DoesNotExist:
            return Response({"error": "Playlist not found."}, status=404)
            
        update_fields = []
        for field in ["loop_enabled", "title_overlay", "autoplay", "is_active"]:
            if field in request.data:
                setattr(playlist, field, request.data[field])
                update_fields.append(field)
                
        if update_fields:
            playlist.save(update_fields=update_fields)
            
        playlist = Playlist.objects.prefetch_related("playlistvideos__video").get(pk=pk)
        return Response(PlaylistSerializer(playlist).data, status=status.HTTP_200_OK)

class DeviceAssignmentView(APIView):
    """POST — Assign a playlist to a device. GET — list all assignments."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        assignments = DeviceAssignment.objects.select_related("device", "playlist").all()
        return Response(DeviceAssignmentSerializer(assignments, many=True).data)

    def post(self, request):
        device_id = request.data.get("device_id")
        playlist_id = request.data.get("playlist_id")
        video_id = request.data.get("video_id")

        try:
            device = Device.objects.get(pk=device_id)
        except Device.DoesNotExist:
            return Response({"error": "Device not found."}, status=404)

        playlist = None
        if playlist_id:
            try:
                playlist = Playlist.objects.get(pk=playlist_id)
            except Playlist.DoesNotExist:
                return Response({"error": "Playlist not found."}, status=404)

        video = None
        if video_id:
            try:
                video = Video.objects.get(pk=video_id)
            except Video.DoesNotExist:
                return Response({"error": "Video not found."}, status=404)

        existing = DeviceAssignment.objects.filter(device=device, active=True).first()
        if existing and existing.playlist == playlist and existing.video == video:
            return Response({"status": "already_assigned"}, status=status.HTTP_200_OK)

        assignment, _ = DeviceAssignment.objects.update_or_create(
            device=device,
            defaults={
                "playlist": playlist,
                "video": video,
                "loop_enabled": request.data.get("loop_enabled", True),
                "active": request.data.get("active", True),
                "start_time": request.data.get("start_time"),
                "end_time": request.data.get("end_time"),
            },
        )
        return Response(DeviceAssignmentSerializer(assignment).data, status=status.HTTP_200_OK)
