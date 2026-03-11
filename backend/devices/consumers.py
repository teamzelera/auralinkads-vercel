"""
WebSocket consumers — broadcasts real-time device status updates and file transfers.
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


class FileTransferConsumer(AsyncWebsocketConsumer):
    """WebSocket for real-time file transfer between phone and TV.
    Path: ws/device/<device_code>/transfer/
    Group: device_transfer_<device_code>
    """

    async def connect(self):
        self.device_code = self.scope["url_route"]["kwargs"]["device_code"]
        self.group_name = f"device_transfer_{self.device_code}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        """Forward messages from phone to TV within the same device group."""
        data = json.loads(text_data)
        await self.channel_layer.group_send(self.group_name, {
            "type": "transfer_message",
            **data,
        })

    # ─── Event handlers ────────────────────────────────────

    async def transfer_message(self, event):
        """Generic passthrough — forwards any transfer event to connected clients."""
        payload = {k: v for k, v in event.items() if k != "type"}
        payload["type"] = event.get("event_type", "transfer_message")
        await self.send(text_data=json.dumps(payload))

    async def transfer_started(self, event):
        await self.send(text_data=json.dumps({
            "type": "transfer_started",
            "file_name": event.get("file_name", ""),
        }))

    async def file_transfer(self, event):
        await self.send(text_data=json.dumps({
            "type": "file_transfer",
            "file_url": event.get("file_url", ""),
            "file_name": event.get("file_name", ""),
            "file_type": event.get("file_type", ""),
            "file_size": event.get("file_size", 0),
            "transfer_id": event.get("transfer_id", ""),
        }))

    async def transfer_completed(self, event):
        await self.send(text_data=json.dumps({
            "type": "transfer_completed",
            "file_name": event.get("file_name", ""),
            "transfer_id": event.get("transfer_id", ""),
        }))

    async def transfer_failed(self, event):
        await self.send(text_data=json.dumps({
            "type": "transfer_failed",
            "file_name": event.get("file_name", ""),
            "error": event.get("error", ""),
        }))
