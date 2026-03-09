"""
Videos views — Admin uploads videos via Cloudinary; endpoints register metadata.
"""
import cloudinary
import cloudinary.uploader
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import Video
from .serializers import VideoSerializer, VideoUploadSerializer


class VideoListCreateView(APIView):
    """GET all videos + POST to upload a new video to Cloudinary."""
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        videos = Video.objects.all()
        return Response(VideoSerializer(videos, many=True).data)

    def post(self, request):
        # Case 1: File upload (multipart) — we upload to Cloudinary ourselves
        if "file" in request.FILES:
            file = request.FILES["file"]
            title = request.data.get("title", file.name.rsplit(".", 1)[0])

            cloudinary.config(
                cloud_name=settings.CLOUDINARY_STORAGE.get("CLOUD_NAME"),
                api_key=settings.CLOUDINARY_STORAGE.get("API_KEY"),
                api_secret=settings.CLOUDINARY_STORAGE.get("API_SECRET"),
            )

            try:
                result = cloudinary.uploader.upload(
                    file,
                    resource_type="video",
                    folder="auralink/videos",
                )
            except Exception as e:
                return Response({"error": f"Cloudinary upload failed: {str(e)}"}, status=500)

            video = Video.objects.create(
                title=title,
                cloudinary_url=result.get("secure_url", ""),
                cloudinary_public_id=result.get("public_id", ""),
                thumbnail=result.get("thumbnail_url", ""),
                duration=result.get("duration", 0),
                uploaded_by=request.user,
            )
            return Response(VideoSerializer(video).data, status=status.HTTP_201_CREATED)

        # Case 2: Pre-uploaded (Cloudinary widget) — just register the metadata
        serializer = VideoUploadSerializer(data=request.data)
        if serializer.is_valid():
            video = Video.objects.create(
                uploaded_by=request.user,
                **serializer.validated_data,
            )
            return Response(VideoSerializer(video).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VideoDetailView(APIView):
    """GET / DELETE a specific video."""
    permission_classes = [IsAuthenticated]

    def _get_video(self, pk):
        try:
            return Video.objects.get(pk=pk)
        except Video.DoesNotExist:
            return None

    def get(self, request, pk):
        video = self._get_video(pk)
        if not video:
            return Response({"error": "Video not found."}, status=404)
        return Response(VideoSerializer(video).data)

    def delete(self, request, pk):
        video = self._get_video(pk)
        if not video:
            return Response({"error": "Video not found."}, status=404)

        # Optional: delete from Cloudinary too
        if video.cloudinary_public_id:
            try:
                cloudinary.config(
                    cloud_name=settings.CLOUDINARY_STORAGE.get("CLOUD_NAME"),
                    api_key=settings.CLOUDINARY_STORAGE.get("API_KEY"),
                    api_secret=settings.CLOUDINARY_STORAGE.get("API_SECRET"),
                )
                cloudinary.uploader.destroy(video.cloudinary_public_id, resource_type="video")
            except Exception:
                pass  # Don't block deletion if Cloudinary cleanup fails

        video.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class VideoRotateView(APIView):
    """PATCH — Updates a video's rotation by 90-degree increments."""
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            video = Video.objects.get(pk=pk)
        except Video.DoesNotExist:
            return Response({"error": "Video not found."}, status=404)
            
        video.rotation = (video.rotation + 90) % 360
        video.save(update_fields=["rotation"])
        return Response(VideoSerializer(video).data, status=status.HTTP_200_OK)


class CloudinarySignatureView(APIView):
    """GET — returns a signed Cloudinary upload signature for frontend widget."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        import time, hashlib
        timestamp = int(time.time())
        api_secret = settings.CLOUDINARY_STORAGE.get("API_SECRET", "")
        folder = "auralink/videos"
        params_to_sign = f"folder={folder}&timestamp={timestamp}{api_secret}"
        signature = hashlib.sha1(params_to_sign.encode()).hexdigest()
        return Response({
            "signature": signature,
            "timestamp": timestamp,
            "cloud_name": settings.CLOUDINARY_STORAGE.get("CLOUD_NAME"),
            "api_key": settings.CLOUDINARY_STORAGE.get("API_KEY"),
            "folder": folder,
        })
