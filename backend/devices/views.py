"""
Devices views — Admin endpoints for device management + Device-facing endpoints.
"""
import os
import uuid
import secrets
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Device, Heartbeat, FileTransfer
from .serializers import (
    DeviceSerializer, DeviceCreateSerializer, DeviceAuthSerializer,
    HeartbeatSerializer, FileTransferSerializer,
)
from .authentication import DeviceUser
from playlists.models import DeviceAssignment
from playlists.serializers import DeviceAssignmentSerializer

# ─── Constants ─────────────────────────────────────────────────────
MAX_TRANSFER_SIZE = 200 * 1024 * 1024  # 200 MB
ALLOWED_TRANSFER_TYPES = ["video/mp4", "video/webm", "video/quicktime"]


def _broadcast_status_change(device_id, status_val, last_seen=None):
    """Broadcast device status change via WebSocket channel layer."""
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "device_status",
        {
            "type": "device_status_update",
            "device_id": str(device_id),
            "status": status_val,
            "last_seen": last_seen.isoformat() if last_seen else None,
        },
    )


# ─── Admin Device Views ────────────────────────────────────────────

class DeviceListCreateView(APIView):
    """GET (list all devices) + POST (register device with generated code)."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Mark stale devices as offline before responding
        threshold = timezone.now() - timedelta(seconds=settings.DEVICE_OFFLINE_THRESHOLD)
        Device.objects.filter(last_seen__lt=threshold, status=Device.STATUS_ONLINE).update(
            status=Device.STATUS_OFFLINE
        )
        devices = Device.objects.all()
        return Response(DeviceSerializer(devices, many=True).data)

    def post(self, request):
        serializer = DeviceCreateSerializer(data=request.data)
        if serializer.is_valid():
            # Generate unique 8-char code: AUR-XXXX
            code = None
            for _ in range(10):
                candidate = "AUR-" + secrets.token_hex(2).upper()
                if not Device.objects.filter(device_code=candidate).exists():
                    code = candidate
                    break
            if not code:
                return Response({"error": "Could not generate unique code."}, status=500)

            device = serializer.save(device_code=code)
            return Response({
                **DeviceSerializer(device).data,
                "device_code": device.device_code,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeviceDetailView(APIView):
    """GET / PATCH / DELETE a specific device."""
    permission_classes = [IsAuthenticated]

    def _get_device(self, pk):
        try:
            return Device.objects.get(pk=pk)
        except Device.DoesNotExist:
            return None

    def get(self, request, pk):
        device = self._get_device(pk)
        if not device:
            return Response({"error": "Device not found."}, status=404)
        return Response(DeviceSerializer(device).data)

    def patch(self, request, pk):
        device = self._get_device(pk)
        if not device:
            return Response({"error": "Device not found."}, status=404)
        serializer = DeviceSerializer(device, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        device = self._get_device(pk)
        if not device:
            return Response({"error": "Device not found."}, status=404)
        device.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class GenerateDeviceCodeView(APIView):
    """POST — generate a new device code without creating the device record."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Generate a unique device code and create a pending device."""
        serializer = DeviceCreateSerializer(data=request.data)
        if serializer.is_valid():
            for _ in range(10):
                candidate = "AUR-" + secrets.token_hex(2).upper()
                if not Device.objects.filter(device_code=candidate).exists():
                    device = serializer.save(device_code=candidate)
                    return Response({
                        **DeviceSerializer(device).data,
                        "message": "Device created. Use the device_code to authenticate on the device.",
                    }, status=201)
            return Response({"error": "Could not generate unique code."}, status=500)
        return Response(serializer.errors, status=400)


# ─── Device Self-Authentication ────────────────────────────────────

class DeviceAuthView(APIView):
    """POST — device submits its code, receives an auth token."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = DeviceAuthSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        code = serializer.validated_data["device_code"].upper()
        try:
            device = Device.objects.get(device_code=code, is_active=True)
        except Device.DoesNotExist:
            return Response({"error": "Invalid or inactive device code."}, status=404)

        token = device.generate_auth_token()
        device.status = Device.STATUS_ONLINE
        device.last_seen = timezone.now()
        device.save(update_fields=["status", "last_seen"])

        _broadcast_status_change(device.pk, Device.STATUS_ONLINE, device.last_seen)

        return Response({
            "device_token": token,
            "device": DeviceSerializer(device).data,
        })


# ─── Device Self-Service (requires Device token) ───────────────────

class DeviceHeartbeatView(APIView):
    """POST — device sends heartbeat to update last_seen and status."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not isinstance(request.user, DeviceUser):
            return Response({"error": "Device token required."}, status=403)

        device = request.user.device
        playback_status = request.data.get("status", "playing")

        now = timezone.now()
        device.status = Device.STATUS_ONLINE
        device.last_seen = now
        device.save(update_fields=["status", "last_seen"])

        Heartbeat.objects.create(device=device, status=playback_status)

        _broadcast_status_change(device.pk, Device.STATUS_ONLINE, now)

        return Response({"ok": True, "timestamp": now.isoformat()})


