"""
Device Token Authentication — devices authenticate with `Authorization: Device <token>`
"""
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import Device


class DeviceUser:
    """Wrapper so DRF sees a device as a user-like object."""
    def __init__(self, device):
        self.device = device
        self.is_authenticated = True
        self.pk = device.pk

    def __str__(self):
        return f"Device:{self.device.device_code}"


class DeviceTokenAuthentication(BaseAuthentication):
    keyword = "Device"

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith(f"{self.keyword} "):
            return None

        token = auth_header[len(self.keyword) + 1:].strip()
        if not token:
            return None

        try:
            device = Device.objects.get(auth_token=token, is_active=True)
        except Device.DoesNotExist:
            raise AuthenticationFailed("Invalid or inactive device token.")

        return (DeviceUser(device), token)

    def authenticate_header(self, request):
        return self.keyword
