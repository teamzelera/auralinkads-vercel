"""
WebSocket consumer — broadcasts real-time device status updates to admin dashboard.
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer


class DeviceStatusConsumer(AsyncWebsocketConsumer):
    GROUP_NAME = "device_status"

    async def connect(self):
        await self.channel_layer.group_add(self.GROUP_NAME, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.GROUP_NAME, self.channel_name)

    async def receive(self, text_data):
        # Clients don't send to this socket — admin dashboard is read-only
        pass

    async def device_status_update(self, event):
        """Called by channel layer when a device status changes."""
        await self.send(text_data=json.dumps({
            "type": "device_status",
            "device_id": event["device_id"],
            "status": event["status"],
            "last_seen": event.get("last_seen"),
        }))
