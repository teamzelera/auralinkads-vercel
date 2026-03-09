"""
Devices views — Admin endpoints for device management + Device-facing endpoints.
"""
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

from .models import Device, Heartbeat
from .serializers import DeviceSerializer, DeviceCreateSerializer, DeviceAuthSerializer, HeartbeatSerializer
from .authentication import DeviceUser
from playlists.models import DeviceAssignment
from playlists.serializers import DeviceAssignmentSerializer


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
