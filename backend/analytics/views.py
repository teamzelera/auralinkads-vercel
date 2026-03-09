from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta

from devices.models import Device, Heartbeat
from videos.models import Video
from playlists.models import Playlist, DeviceAssignment


class DashboardStatsView(APIView):
    """GET — Returns summary stats for admin dashboard."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Update stale device statuses
        threshold = timezone.now() - timedelta(seconds=90)
        Device.objects.filter(
            last_seen__lt=threshold, status=Device.STATUS_ONLINE
        ).update(status=Device.STATUS_OFFLINE)

        total_devices = Device.objects.count()
        online_devices = Device.objects.filter(status=Device.STATUS_ONLINE).count()
        offline_devices = Device.objects.filter(status=Device.STATUS_OFFLINE).count()
        total_videos = Video.objects.count()
        total_playlists = Playlist.objects.count()
        active_assignments = DeviceAssignment.objects.filter(active=True).count()

        return Response({
            "total_devices": total_devices,
            "online_devices": online_devices,
            "offline_devices": offline_devices,
            "total_videos": total_videos,
            "total_playlists": total_playlists,
            "active_assignments": active_assignments,
        })


class DeviceUptimeView(APIView):
    """GET — Returns uptime data per device for analytics page."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        devices = Device.objects.all()
        data = []
        last_24h = timezone.now() - timedelta(hours=24)

        for device in devices:
            heartbeat_count = Heartbeat.objects.filter(
                device=device, timestamp__gte=last_24h
            ).count()
            # Each heartbeat represents 30s of uptime
            uptime_seconds = heartbeat_count * 30
            uptime_pct = min(round((uptime_seconds / 86400) * 100, 1), 100)

            data.append({
                "device_id": str(device.id),
                "device_name": device.name,
                "status": device.status,
                "last_seen": device.last_seen.isoformat() if device.last_seen else None,
                "heartbeat_count_24h": heartbeat_count,
                "uptime_pct_24h": uptime_pct,
            })

        return Response(data)
