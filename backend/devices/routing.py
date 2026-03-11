from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/devices/status/$", consumers.DeviceStatusConsumer.as_asgi()),
    re_path(r"ws/device/(?P<device_code>[A-Z0-9-]+)/transfer/$", consumers.FileTransferConsumer.as_asgi()),
]