class DeviceAssignmentView(APIView):
    """GET — device retrieves its current content assignment."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not isinstance(request.user, DeviceUser):
            return Response({"error": "Device token required."}, status=403)

        device = request.user.device
        try:
            assignment = DeviceAssignment.objects.select_related(
                "playlist"
            ).prefetch_related(
                "playlist__playlistvideos__video"
            ).get(device=device, active=True)
            return Response(DeviceAssignmentSerializer(assignment).data)
        except DeviceAssignment.DoesNotExist:
            return Response({"assignment": None})


class DeviceRestartView(APIView):
    """POST — admin triggers a restart signal for a device (via WebSocket)."""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            device = Device.objects.get(pk=pk)
        except Device.DoesNotExist:
            return Response({"error": "Device not found."}, status=404)

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "device_status",
            {
                "type": "device_status_update",
                "device_id": str(device.pk),
                "status": "restart_requested",
                "last_seen": None,
            },
        )
        return Response({"ok": True, "message": f"Restart signal sent to {device.name}."})


# ─── Device Local Video Metadata ──────────────────────────────────

class LocalVideoMetadataView(APIView):
    """POST — device reports local video metadata for analytics.
    Does NOT receive the video file itself; playback is entirely client-side.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        device_code = request.data.get("device_code", "")
        video_name  = request.data.get("video_name", "")
        video_type  = request.data.get("type", "local")

        if not device_code or not video_name:
            return Response(
                {"error": "device_code and video_name are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "ok": True,
                "message": f"Local video '{video_name}' recorded for device {device_code}.",
            },
            status=status.HTTP_201_CREATED,
        )


# ─── Phone → TV File Transfer ─────────────────────────────────────

class SendFileView(APIView):
    """POST — phone uploads a video file to be transferred to a TV device.
    The file is saved to media/transfers/ and the TV is notified via WebSocket.
    """
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        device_code = request.data.get("device_code", "").upper()
        file_obj = request.FILES.get("file")

        if not device_code or not file_obj:
            return Response(
                {"error": "device_code and file are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate device
        try:
            device = Device.objects.get(device_code=device_code, is_active=True)
        except Device.DoesNotExist:
            return Response(
                {"error": "Invalid or inactive device code."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Validate file type
        if file_obj.content_type not in ALLOWED_TRANSFER_TYPES:
            return Response(
                {"error": f"Unsupported file type: {file_obj.content_type}. Allowed: mp4, webm, quicktime."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate file size
        if file_obj.size > MAX_TRANSFER_SIZE:
            return Response(
                {"error": f"File too large ({file_obj.size // (1024*1024)} MB). Maximum is 200 MB."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Save file to media/transfers/
        transfer_dir = os.path.join(settings.MEDIA_ROOT, "transfers")
        os.makedirs(transfer_dir, exist_ok=True)

        safe_name = f"{uuid.uuid4().hex[:8]}_{file_obj.name}"
        file_path = os.path.join(transfer_dir, safe_name)

        with open(file_path, "wb+") as dest:
            for chunk in file_obj.chunks():
                dest.write(chunk)

        file_url = f"{settings.MEDIA_URL}transfers/{safe_name}"

        # Create transfer record
        transfer = FileTransfer.objects.create(
            device=device,
            file_name=file_obj.name,
            file_url=file_url,
            file_type=file_obj.content_type,
            file_size=file_obj.size,
            status=FileTransfer.STATUS_SENT,
        )

        # Send WebSocket events to TV
        channel_layer = get_channel_layer()
        group_name = f"device_transfer_{device_code}"

        # 1. transfer_started
        async_to_sync(channel_layer.group_send)(group_name, {
            "type": "transfer_started",
            "file_name": file_obj.name,
        })

        # 2. file_transfer (with download URL)
        async_to_sync(channel_layer.group_send)(group_name, {
            "type": "file_transfer",
            "file_url": file_url,
            "file_name": file_obj.name,
            "file_type": file_obj.content_type,
            "file_size": file_obj.size,
            "transfer_id": str(transfer.id),
        })

        return Response({
            "status": "file_sent",
            "device": device_code,
            "file_name": file_obj.name,
            "file_url": file_url,
            "transfer_id": str(transfer.id),
        }, status=status.HTTP_201_CREATED)


class TransferHistoryView(APIView):
    """GET — list transfer history for a device."""
    permission_classes = [AllowAny]

    def get(self, request):
        device_code = request.query_params.get("device_code", "").upper()
        if not device_code:
            return Response({"error": "device_code is required."}, status=400)

        try:
            device = Device.objects.get(device_code=device_code)
        except Device.DoesNotExist:
            return Response({"error": "Device not found."}, status=404)

        transfers = FileTransfer.objects.filter(device=device)[:50]
        return Response(FileTransferSerializer(transfers, many=True).data)


class TransferConfirmView(APIView):
    """POST — TV confirms a file was downloaded successfully.
    Optionally deletes the temp file from server.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        transfer_id = request.data.get("transfer_id", "")
        if not transfer_id:
            return Response({"error": "transfer_id is required."}, status=400)

        try:
            transfer = FileTransfer.objects.get(id=transfer_id)
        except FileTransfer.DoesNotExist:
            return Response({"error": "Transfer not found."}, status=404)

        transfer.status = FileTransfer.STATUS_RECEIVED
        transfer.save(update_fields=["status"])

        # Optionally delete temp file
        file_path = os.path.join(settings.BASE_DIR, transfer.file_url.lstrip("/"))
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                pass

        # Notify via WebSocket
        channel_layer = get_channel_layer()
        group_name = f"device_transfer_{transfer.device.device_code}"
        async_to_sync(channel_layer.group_send)(group_name, {
            "type": "transfer_completed",
            "file_name": transfer.file_name,
            "transfer_id": str(transfer.id),
        })

        return Response({"ok": True, "message": "Transfer confirmed."})
